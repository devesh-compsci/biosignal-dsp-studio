import numpy as np
from scipy.signal import iirnotch, filtfilt,freqz

class NotchFilter:
    def __init__(self, freq, Q=30):

        self.freq = freq
        self.Q = Q

    def apply(self, signal, fs):

        b, a = iirnotch(self.freq, self.Q, fs)

        filtered = filtfilt(b, a, signal)

        return filtered

    def frequency_response(self, fs):

        b, a = iirnotch(self.freq, self.Q, fs)
        w, h = freqz(b, a, worN=2048,  fs=fs)

        return w, np.abs(h)

    def summary(self):
        return f"Notch Filter | freq={self.freq}Hz | Q={self.Q}"
