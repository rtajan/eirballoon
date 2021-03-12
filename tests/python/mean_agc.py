import math
from py_aff3ct.module.py_module import Py_Module
import numpy as np
import sys
sys.path.insert(0, '../../build/lib')


class Mean_Agc(Py_Module):

    def ampli(self, amp_in, amp_out):
        
        y = np.mean(abs(amp_in[0,::2] + 1j*amp_in[0,1::2]))
        gain = np.sqrt(self.ref)/y
        amp_out[:]= amp_in[:]*gain
        

        return 0

    def __init__(self,ref, K):
        # init
        Py_Module.__init__(self)
        self.ref = ref
        self.name = "agc"
        t_amp = self.create_task('amplify')
        sin = self.create_socket_in(t_amp, "amp_in", K, np.float32)
        sout = self.create_socket_out(t_amp, "amp_out", K, np.float32)

        # properties
        self.gain = 1
        self.create_codelet(t_amp, lambda slf, lsk,
                            fid: self.ampli(lsk[sin], lsk[sout]))
