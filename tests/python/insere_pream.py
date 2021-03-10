import matplotlib.pyplot as plt
import numpy as np
import sys  
sys.path.insert(0, '../../build/lib')
from py_aff3ct.module.py_module import Py_Module

class preamble(Py_Module):

    def inserepream(self, n,  in_, out_):
        pream=np.zeros((n,1),dtype=np.complex64)
        for i in range(n):
            pream[i]=np.exp(1j*2*np.pi*(i%4)/4) #1 1j -1 ... 

        print(pream)
        out_=np.concatenate((pream, in_), axis=0)
        return 0

    def __init__(self,n): #const
        Py_Module.__init__(self)
        self.name = 'Preamble_Generator'
        self.n = n
        t_pream = self.create_task('insert_preamble')
        sin = self.create_socket_in(t_pream, "s_in",n,np.float32)
        sout = self.create_socket_out(t_pream, "s_out", n, np.complex64)

        self.create_codelet(t_pream,lambda slf, lsk, fid: self.fairepream(lsk[sin],lsk[sout]))