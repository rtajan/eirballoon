import argparse
import decapsulation
import source_file
import float_to_int
import detect_coming_trame
import scrambler
import correc_saut_phase
import frame_synchro
import preamble
import estimateur_bruit
import mean_agc
import signal
import synchro_freq_fine
import display_info
import py_display
import matplotlib.pyplot as plt
import numpy as np
import eirballoon
import py_aff3ct
import os
import sys
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib')
sys.path.insert(0, '../../src/python')

process = None


def signal_handler(sig, frame):
    #print('You pressed Ctrl+C!')
    sequence.export_dot("seq.dot")
    sequence.show_stats()
    process.send_signal(signal.SIGINT)

    # raise KeyboardInterrupt


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str)  # fichier d'enregistrement
    parser.add_argument("--fech", type=int, default=0.5e6)
    args = parser.parse_args()

    ###Creation du dossier d'enregistrement###
    path = "./"+args.file
    try:
        os.mkdir(path)
    except OSError:
        print("Les images et vidéos seront enregistrées ici : %s " % path)
    else:
        print("Les images et vidéos seront enregistrées ici : %s " % path)


    H = 60  # taille du Header
    K = 8*188  # nombre de bits utiles
    HK = K+H  # Taille packet
    N = 3*HK  # Taille packet encodé
    Ns = N//2  # Nombre de symbole
    h = 64  # taille du préambule

    fse = 2
    fech = args.fech
    ref = 1
    Ne = (h+Ns)*fse

    usrp_params = eirballoon.radio.USRP_params()
    usrp_params.N = Ne
    usrp_params.threaded = True
    usrp_params.usrp_addr = "type=b100"
    usrp_params.rx_enabled = True
    usrp_params.rx_rate = fech
    usrp_params.fifo_size = 100000
    usrp_params.rx_antenna = "RX2"
    usrp_params.rx_freq = 2450e6
    usrp_params.rx_gain = 10

    pre = preamble.preamble(h, 2*(Ns+h))
    head = pre.header
    radio = eirballoon.radio.Radio_USRP(usrp_params)
    amp = mean_agc.Mean_Agc(ref, 2*Ne)
    itr = eirballoon.interrupteur.Interrupteur_f(2*Ne)

    # sync_freq= freq_sync.freq_sync(fech,N*fse)
    flt = eirballoon.filter.Filter_root_raised_cosine(2*Ne, 0.5, fse, 20)
    stm = eirballoon.synchronizer.timing.Synchronizer_Gardner(2*Ne, fse)
    stm.name = "Stm"
    sync_fine = synchro_freq_fine.synchro_freq_fine(fse, 2*(Ns+h))
    sync_fine.name = "PPL"
    fr_syn = frame_synchro.Frame_Synchronizer(2*(Ns+h), 2*(Ns+h), head)
    itr_trame = eirballoon.interrupteur.Interrupteur_f(2*(Ns+h))
    correc_phase = correc_saut_phase.Anti_saut_phase(2*(Ns+h), head)

    noise = estimateur_bruit.Estimateur_bruit(2*(Ns+h), 0.01)

    mdm = py_aff3ct.module.modem.Modem_BPSK_fast(N)
    dec = py_aff3ct.module.decoder.Decoder_repetition_std(HK, N)
    scramb = scrambler.scrambler(HK, "scramble")
    dcp = decapsulation.decapsulation(K)

    detector_file = detect_coming_trame.detect_coming_trame(K,path)
    # itr_writing = eirballoon.interrupteur.Interrupteur_i(K)

    # itr = eirballoon.interrupteur.Interrupteur(K)
    # itr_jpeg = eirballoon.interrupteur.Interrupteur(K)

    # converter_jpeg = float_to_int.f2i(K)
    # snk_jpeg = py_aff3ct.module.sink.Sink_user_binary(K, args.name+".jpeg")
    # snk = py_aff3ct.module.sink.Sink_user_binary(K, args.name)  # +".ts")

    display = py_display.Display(2*(Ns+h), 5)
    info = display_info.display_info(1)

    info.bind_display(dcp["decapsulate::Packet_ID"])
    info.bind_display(dcp["decapsulate::out_f_size"])
    info.bind_display(dcp["decapsulate::p_type"])
    # info.bind_display(stm['synchronize::MU'])
    # info.bind_display(noise['estimate::cp'])
    info.bind_display(noise["estimate::snr"])
    # info.bind_display(amp["amplify::gain_out"])
    info.bind_display(fr_syn["tr_synchronize::delay"])
    info.bind_display(correc_phase["sync::phase_jump"])
    info.bind_display(dcp["decapsulate::jpeg_type"])
    # info.bind_display(fr_syn["tr_synchronize::itr_tr"])

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
    # stm['synchronize::X_N1'].bind(flt['filter::Y_N2'])
    # display["plot::x"].bind(flt["filter::Y_N2"])
    stm["synchronize::X_N1"].bind(flt['filter::Y_N2'])

    # stm['synchronize::X_N1'].bind(pre["remove_preamble::s_out"])
    stm['extract::Y_N1'].bind(stm['synchronize::Y_N1'])
    stm['extract::B_N1'].bind(stm['synchronize::B_N1'])
    # pream['sync_pream::sync_in'].bind(stm['extract::Y_N2'])
    # display["plot::x"].bind(stm["extract::Y_N2"])
    sync_fine['synchronize::sync_in'].bind(stm['extract::Y_N2'])
    fr_syn["tr_synchronize::IN"].bind(sync_fine['synchronize::sync_out'])
    # display['plot::x'].bind(sync_fine['synchronize::sync_out'])
    itr_trame["select::X_N"].bind(fr_syn['tr_synchronize::OUT'])
    itr_trame["select::bln"].bind(fr_syn['tr_synchronize::itr_tr'])

    noise['estimate::y'].bind(fr_syn['tr_synchronize::OUT'])
    # pre["remove_preamble::s_in"].bind(fr_syn['tr_synchronize::OUT'])
    correc_phase['sync::X_N'].bind(itr_trame["select::Y_N"])
    pre["remove_preamble::s_in"].bind(correc_phase["sync::Y_N"])
    mdm["demodulate::Y_N1"].bind(pre["remove_preamble::s_out"])
    # display['plot::x'].bind(sync_fine['synchronize::sync_out'])
    # display['plot::x'].bind(correc_phase["sync::Y_N"])
    # display['plot::x'].bind(fr_syn['tr_synchronize::OUT'])
    # display['plot::x'].bind(pre["remove_preamble::s_out"])

    # CP = np.array([[1]],dtype=np.float32)
    noise['estimate::y'].bind(fr_syn['tr_synchronize::OUT'])
    mdm['demodulate::CP'].bind(noise['estimate::cp'])
    # mdm['demodulate::CP'].bind(CP)
    dec['decode_siho::Y_N'].bind(mdm['demodulate::Y_N2'])
    scramb['scramble::X_N'].bind(dec['decode_siho::V_K'])
    dcp["decapsulate::IN"].bind(scramb["scramble::Y_N"])
    detector_file['detect::X_N'].bind(dcp["decapsulate::OUT"])
    detector_file['detect::end_packet'].bind(dcp["decapsulate::p_type"])
    detector_file['detect::T_Type'].bind(dcp['decapsulate::out_f_type'])
    # itr_writing["select::bln"].bind(detector_file["detect::itr"])
    # itr_writing["select::X_N"].bind(detector_file["detect::Y_N"])
    # snk['send::V'].bind(itr_writing['select::Y_N'])
    # converter['convert::X_N'].bind(detector_file["detect::Y_N"])
    # converter_ts['convert::X_N'].bind(itr_writing["select::Y_N"])
    # itr_ts["select::bln"].bind(dcp["decapsulate::ts_type"])
    # itr_jpeg["select::bln"].bind(dcp["decapsulate::jpeg_type"])

    # itr_ts["select::X_N"].bind(itr_writing["select::Y_N"])
    # itr_jpeg["select::X_N"].bind(itr_writing["select::Y_N"])

    # converter_ts['convert::X_N'].bind(itr_ts["select::Y_N"])
    # converter_jpeg['convert::X_N'].bind(itr_jpeg["select::Y_N"])
    # snk_jpeg['send::V'].bind(converter_jpeg['convert::Y_N'])
    # snk['send::V'].bind(scramb["scramble::Y_N"])
    # dec('decode_siho').debug = True
    # mdm('demodulate').debug = True

    sequence = py_aff3ct.tools.sequence.Sequence(radio("receive"))
    #fr_syn("tr_synchronize").debug = True
    # sequence = py_aff3ct.tools.sequence.Sequence(radio("receive"),dec('decode_siho'))
    # amp("amplify").debug = True
    # amp("amplify").set_debug_limit(1)
    l_tasks = sequence.get_tasks_per_types()
    for lt in l_tasks:
        for t in lt:
            t.stats = True
            #t.debug = True
            # t.set_debug_limit(1)
    signal.signal(signal.SIGINT, signal_handler)
    # signal.signal(signal.SIGINT, signal.default_int_handler)
    # try:
    sequence.exec()
    # raise KeyboardInterrupt
    # except KeyboardInterrupt:
    sequence.show_stats()
