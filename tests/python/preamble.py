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
sys.path.insert(0, '../../py_aff3ct/build/lib')
import py_aff3ct
from py_aff3ct.module.py_module import Py_Module
import math

#use insert_preamble to insert an N_source-sized pre-defined preamble in the beginnning of a vector and remove_preamble to remove it.
#the preamble is composed of BPSK modulated syms in this sequence 1 j -1 -j .... 

class preamble(Py_Module):
    
    def get_header(self,path):  #get header from file
        out=[]
        with open(path, 'r') as filehandle:
            for word in filehandle:
                out.append(float(word))
        return out
    

    def create_preamble(self):        
        pream_cp=np.zeros((self.len_pream,1),dtype=np.complex64)
        pream=np.zeros((2*self.len_pream,1), dtype=np.float32)
        for i in range(self.len_pream):
            a=1-2*np.random.randint(2)
            pream_cp[i]=np.exp(1j*2*np.pi*(i%4)/4) #1 1j -1 ...             
            pream[2*i]=math.floor(np.real(pream_cp[i]))
            pream[2*i+1]=a*math.floor(np.imag(pream_cp[i]))
        out=np.transpose(pream)
        return out

    def insert_preamble(self, in_, out_):
        out_[:]=np.transpose(np.concatenate((np.transpose(self.header),np.transpose(in_)), axis=0))    
        return 0
   

    def remove_preamble(self, in_, out_):
        out_=in_[self.len_pream:]
        return 0

    def __init__(self,len_pream,len_frame ): 
        Py_Module.__init__(self)
        self.name = 'preamble'
        self.len_frame=len_frame 

        #self.header1=self.create_preamble() #creer
        self.header=np.array(self.get_header("header.txt")).reshape(1,2*len_pream) #utiliser le preambule dans le fishier header.txt

        t_ins_pream = self.create_task('insert_preamble')
        sin = self.create_socket_in(t_ins_pream, "s_in",len_frame,np.float32)
        sout = self.create_socket_out(t_ins_pream, "s_out", len_frame+2*len_pream, np.float32)
        self.create_codelet(t_ins_pream,lambda slf, lsk, fid: self.insert_preamble(lsk[sin], lsk[sout]))

        t_rem_pream=self.create_task('remove_preamble')
        s_in=self.create_socket_in(t_rem_pream, "s_in",len_frame+len_pream,np.float32)
        s_out=self.create_socket_out(t_rem_pream, "s_out",self.len_frame,np.float32)
        self.create_codelet(t_rem_pream, lambda slf, lsk, fid: self.remove_preamble(lsk[s_in], lsk[s_out]))


