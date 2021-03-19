from math import *
from py_aff3ct.module.py_module import Py_Module
import numpy as np
import sys
sys.path.insert(0, '../../build/lib')


class Estimateur_bruit(Py_Module):

    def estimate(self, y, cp, snr):

        M2 = np.mean(abs(y[0,:]**2))
        M4 = np.mean(abs(y[0,:]**4))
        Es = sqrt(abs(2*(M2**2)-M4))
        N0 = abs(M2-Es)
        cp[0,:] = N0/2
        snr[0,:] = 10*log10(Es/N0)
        return 0

    def __init__(self, K):
        # init
        Py_Module.__init__(self)
        self.name = "est_noise"
        t_estimate = self.create_task('estimate')
        sin = self.create_socket_in(t_estimate, "y", K, np.float32)
        sout1 = self.create_socket_out(t_estimate, "cp", 1, np.float32)
        sout2 = self.create_socket_out(t_estimate, "snr", 1, np.float32)

        # properties
        self.gain = 1
        self.create_codelet(t_estimate, lambda slf, lsk,
                            fid: self.estimate(lsk[sin], lsk[sout1], lsk[sout2]))
