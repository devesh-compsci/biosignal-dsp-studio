import numpy as np
from scipy.signal import butter, filtfilt, freqz


class ButterworthFilter:
    def __init__(self, filter_type: str, cutoff, order: int = 4):
        """
        filter_type: 'low', 'high', or 'band'
        cutoff: float or tuple for bandpass
        order: filter order
        """
        self.filter_type = filter_type
        self.cutoff = cutoff
        self.order = order

    def apply(self, signal: np.ndarray, fs: float) -> np.ndarray:
        nyquist = 0.5 * fs

        if self.filter_type == "band":
            normalized = [c / nyquist for c in self.cutoff]
        else:
            normalized = self.cutoff / nyquist

        b, a = butter(self.order, normalized, btype=self.filter_type)

        return filtfilt(b, a, signal)

    def frequency_response(self, fs: float):
        nyquist = 0.5 * fs

        if self.filter_type == "band":
            normalized = [c / nyquist for c in self.cutoff]
        else:
            normalized = self.cutoff / nyquist

        b, a = butter(self.order, normalized, btype=self.filter_type)

        w, h = freqz(b, a, worN=2048, fs=fs)

        return w, np.abs(h)
