from bitstring import BitArray
import math
from py_aff3ct.module.py_module import Py_Module
import numpy as np
import sys
sys.path.insert(0, '../../build/lib')


class detect_coming_trame(Py_Module):

    def func(self, _in, _out, bol, packet_type):
        if(self.end == 1):
                print("C'est fini mon vieux")
                bol[0,:]=1
                self.reception = 0
                self.end = 0
                #_out[0,:] = np.zeros(self.K,dtype=np.int32)
                return 0
        # print(self.nb_packet)
        bol[0,:] = 1
        if(self.reception == 0):
            if(np.sum(np.abs(self.pream[:] - _in[:])) < self.K/100):
                self.count += 1
            if(self.count > 5 and np.sum(np.abs(self.last[:] - _in[:])) < self.K/100):
                self.reception = 1
                self.count = 0
        else:
            if (np.sum(_in[:])==0):
                bol[0,:]=1
            else:
                bol[0,:]=0

            _out[:] = np.float32(_in[:])

            if(packet_type == 2):
                self.end = 1
        return 0

    def __init__(self, K):
        self.end = 0
        self.start = 0
        Py_Module.__init__(self)
        self.name = "detect"
        self.K = K
        self.count = 0
        self.pream = np.zeros((1, K))
        self.pream[0, ::2] = np.ones((1, K//2))
        self.last = np.ones((1, K))
        self.reception = 0
        self.nb_packet = -1
        t_func = self.create_task('detect')
        sin = self.create_socket_in(t_func, "X_N", self.K, np.int32)
        sout = self.create_socket_out(t_func, "Y_N", self.K, np.float32)
        s_end_packet = self.create_socket_out(
            t_func, "end_packet", 1, np.int32)
        sout_itr = self.create_socket_out(t_func, "itr", 1, np.int32)

        self.create_codelet(t_func, lambda slf, lsk,
                            fid: self.func(lsk[sin], lsk[sout], lsk[sout_itr], lsk[s_end_packet]))
