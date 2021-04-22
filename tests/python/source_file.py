import sys  
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib')
sys.path.insert(0, '../../src/python')
from py_aff3ct.module.py_module import Py_Module
import py_aff3ct
import numpy as np
import os

class source_file(Py_Module):

    def generate(self,_out):
        _out[:] = self.src['generate::U_K'][:]
        self.src('generate').exec()
        return 1
        


    def compute_packet_number(self):
        binary_size = os.path.getsize(self.path) * 8
        return np.ceil(binary_size//self.N)


    def __init__(self, path, N):
        Py_Module.__init__(self)
        self.src = py_aff3ct.module.source.Source_user_binary(N, path, auto_reset=False)
        self.path = path
        self.N = N

        self.number_packet = self.compute_packet_number()

        t_source = self.create_task('generate')
        _out = self.create_socket_out(t_source, 'U_K', N, np.int32)
        self.create_codelet(t_source, lambda slf, lsk,
                            fid: slf.generate(lsk[_out]))