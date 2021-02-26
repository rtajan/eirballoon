import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.insert(0, '../../py_aff3ct/build/lib')
sys.path.insert(0, '../../src/python')
sys.path.insert(0, '../../build/lib')
import py_display
import py_aff3ct
import math
import source_img
import eirballoon


K = 2048  # msg_size
N = 4096  # packet size
bps = 1 #bits/symbol
Ns = N//bps
path = 'doggo.jpeg'

##Creating object



usrp_params = eirballoon.radio.USRP_params()
usrp_params.N          = K
usrp_params.threaded   = True
usrp_params.usrp_addr  = "type=b100"
usrp_params.tx_enabled = True
usrp_params.tx_rate    = 1e6
usrp_params.fifo_size = 10000
usrp_params.tx_antenna = "TX/RX"

radio   = eirballoon.radio.Radio_USRP(usrp_params)

#src = py_aff3ct.module.source.Source_random(K)

src = source_img.source_img(path,K)
#enc = py_aff3ct.module.encoder.Encoder_repetition_sys(K,N)
#cstl = py_aff3ct.tools.constellation.Constellation_QAM(bps)
mdm = py_aff3ct.module.modem.Modem_BPSK(K)
#chnl = py_aff3ct.module.channel.Channel_AWGN_LLR(K)
# dec = py_aff3ct.module.decoder.Decoder_repetition_std(K,N)
display = py_display.Display(N)
h   = eirballoon.filter.Filter_root_raised_cosine.synthetize(0.5,2,20)
flt = eirballoon.filter.Filter_UPFIR(K,h,2)
# mnt = py_aff3ct.module.monitor.Monitor_BFER_AR(K,100)

##Binding object

# enc['encode::U_K'].bind(src['generate::img'])
mdm['modulate::X_N1'].bind(src['generate::img'])
flt[  'filter::X_N1'].bind(mdm['modulate::X_N2'])
#chnl['add_noise::X_N'].bind(flt['filter::Y_N2'])
#display['plot::x'].bind(chnl['add_noise::Y_N'])
# mdm['demodulate::Y_N1'].bind(chnl['add_noise::Y_N'])
# dec['decode_siho::Y_N'].bind(mdm['demodulate::Y_N2'])
# display['plot::x'].bind(dec['decode_siho::V_K'])
# mnt['check_errors::U'].bind(src['generate::img'])
# mnt['check_errors::V'].bind(dec['decode_siho::V_K'])

##Paramètres cannal
sigma = np.ndarray(shape=(1,1),dtype = np.float32)
sigma[0]= 0

chnl['add_noise::CP'].bind(sigma)
#mdm['demodulate::CP'].bind(sigma)

#Execution
# src('generate').exec()
# enc('encode').exec()
# mdm('modulate').exec()
# chnl('add_noise').exec()
# mdm('demodulate').exec()
# dec('decode_siho').exec()
# display('plot').exec()
sequence = py_aff3ct.tools.sequence.Sequence(src('generate'),display('plot'),1)
sequence.exec()

# #Affichage
sent_signal = mdm['modulate::X_N2'][:]
recv_signal = mdm['demodulate::Y_N1'][:]

# fig1 = plt.figure(1)
# plt.plot(recv_signal[0, ::2],recv_signal[0, 1::2], '.')
# plt.plot(sent_signal[0, ::2], sent_signal[0,1::2],'+')
# plt.title("16-QAM constellation")
# plt.xlabel("In phase")
# plt.ylabel("Quadrature")
# plt.grid()

# plt.show()

#Erreur
# mnt('check_errors').debug=True
# mnt('check_errors').set_debug_limit(8)
# mnt('check_errors').exec()
# mnt('check_errors').debug=False


#BER/FER (frame error rate)
# ebn0_min = 0
# ebn0_max = 15.0
# ebn0_step = 0.5

# ebn0 = np.arange(ebn0_min,ebn0_max,ebn0_step)
# esn0 = ebn0 + 10 * math.log10(K/Ns)
# sigma_vals = 1/(math.sqrt(2) * 10 ** (esn0 / 20))

# fer = np.zeros(len(ebn0))
# ber = np.zeros(len(ebn0))

# n_threads = 6
# seq = py_aff3ct.tools.sequence.Sequence(src('generate'),mnt('check_errors'),n_threads)

# for i in range(len(sigma_vals)):
#     mnt.reset()
#     sigma[:]=sigma_vals[i]
#     seq.exec()

#     ber[i] = mnt.get_ber()
#     fer[i]=mnt.get_fer()

##Affichage BER/FER
# fig2= plt.figure(2)
# plt.semilogy(ebn0,fer,'r-',ebn0,ber,'b--')
# plt.show()
# plt.title("BER/FER en fonction de EbN0")
# plt.xlabel("EbN0")
# plt.ylabel("BER/FER")
# plt.grid()