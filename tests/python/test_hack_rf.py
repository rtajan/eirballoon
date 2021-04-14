from os import remove
import sys
import signal
sys.path.insert(0, '../../build/lib')
sys.path.insert(0, '../../py_aff3ct/build/lib')
sys.path.insert(0, '../../src/python')
import eirballoon
import py_display
import py_aff3ct
import numpy as np

#process=None
#def signal_handler(sig, frame):
#    print('You pressed Ctrl+C!')
#    radio.stop_tx()
#    sequence.show_stats()
#    process.send_signal(signal.SIGINT)
#    # raise KeyboardInterrupt

hrfp = eirballoon.radio.HACKRF_params()
hrfp.N = 1024
hrfp.fifo_size = 10000
hrfp.rx_rate = 20000000
hrfp.tx_rate = 20000000
radio = eirballoon.radio.Radio_HACKRF(hrfp)
X_N1 = np.zeros([1,hrfp.N * 2], np.float32)

for i in range(hrfp.N):
    X_N1[0,2*i  ] = np.cos(2*np.pi*i*0.1)
    X_N1[0,2*i+1] = np.sin(2*np.pi*i*0.1)

f2i = eirballoon.converter.Converter_f2i(hrfp.N*2)

#display = py_display.Display(2*hrfp.N ,10)

f2i  ["convert::X_N" ].bind(X_N1               )
radio[   "send::X_N1"].bind(f2i["convert::Y_N"])
#display['plot::x'].bind(f2i["convert::X_N"])
sequence = py_aff3ct.tools.sequence.Sequence(f2i('convert'),radio('send'),1)

l_tasks = sequence.get_tasks_per_types()
for lt in l_tasks:
    for t in lt:
        t.stats = True

radio.start_tx()
#signal.signal(signal.SIGINT, signal_handler)
print("Start sequence...")
sequence.exec()
print("Stop sequence.")
sequence.show_stats()

radio.stop_tx()