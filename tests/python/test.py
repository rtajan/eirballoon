from os import fsencode
import sys  
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib')
sys.path.insert(0, '../../src/python')
import py_aff3ct
import eirballoon
import display_info
import test_ampli
import numpy as np
# import source_img
import matplotlib.pyplot as plt
import signal
import preamble
import scrambler
import source_file
import argparse

process=None

def signal_handler(sig, frame):
    sequence.show_stats()
    sequence.export_dot("seq.dot")
    radio.stop_tx()
    raise RuntimeError

if __name__ == "__main__":
    parser =  argparse.ArgumentParser()
    parser.add_argument("name",type=str)
    parser.add_argument("-f","--fech",type=float,default=1)
    args = parser.parse_args()

    N= 8*188
    H = 60
    HN = N + H
    Nenc = 3*HN
    P = 64
    K = 2*Nenc+4*P
    #src = py_aff3ct.module.source.Source_random(N)
    src = source_file.source_file(args.name,N)
    #src = py_aff3ct.module.source.Source_user_binary(N,'source.ts',auto_reset=True)
    scb = scrambler.scrambler(HN,"scramble")
    enc = py_aff3ct.module.encoder.Encoder_repetition_sys(HN,Nenc)
    mod = py_aff3ct.module.modem.Modem_BPSK_fast(Nenc)
    pre = preamble.preamble(P,Nenc)
    h   = eirballoon.filter.Filter_root_raised_cosine.synthetize(0.7,2,20)
    flt = eirballoon.filter.Filter_UPFIR(Nenc+2*P,h,2)
    

    amp = test_ampli.test_ampli(0.7,K)
    

    fech = args.fech*1e6

    hrfp = eirballoon.radio.HACKRF_params()
    hrfp.N = K//2
    hrfp.fifo_size = 100
    hrfp.rx_rate = fech
    hrfp.rx_freq = 2450e6
    hrfp.tx_rate =  fech
    radio = eirballoon.radio.Radio_HACKRF(hrfp)

    # usrp_params = eirballoon.radio.USRP_params()
    # usrp_params.N          = K//2
    # usrp_params.threaded   = True
    # usrp_params.usrp_addr  = "type=b100"
    # usrp_params.tx_enabled = True
    # usrp_params.tx_rate    = fech
    # usrp_params.fifo_size  = 100000
    # usrp_params.tx_antenna = "TX/RX"
    # usrp_params.tx_freq    = 2450e6

    # radio   = eirballoon.radio.Radio_USRP(usrp_params)
    f2i = eirballoon.converter.Converter_f2i(hrfp.N*2)


    scb["scramble::X_N"].bind(src['generate::U_K' ])
    enc['encode::U_K'].bind(scb["scramble::Y_N"])
    mod['modulate::X_N1'].bind(enc['encode::X_N'])
    pre['insert_preamble::s_in'].bind(mod['modulate::X_N2'])
    flt[  'filter::X_N1'].bind(pre['insert_preamble::s_out'])
    amp['amplify::amp_in'].bind(flt['filter::Y_N2'])
    f2i  ["convert::X_N" ].bind(amp['amplify::amp_out'])
    radio['send::X_N1'].bind(f2i["convert::Y_N"])
    # radio['send::X_N1'].bind(amp['amplify::amp_out'])


    inf = display_info.display_info(dc=10)
    inf.bind_display(src['generate::NB'])
    inf.bind_display(src['generate::ID'])
    inf.bind_display(src['generate::type'])
    inf.done()


    sequence = py_aff3ct.tools.sequence.Sequence(src('generate'),radio('send'),1)



    l_tasks = sequence.get_tasks_per_types()
    for lt in l_tasks:
        for t in lt:
            t.stats = True
            #t.debug = True


    signal.signal(signal.SIGINT, signal_handler)
    radio.start_tx()
    sequence.exec()
    sequence.show_stats()
# src('generate').exec()
# mod('modulate').exec()
# flt('filter'  ).exec()
# amp('amplify' ).exec()
# display('plot').exec()

# src_signal = src['generate::img'][:]
# sent_signal = mod['modulate::X_N2'][:]

# radio('send').exec()