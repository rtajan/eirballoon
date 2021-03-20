import sys
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib') 
import py_aff3ct
from py_aff3ct.module.py_module import Py_Module
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import math
import numpy.random as rd
import preamble

class Frame_Synchronizer(Py_Module):
    
 # Conjugated and "turned-around" version of the actual header ) to define when framing
    
    def synchronize(self,s_recv,s_out):
        
        
        re=np.zeros(s_recv.size//2)
        im=np.zeros(s_recv.size//2)
        i=0
        for i in range(s_recv.size//2):
            re[i]=s_recv[0][2*i]
            im[i]=s_recv[0][2*i+1]
        re=s_recv[0][0::2]
        im=s_recv[0][1::2]
        
        sig=re+1j*im      
        print(s_recv) 
        corr=np.correlate(sig,self.HEADER,"full")

        tmp=np.zeros(np.size(corr),dtype=complex)
        tmp[np.size(sig):]=self.buff
        
        corr_fin=abs(np.add(corr,tmp))

        #update buff
        self.buff=corr[sig.size-1:] 

        #correlation
        delay=np.where(corr_fin-np.amax(corr_fin)==0)
        
        d=np.shape(sig)
        
        self.frame[:d[0]-delay[0][0]]=sig[delay[0][0]:]
        #output
        s_out[0][0::2]=np.real(self.frame)
        s_out[0][1::2]=np.imag(self.frame)

       #
        self.frame[self.frame.size-delay[0][0]:]=sig[:delay[0][0]]
        
        return 0     
    
    def reset_mem(self):  #reset mem
        self.buff=np.zeros(size_header-1) 
        self.frame=np.zeros(size+size_header) 
        return 0

    
    def __init__(self,window,len,header):
        self.len=len
        self.HEADER=header[0]
        self.size_header=header.size
        self.buff=np.zeros(self.size_header-1,dtype=complex)  #keep incomplete corr
        self.frame=np.zeros(self.len//2,dtype=complex) #buffer to temporarly store the frame 
        
        
        Py_Module.__init__(self)
        self.name = "Frame_Synchronizer"
        tr_synch = self.create_task("tr_synchronize")
        s_in_sig= self.create_socket_in (tr_synch, "IN", window, np.float32)  #preferably input window should be smaller thacn frame size bigger than data size
        s_out= self.create_socket_out(tr_synch,"OUT", len, np.float32)   #return frame size
      
        self.create_codelet(tr_synch, lambda slf, lsk, fid: slf.synchronize(lsk[s_in_sig],lsk[s_out]))


window=2048
size_header=64 #header size in symbols (cst to def) 
size= 1000  #data size in symbols (cst to def )
bps=2



src = py_aff3ct.module.source.Source_random(size)
cstl = py_aff3ct.tools.constellation.Constellation_QAM(bps)
mdm  = py_aff3ct.module.modem.Modem_generic(size, cstl)
pre=preamble.preamble(size_header,size)
head=pre.header 

fr_syn=Frame_Synchronizer(size+2*size_header,size+2*size_header,head)


#src("generate").info()
pre("insert_preamble").info()
#mdm("modulate").info()
fr_syn("tr_synchronize").info()


mdm["modulate::X_N1"].bind(src["generate::U_K"])
pre["insert_preamble::s_in"].bind(mdm["modulate::X_N2"])
fr_syn['tr_synchronize::IN'].bind(pre["insert_preamble::s_out"])


#src('generate').debug = True
#mdm('modulate').debug = True
#fr_syn('tr_synchronize').debug = True
#pre('insert_preamble').debug=True

src("generate").exec()
mdm("modulate").exec()
fr_syn("tr_synchronize").exec()
pre("insert_preamble").exec()
