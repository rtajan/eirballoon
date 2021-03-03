import sys
sys.path.insert(0, '../../build/lib')
from py_aff3ct.module.py_module import Py_Module
import numpy as np
import fairepream


class source_img(Py_Module):

    def sendImg(self):
        Bytes = np.fromfile(self.path,dtype="uint8")
        bits = np.unpackbits(Bytes)
        self.bmax = len(bits)
        s_out=self.tabpream + bits[self.offset:min(self.offset+self.N-64,self.bmax)].astype('int32')
        
        if (self.offset+self.N-64>self.bmax):
            s_out = np.concatenate([s_out,[0]*(self.N-64-(self.bmax-self.offset))])
            self.offset = 0
        else:   
            self.offset=self.offset+self.N-64
        return s_out
    
    def sendPream(self):
        s_out = np.array([1]*self.N,dtype='int32')
        self.pream = True
        return s_out

    def imgToBits(self,s_out):
        if (self.pream):
            s_out[:] = self.sendImg()[:]
        else:
            s_out[:] = self.sendPream()[:]

            
        return 0

    def __init__(self, path,N):
        Py_Module.__init__(self)
        self.name = "py_Source_image"
        self.path = path
        self.N=N
        self.pream = True
        self.offset = 0
        self.tabpream = fairepream(64)
        t_source = self.create_task('generate')
        s_out = self.create_socket_out(t_source, 'img',N,np.int32)

        self.create_codelet(t_source, lambda slf, lsk, fid: slf.imgToBits(lsk[s_out]))