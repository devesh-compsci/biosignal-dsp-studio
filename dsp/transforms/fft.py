import numpy as np

def compute_fft(signal, fs):
    N = len(signal)
    freq = np.fft.fftfreq(N, d=1/fs)
    fft_vals = np.fft.fft(signal)
    magnitude = np.abs(fft_vals) / N
    
    return freq[:N//2], magnitude[:N//2]
