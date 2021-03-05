import fairepream
from math import *
import numpy as np
import sys
sys.path.insert(0, '../../build/lib')
from py_aff3ct.module.py_module import Py_Module



class synchro_freq_fine(Py_Module):

    def func(self, s_in, s_out):
        ylreal = s_in[0,::2]
        ylimag = s_in[0,1::2]
        yl = np.array(ylreal + 1j *ylimag,dtype=np.complex64)
        y = np.zeros((1,self.N//2),dtype=np.complex64)
        for k in range(self.N//2):
            phErr = np.sign(np.real(self.previousSample))*np.imag(self.previousSample)-np.sign(np.imag(self.previousSample))*np.real(self.previousSample)
            y[0,k] = yl[k]*np.exp(1j*self.phase)

            loopFiltOut = phErr*self.gI + self.loopFiltState
            self.loopFiltState = loopFiltOut

            DDSout = self.DDSPreviousInp + self.IntegFiltState
            self.IntegFiltState= DDSout
            self.DDSPreviousInp = phErr * self.gP+loopFiltOut

            self.phase = -DDSout
            self.previousSample = y[0,k]
        yl_sync = np.zeros(2*len(y[0]),dtype=np.float32)
        yl_sync[0::2] = np.real(y)
        yl_sync[1::2] = np.imag(y)

        s_out[:]=yl_sync[:]

        return 0


    def __init__(self, fse, N):
        Py_Module.__init__(self)
        self.name = "py_sync_freq_fine"
        self.N = N
        self.Bn = 0.01
        self.zeta = sqrt(2)/2
        self.Kp = 2
        self.SPS = fse
        self.teta = (self.Bn * self.SPS)/((self.zeta + 0.25/self.zeta)*self.SPS)
        self.d = 1+2*self.zeta*self.teta+self.teta**2
        self.gI = (4*(self.teta**2)/self.d)/(self.Kp*self.SPS)
        self.gP = (4*(self.teta*self.zeta)/self.d)/(self.Kp*self.SPS)
        self.previousSample = 1
        self.phase = 0
        self.loopFiltState = 0
        self.DDSPreviousInp = 0
        self.IntegFiltState = 0

        t_source = self.create_task('synchronize')
        s_in = self.create_socket_in(t_source, 'sync_in', N, np.float32)
        s_out = self.create_socket_out(t_source, 'sync_out', N, np.float32)

        self.create_codelet(t_source, lambda slf, lsk,
                            fid: slf.func(lsk[s_in], lsk[s_out]))
