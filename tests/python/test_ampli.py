import numpy as np
import sys  
sys.path.insert(0, '../../build/lib')
from py_aff3ct.module.py_module import Py_Module
from numba import jit

class test_ampli(Py_Module):

    @jit(nopython=True, nogil=True, cache = True)
    def ampli_(alpha,in_,_out_):
        return alpha * in_[:]

    def ampli(self,in_,out_):
        out_[:] = self.ampli_(self.alpha,in_,out_)
        return 0


    def __init__(self,alpha,K):
        Py_Module.__init__(self)
        self.name = 'py_ampli'
        self.alpha = alpha
        t_amp = self.create_task('amplify')
        sin = self.create_socket_in(t_amp, "amp_in",K,np.float32)
        sout = self.create_socket_out(t_amp, "amp_out", K, np.float32)

        self.create_codelet(t_amp,lambda slf, lsk, fid: self.ampli(lsk[sin],lsk[sout]))