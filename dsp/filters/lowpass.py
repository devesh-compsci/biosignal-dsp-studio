import numpy as np
from scipy.signal import butter, filtfilt

def butter_lowpass(signal, cutoff, fs, order=4):
    nyquist = 0.5 * fs
    normalized_cutoff = cutoff/nyquist
    b, a = butter(order, normalized_cutoff, btype='low')
    filtered = filtfilt(b, a, signal)
    return filtered
