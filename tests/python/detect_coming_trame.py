from bitstring import BitArray
import math
from py_aff3ct.module.py_module import Py_Module
import numpy as np
import sys
sys.path.insert(0, '../../build/lib')
from bitstring import BitArray



class detect_coming_trame(Py_Module):

    def func(self, _in, _out, bol, packet_type, tram_type):
        if(self.end == 1):
            bol[0, :] = 1
            self.reception = 0
            self.end = 0
            #_out[0,:] = np.zeros(self.K,dtype=np.int32)

            ##Fermeture du fichier##
            self.file.close()
            self.file = None

            return 0
        # print(self.nb_packet)
        bol[0, :] = 1
        if(self.reception == 0):
            if(np.sum(np.abs(self.pream[:] - _in[:])) < self.K/100):
                self.count += 1
            if(self.count > 5 and np.sum(np.abs(self.last[:] - _in[:])) < self.K/100):
                self.reception = 1
                self.count = 0
        else:
            if (np.sum(_in[:]) == 0):
                bol[0, :] = 1
            else:
                bol[0, :] = 0

            _out[:] = _in[:]

            if(self.file == None):
                if(tram_type[::] == 0):
                    name = "%s/video_%i.ts" % (self.path_dir, self.count_video)
                    self.count_video+=1
                else:
                    name = "%s/image_%i.jpeg" % (self.path_dir, self.count_image)
                    self.count_image+=1
                ##Ouverture du fichier##
                self.file = open(name,"wb")

            # écriture dans le fichier
            if(self.file != None) and (np.sum(_in[:]) != 0):
                byte = [0] * (len(_in[0,:])//8)
                for k in range(len(_in[0,:])//8):
                    byte[k]=int(''.join(map(str,np.flip(_in[0,8*k:8*(k+1)]))),base=2)
                    self.file.write(byte[k].to_bytes(1,"big"))
            ##


            if(packet_type == 2):
                self.end = 1
        return 0

    def __init__(self, K, path):
        self.end = 0
        self.start = 0
        Py_Module.__init__(self)
        self.name = "detect"
        self.K = K
        self.path_dir = path
        self.count = 0
        self.pream = np.zeros((1, K))
        self.pream[0, ::2] = np.ones((1, K//2))
        self.last = np.ones((1, K))
        self.reception = 0
        self.nb_packet = -1

        self.file = None
        self.count_image = 0
        self.count_video = 0

        t_func = self.create_task('detect')
        sin = self.create_socket_in(t_func, "X_N", self.K, np.int32)
        sout = self.create_socket_out(t_func, "Y_N", self.K, np.int32)
        s_end_packet = self.create_socket_out(
            t_func, "end_packet", 1, np.int32)
        tram_type = self.create_socket_in(t_func, "T_Type", 1, np.int32)
        sout_itr = self.create_socket_out(t_func, "itr", 1, np.int32)

        self.create_codelet(t_func, lambda slf, lsk,
                            fid: self.func(lsk[sin], lsk[sout], lsk[sout_itr], lsk[s_end_packet], lsk[tram_type]))
