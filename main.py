import numpy as np
import matplotlib.pyplot as plt
from dsp.filters.lowpass import butter_lowpass
from dsp.transforms.fft import compute_fft

# ---- TEST ----    
fs = 1000
t = np.linspace(0,1,fs)
signal = np.sin(2*np.pi*5*t) + 0.5*np.sin(2*np.pi*50*t)

filtered = butter_lowpass(signal, cutoff=10, fs = fs)

plt.figure()
plt.plot(t, signal, label='RAW')
plt.plot(t, filtered, label='FILTERED')
plt.legend()
plt.show()
