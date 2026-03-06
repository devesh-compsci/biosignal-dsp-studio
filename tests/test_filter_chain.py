import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Qt5Agg")

from dsp.filters.butterworth import ButterworthFilter
from dsp.filters.notch import NotchFilter
from dsp.filter_chain import FilterChain
from dsp.transforms.fft import compute_fft


fs = 1000
t = np.arange(0, 1, 1/fs)

signal = (
    np.sin(2*np.pi*5*t)
    + 0.5*np.sin(2*np.pi*50*t)
    + 0.5*np.sin(2*np.pi*100*t)
)

chain = FilterChain()

chain.add_filter(NotchFilter(50))
chain.add_filter(ButterworthFilter("low", cutoff=20))

filtered = chain.apply(signal, fs)


# ---- TIME DOMAIN ----

plt.figure()

plt.plot(t, signal, label="RAW", alpha=0.6)
plt.plot(t, filtered, label="FILTERED")

plt.title("Filter Chain Test")
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
