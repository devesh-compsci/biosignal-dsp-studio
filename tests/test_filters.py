import numpy as np
import matplotlib.pyplot as plt

from dsp.filters.butterworth import ButterworthFilter
from dsp.transforms.fft import compute_fft


# ------------------------
# Signal generation
# ------------------------

fs = 1000
t = np.arange(0, 1, 1/fs)

signal = (
    np.sin(2*np.pi*5*t) +
    0.5*np.sin(2*np.pi*50*t) +
    3*np.sin(2*np.pi*100*t)
)

# ------------------------
# Filter
# ------------------------

filter = ButterworthFilter(
    filter_type="low",
    cutoff=10,
    order=4
)

filtered = filter.apply(signal, fs)

# ------------------------
# Time domain plot
# ------------------------

plt.figure(figsize=(10,4))

plt.plot(t, signal, label="RAW")
plt.plot(t, filtered, label="FILTERED")

plt.title("Lowpass Filtering Test")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")

plt.legend()
plt.tight_layout()
plt.show()

# ------------------------
# FFT comparison
# ------------------------

freq, raw_fft = compute_fft(signal, fs)
freq, filtered_fft = compute_fft(filtered, fs)

plt.figure(figsize=(10,4))

plt.plot(freq, raw_fft, label="RAW FFT")
plt.plot(freq, filtered_fft, label="FILTERED FFT")

plt.title("Frequency Domain")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")

plt.xlim(0,150)

plt.legend()
plt.tight_layout()
plt.show()

# ------------------------
# Filter frequency response
# ------------------------

w, h = filter.frequency_response(fs)

plt.figure(figsize=(10,4))

plt.plot(w, h)

plt.title("Filter Frequency Response")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")

plt.xlim(0,150)

plt.tight_layout()
plt.show()
