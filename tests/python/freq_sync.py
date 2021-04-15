import math
from py_aff3ct.module.py_module import Py_Module
import numpy as np
import sys
sys.path.insert(0, '../../build/lib')
import scipy.signal
import math

class freq_sync(Py_Module):

    def sync(self,yl,out):
        real = yl[0,::2]
        imag = yl[0,1::2]
        yl2 = np.array(real + 1j *imag,dtype=np.complex64)
        f, Pxx = scipy.signal.welch(abs(yl2)**4, self.fech)
        delta_f_est = f[np.argmax(Pxx)]/4
        t = np.arange(0,(len(yl2))/self.fech,1/self.fech)
        decalage = np.exp(1j*2*np.pi*delta_f_est*t)
        yl_complex = yl2*decalage


        yl_complex = np.array(yl_complex,dtype=np.complex64)
        yl_sync = np.zeros(2*len(yl_complex),dtype=np.float32)
        yl_sync[0::2] = np.real(yl_complex)
        yl_sync[1::2] = np.imag(yl_complex)

        out[:]=yl_sync[:]
        return 0


    def __init__(self, fech, K):
        # init
        Py_Module.__init__(self)
        self.name = "frequency_sync"
        t_amp = self.create_task('sync')
        self.fech = fech

        sin = self.create_socket_in(t_amp, "sync_in", K, np.float32)
        sout = self.create_socket_out(t_amp, "sync_out", K, np.float32)

        # properties
        self.create_codelet(t_amp, lambda slf, lsk,
                            fid: self.sync(lsk[sin], lsk[sout]))
