import sys  
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib')
import py_aff3ct
import eirballoon

import numpy as np

src = py_aff3ct.module.source.Source_random(1024)
mod = py_aff3ct.module.modem.Modem_BPSK(1024)
h   = eirballoon.filter.Filter_root_raised_cosine.synthetize(0.5,2,20)
flt = eirballoon.filter.Filter_UPFIR(1024,h,2)

usrp_params = eirballoon.radio.USRP_params()
usrp_params.N          = 1024
usrp_params.threaded   = False
usrp_params.usrp_addr  = "type=b100"
usrp_params.tx_enabled = True
usrp_params.tx_rate    = 1e6
usrp_params.fifo_size  = 10000
usrp_params.tx_antenna = "TX/RX"

radio   = eirballoon.radio.Radio_USRP(usrp_params)

mod['modulate::X_N1'].bind(src['generate::U_K' ])
flt[  'filter::X_N1'].bind(mod['modulate::X_N2'])
#flt.info()
#radio.info()
radio['send::X_N1'].bind(flt['filter::Y_N2'])

sequence = py_aff3ct.tools.sequence.Sequence(src('generate'),radio('send'),1)
sequence.exec()

# src('generate').exec()
# mod('modulate').exec()
# flt('filter'  ).exec()
# radio('send').exec()