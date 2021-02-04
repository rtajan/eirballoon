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

mod['modulate::X_N1'].bind(src['generate::U_K' ])
flt[  'filter::X_N1'].bind(mod['modulate::X_N2'])

src('generate').exec()
mod('modulate').exec()
flt('filter'  ).exec()