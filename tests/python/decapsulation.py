import sys

import numpy as np
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib')
sys.path.insert(0, '../../src/python')
from py_aff3ct.module.py_module import Py_Module
from bitstring import BitArray



class decapsulation(Py_Module):


    def binseq2int(self,seq): #binnary sequence 2 int 
        return BitArray(seq[:]).uint



    def decapsulate(self,enc_bits,out_data,out_p_type,out_p_id,out_f_type,out_f_id,out_f_size,out_ts, out_jpeg):  
        out_data[:]=enc_bits[0,self.INFO_SIZE:]
        out_p_type[:]=self.binseq2int(enc_bits[0,:2])
        out_p_id[:]=self.binseq2int(enc_bits[0,2:18])
        out_f_id[:]=self.binseq2int(enc_bits[0,18:34])
        out_f_type[:]=self.binseq2int(enc_bits[0,34:36])
        out_f_size[:]=self.binseq2int(enc_bits[0,36:60])

        if out_f_type[::] == 0:
            out_ts[:]=0
            out_jpeg[:] = 1
        else:
            out_ts[:]=1
            out_jpeg[:] = 0
        return 0

    def __init__(self, N):

        Py_Module.__init__(self)

        self.N = N
        #infos
        self.F_ID=0 #16 bits, file id (65536 file)
        self.F_TYPE=0 #1 bit , file type (0 .Ts file, 1 img any type
        self.PACKET_ID=0#16 bits, packet order received for a ts file used to reorder in another  
        self.PACKET_TYPE=0 #2 bits to encode 3 types of frames ;1 start// 0 mid// 2 end// 
        #total 59 bits ########## [P_TYPE P_ID F_ID F_TYPE F_SIZE]
        self.INFO_SIZE=60

        dt_dec = self.create_task("decapsulate")
        # preferably input window should be smaller thacn frame size bigger than data size
        b_in_dec = self.create_socket_in(
            dt_dec, "IN", self.N+self.INFO_SIZE, np.int32)
        b_out_dec = self.create_socket_out(
            dt_dec, "OUT", self.N, np.int32)  # return frame size
        b_p_type = self.create_socket_out(dt_dec, "p_type", 1, np.int32)
        out_p_id = self.create_socket_out(dt_dec, "Packet_ID", 1, np.int32)
        out_f_id = self.create_socket_out(dt_dec, "Frame_ID", 1, np.int32)
        out_f_type = self.create_socket_out(
            dt_dec, "out_f_type", 1, np.int32)
        out_f_size = self.create_socket_out(
            dt_dec, "out_f_size", 1, np.int32)
        b_ts = self.create_socket_out(dt_dec, "ts_type", 1, np.int32)
        b_jpeg = self.create_socket_out(dt_dec, "jpeg_type", 1, np.int32)    

        self.create_codelet(dt_dec, lambda slf, lsk, fid: slf.decapsulate(
            lsk[b_in_dec], lsk[b_out_dec], lsk[b_p_type], lsk[out_p_id], lsk[out_f_type], lsk[out_f_id], lsk[out_f_size],lsk[b_ts],lsk[b_jpeg]))
