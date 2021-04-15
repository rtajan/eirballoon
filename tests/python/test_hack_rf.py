from os import remove
import sys
import signal
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib')
sys.path.insert(0, '../../src/python')
import eirballoon
import py_display
import numpy as np
import py_aff3ct
import display_info
import test_ampli
import preamble


N= 8*188
Nenc = 2*N
P = 64
K = 2*Nenc+4*P

src = py_aff3ct.module.source.Source_user_binary(N,'video_src.ts',auto_reset=True)
enc = py_aff3ct.module.encoder.Encoder_repetition_sys(N,Nenc)
mod = py_aff3ct.module.modem.Modem_BPSK_fast(Nenc)
pre = preamble.preamble(P,Nenc)
h   = eirballoon.filter.Filter_root_raised_cosine.synthetize(0.7,2,20)
flt = eirballoon.filter.Filter_UPFIR(Nenc+2*P,h,2)

amp = test_ampli.test_ampli(0.7,K)

hrfp = eirballoon.radio.HACKRF_params()
hrfp.N = K//2
hrfp.fifo_size = 10000
hrfp.rx_rate = 0.5e6
hrfp.rx_freq = 2450e6
hrfp.tx_rate =  0.5e6
radio = eirballoon.radio.Radio_HACKRF(hrfp)
f2i = eirballoon.converter.Converter_f2i(hrfp.N*2)

#display = py_display.Display(2*hrfp.N ,10)

enc['encode::U_K'].bind(src['generate::U_K' ])
mod['modulate::X_N1'].bind(enc['encode::X_N'])
pre['insert_preamble::s_in'].bind(mod['modulate::X_N2'])
flt[  'filter::X_N1'].bind(pre['insert_preamble::s_out'])
amp['amplify::amp_in'].bind(flt['filter::Y_N2'])
f2i  ["convert::X_N" ].bind(amp['amplify::amp_out'])
radio[   "send::X_N1"].bind(f2i["convert::Y_N"])

#display['plot::x'].bind(f2i["convert::X_N"])
sequence = py_aff3ct.tools.sequence.Sequence(src('generate'),radio('send'),1)

l_tasks = sequence.get_tasks_per_types()
for lt in l_tasks:
    for t in lt:
        t.stats = True

radio.start_tx()
#signal.signal(signal.SIGINT, signal_handler)
sequence.exec()
sequence.show_stats()

radio.stop_tx()