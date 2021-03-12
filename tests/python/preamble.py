#####################################
#
#preamble has method create_preamble to create an n-sized preamble 
## method insert_preamble to encapsulate a frame (input: np.float32 --> output: np.float32) 
## and method remove_preamble 
#
#####################################



import matplotlib.pyplot as plt
import numpy as np
import sys  
sys.path.insert(0, '../../build/lib')
from py_aff3ct.module.py_module import Py_Module

#use insert_preamble to insert an n-sized pre-defined preamble in the beginnning of a vector and remove_preamble to remove it.
#the preamble is composed of BPSK modulated syms in this sequence 1 j -1 -j .... 

class preamble(Py_Module):


    def create_preamble(self):        
        pream_cp=np.zeros((self.n,1),dtype=np.complex64)
        pream=np.zeros((2*self.n,1), dtype=np.int32)
        for i in range(n):
            pream_cp[i]=np.exp(1j*2*np.pi*(i%4)/4) #1 1j -1 ... 
            pream[2*i]=np.real(pream_cp[i])
            pream[2*i+1]=np.imag(pream_cp[i])

        return np.transpose(pream)

    def insert_preamble(self, in_):
        pream=self.create_preamble()
        out_=np.concatenate((np.transpose(pream),np.transpose(in_)), axis=0)
        return np.transpose(out_)
   

    def remove_preamble(self, in_):
        return in_[self.n:]

    def __init__(self,n): 
        Py_Module.__init__(self)
        self.name = 'Preamble_Generator'
        self.n = n
        t_create_pream=self.create_task('create_preamble')
        self.create_codelet(t_create_pream, lambda slf, lsk, fid:self.create_preamble())


        t_ins_pream = self.create_task('insert_preamble')
        sin = self.create_socket_in(t_ins_pream, "s_in",n,np.float32)
        sout = self.create_socket_out(t_ins_pream, "s_out", n, np.float32)
        self.create_codelet(t_ins_pream,lambda slf, lsk, fid: self.insert_preamble(lsk[sin], lsk[sout]))

        t_rem_pream=self.create_task('remove_preamble')
        sin=self.create_socket_in(t_rem_pream, "s_in",n,np.float32)
        sout=self.create_socket_out(t_rem_pream, "s_out",n,np.float32)
        self.create_codelet(t_rem_pream, lambda slf, lsk, fid: self.remove_preamble(lsk[sin], lsk[sout]))

