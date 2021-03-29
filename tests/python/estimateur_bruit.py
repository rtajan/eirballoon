from py_aff3ct.module.py_module import Py_Module
import numpy as np
import sys
sys.path.insert(0, '../../build/lib')
from numba import jit

class Estimateur_bruit(Py_Module):

    @jit(nopython=True, nogil=True, cache = True)
    def estimate_(y,prev_snr,alpha):
        M2 = np.mean(np.abs(y[0,:]**2))
        M4 = np.mean(np.abs(y[0,:]**4))
        Es = np.sqrt(np.abs(2*(M2**2)-M4))
        N0 = np.abs(M2-Es)
        cp = N0/2
        if M2< 1e-6:
            snr_= 0
        else:
            snr_ = Es/N0
        prev_snr = alpha*snr_+(1-alpha)*prev_snr
        snr = 10*np.log10(prev_snr)
        return cp, snr, prev_snr

    def estimate(self, y, cp, snr):

        # M2 = np.mean(abs(y[0,:]**2))
        # M4 = np.mean(abs(y[0,:]**4))
        # Es = sqrt(abs(2*(M2**2)-M4))
        # N0 = abs(M2-Es)
        # cp[:,0] = N0/2
        # if M2< 1e-6:
        #     snr_= 0
        # else:
        #     snr_ = Es/N0
        # self.prev_snr = self.alpha*snr_+(1-self.alpha)*self.prev_snr
        # snr[:,0] = 10*log10(self.prev_snr)
        # print("Es ",Es ,"\nN0 ",N0,"\nM2 ",M2,"\nSnr ",snr[:,0])

        cp_,snr_,prev_snr = Estimateur_bruit.estimate_(y,self.prev_snr,self.alpha)
        cp[:,0] = cp_
        snr[:,0] = snr_
        self.prev_snr = prev_snr

        return 0

    def __init__(self, K, alpha):
        # init
        Py_Module.__init__(self)
        self.name = "est_noise"
        self.alpha = alpha
        self.prev_snr = 0
        t_estimate = self.create_task('estimate')
        sin = self.create_socket_in(t_estimate, "y", K, np.float32)
        sout1 = self.create_socket_out(t_estimate, "cp", 1, np.float32)
        sout2 = self.create_socket_out(t_estimate, "snr", 1, np.float32)

        # properties
        self.gain = 1
        self.create_codelet(t_estimate, lambda slf, lsk,
                            fid: self.estimate(lsk[sin], lsk[sout1], lsk[sout2]))
