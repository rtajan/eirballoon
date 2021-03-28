import sys  
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib')
sys.path.insert(0, '../../src/python')
import py_aff3ct
import eirballoon
import numpy as np
import matplotlib.pyplot as plt
import py_display
import display_info
import synchro_freq_fine
import signal
import mean_agc
import estimateur_bruit

process=None

def signal_handler(sig, frame):
    #print('You pressed Ctrl+C!')
    sequence.show_stats()
    process.send_signal(signal.SIGINT)
    # raise KeyboardInterrupt

N=1024
fse = 2
fech = 1e6
usrp_params = eirballoon.radio.USRP_params()
usrp_params.N          = N*fse
usrp_params.threaded   = True
usrp_params.usrp_addr  = "type=b100"
usrp_params.rx_enabled = True
usrp_params.rx_rate    = fech
usrp_params.fifo_size = 100000
usrp_params.rx_antenna = "RX2"
usrp_params.rx_freq = 2450e6
usrp_params.rx_gain = 10

radio   = eirballoon.radio.Radio_USRP(usrp_params)
# amp = test_ampli.test_ampli(25,N*fse)
# amp = agc.Agc(0.001,1e-5,N*fse)
amp = mean_agc.Mean_Agc(2,N*fse*2)
# sync_freq= freq_sync.freq_sync(fech,N*fse)
display = py_display.Display(N*fse,10)
flt = eirballoon.filter.Filter_root_raised_cosine(N*fse*2,0.5,fse,20)
stm = eirballoon.synchronizer.timing.Synchronizer_Gardner(N*fse*2,fse)
stm.name="Stm"
noise = estimateur_bruit.Estimateur_bruit(N*2,0.01)
sync_fine = synchro_freq_fine.synchro_freq_fine(fse,N*2)
sync_fine.name="Sfr"
dec = py_aff3ct.module.decoder.Decoder_repetition_std(N,N*2)
mdm = py_aff3ct.module.modem.Modem_BPSK_fast(N*fse)
snk = py_aff3ct.module.sink.Sink_user_binary(N, 'toto.dat')
info = display_info.display_info()
itr = eirballoon.interrupteur.Interrupteur(N*fse*2)

info.bind_display(stm['synchronize::MU'])
info.bind_display(noise['estimate::cp'])
info.bind_display(noise["estimate::snr"])
info.bind_display(amp["amplify::gain_out"])
info.bind_display(amp["amplify::itr"])
info.done()


# pream = sync_pream.sync_pream(128,N)



amp["amplify::amp_in"].bind(radio["receive::Y_N1"])
itr["select::bln"].bind(amp["amplify::itr"])
itr["select::X_N"].bind(amp["amplify::amp_out"])
# sync_freq["sync::sync_in"].bind(amp['amplify::amp_out'])
# flt['filter::X_N1'].bind(sync_freq["sync::sync_out"])
flt['filter::X_N1'].bind(itr["select::Y_N"])
# sync_freq['sync::sync_in'].bind(flt['filter::Y_N2'])
# stm['synchronize::X_N1'].bind(sync_freq['sync::sync_out'])
stm['synchronize::X_N1'].bind(flt['filter::Y_N2'])

stm['extract::Y_N1'].bind(stm['synchronize::Y_N1'])
stm['extract::B_N1'].bind(stm['synchronize::B_N1'])
# pream['sync_pream::sync_in'].bind(stm['extract::Y_N2'])
sync_fine['synchronize::sync_in'].bind(stm['extract::Y_N2'])

#display['plot::x'].bind(sync_fine['synchronize::sync_out'])
mdm['demodulate::Y_N1'].bind(sync_fine['synchronize::sync_out'])
# CP = np.array([[1]],dtype=np.float32)
noise['estimate::y'].bind(sync_fine['synchronize::sync_out'])
mdm['demodulate::CP'].bind(noise['estimate::cp'])
dec['decode_siho::Y_N'].bind(mdm['demodulate::Y_N2'])
snk['send::V'].bind(dec['decode_siho::V_K'])
# display['plot::x'].bind(sync_fine["synchronize::sync_out"])
# dec('decode_siho').debug = True
# mdm('demodulate').debug = True




sequence = py_aff3ct.tools.sequence.Sequence(radio("receive"),snk("send"))

# sequence = py_aff3ct.tools.sequence.Sequence(radio("receive"),dec('decode_siho'))

l_tasks = sequence.get_tasks_per_types()
for lt in l_tasks:
    for t in lt:
        t.stats = True
        #t.debug = True
        t.set_debug_limit(1)
#sequence . export_dot("seq.dot")
signal.signal(signal.SIGINT, signal_handler)
# signal.signal(signal.SIGINT, signal.default_int_handler)
# try:
sequence.exec()
    # raise KeyboardInterrupt
# except KeyboardInterrupt:
sequence.show_stats()

    
