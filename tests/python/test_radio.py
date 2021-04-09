from os import remove
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
import preamble
import frame_synchro
import correc_saut_phase

process=None

def signal_handler(sig, frame):
    #print('You pressed Ctrl+C!')
    sequence.show_stats()
    process.send_signal(signal.SIGINT)
    # raise KeyboardInterrupt

K=1024
N=2*K
Ns = N//2
h = 64
fse = 2
fech = 0.5e6
ref = 1
Ne = (h+Ns)*fse

usrp_params = eirballoon.radio.USRP_params()
usrp_params.N          = Ne
usrp_params.threaded   = True
usrp_params.usrp_addr  = "type=b100"
usrp_params.rx_enabled = True
usrp_params.rx_rate    = fech
usrp_params.fifo_size = 100000
usrp_params.rx_antenna = "RX2"
usrp_params.rx_freq = 2450e6
usrp_params.rx_gain = 10



pre=preamble.preamble(h,2*(Ns+h))
head=pre.header 

radio   = eirballoon.radio.Radio_USRP(usrp_params)
amp = mean_agc.Mean_Agc(ref,2*Ne)
itr = eirballoon.interrupteur.Interrupteur(2*Ne)

# sync_freq= freq_sync.freq_sync(fech,N*fse)
flt = eirballoon.filter.Filter_root_raised_cosine(2*Ne,0.5,fse,20)
stm = eirballoon.synchronizer.timing.Synchronizer_Gardner(2*Ne,fse)
stm.name="Stm"
sync_fine = synchro_freq_fine.synchro_freq_fine(fse,2*(Ns+h))
sync_fine.name="Sfr"
fr_syn=frame_synchro.Frame_Synchronizer(2*(Ns+h),2*(Ns+h),head)
itr_trame = eirballoon.interrupteur.Interrupteur(2*(Ns+h))
correc_phase = correc_saut_phase.Anti_saut_phase(2*(Ns+h),head)

noise = estimateur_bruit.Estimateur_bruit(2*(Ns+h),0.01)

mdm = py_aff3ct.module.modem.Modem_BPSK_fast(2*Ns)
dec = py_aff3ct.module.decoder.Decoder_repetition_std(K,N)
snk = py_aff3ct.module.sink.Sink_user_binary(K, 'toto.txt')


display = py_display.Display(2*(Ns+h),10)
info = display_info.display_info(1)

info.bind_display(stm['synchronize::MU'])
# info.bind_display(noise['estimate::cp'])
info.bind_display(noise["estimate::snr"])
info.bind_display(amp["amplify::gain_out"])
info.bind_display(fr_syn["tr_synchronize::delay"])
info.bind_display(amp["amplify::itr"])
info.bind_display(fr_syn["tr_synchronize::itr_tr"])
info.bind_display(correc_phase["sync::phase_jump"])
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
#stm['synchronize::X_N1'].bind(flt['filter::Y_N2'])


stm["synchronize::X_N1"].bind(flt['filter::Y_N2'])


#stm['synchronize::X_N1'].bind(pre["remove_preamble::s_out"])
stm['extract::Y_N1'].bind(stm['synchronize::Y_N1'])
stm['extract::B_N1'].bind(stm['synchronize::B_N1'])
# pream['sync_pream::sync_in'].bind(stm['extract::Y_N2'])

sync_fine['synchronize::sync_in'].bind(stm['extract::Y_N2'])
fr_syn["tr_synchronize::IN"].bind(sync_fine['synchronize::sync_out'])
display['plot::x'].bind(sync_fine['synchronize::sync_out'])
itr_trame["select::X_N"].bind(fr_syn['tr_synchronize::OUT'])
itr_trame["select::bln"].bind(fr_syn['tr_synchronize::itr_tr'])

noise['estimate::y'].bind(fr_syn['tr_synchronize::OUT'])
# pre["remove_preamble::s_in"].bind(fr_syn['tr_synchronize::OUT'])
correc_phase['sync::X_N'].bind(itr_trame["select::Y_N"])
pre["remove_preamble::s_in"].bind(correc_phase["sync::Y_N"])
mdm["demodulate::Y_N1"].bind(pre["remove_preamble::s_out"])
#display['plot::x'].bind(sync_fine['synchronize::sync_out'])
# CP = np.array([[1]],dtype=np.float32)
noise['estimate::y'].bind(fr_syn['tr_synchronize::OUT'])
mdm['demodulate::CP'].bind(noise['estimate::cp'])
# mdm['demodulate::CP'].bind(CP)
dec['decode_siho::Y_N'].bind(mdm['demodulate::Y_N2'])
snk['send::V'].bind(dec['decode_siho::V_K'])
# dec('decode_siho').debug = True
# mdm('demodulate').debug = True




sequence = py_aff3ct.tools.sequence.Sequence(radio("receive"))
#fr_syn("tr_synchronize").debug = True
# sequence = py_aff3ct.tools.sequence.Sequence(radio("receive"),dec('decode_siho'))

l_tasks = sequence.get_tasks_per_types()
for lt in l_tasks:
    for t in lt:
        t.stats = True
        #t.debug = True
        #t.set_debug_limit(1)
sequence.export_dot("seq.dot")
signal.signal(signal.SIGINT, signal_handler)
# signal.signal(signal.SIGINT, signal.default_int_handler)
# try:
sequence.exec()
    # raise KeyboardInterrupt
# except KeyboardInterrupt:
sequence.show_stats()

    
