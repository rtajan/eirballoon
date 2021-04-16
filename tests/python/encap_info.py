import sys
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib') 
import py_aff3ct
from py_aff3ct.module.py_module import Py_Module
import numpy as np
import eirballoon
import os 

######################
class data_encapsulation(Py_Module):

    def int2binseq(self,N,size):     #int to numpy binary array of output size 
        tmp=bin(N)
        if(size<len(tmp)-2):
            print("taille donnée est trop petite")
            exit(1)
        out=np.zeros(size,dtype=int)
        for i in range(len(tmp)-2):
            out[i]=int(tmp[i+2])
        return out
    
    def build_info_header(self): #updates info header   
        
        #set file type
        if (os.path.splitext(self.F_PATH)==".ts"):
            self.F_TYPE=0
        else:
            self.F_TYPE=1
        
        #set packet type
        self.PACKET_TYPE=0
        if(self.PACKET_ID==0):
            print("first packet")
            self.PACKET_TYPE=1
            self.F_SIZE=os.path.getsize(self.F_PATH) #set total file size (in bytes)
        
        elif (self.PACKET_ID+1)*self.PACKET_SIZE>=self.F_SIZE:
            self.PACKET_TYPE=2

        #building the header [P_TYPE P_ID F_ID F_TYPE F_SIZE]
        self.INFO=[]
        self.INFO=list(self.int2binseq(self.PACKET_TYPE,2))+list(self.int2binseq(self.PACKET_ID,16))+list(self.int2binseq(self.F_ID,16))+list(self.int2binseq(self.F_TYPE,1))+list(self.int2binseq(self.F_SIZE,24))
        return 0

    def update_attr(self):  #update class attributes 

        self.PACKET_ID+=1
    
        if self.PACKET_TYPE==2: #last packet
            self.F_ID+=1 
            self.PACKET_ID=0
        return 0


    def encapsulate(self,bits,s_out):    
        s_out=np.array(self.INFO+list(bits[0]))
        print(s_out)
        return 0     
    
    #def deencapsulate(self,recv,):  
        #return 0
    
    def __init__(self,len):
        
        #infos
        self.F_ID=0 #16 bits, file id (65536 file)
        self.F_TYPE=0 #1 bit , file type (0 .Ts file, 1 img any type) 
        self.F_SIZE=0 #24 bits to encode file size in bytes (< 16Mbytes)
        self.PACKET_ID=0#16 bits, packet order received for a ts file used to reorder in another  
        self.PACKET_TYPE=0 #2 bits to encode 3 types of frames ;1 start// 0 mid// 2 end// 
        #total 59 bits ########## [P_TYPE P_ID F_ID F_TYPE F_SIZE]
        
        
        #
        self.PACKET_SIZE=len #packet size
        self.INFO_SIZE=59
        self.F_PATH='./test_tmp/test.ts'
        
        #create/update info header
        self.build_info_header() #

        print(self.INFO)

        Py_Module.__init__(self)
        self.name = "data_encapsulation"
        dt_enc = self.create_task("encapsulate")
        b_in= self.create_socket_in (dt_enc, "IN", self.PACKET_SIZE, np.int32)  #preferably input window should be smaller thacn frame size bigger than data size
        b_out_main= self.create_socket_out(dt_enc,"OUT", self.PACKET_SIZE+self.INFO_SIZE, np.int32)   #return frame size

        self.create_codelet(dt_enc, lambda slf, lsk, fid: slf.encapsulate(lsk[b_in],lsk[b_out_main]))




#test

N=300
src = py_aff3ct.module.source.Source_user_binary(N,'./test_tmp/test.ts',auto_reset=True)
enc=data_encapsulation(300)


enc["encapsulate::IN"].bind(src["generate::U_K"])

src('generate').debug = True
enc('encapsulate').debug = True

src("generate").exec()
enc("encapsulate").exec()


