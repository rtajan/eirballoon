from numba import jit
import math
from py_aff3ct.module.py_module import Py_Module
import numpy as np
import sys
sys.path.insert(0, '../../build/lib')


class Mean_Agc(Py_Module):

    @jit(nopython=True, nogil=True, cache=True)
    def ampli_(amp_in, ref,gain_):
        y = np.mean((amp_in[0, ::2]*amp_in[0, ::2] +
                     amp_in[0, 1::2]*amp_in[0, 1::2]))
        is_signal = y > 1e-8
        if is_signal:
            gain = ref/np.sqrt(y)
            itr = 0
        else:
            gain = 1
            itr = 1
        return gain, amp_in*gain, itr

    def ampli(self, amp_in, amp_out, gain_out,itr):

        # self.gain = gain_ #* 0.9+0.1*self.gain
        ref = self.ref
        gain, tmp, itr[0,0] = Mean_Agc.ampli_(amp_in, ref,self.gain)
        self.gain = gain *0.8 + 0.2 * self.gain
        amp_out[:] = tmp
        gain_out[:] = self.gain
        return 0

    def __init__(self, ref, K):
        # init
        Py_Module.__init__(self)
        self.ref = ref
        self.name = "agc"
        t_amp = self.create_task('amplify')
        sin = self.create_socket_in(t_amp, "amp_in", K, np.float32)
        sout2 = self.create_socket_out(t_amp, "gain_out", 1, np.float32)
        itr = self.create_socket_out(t_amp, "itr", 1, np.int32)
        sout = self.create_socket_out(t_amp, "amp_out", K, np.float32)

        # properties
        self.gain = 1
        self.create_codelet(t_amp, lambda slf, lsk,
                            fid: self.ampli(lsk[sin], lsk[sout], lsk[sout2], lsk[itr]))
