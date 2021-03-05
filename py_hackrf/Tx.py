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

class Tx(gr.top_block):
    
    

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet")

        ##################################################
        # Variables
        ##################################################
        config =  Mytools.Config.read()
        path_pip = Mytools.getPipPath( config['pip']["Aff3ct2Tx"])

        self.samp_rate = samp_rate = float(config['hackRF']["samp_rate"]) # 32000
        self.freq_p    = freq_p    = float(config['hackRF']["Fp"])
        self.gain    = gain    = int(config['hackRF']['Tx']["gain"])
        self.IFgain    = IFgain  = int(config['hackRF']['Tx']["IFgain"])
        self.BBgain    = BBgain  = int(config['hackRF']['Tx']["BBgain"])
        ##################################################
        # Blocks
        ##################################################
        self.osmosdr_sink_0 = osmosdr.sink(
            args="numchan=" + str(1) + " " + 'hackrf'
        )
        self.osmosdr_sink_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq(freq_p, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(gain, 0)
        self.osmosdr_sink_0.set_if_gain(IFgain, 0)
        self.osmosdr_sink_0.set_bb_gain(BBgain, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)
        self.blocks_file_descriptor_source_0 = blocks.file_descriptor_source(gr.sizeof_gr_complex*1, os.open(path_pip,os.O_RDONLY), False)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_descriptor_source_0, 0), (self.osmosdr_sink_0, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)

    def get_freq_p(self):
        return self.freq_p

    def set_freq_p(self, freq_p):
        self.freq_p = freq_p
        self.osmosdr_sink_0.set_center_freq(self.freq_p, 0)



def main(top_block_cls=Tx, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
