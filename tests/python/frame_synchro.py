#output metric value



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
import eirballoon



#####
#Socket Output:# 1:  header+data if frame is ready, zero array if not(ex: first frame)
#Socket Output:# 2:  delay,  delay-len_header is where the frame starts
#Socket Output:# 3:  1 if Output 1 contains data , 0 if not 
####
class Frame_Synchronizer(Py_Module):
    
 
    def synchronize(self,s_recv,s_out,s_out_del,s_out_bo):        
        
        #finding the delay
        re=s_recv[0][0::2]
        im=s_recv[0][1::2]
        
        tmp1_head=self.HEADER[0::2]
        tmp2_head=self.HEADER[1::2]
        
        re_head=tmp1_head[::-1]
        im_head=-tmp2_head[::-1]
        
        head=re_head+1j*im_head #returned conjugate       
        sig=re+1j*im             
        corr=np.correlate(sig,head,"full")
        tmp=np.zeros(np.size(corr),dtype=complex)

        #add previous frame contribution in correlation          
        tmp[sig.size:]=self.buff     
        corr_fin=abs(np.add(corr,tmp))
        
        #plt.plot(corr_fin)
        #plt.show()

        #update buff
        self.buff=corr[sig.size:]
 
        #correlation
        delay=np.where(corr_fin-np.amax(corr_fin)==0)[0][0]
        s_out_del[0]=delay
        d=np.shape(sig)
        #with open('aaa.txt', 'w') as f:
            #print('header',self.HEADER,"delay",delay, file=f) 


        #completing the current frame and updating the frame buffer
        s=delay-head.size #start of frame
        s_out_bo[0]=0
        if self.left!=0:
            self.frame[sig.size-self.left:]=sig[:self.left]
            #output
            s_out[0][0::2]=np.real(self.frame)
            s_out[0][1::2]=np.imag(self.frame)
            s_out_bo[0]=1
            #
            self.frame[:sig.size-s]=sig[s:]
        else: #no data left from previous frame
            self.frame[:sig.size-s]=sig[s:]
            if (s==0):
                 #output
                s_out[0][0::2]=np.real(self.frame)
                s_out[0][1::2]=np.imag(self.frame)
                s_out_bo[0]=1
                #
        self.left=s
        return 0     
    
    def reset_mem(self):  #reset mem
        self.buff=np.zeros(size_header-1) 
        self.frame=np.zeros(size+size_header) 
        return 0

    
    def __init__(self,window,len,header):
        self.len=len
        self.HEADER=header[0] #HEADER not yet Conjugated and "turned-around" version of the actual header ) to defined when framing
    
        self.size_header=header.size//2
        self.buff=np.zeros(self.size_header-1,dtype=complex)  #keep incomplete corr
        self.frame=np.zeros(self.len//2,dtype=complex) #buffer to temporarly store the frame 
        self.buff_empty=1
        self.left=0 #size left to complete current frame 

        Py_Module.__init__(self)
        self.name = "Frame_Synchronizer"
        tr_synch = self.create_task("tr_synchronize")
        s_in_sig= self.create_socket_in (tr_synch, "IN", window, np.float32)  #preferably input window should be smaller thacn frame size bigger than data size
        s_out_main= self.create_socket_out(tr_synch,"OUT1", len, np.float32)   #return frame size
        s_out_delay=self.create_socket_out(tr_synch,"OUT2", 1, np.int32)  #delay
        s_out_bool=self.create_socket_out(tr_synch,"OUT3", 1, np.int8)  #1 if output1 contains data

        self.create_codelet(tr_synch, lambda slf, lsk, fid: slf.synchronize(lsk[s_in_sig],lsk[s_out_main],lsk[s_out_delay],lsk[s_out_bool]))




#test


window=2048
size_header=64 #header size in symbols (cst to def) 
size= 1000  #data size in symbols (cst to def )
bps=2

src = py_aff3ct.module.source.Source_random(size)
cstl = py_aff3ct.tools.constellation.Constellation_QAM(bps)
mdm  = py_aff3ct.module.modem.Modem_generic(size, cstl)
pre=preamble.preamble(size_header,size)
head=pre.header 


h = []
for i in range(400):
    h.append(0)
h.append(1)
h.append(0)
h.append(0)
h.append(0)
h.append(0)

flt=eirballoon.filter.Filter_FIR_ccr_fast(size+2*size_header,h)
fr_syn=Frame_Synchronizer(size+2*size_header,size+2*size_header,head)


#src("generate").info()
#pre("insert_preamble").info()
#mdm("modulate").info()
#fr_syn("tr_synchronize").info()


mdm["modulate::X_N1"].bind(src["generate::U_K"])
pre["insert_preamble::s_in"].bind(mdm["modulate::X_N2"])
flt["filter :: X_N1"].bind(pre["insert_preamble::s_out"])
fr_syn["tr_synchronize::IN"].bind(flt["filter :: Y_N2"])


#src('generate').debug = True
#mdm('modulate').debug = True
fr_syn('tr_synchronize').debug = True
#pre('insert_preamble').debug=True
#fr_syn('tr_synchronize').set_debug_limit = 128
#pre('insert_preamble').set_debug_limit = 128

for i in range(10):

    src("generate").exec()
    mdm("modulate").exec()
    pre("insert_preamble").exec()
    flt("filter").exec()
    fr_syn("tr_synchronize").exec()

