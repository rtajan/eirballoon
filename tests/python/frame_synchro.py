import sys
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib') 

from py_aff3ct.module.py_module import Py_Module
import numpy as np
import py_aff3ct
from scipy import signal
import matplotlib.pyplot as plt
import math
import numpy.random as rd

###
class Frame_Synchronizer(Py_Module):
    size_header=64 #header size in symbols (cst to def) 
    size= 1000  #data size in symbols (cst to def)
    bps=2
    buff=np.zeros(size_header-1) #keep incomplete corr

    def synchronize(self,s_recv,s_out):
        HEADER =np.ones(size_header) # size_header complex values conjugate and "turned-around" version of the actual header ) to define when framing
        
        re=np.zeros(s_recv.size//2)
        im=np.zeros(s_recv.size//2)
        i=0
        for i in range(s_recv.size//2):
            re[i]=s_recv[0][2*i]
            im[i]=s_recv[0][2*i+1]
        re=s_recv[0][0::2]
        im=s_recv[0][1::2]

        ###
        sig=re+1j*im       
        corr=np.correlate(sig,HEADER,"full")

        tmp=np.zeros(np.size(corr))
        tmp[np.size(sig):]=Frame_Synchronizer.buff
        
        corr_fin=abs(np.add(corr,tmp))

        #update buff
        buff=corr[sig.size-1:] 

        #print("corr:", np.add(corr,tmp))
        delay=np.where(corr_fin-np.amax(corr_fin)==0)
        
        #print("delay is:",delay[0][0])
        
        sig[0:delay[0][0]]=0
        s_out[0][0::2]=np.real(sig)
        s_out[0][1::2]=np.imag(sig)
        return 0     

    def __init__(self,window,len):

        Py_Module.__init__(self)
        self.name = "Frame_Synchronizer"
        tr_synch = self.create_task("tr_synchronize")
        s_in_sig= self.create_socket_in (tr_synch, "IN", window, np.float32)
        s_out= self.create_socket_out(tr_synch,"OUT", window, np.float32)
      
        self.create_codelet(tr_synch, lambda slf, lsk, fid: slf.synchronize(lsk[s_in_sig],lsk[s_out]))


window=2000 
size_header=64 #header size in symbols (cst to def) 
size= 1000  #data size in symbols (cst to def )
bps=2

src = py_aff3ct.module.source.Source_random(window)
cstl = py_aff3ct.tools.constellation.Constellation_QAM(bps)
mdm  = py_aff3ct.module.modem.Modem_generic(window, cstl)
fr_syn=Frame_Synchronizer(window,size+size_header)

#bits=np.concatenate(np.ones(size_header*bps),np.zeros(window-size_header*bps))
#print(bits.size)
mdm("modulate").info()
fr_syn("tr_synchronize").info()

mdm["modulate::X_N1"].bind(src["generate::U_K"])
#mdm["modulate::X_N1"].bind(bits)
fr_syn["tr_synchronize::IN"].bind(mdm["modulate::X_N2"])


#src('generate').debug = True
#mdm('modulate').debug = True
fr_syn('tr_synchronize').debug = True

src("generate").exec()
mdm("modulate").exec()
fr_syn("tr_synchronize").exec()
