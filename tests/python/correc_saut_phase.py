import math
from py_aff3ct.module.py_module import Py_Module
import numpy as np
import sys
sys.path.insert(0, '../../build/lib')


class Anti_saut_phase(Py_Module):

    def sync(self, in_, out,jump):
        header_est = in_[0][:len(self.header[0])]
        
        header_est_comp = np.array(header_est[::2]+1j*header_est[1::2])
        true_header = np.array(self.header[0,::2]+1j*self.header[0,1::2])
        # diff_phase = np.angle(header_est_comp)
        # diff_phase = diff_phase - np.angle(true_header)
        z = np.mean(header_est_comp*np.conjugate(true_header))
        #print(diff_phase)
        zr = np.real(z)
        zi = np.imag(z)
        abs_z = zr*zr+zi*zi
        jump[:] = np.angle(z)
        out[0,::2] = in_[0,::2]*zr+in_[0,1::2]*zi
        out[0,1::2] = in_[0,1::2]*zr-in_[0,::2]*zi
        out /= abs_z

        return 0

    def __init__(self, K , header):
        # init
        Py_Module.__init__(self)
        self.name = "sync"
        self.header = header
        t_amp = self.create_task('sync')

        sin = self.create_socket_in(t_amp, "X_N", K, np.float32)
        sout = self.create_socket_out(t_amp, "Y_N", K, np.float32)
        sout_jump = self.create_socket_out(t_amp, "phase_jump", 1, np.float32)

        # properties
        self.create_codelet(t_amp, lambda slf, lsk,
                            fid: self.sync(lsk[sin], lsk[sout], lsk[sout_jump]))
