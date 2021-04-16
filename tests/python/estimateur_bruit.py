from py_aff3ct.module.py_module import Py_Module
import numpy as np
import sys
sys.path.insert(0, '../../build/lib')
from numba import jit

######################################
#Entrée "y" : signal à analyser
#Sortie "cp" : variance du bruit
#Sortie "snr" : Rapport siganl sur bruit en dB
######################################

class Estimateur_bruit(Py_Module):

    @jit(nopython=True, nogil=True, cache = True) #Optimisation du temps de calcul
    def estimate_(y,prev_snr,alpha):
        M2 = np.mean(np.abs(y[0,:]**2)) #Moment d'ordre 2
        M4 = np.mean(np.abs(y[0,:]**4)) #Moment d'ordre 4
        Es = np.sqrt(np.abs(2*(M2**2)-M4)) #Energie du signal 
        N0 = np.abs(M2-Es) #Energie du bruit
        cp = N0/2 #Variance du bruit
        if M2< 1e-6:
            snr_= 0 #Cas du siganl trop faible
        else:
            snr_ = Es/N0
        prev_snr = alpha*snr_+(1-alpha)*prev_snr #Transition lissée entre les snr
        snr = 10*np.log10(prev_snr) #Passage en dB
        return cp, snr, prev_snr

    def estimate(self, y, cp, snr):

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
