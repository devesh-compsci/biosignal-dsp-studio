import numpy as np


def compute_fft(signal, fs):
    """
    Compute FFT magnitude spectrum
    """

    N = len(signal)

    fft_vals = np.fft.fft(signal)
    freqs = np.fft.fftfreq(N, d=1/fs)

    magnitude = np.abs(fft_vals) / N

    return freqs[:N//2], magnitude[:N//2]
