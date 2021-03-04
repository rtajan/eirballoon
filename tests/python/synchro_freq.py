#!/usr/bin/env python3

import sys
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib')

from py_aff3ct.module.py_module import Py_Module
import numpy as np
import py_aff3ct
from scipy import signal
from scipy.signal import welch
import matplotlib.pyplot as plt
import math

class Frequency_Synchronizer(Py_Module):

    def pWelch(self,s_recv,M,overlap,Nfft):
        F,P = welch(s_recv**M)
        idx = np.argmax(P)
        return F[idx]


    def synchronize(self,s_recv,s_synch,M,overlap,Nfft):
        f = self.pWelch(s_recv,M,overlap,Nfft)
        s_recv1 = s_recv.reshape(np.size(s_recv,1)//2,2)
        s_desynch1 = np.ndarray(shape = (np.size(s_recv,1)//2,2),  dtype = np.float32)
        for i in range(np.size(s_recv1,0)):
            s_desynch1[i]=np.dot(s_recv1[i],np.array([[np.cos(2*np.pi*f*(i+1)),-np.sin(2*np.pi*f*(i+1))] , [-np.sin(2*np.pi*f*(i+1)),np.cos(2*np.pi*f*(i+1))]]))
        s_desynch = s_desynch1.reshape(1,np.size(s_recv,1))
        return 0

    def desynchronize(self,s_recv,s_desynch):
        print("received",s_recv)
        s_recv1 = s_recv.reshape(np.size(s_recv,1)//2,2)
        print("reshpe",s_recv1)
        s_desynch1 = np.ndarray(shape = (np.size(s_recv,1)//2,2),  dtype = np.float32)
        for i in range(np.size(s_recv1,0)):
            s_desynch1[i]=np.dot(s_recv1[i],np.array([[np.cos(2*np.pi*1.8*(i+1)),np.sin(2*np.pi*1.8*(i+1))] , [np.sin(2*np.pi*1.8*(i+1)),np.cos(2*np.pi*1.8*(i+1))]]))
        s_desynch = s_desynch1.reshape(1,np.size(s_recv,1))
        print("sdes",s_desynch1)
        print("sdes",s_desynch)
        return 0

    def __init__(self,N):
        Py_Module.__init__(self)
        self.name = "Frequency_Synchronizer"
        t_synch = self.create_task("synchronize")
        s_in = self.create_socket_in (t_synch, "IN", N, np.float32)
        s_in_M = self.create_socket_in (t_synch, "IN_m", 1, np.int32)
        s_in_overlap = self.create_socket_in (t_synch, "IN_over",1, np.int32)
        s_in_nfft = self.create_socket_in (t_synch, "IN_nfft", 1, np.int32)
        s_out = self.create_socket_out(t_synch, "OUT", N, np.float32)

        self.create_codelet(t_synch, lambda slf, lsk, fid: slf.synchronize(lsk[s_in], lsk[s_in_M], lsk[s_in_overlap], lsk[s_in_nfft], lsk[s_out],))

        t_desynch = self.create_task("desynchronize")
        s_in1 = self.create_socket_in (t_desynch, "IN_1", N, np.float32)
        s_out1 = self.create_socket_out(t_desynch, "OUT_1", N, np.float32)
        self.create_codelet(t_desynch, lambda slf, lsk, fid: slf.desynchronize(lsk[s_in1], lsk[s_out1]))



N = 128
bps = np.ndarray(shape = (1,1),  dtype = np.int32)
bps[0] = 4
Ns = N//bps[0]


overlap = np.ndarray(shape = (1,1),  dtype = np.int32)
overlap[0] = N//16

Nfft = np.ndarray(shape = (1,1),  dtype = np.int32)
Nfft[0]=256

sigma = np.ndarray(shape = (1,1),  dtype = np.float32)
sigma[0] = 0

src = py_aff3ct.module.source.Source_random(N)
cstl = py_aff3ct.tools.constellation.Constellation_QAM(bps)
mdm  = py_aff3ct.module.modem.Modem_generic(N, cstl)
chn  = py_aff3ct.module.channel.Channel_AWGN_LLR(2*Ns)
syn = Frequency_Synchronizer(2*Ns)

src("generate").info()
mdm("modulate").info()
chn("add_noise").info()
mdm("demodulate").info()
syn("synchronize").info()

mdm["modulate::X_N1"].bind(src["generate::U_K"])
chn["add_noise::X_N"].bind(mdm["modulate::X_N2"])
syn["desynchronize::IN_1"].bind(chn[ "add_noise::Y_N"])
syn["synchronize::IN"].bind(syn["desynchronize::OUT_1"])
mdm["demodulate::Y_N1"].bind(syn["synchronize::OUT"])


chn[ 'add_noise::CP'].bind(sigma)
mdm['demodulate::CP'].bind(sigma)
syn["synchronize::IN_m"].bind(bps)
syn["synchronize::IN_over"].bind(overlap)
syn["synchronize::IN_nfft"].bind(Nfft)


src('generate').debug = True
mdm('modulate').debug = True
chn('add_noise').debug = True
syn('synchronize').debug = True
syn('desynchronize').debug = True
mdm('demodulate').debug = True

src("generate").exec()
mdm("modulate").exec()
chn("add_noise").exec()
syn("desynchronize").exec()
syn("synchronize").exec()
mdm("demodulate").exec()
