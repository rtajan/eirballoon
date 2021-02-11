import sys  
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib')
sys.path.insert(0, '../../src/python')
import py_aff3ct
import eirballoon
import numpy as np
import matplotlib.pyplot as plt
import py_display

usrp_params = eirballoon.radio.USRP_params()
usrp_params.N          = 1024
usrp_params.threaded   = True
usrp_params.usrp_addr  = "type=b100"
usrp_params.rx_enabled = True
usrp_params.rx_rate    = 1e6

radio   = eirballoon.radio.Radio_USRP(usrp_params)
display = py_display.Display(2048)

display["plot::x"].bind(radio["receive::Y_N1"])

sequence = py_aff3ct.tools.sequence.Sequence(radio("receive"), display("plot"))
sequence.exec()