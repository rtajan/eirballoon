import numpy as np
import sys  
sys.path.insert(0, '../build/lib')
from py_aff3ct.module.py_module import Py_Module


class test_ampli(Py_Module):

    def ampli(self,in_,out_):
        out_[:] = self.alpha * in_[:]
        return 0


    def __init__(self,alpha,K):
        Py_Module.__init__(self)
        self.name = 'py_ampli'
        self.alpha = alpha
        t_amp = self.create_task('amplify')
        sin = self.create_socket_in(t_amp, "amp_in",K,np.float32)
        sout = self.create_socket_out(t_amp, "amp_out", K, np.float32)

        self.create_codelet(t_amp,lambda slf, lsk, fid: self.ampli(lsk[sin],lsk[sout]))