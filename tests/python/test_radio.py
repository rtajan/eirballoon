import sys  
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib')
sys.path.insert(0, '../../src/python')
import py_aff3ct
import eirballoon
import numpy as np
import matplotlib.pyplot as plt
import py_display
import test_ampli

N=4096
fse = 2

usrp_params = eirballoon.radio.USRP_params()
usrp_params.N          = N*fse//2
usrp_params.threaded   = True
usrp_params.usrp_addr  = "type=b100"
usrp_params.rx_enabled = True
usrp_params.rx_rate    = 1e6
usrp_params.fifo_size = 10000
usrp_params.rx_antenna = "RX2"
usrp_params.rx_freq = 833e6
usrp_params.rx_gain = 10

radio   = eirballoon.radio.Radio_USRP(usrp_params)
amp = test_ampli.test_ampli(5,N*fse)
display = py_display.Display(N)
flt = eirballoon.filter.Filter_root_raised_cosine(N*fse,0.5,fse,20)
stm = eirballoon.synchronizer.timing.Synchronizer_Gardner(N*fse,fse)

amp["amplify::amp_in"].bind(radio["receive::Y_N1"])
flt['filter::X_N1'].bind(amp['amplify::amp_out'])
stm['synchronize::X_N1'].bind(flt['filter::Y_N2'])
stm['extract::Y_N1'].bind(stm['synchronize::Y_N1'])
stm['extract::B_N1'].bind(stm['synchronize::B_N1'])

display['plot::x'].bind(stm['extract::Y_N2'])



sequence = py_aff3ct.tools.sequence.Sequence(radio("receive"), display("plot"))
sequence.exec()