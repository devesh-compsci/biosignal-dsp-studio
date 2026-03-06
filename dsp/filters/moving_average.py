import numpy as np
from scipy.signal import freqz


class MovingAverageFilter:
    def __init__(self, window_size=5):
        self.window_size = window_size

    def apply(self, signal, fs=None):

        kernel = np.ones(self.window_size) / self.window_size

        filtered = np.convolve(signal, kernel, mode="same")

        return filtered

    def frequency_response(self, fs):

        kernel = np.ones(self.window_size) / self.window_size

        w, h = freqz(kernel, [1], worN=2048, fs=fs)

        return w, np.abs(h)

    def summary(self):
        return f"MovingAverage(window={self.window_size})"
