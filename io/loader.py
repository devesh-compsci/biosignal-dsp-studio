import numpy as np
from core.signal_model import Signal

def load_txt(path, fs, index=0):
    
    data = np.loadtxt(path)
    
    # to check 2d data
    if data.ndim == 1:
        signal = data
    else:
        if index >= data.shape[1]:
            raise ValueError(f"column {index} does not exist in file")
        signal = data[:, index]

    return Signal(signal, fs, name=path)
