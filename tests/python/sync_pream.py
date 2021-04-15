import fairepream
from math import *
import numpy as np
from py_aff3ct.module.py_module import Py_Module
import sys

from numpy.core.fromnumeric import size
sys.path.insert(0, '../../build/lib')


class sync_pream(Py_Module):

    def func(self, s_in, s_out):

        ind = self.start_index(s_in)
        uti = s_in[0, ind:]
        s_out[:] = [np.concatenate([uti[:], [0]*(self.N-len(uti))])]
        return 0

    def start_index(self, s_in):
        tmp = [abs(i)*abs(i) for i in self.pream]
        den1 = sqrt(sum(tmp))
        delta = np.zeros((self.N-self.size_pream, 1), dtype="float32")
        for i in range(self.N-self.size_pream):
            num = np.correlate(self.pream, s_in[0, i:i+self.size_pream])
            tmp2 = [abs(i)*abs(i) for i in s_in[0, i:i+self.size_pream]]
            den2 = sqrt(sum(tmp2))
            delta[i] = num/(den1*den2)
            if delta[i] > 0.8:
                print(i//2)
                return i//2
        ind = np.argmax(delta)
        return ind//2

    def __init__(self, size_pream, N):
        Py_Module.__init__(self)
        self.name = "py_sync_pream"
        self.N = N
        self.size_pream = size_pream
        self.pream = [cos(3*np.pi/4), sin(3*np.pi/4)]*(size_pream//2)
        t_source = self.create_task('sync_pream')
        s_in = self.create_socket_in(t_source, 'sync_in', N, np.float32)
        s_out = self.create_socket_out(t_source, 'sync_out', N, np.float32)

        self.create_codelet(t_source, lambda slf, lsk,
                            fid: slf.func(lsk[s_in], lsk[s_out]))
