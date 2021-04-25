import sys  
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib')
sys.path.insert(0, '../../src/python')
from py_aff3ct.module.py_module import Py_Module
import py_aff3ct
import numpy as np
import os

class source_file(Py_Module):

    def generate(self,_out,nb):
        if self.frame_nb < 10:
            _out[0,::2]=np.ones((1,self.N//2))
            _out[0,1::2]=np.zeros((1,self.N//2))
        elif self.frame_nb==10:
            _out[0,::]=np.ones((1,self.N))
            
        elif self.frame_nb == 11:
            a = [np.int32(x) for x in bin(np.int32(self.number_packet))[2:]]
            tmp = np.concatenate([np.zeros(32-len(a)), a])
            # print(tmp)
            _out[0,0:len(tmp)] = tmp 
            _out[0,len(tmp):] = np.zeros((1,self.N-len(tmp)))
        else:
            _out[:] = self.src['generate::U_K'][:]
            self.src('generate').exec()
            nb[:]=self.number_packet
        self.frame_nb+=1
        return 1
        


    def compute_packet_number(self):
        binary_size = os.path.getsize(self.path) * 8
        return np.ceil(binary_size//self.N)


    def __init__(self, path, N,auto_reset=False):
        Py_Module.__init__(self)
        self.src = py_aff3ct.module.source.Source_user_binary(N, path, auto_reset=False)
        self.path = path
        self.N = N
        self.frame_nb = 1
        self.name = "source_file"
        self.number_packet = self.compute_packet_number()

        t_source = self.create_task('generate')
        _out = self.create_socket_out(t_source, 'U_K', N, np.int32)
        nb = self.create_socket_out(t_source, 'NB', 1, np.int32)
        self.create_codelet(t_source, lambda slf, lsk,
                            fid: slf.generate(lsk[_out],lsk[nb]))