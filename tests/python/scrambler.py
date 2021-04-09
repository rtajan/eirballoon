import math
from py_aff3ct.module.py_module import Py_Module
import numpy as np
import sys
sys.path.insert(0, '../../build/lib')


class Agc(Py_Module):

    def scramble(self, in_, out_):
        out_[:]=np.logical_xor(in_[:],self.scram,dtypte =np.int32)

        return 0

    def __init__(self, K,scram=None):
        # init
        Py_Module.__init__(self)
        self.name = "scrambler"
        t_amp = self.create_task('scramble')
        if (scram):
            self.scram = scram
        else:
            self.scram = np.random.randint(2,size=K)

        sin = self.create_socket_in(t_amp, "X_N", K, np.int32)
        sout = self.create_socket_out(t_amp, "Y_N", K, np.int32)

        # properties
        self.create_codelet(t_amp, lambda slf, lsk,
                            fid: self.scramble(lsk[sin], lsk[sout]))
