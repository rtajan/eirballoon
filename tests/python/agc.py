import math
from py_aff3ct.module.py_module import Py_Module
import numpy as np
import sys
sys.path.insert(0, '../../build/lib')


class Agc(Py_Module):

    def ampli(self, amp_in, amp_out):
        varNoise = self.varNoise
        out_amp = self.out_amp

        #y = amp_in[0,abs(amp_in[0,:]) > varNoise]
        # y = [i for i in amp_in[0,:] if abs(i)>varNoise]
        # y=amp_in
        v_ = np.var(y)
        gain = (out_amp / v_)
        amp_out[:] = gain*amp_in[:]
        return 0

    def __init__(self, out_amp, varNoise, K):
        # init
        Py_Module.__init__(self)
        self.name = "agc"
        t_amp = self.create_task('amplify')

        self.out_amp = out_amp
        self.varNoise = varNoise

        sin = self.create_socket_in(t_amp, "amp_in", K, np.float32)
        sout = self.create_socket_out(t_amp, "amp_out", K, np.float32)

        # properties
        self.gain = 1
        self.create_codelet(t_amp, lambda slf, lsk,
                            fid: self.ampli(lsk[sin], lsk[sout]))
