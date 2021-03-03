#!/usr/bin/env python3


import sys
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib')

from py_aff3ct.module.py_module import Py_Module
import numpy as np
import py_aff3ct
from scipy.signal import welch
from scipy.signal.windows import hann
import matplotlib.pyplot as plt
import math

class Frequency_Synchronizer(Py_Module):

    def pWelch(self,s_recv,M): #,win,overlap,Nfft):
        #F,P = welch(s_recv**M,window=win,noverlap=overlap,nfft=Nfft,return_onesided=False)
        F,P = welch(s_recv**M,nfft=1024)
        #print("fréquences",F)
        #print("periodgramme",P)
        idx = np.argmax(P)
        #print("indice",idx)
        return F[idx]


    def synchronize(self,s_recv,s_synch,M): #,win,overlap,Nfft):
        s_recv1 = s_recv.reshape(np.size(s_recv,1)//2,2)
        N = np.dot((np.arange(np.size(s_recv,1)//2)).reshape(4,1),(np.array([np.cos(2*np.pi*self.pWelch(s_recv,M)) ,np.sin(2*np.pi*self.pWelch(s_recv,M))])).reshape(1,2))
        s_synch = (s_recv1*N).reshape(1,np.size(s_recv,1));
        return 0

    def desynchronize(self,s_recv,s_desynch): #,win,overlap,Nfft):
        s_recv1 = s_recv.reshape(np.size(s_recv,1)//2,2)
        N = np.dot((np.arange(np.size(s_recv,1)//2)).reshape(4,1),(np.array([np.cos(2*np.pi*12.5) ,np.sin(2*np.pi*12.5)])).reshape(1,2))
        print(N)
        print(s_recv1)
        s_desynch = (s_recv1*N).reshape(1,np.size(s_recv,1));
        print(s_desynch)
        return 0

    def __init__(self,N):
        Py_Module.__init__(self)
        self.name = "Frequency_Synchronizer"
        t_synch = self.create_task("synchronize")
        s_in = self.create_socket_in (t_synch, "IN", N, np.float32)
        s_in_M = self.create_socket_in (t_synch, "IN_m", 1, np.int32)
        #s_in_win = self.create_socket_in (t_synch, "IN_win", N//2, np.float32)
        #s_in_overlap = self.create_socket_in (t_synch, "IN_over",1, np.int32)
        #s_in_nfft = self.create_socket_in (t_synch, "IN_nfft", 1, np.int32)
        s_out = self.create_socket_out(t_synch, "OUT", N, np.float32)

        #self.create_codelet(t_synch, lambda slf, lsk, fid: slf.synchronize(lsk[s_in], lsk[s_in_M], lsk[s_in_win], lsk[s_in_overlap], lsk[s_in_nfft], lsk[s_out],))
        self.create_codelet(t_synch, lambda slf, lsk, fid: slf.synchronize(lsk[s_in], lsk[s_in_M], lsk[s_out]))

        t_desynch = self.create_task("desynchronize")
        s_in1 = self.create_socket_in (t_desynch, "IN_1", N, np.float32)
        s_out1 = self.create_socket_out(t_desynch, "OUT_1", N, np.float32)
        self.create_codelet(t_desynch, lambda slf, lsk, fid: slf.desynchronize(lsk[s_in1], lsk[s_out1]))

N = 16
bps = np.ndarray(shape = (1,1),  dtype = np.int32)
bps[0] = 4
Ns = N//bps

#win = np.ndarray(shape = (1,Ns),  dtype = np.float32)
#win[:] = hann(Ns)

#overlap = np.ndarray(shape = (1,1),  dtype = np.int32)
#overlap[0] = N//8

#Nfft = np.ndarray(shape = (1,1),  dtype = np.int32)
#Nfft[0]=256

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
#syn["synchronize::IN_over"].bind(overlap)
#syn["synchronize::IN_win"].bind(win)
#syn["synchronize::IN_nfft"].bind(Nfft)


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
