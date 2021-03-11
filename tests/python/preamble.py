import matplotlib.pyplot as plt
import numpy as np
import sys  
sys.path.insert(0, '../../build/lib')
from py_aff3ct.module.py_module import Py_Module

#use insert_preamble to insert an n-sized pre-defined preamble in the beginnning of a vector and remove_preamble to remove it.
#the preamble is composed of BPSK modulated syms in this sequence 1 j -1 -j .... 

class preamble(Py_Module):

    def insert_preamble(self, n,  in_, out_):
        pream=np.zeros((n,1),dtype=np.complex64)
        for i in range(n):
            pream[i]=np.exp(1j*2*np.pi*(i%4)/4) #1 1j -1 ... 
        print(pream)
        out_=np.concatenate((pream, in_), axis=0)
        return 0

    def remove_preamble(self, n, in_, out_):
        out_=in_[n:]
        return 0

    def __init__(self,n): 
        Py_Module.__init__(self)
        self.name = 'Preamble_Generator'
        self.n = n
        t_ins_pream = self.create_task('insert_preamble')
        sin = self.create_socket_in(t_ins_pream, "s_in",n,np.complex64)
        sout = self.create_socket_out(t_ins_pream, "s_out", n, np.complex64)
        self.create_codelet(t_ins_pream,lambda slf, lsk, fid: self.insert_preamble(lsk[sin],lsk[sout]))

        t_rem_pream=self.create_task('remove_preamble')
        sin=self.create_socket_in(t_rem_pream, "s_in",n,np.complex64)
        sout=self.create_socket_out(t_rem_pream, "s_out",n,np.complex64)
        self.create_codelet(t_rem_pream, lambda slf, lsk, fid: self.remove_preamble(lsk[sin], lsk[sout]))

