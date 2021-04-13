from numba import jit
from py_aff3ct.module.py_module import Py_Module
from math import *
import numpy as np
import sys
sys.path.insert(0, '../../build/lib')


class synchro_freq_fine(Py_Module):
    @jit(nopython=True)
    def func_(s_in, s_out, previousSample, phase, loopFiltState, DDSPreviousInp, IntegFiltState, gI, gP):
        for k in range(len(s_in[0, :])//2):
            phErr = np.sign(np.real(previousSample))*np.imag(previousSample) - \
                np.sign(np.imag(previousSample))*np.real(previousSample)
            c = cos(phase)
            s = sin(phase)
            t = s_in[0, 2*k:2*k+2]
            s_out[0, 2*k] = t[0]*c-t[1]*s
            s_out[0, 2*k+1] = t[0]*s+t[1]*c

            loopFiltOut = phErr*gI + loopFiltState
            loopFiltState = loopFiltOut

            DDSout = DDSPreviousInp + IntegFiltState
            IntegFiltState = DDSout
            DDSPreviousInp = phErr * gP+loopFiltOut

            phase = -DDSout
            previousSample = s_out[0, 2*k] + 1j * s_out[0, 2*k+1]
        return previousSample, phase, loopFiltState, DDSPreviousInp, IntegFiltState
        

    def func(self, s_in, s_out):
        self.previousSample, self.phase, self.loopFiltState, self.DDSPreviousInp, self.IntegFiltState = synchro_freq_fine.func_(
            s_in, s_out, self.previousSample, self.phase, self.loopFiltState, self.DDSPreviousInp, self.IntegFiltState, self.gI, self.gP)
        return 0

    def __init__(self, fse, N):
        Py_Module.__init__(self)
        self.name = "py_sync_freq_fine"
        self.N = N
        self.Bn = 0.01
        self.zeta = sqrt(2)/2
        self.Kp = 2
        self.SPS = fse
        self.teta = (self.Bn * self.SPS) / \
        ((self.zeta + 0.25/self.zeta)*self.SPS)
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
