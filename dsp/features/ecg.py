import numpy as np
from scipy.signal import find_peaks

def detect_r_peaks(signal, fs):

    # Min distance between heart-beats (~240~ BPS maximum)
    min_distance = int(0.25 * fs)

    #adaptive threshold
    threshold = np.mean(signal) + 0.5 * np.std(signal)

    peaks, _ = find_peaks(
        signal,
        distance=min_distance,
        height=threshold
    )

    return peaks

def rr_intervals(peaks, fs):

    rr = np.diff(peaks) / fs

    return rr

def heart_rate(peaks, fs):

    rr = rr_intervals(peaks, fs)

    if len(rr) == 0:
        return None

    hr = 60 / rr

    return hr
