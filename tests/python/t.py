import numpy as np


a=np.array([0,1,0,0,5,6,5,6,56,6,5,5,5,6,89,2,89,52,8,8,9])

print(np.size(a))
s_desynch1 = np.ndarray(shape = (np.size(a,1)//2,2),  dtype = np.float32)
