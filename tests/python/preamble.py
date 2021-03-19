#####################################
#
#preamble has method create_preamble to create an N_source-sized preamble 
## method insert_preamble to encapsulate a frame (input: np.float32 --> output: np.float32) 
## and method remove_preamble 
#
#####################################



import matplotlib.pyplot as plt
import numpy as np
import sys  
sys.path.insert(0, './py_aff3ct/build/lib')
import py_aff3ct
from py_aff3ct.module.py_module import Py_Module

#use insert_preamble to insert an N_source-sized pre-defined preamble in the beginnning of a vector and remove_preamble to remove it.
#the preamble is composed of BPSK modulated syms in this sequence 1 j -1 -j .... 

class preamble(Py_Module):


    def create_preamble(self):        
        pream_cp=np.zeros((self.len_pream,1),dtype=np.complex64)
        pream=np.zeros((2*self.len_pream,1), dtype=np.int32)
        for i in range(self.len_pream):
            pream_cp[i]=np.exp(1j*2*np.pi*(i%4)/4) #1 1j -1 ... 
            pream[2*i]=np.real(pream_cp[i])
            pream[2*i+1]=np.imag(pream_cp[i])
            out=np.transpose(pream)
        return out

    def insert_preamble(self, in_, out_):
        pream=self.create_preamble()
        out_=np.concatenate((np.transpose(pream),np.transpose(in_)), axis=0)
        out_=np.transpose(out_)
        return 0
   

    def remove_preamble(self, in_, out_):
        out_=in_[self.len_pream:]
        return 0

    def __init__(self,len_pream,len_frame ): 
        Py_Module.__init__(self)
        self.name = 'preamble'
        self.len_pream = len_pream
        self.len_frame=len_frame
        t_create_pream=self.create_task('create_preamble')
        self.create_codelet(t_create_pream, lambda slf, lsk, fid:self.create_preamble())


        t_ins_pream = self.create_task('insert_preamble')
        sin = self.create_socket_in(t_ins_pream, "s_in",self.len_frame,np.float32)
        sout = self.create_socket_out(t_ins_pream, "s_out", self.len_frame+self.len_pream, np.float32)
        self.create_codelet(t_ins_pream,lambda slf, lsk, fid: self.insert_preamble(lsk[sin], lsk[sout]))

        t_rem_pream=self.create_task('remove_preamble')
        sin=self.create_socket_in(t_rem_pream, "s_in",self.len_frame+self.len_pream,np.float32)
        sout=self.create_socket_out(t_rem_pream, "s_out",self.len_frame,np.float32)
        self.create_codelet(t_rem_pream, lambda slf, lsk, fid: self.remove_preamble(lsk[sin], lsk[sout]))


N_source = 2048

M = np.ndarray(shape = (1,1),  dtype = np.int32)
M[0] = 2

Ns = N_source//M[0]

alpha = np.ndarray(shape = (1,1),  dtype = np.float32)
alpha[0] = 0.2

in_fft= np.ndarray(shape = (1,Ns[0]),  dtype = np.float32)
in_fft[0, :] = np.zeros(Ns[0])

sigma = np.ndarray(shape = (1,1),  dtype = np.float32)
sigma[0] = 0.0001

Ts = np.ndarray(shape = (1,1),  dtype = np.float32)
Ts[0] = 0.01

N_pream=64
for i in range(10):

    src = py_aff3ct.module.source.Source_random(N_source)
    cstl = py_aff3ct.tools.constellation.Constellation_QAM(M)
    mdm  = py_aff3ct.module.modem.Modem_generic(N_source, cstl)
    mdm("modulate").info()
    pream=preamble(N_pream, N_source)
    pream("insert_preamble").info()
    chn  = py_aff3ct.module.channel.Channel_AWGN_LLR((N_source+N_pream))
    chn("add_noise").info()
    dec  = py_aff3ct.module.decoder.Decoder_repetition_std(N_source,N_source)
    # syn = Frequency_Synchronizer(2*Ns)


    mdm["modulate::X_N1"].bind(src["generate::U_K"])
    pream["insert_preamble::s_in"].bind(mdm["modulate::X_N2"])
    chn[ "add_noise::X_N"].bind(pream[ "insert_preamble::s_out"])
    pream["remove_preamble::s_in"].bind(chn[ "add_noise::Y_N"])
    mdm["demodulate::Y_N1"].bind(pream["remove_preamble::s_out"])
    dec[ 'decode_siho::Y_N' ].bind(mdm[ 'demodulate::Y_N2'])

    chn[ 'add_noise::CP'].bind(sigma)
    mdm['demodulate::CP'].bind(sigma)
    # syn['synchronize::IN_m'].bind(M)
    # syn['synchronize::IN_ts'].bind(Ts)
    # syn['synchronize::IN_fft'].bind(in_fft)
    # syn['synchronize::IN_alpha'].bind(alpha)
    # syn['desynchronize::IN_ts1'].bind(Ts)

    src("generate").exec()
    mdm("modulate").exec()
    pream("insert_preamble").exec()
    # syn('desynchronize').exec()
    chn("add_noise").exec()
    # syn('synchronize').exec()
    pream("remove_preamble").exec()
    mdm('demodulate').exec()
    dec('decode_siho').exec()

    # in_fft[0, :] = syn['synchronize::OUT_fft'][:]
