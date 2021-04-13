#!/usr/bin/env python3


import sys
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib')

from py_aff3ct.module.py_module import Py_Module
import numpy as np
import py_aff3ct
import math
from scipy.fftpack import fft, fftfreq
import matplotlib.pyplot as plt

class Frequency_Synchronizer(Py_Module):


    def synchronize(self,s_recv,M,Ts,in_fft,alpha,s_synch,out_fft):
        yl = np.array(s_recv[0, ::2] + 1j *s_recv[0, 1::2],dtype=np.complex64)

        y = alpha* (np.abs(fft(yl**M)))**2 + (1-alpha)* in_fft
        f =fftfreq(np.size(s_recv,1)//2, Ts)

        idx = np.argmax(y)

        f_synch = f[0,idx]/M
        t = np.arange(0,(len(yl))*Ts,Ts)
        yl = np.array(yl* np.exp(-1j*2*np.pi*f_synch*t),dtype=np.complex64)

        s_synch[0, ::2] = np.real(yl)
        s_synch[0, 1::2] = np.imag(yl)

        out_fft[0, :] = y

        print("f is",f_synch)
        return 0

    def desynchronize(self,s_recv,Ts,s_desynch):
        yl = np.array(s_recv[0, ::2] + 1j *s_recv[0, 1::2],dtype=np.complex64)
        t = np.arange(0,(len(yl))*Ts,Ts)
        yl = np.array(yl* np.exp(1j*2*np.pi*0.88*t),dtype=np.complex64)

        s_desynch[0, ::2] = np.real(yl)
        s_desynch[0, 1::2] = np.imag(yl)
        return 0

    def __init__(self,N,):
        Py_Module.__init__(self)
        self.name = "Frequency_Synchronizer"
        t_synch = self.create_task("synchronize")
        s_in = self.create_socket_in (t_synch, "IN", N, np.float32)
        s_in_M = self.create_socket_in (t_synch, "IN_m", 1, np.int32)
        s_in_ts = self.create_socket_in (t_synch, "IN_ts", 1, np.float32)
        s_in_fft = self.create_socket_in (t_synch, "IN_fft", N//2, np.float32)
        s_in_alpha = self.create_socket_in (t_synch, "IN_alpha", 1, np.float32)
        s_out_fft = self.create_socket_out (t_synch, "OUT_fft", N//2, np.float32)
        s_out = self.create_socket_out (t_synch, "OUT", N, np.float32)

        self.create_codelet(t_synch, lambda slf, lsk, fid: slf.synchronize(lsk[s_in], lsk[s_in_M], lsk[s_in_ts],
            lsk[s_in_fft], lsk[s_in_alpha], lsk[s_out], lsk[s_out_fft]))

        t_desynch = self.create_task("desynchronize")
        s_in1 = self.create_socket_in (t_desynch, "IN_1", N, np.float32)
        s_in_ts1 = self.create_socket_in (t_desynch, "IN_ts1", 1, np.float32)
        s_out1 = self.create_socket_out (t_desynch, "OUT_1", N, np.float32)

        self.create_codelet(t_desynch, lambda slf, lsk, fid: slf.desynchronize(lsk[s_in1], lsk[s_in_ts1], lsk[s_out1]))


N = 2048

M = np.ndarray(shape = (1,1),  dtype = np.int32)
M[0] = 4

Ns = N//M[0]

alpha = np.ndarray(shape = (1,1),  dtype = np.float32)
alpha[0] = 0.2

in_fft= np.ndarray(shape = (1,Ns[0]),  dtype = np.float32)
in_fft[0, :] = np.zeros(Ns[0])

sigma = np.ndarray(shape = (1,1),  dtype = np.float32)
sigma[0] = 0.0001

Ts = np.ndarray(shape = (1,1),  dtype = np.float32)
Ts[0] = 0.01

for i in range(10):

    src = py_aff3ct.module.source.Source_random(N)
    cstl = py_aff3ct.tools.constellation.Constellation_QAM(M)
    mdm  = py_aff3ct.module.modem.Modem_generic(N, cstl)
    chn  = py_aff3ct.module.channel.Channel_AWGN_LLR(2*Ns)
    dec  = py_aff3ct.module.decoder.Decoder_repetition_std(N,N)
    syn = Frequency_Synchronizer(2*Ns)


    mdm["modulate::X_N1"].bind(src["generate::U_K"])
    syn["desynchronize::IN_1"].bind(mdm["modulate::X_N2"])
    chn[ "add_noise::X_N"].bind(syn[ "desynchronize::OUT_1"])
    syn["synchronize::IN"].bind(chn[ "add_noise::Y_N"])
    mdm["demodulate::Y_N1"].bind(syn["synchronize::OUT"])
    dec[ 'decode_siho::Y_N' ].bind(mdm[ 'demodulate::Y_N2'])

    chn[ 'add_noise::CP'].bind(sigma)
    mdm['demodulate::CP'].bind(sigma)
    syn['synchronize::IN_m'].bind(M)
    syn['synchronize::IN_ts'].bind(Ts)
    syn['synchronize::IN_fft'].bind(in_fft)
    syn['synchronize::IN_alpha'].bind(alpha)
    syn['desynchronize::IN_ts1'].bind(Ts)

    src("generate").exec()
    mdm("modulate").exec()
    syn('desynchronize').exec()
    chn("add_noise").exec()
    syn('synchronize').exec()
    mdm('demodulate').exec()
    dec('decode_siho').exec()

    in_fft[0, :] = syn['synchronize::OUT_fft'][:]
