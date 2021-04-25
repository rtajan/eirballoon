import sys  
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib')
sys.path.insert(0, '../../src/python')
from py_aff3ct.module.py_module import Py_Module
import py_aff3ct
import numpy as np
import os

class source_file(Py_Module):


    def int2binseq(self,N,size):     #int to numpy binary array of output size 
        tmp=bin(N)
        if(size<len(tmp)-2):
            print("taille donnée est trop petite")
            exit(1)
        out=np.zeros(size,dtype=int)
        for i in range(len(tmp)-2):
            out[i]=int(tmp[i+2])
        return out

    def update_attr(self):  #update class attributes 
        self.PACKET_TYPE=0
        self.PACKET_ID+=1
    
        if self.PACKET_ID==self.number_packet: #last packet
            self.PACKET_ID=2
        return 0

    def build_info_header(self): #updates info header   
        
        #set file type
        if (os.path.splitext(self.path)==".ts"):
            self.F_TYPE=0
        else:
            self.F_TYPE=1
        self.PACKET_ID = 1
        #set packet type
        self.PACKET_TYPE=1
        #building the header [P_TYPE P_ID F_ID F_TYPE F_SIZE]
        self.INFO=[]
        self.INFO=list(self.int2binseq(self.PACKET_TYPE,2))+list(self.int2binseq(self.PACKET_ID,16))+list(self.int2binseq(self.F_ID,16))+list(self.int2binseq(self.F_TYPE,2))+list(self.int2binseq(self.F_SIZE,24))
        return 0

    def generate(self,_out,nb,id):
        if self.frame_nb < 10:
            _out[0,::2]=np.ones((1,(self.N+self.INFO_SIZE)//2+1),dtype=np.int32)
            _out[0,1::2]=np.zeros((1,(self.N+self.INFO_SIZE)//2),dtype=np.int32)
        elif self.frame_nb==10:
            _out[0,::]=np.ones((1,self.N+self.INFO_SIZE),dtype=np.int32)
            
        else:
            _out[0,0:self.INFO_SIZE] = self.INFO
            _out[0,self.INFO_SIZE:] = self.src['generate::U_K'][:]
            self.src('generate').exec()
            nb[:]=self.number_packet
            id[:]=self.PACKET_ID
            self.update_attr()
            
        self.frame_nb+=1
        return 1
        


    def compute_packet_number(self):
        binary_size = os.path.getsize(self.path) * 8
        return np.ceil(binary_size//self.N)

    def binseq2int(self,seq): #binnary sequence 2 int 
        tmp=''
        for i in range(len(seq)):
            tmp+=str(seq(i))
        return(int(tmp,2))


    def decapsulate(self,enc_bits,out_data,out_p_type,out_p_id,out_f_type,out_f_id,out_f_size):  
        out_data[:]=enc_bits[self.INFO_SIZE:]
        out_p_type[:]=self.binseq2int(enc_bits[:2])
        out_p_id[:]=self.binseq2int(enc_bits[2:18])
        out_f_id[:]=self.binseq2int(enc_bits[18:34])
        out_f_type[:]=self.binseq2int(enc_bits[34:36])
        out_f_size[:]=self.binseq2int(enc_bits[36:60])
        return 0


    def __init__(self, path, N,auto_reset=False):
        Py_Module.__init__(self)
        if path:
            self.src = py_aff3ct.module.source.Source_user_binary(N, path, auto_reset=False)
        self.path = path
        self.N = N
        self.frame_nb = 1
        self.name = "source_file"
        if path:
            self.number_packet = self.compute_packet_number()

        #infos
        self.F_ID=0 #16 bits, file id (65536 file)
        self.F_TYPE=0 #1 bit , file type (0 .Ts file, 1 img any type) 
        self.F_SIZE=0 #24 bits to encode file size in bytes (< 16Mbytes)
        self.PACKET_ID=0#16 bits, packet order received for a ts file used to reorder in another  
        self.PACKET_TYPE=0 #2 bits to encode 3 types of frames ;1 start// 0 mid// 2 end// 
        #total 59 bits ########## [P_TYPE P_ID F_ID F_TYPE F_SIZE]
        self.INFO_SIZE=60
        if path:
            self.build_info_header()

        t_generate = self.create_task('generate')
        _out = self.create_socket_out(t_generate, 'U_K', N+self.INFO_SIZE, np.int32)
        nb = self.create_socket_out(t_generate, 'NB', 1, np.int32)
        id = self.create_socket_out(t_generate, 'ID', 1, np.int32)
        self.create_codelet(t_generate, lambda slf, lsk,
                            fid: slf.generate(lsk[_out],lsk[nb],lsk[id]))

        dt_dec = self.create_task("decapsulate")
        b_in_dec= self.create_socket_in (dt_dec, "IN", self.N+self.INFO_SIZE, np.int32)  #preferably input window should be smaller thacn frame size bigger than data size
        b_out_dec= self.create_socket_out(dt_dec,"OUT", self.N, np.int32)   #return frame size
        b_p_type= self.create_socket_out(dt_dec,"p_type", 1, np.int32)
        out_p_id= self.create_socket_out(dt_dec,"Packet_ID", 1, np.int32)
        out_f_id= self.create_socket_out(dt_dec,"Frame_ID", 1, np.int32)
        out_f_type= self.create_socket_out(dt_dec,"out_f_type", 1, np.int32)
        out_f_size= self.create_socket_out(dt_dec,"out_f_size", 1, np.int32)

        self.create_codelet(dt_dec, lambda slf, lsk, fid: slf.decapsulate(lsk[b_in_dec],lsk[b_out_dec],lsk[b_p_type],lsk[out_p_id],lsk[out_f_type],lsk[out_f_id],lsk[out_f_size]))