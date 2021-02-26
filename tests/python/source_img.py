import sys
sys.path.insert(0, '../../build/lib')
from py_aff3ct.module.py_module import Py_Module
import numpy as np

class source_img(Py_Module):

    def imgToBits(self,s_out):
        Bytes = np.fromfile(self.path,dtype="uint8")
        bits = np.unpackbits(Bytes)
        self.bmax = len(bits)
        s_out=bits[self.offset:min(self.offset+self.N,self.bmax)]
        self.offset=self.offset+self.N
        if (self.offset>self.bmax):
            self.offset = 0
            print("-------------------------------------------------")
        print(s_out)
        print(len(s_out))
        return 0

    def __init__(self, path,N):
        Py_Module.__init__(self)
        self.name = "py_Source_image"
        self.path = path
        self.N=N
        self.offset = 0
        t_source = self.create_task('generate')
        s_out = self.create_socket_out(t_source, 'img',N,np.int32)

        self.create_codelet(t_source, lambda slf, lsk, fid: slf.imgToBits(lsk[s_out]))