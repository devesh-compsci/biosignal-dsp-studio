import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Qt5Agg")

from dsp.filters.butterworth import ButterworthFilter
from dsp.filters.notch import NotchFilter
from dsp.filters.moving_average import MovingAverageFilter
from dsp.filter_chain import FilterChain
from dsp.transforms.fft import compute_fft

from dsp.features.ecg import detect_r_peaks, heart_rate


fs = 1000

# Loading ECG Data  
data = np.loadtxt("biosignal.txt")

samples = fs #milli Seconds

signal = data[:samples, 0]

t = np.arange(len(signal)) / fs


chain = FilterChain()

chain.add_filter(MovingAverageFilter(window_size=10))
chain.add_filter(NotchFilter(50))
chain.add_filter(ButterworthFilter("low", cutoff=80))

filtered = chain.apply(signal, fs)

# ---- FEATURES ----

peaks = detect_r_peaks(filtered, fs)
hr = heart_rate(peaks, fs)

print("\n---------->  Detected beats:", len(peaks))

if hr is not None:
    print("\n---------->  Average HR:", np.mean(hr))
print("\n\n")
# ---- TIME DOMAIN ----

plt.figure()

plt.plot(t, signal, label="RAW", alpha=0.6)
plt.plot(t, filtered, label="FILTERED")

plt.title("Filter Chain Test")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")

plt.legend()
plt.show()

# ---- PEAKS ----

plt.figure()

plt.plot(t, filtered, label="Filtered ECG")
plt.scatter(t[peaks], filtered[peaks], color="red", label="R Peaks")

plt.title("R Peak Detection")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")

plt.legend()
plt.show()

# ---- FFT ----

freq, raw_fft = compute_fft(signal, fs)
freq, filtered_fft = compute_fft(filtered, fs)

plt.figure()

plt.plot(freq, raw_fft, label="RAW FFT")
plt.plot(freq, filtered_fft, label="FILTERED FFT")

plt.xlim(0,150)

plt.title("Frequency Domain")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")

plt.legend()
plt.show()


# ---- FILTER RESPONSE ----

w, h = chain.frequency_response(fs)

plt.figure()

plt.plot(w, h)

plt.title("Combined Filter Response")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")

plt.xlim(0,150)

plt.show()

