import math
from py_aff3ct.module.py_module import Py_Module
import numpy as np
import sys
sys.path.insert(0, '../../build/lib')


class display_info(Py_Module):

    def display(self,lsk):
        if self.init:
            print("|----------"*len(lsk),"|\n")
            # for i in lsk:
                # print("|"," "*(10-len(i.name)),i.name)
            print("|\n")
            print("|----------"*len(lsk),"|\n")
            self.init=False
        for i in lsk:
            print("|"," "*(10-len(str(i[0,0]))),i[0,0],end='')
        print("|\r",end='')
        return 0

    def bind_display(self,sck):
        shp = sck[:].shape
        tp = sck[:].dtype.type
        if shp[1] > 1:
            raise RuntimeError
        s = self.create_socket_in(self("display"),sck.name,shp[0]*shp[1],tp)
        self("display").sockets[s].bind(sck)

    # def register_input(self,nom,type,N):
    #     self.create_socket_in(self('display'),nom,N,type)

    def done(self):
        self.create_codelet(self('display'), lambda slf, lsk,
                            fid: self.display(lsk))




    def __init__(self):
        # init
        Py_Module.__init__(self)
        self.name = "display_info"
        t_dis = self.create_task('display')
        self.frame = 0
        self.init = True
