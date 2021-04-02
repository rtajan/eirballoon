import sys  
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib')
sys.path.insert(0, '../../src/python')
import py_display
import py_aff3ct
import eirballoon
import display_info
import test_ampli
import numpy as np
# import source_img
import matplotlib.pyplot as plt
import signal
import preamble

process=None

def signal_handler(sig, frame):
    sequence.show_stats()
    raise RuntimeError


N= 1024
Nenc = 2*N
P = 64
K = 2*Nenc+4*P
#src = py_aff3ct.module.source.Source_random(N)
#src = source_img.source_img('doggo.jpeg',N)
src = py_aff3ct.module.source.Source_user_binary(N,'doggo.jpeg',auto_reset=True)
enc = py_aff3ct.module.encoder.Encoder_repetition_sys(N,Nenc)
mod = py_aff3ct.module.modem.Modem_BPSK_fast(Nenc)
pre = preamble.preamble(P,Nenc)
h   = eirballoon.filter.Filter_root_raised_cosine.synthetize(0.7,2,20)
flt = eirballoon.filter.Filter_UPFIR(Nenc+2*P,h,2)

amp = test_ampli.test_ampli(0.7,K)
#inf = display_info.display_info()
# inf.register_input("source",np.int32,N)
# inf.bind_display(src['generate::U_K' ])
# inf.done()

usrp_params = eirballoon.radio.USRP_params()
usrp_params.N          = K//2
usrp_params.threaded   = True
usrp_params.usrp_addr  = "type=b100"
usrp_params.tx_enabled = True
usrp_params.tx_rate    = 1e6
usrp_params.fifo_size  = 10000
usrp_params.tx_antenna = "TX/RX"
usrp_params.tx_freq    = 2450e6

radio   = eirballoon.radio.Radio_USRP(usrp_params)
display = py_display.Display(K,2)



enc['encode::U_K'].bind(src['generate::U_K' ])
mod['modulate::X_N1'].bind(enc['encode::X_N'])
pre['insert_preamble::s_in'].bind(mod['modulate::X_N2'])
flt[  'filter::X_N1'].bind(pre['insert_preamble::s_out'])
amp['amplify::amp_in'].bind(flt['filter::Y_N2'])
radio['send::X_N1'].bind(amp['amplify::amp_out'])
display['plot::x'].bind(amp['amplify::amp_out'])


sequence = py_aff3ct.tools.sequence.Sequence(src('generate'),radio('send'),1)



l_tasks = sequence.get_tasks_per_types()
for lt in l_tasks:
    for t in lt:
        t.stats = True


signal.signal(signal.SIGINT, signal_handler)

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