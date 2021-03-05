#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: damienm
# GNU Radio version: 3.8.1.0

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import osmosdr
import time
import os
import Mytools
from time import sleep
from scipy.io import savemat # pour save en fichier *.mat
import numpy as np

# https://www.reddit.com/r/hackrf/comments/49aa2i/using_gain_controls_with_osmocom_sourcesink_in/
    # [-l gain_db] # RX LNA (IF) gain, 0-40dB, 8dB steps
    # [-g gain_db] # RX VGA (baseband) gain, 0-62dB, 2dB steps
    # [-x gain_db] # TX VGA (IF) gain, 0-47dB, 1dB steps
    # [-a amp_enable] # RX/TX RF amplifier 1=Enable, 0=Disable

#     -l corresponds to "IF gain" on the source
#     -g corresponds to "BB gain" on the source
#     -x corresponds to "IF gain" on the sink
#     -a corresponds to "RF gain" on both (0 dB will turn the amp off, 14 dB will turn it on, values in between shouldn't be used, but I think they behave the same as 0).
# BB gain on the sink, AFAIK, does nothing, because the DAC always outputs at the same power.


class Rx_fd(gr.top_block):

    def __init__(self,record = False):
        print("record",record)
        gr.top_block.__init__(self, "Not titled yet")

        ##################################################
        # Variables
        ##################################################
        
        config =  Mytools.Config.read()
        if(record):
            path_pip = Mytools.getRecordDir() + config["record_name"]
        else:
            path_pip = Mytools.getPipPath( config['pip']["Rx2Aff3ct"])

        self.samp_rate = samp_rate = float(config['hackRF']["samp_rate"]) # 32000
        self.freq_p = freq_p       = float(config['hackRF']["Fp"])
        self.gain    = gain        = int(config['hackRF']['Rx']["gain"])
        self.IFgain    = IFgain    = int(config['hackRF']['Rx']["IFgain"])
        self.BBgain    = BBgain    = int(config['hackRF']['Rx']["BBgain"])

        # print("samp_rate",samp_rate)
        # print("freq_p",freq_p)
        # print("gain",gain)
        # print("IFgain",IFgain)
        # print("BBgain",BBgain)

        ##################################################
        # Blocks
        ##################################################
        self.osmosdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + 'hackrf=1'
        )
        self.osmosdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(freq_p, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_gain(gain, 0)
        self.osmosdr_source_0.set_if_gain(IFgain, 0)
        self.osmosdr_source_0.set_bb_gain(BBgain, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, path_pip, False)
        self.blocks_file_sink_0.set_unbuffered(False)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.osmosdr_source_0, 0), (self.blocks_file_sink_0, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)

    def get_freq_p(self):
        return self.freq_p

    def set_freq_p(self, freq_p):
        self.freq_p = freq_p
        self.osmosdr_source_0.set_center_freq(self.freq_p, 0)



def main(top_block_cls=Rx_fd, record=False,time=None):
    tb = top_block_cls(record)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    if(record):
        sleep(time*1e-3)
        tb.stop()
    tb.wait()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-r", "--rec",type=int, help="record, usage -r [time in ms]")
    args = parser.parse_args()
    if args.rec:        
        if not os.path.exists('record'):
            os.makedirs('record')
        rec = True
        time = args.rec
    else:
        rec = False
        time = None
    main(record=rec,time=time)

    if args.rec: 
        ## Enregistrer dans un fichier *.mat
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.savemat.html
        #     
        print("creation fichier matlab")
        type_numbers =  np.complex64

        config =  Mytools.Config.read()   
        path_record_bin = Mytools.getRecordDir() + config["record_name"]
        path_record_mat = Mytools.getRecordDir() + "data.mat"
        
        fd = open(path_record_bin, 'r')
        ele = fd.buffer.read()
        array = np.frombuffer(ele, dtype=type_numbers) 
        out_mat = {"data": array}
        savemat(path_record_mat,out_mat)
