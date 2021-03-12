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
import sync_pream
import agc
import freq_sync
import synchro_freq_fine
import signal
import mean_agc

process=None

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sequence.show_stats()
    process.send_signal(signal.SIGINT)
    # raise KeyboardInterrupt

N=1024
fse = 2

usrp_params = eirballoon.radio.USRP_params()
usrp_params.N          = N*fse//2
usrp_params.threaded   = True
usrp_params.usrp_addr  = "type=b100"
usrp_params.rx_enabled = True
usrp_params.rx_rate    = 125e3
usrp_params.fifo_size = 100000
usrp_params.rx_antenna = "RX2"
usrp_params.rx_freq = 2450e6
usrp_params.rx_gain = 10

radio   = eirballoon.radio.Radio_USRP(usrp_params)
# amp = test_ampli.test_ampli(25,N*fse)
# amp = agc.Agc(0.001,1e-5,N*fse)
amp = mean_agc.Mean_Agc(5,N*fse)
# sync_freq= freq_sync.freq_sync(125e3,N*fse)
display = py_display.Display(N,10)
flt = eirballoon.filter.Filter_root_raised_cosine(N*fse,0.5,fse,20)
stm = eirballoon.synchronizer.timing.Synchronizer_Gardner(N*fse,fse)
stm.name="Stm"
sync_fine = synchro_freq_fine.synchro_freq_fine(fse,N)
sync_fine.name="Sfr"
# pream = sync_pream.sync_pream(128,N)


amp["amplify::amp_in"].bind(radio["receive::Y_N1"])
flt['filter::X_N1'].bind(amp['amplify::amp_out'])
# sync_freq['sync::sync_in'].bind(flt['filter::Y_N2'])
# stm['synchronize::X_N1'].bind(sync_freq['sync::sync_out'])
stm['synchronize::X_N1'].bind(flt['filter::Y_N2'])

stm['extract::Y_N1'].bind(stm['synchronize::Y_N1'])
stm['extract::B_N1'].bind(stm['synchronize::B_N1'])
# pream['sync_pream::sync_in'].bind(stm['extract::Y_N2'])
sync_fine['synchronize::sync_in'].bind(stm['extract::Y_N2'])

display['plot::x'].bind(sync_fine['synchronize::sync_out'])

# sequence = py_aff3ct.tools.sequence.Sequence(radio("receive"),sync_fine("synchronize"))
sequence = py_aff3ct.tools.sequence.Sequence(radio("receive"),display("plot"))

l_tasks = sequence.get_tasks_per_types()
for lt in l_tasks:
    for t in lt:
        t.stats = True
#sequence . export_dot("seq.dot")
signal.signal(signal.SIGINT, signal_handler)
# signal.signal(signal.SIGINT, signal.default_int_handler)
# try:
sequence.exec()
    # raise KeyboardInterrupt
# except KeyboardInterrupt:
sequence.show_stats()

    
