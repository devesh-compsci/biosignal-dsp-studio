import numpy as np
from core.signal_model import Signal

def load_txt(path, fs, index=0, start_time=0, duration=None):
    
    data = np.loadtxt(path)
    
    # to check 2d data
    if data.ndim == 1:
        signal = data
    else:
        if index >= data.shape[1]:
            raise ValueError(f"column {index} does not exist in file")
        signal = data[:, index]

    start_sample = int(start_time * fs)

    if duration is None:
        end_sample = len(signal)
    else:
        end_sample = start_sample + int(duration * fs)

    signal = signal[start_sample:end_sample]

    return Signal(signal, fs, name=path)
