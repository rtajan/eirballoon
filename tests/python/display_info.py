import math
from py_aff3ct.module.py_module import Py_Module
import numpy as np
import sys
sys.path.insert(0, '../../build/lib')


class display_info(Py_Module):

    def title(self,lsk):
        if self.init:
            print(self.sepa[:-1])
            for i in range(len(lsk)):
                print("|"," "*(18-len(self.socket_name[i])),self.socket_name[i],end="")
            print("|")
            print(self.sepa[:-1])
            self.init=False

    def display(self,lsk):
        if self.frame % self.dc == 0:
            self.title(lsk)
            formatted_str = "%20.3f"
            print(" ",end="")
            for i in range(len(lsk)-1):
                #print(" "*(18-len(str(lsk[i][0,0]))),lsk[i][0,0],end='|')
                print(formatted_str%lsk[i][0,0],end='|')
            print(formatted_str%lsk[-1][0,0],end='\r')
            self.frame = 0
        self.frame = self.frame +1
        return 0

    def bind_display(self,sck):
        shp = sck[:].shape
        tp = sck[:].dtype.type
        if shp[1] > 1:
            raise RuntimeError
        s = self.create_socket_in(self("display"),sck.name,shp[0]*shp[1],tp)
        self.socket_name.append(sck.name)
        self("display").sockets[s].bind(sck)
        self.sepa = self.sepa +20*"-"+"|"
    # def register_input(self,nom,type,N):
    #     self.create_socket_in(self('display'),nom,N,type)

    def done(self):
        self.create_codelet(self('display'), lambda slf, lsk,
                            fid: self.display(lsk))




    def __init__(self,dc = 50):
        # init
        Py_Module.__init__(self)
        self.name = "display_info"
        self.dc =dc
        t_dis = self.create_task('display')
        self.frame = 0
        self.init = True
        self.socket_name = []
        self.sepa = "#"