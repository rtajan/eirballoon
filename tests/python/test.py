import sys  
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib')
sys.path.insert(0, '../../src/python')
import py_display
import py_aff3ct
import eirballoon
import test_ampli
import numpy as np
import source_img
import matplotlib.pyplot as plt


N=1024

#src = py_aff3ct.module.source.Source_random(N)
src = source_img.source_img('doggo.jpeg',N)

mod = py_aff3ct.module.modem.Modem_BPSK(N)
h   = eirballoon.filter.Filter_root_raised_cosine.synthetize(0.5,2,20)
flt = eirballoon.filter.Filter_UPFIR(N,h,2)
amp = test_ampli.test_ampli(0.7,2*N)

usrp_params = eirballoon.radio.USRP_params()
usrp_params.N          = N
usrp_params.threaded   = True
usrp_params.usrp_addr  = "type=b100"
usrp_params.tx_enabled = True
usrp_params.tx_rate    = 125e3
usrp_params.fifo_size  = 10000
usrp_params.tx_antenna = "TX/RX"
usrp_params.tx_freq    = 2450e6

radio   = eirballoon.radio.Radio_USRP(usrp_params)
display = py_display.Display(2*N)



mod['modulate::X_N1'].bind(src['generate::img' ])
flt[  'filter::X_N1'].bind(mod['modulate::X_N2'])
amp['amplify::amp_in'].bind(flt['filter::Y_N2'])
radio['send::X_N1'].bind(amp['amplify::amp_out'])
display['plot::x'].bind(amp['amplify::amp_out'])


sequence = py_aff3ct.tools.sequence.Sequence(src('generate'),radio('send'),1)
sequence.exec()

# src('generate').exec()
# mod('modulate').exec()
# flt('filter'  ).exec()
# amp('amplify' ).exec()
# display('plot').exec()

# src_signal = src['generate::img'][:]
# sent_signal = mod['modulate::X_N2'][:]

# radio('send').exec()