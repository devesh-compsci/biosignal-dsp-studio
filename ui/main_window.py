from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QFileDialog,
    QVBoxLayout, QWidget, QTabWidget, QHBoxLayout,
    QLabel, QComboBox, QSpinBox
)

import numpy as np
import pyqtgraph as pg

from data.loader import load_txt

from dsp.filter_chain import FilterChain
from dsp.filters.notch import NotchFilter
from dsp.filters.butterworth import ButterworthFilter

from dsp.transforms.fft import compute_fft

from dsp.features.ecg import detect_r_peaks


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()


        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')


        self.setWindowTitle("Biosignal DSP Studio")

        self.time_plot = pg.PlotWidget()
        self.freq_plot = pg.PlotWidget()
        self.filter_plot = pg.PlotWidget()

        self.time_plot.setLabel('left', 'Amplitude')
        self.time_plot.setLabel('bottom', 'Time', units='s')
        self.time_plot.getAxis('bottom').enableAutoSIPrefix(False)
        self.time_plot.showGrid(x=True, y=True, alpha=0.3)

        tabs = QTabWidget()
        tabs.addTab(self.freq_plot, "Frequency Domain")
        tabs.addTab(self.filter_plot, "Filter Response")

        self.load_btn = QPushButton("Load Signal")
        self.load_btn.clicked.connect(self.load_signal)

        self.signal_type = QComboBox()
        self.signal_type.addItems(["ECG", "EEG", "Custom"])

        self.sample_rate_input = QSpinBox()
        self.sample_rate_input.setRange(1, 10000)
        self.sample_rate_input.setValue(1000)

        self.filter_type = QComboBox()
        self.filter_type.addItems(["Lowpass", "Highpass", "Notch", "Band Pass")

        self.cutoff_input = QSpinBox()
        self.cutoff_input.setRange(1, 500)
        self.cutoff_input.setValue(50)

        self.apply_btn = QPushButton("Apply")
        self.reset_btn = QPushButton("Reset")

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.time_plot)
        left_layout.addWidget(tabs)

        left_panel = QWidget()
        left_panel.setLayout(left_layout)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.load_btn)
        right_layout.addStretch()

        right_panel = QWidget()
        right_panel.setLayout(right_layout)


        main_layout = QHBoxLayout()
        main_layout.addWidget(left_panel,4)
        main_layout.addWidget(right_panel,1)

        container = QWidget()
        container.setLayout(main_layout)

        self.setCentralWidget(container)


        self.signal = None
        self.start_time = 0
        self.duration = 2
        self.fs = 1000
        self.channel_index = 0

    def load_signal(self):

        path, _ = QFileDialog.getOpenFileName(self, "Open Signal")

        if not path:
            return

        sig = load_txt(
            path,
            fs=self.fs,
            index=self.channel_index,
            start_time=self.start_time,
            duration=self.duration
        )

        self.signal = sig.data

        chain = FilterChain()
        chain.add_filter(NotchFilter(50))
        chain.add_filter(ButterworthFilter("low", 40))
        chain.add_filter(ButterworthFilter("high",cutoff = 0.5, order=2))

        filtered = chain.apply(self.signal, self.fs)

        freq, raw_fft = compute_fft(self.signal, self.fs)
        freq, filtered_fft = compute_fft(filtered, self.fs)

        w, h = chain.frequency_response(self.fs)


        t = np.arange(len(self.signal)) / self.fs

        peaks = detect_r_peaks(filtered, self.fs)

        
        # TIME DOMAIN GRAPH TO UI
        self.time_plot.clear()
        
        pen_raw = pg.mkPen('b',width=1)
        pen_filtered = pg.mkPen('r',width=2)
        
        self.time_plot.plot(t, self.signal, pen=pen_raw)
        self.time_plot.plot(t, filtered, pen=pen_filtered)

        self.time_plot.plot(
            t[peaks],
            filtered[peaks],
            pen=None,
            symbol='o',
            symbolBrush='g',
            symbolSize=8
        )

        # FREQUENCY DOMAIN GRAPH TO UI
        self.freq_plot.clear()

        pen_raw = pg.mkPen('b', width=1)
        pen_filtered = pg.mkPen('r', width=2)

        self.freq_plot.plot(freq, raw_fft, pen=pen_raw)
        self.freq_plot.plot(freq, filtered_fft, pen=pen_filtered)

        self.freq_plot.setLabel('left', 'Magnitude')
        self.freq_plot.setLabel('bottom', 'Frequency', units='Hz')
        self.freq_plot.showGrid(x=True, y=False, alpha=0.3)
        self.freq_plot.setXRange(0,150)

        # FILTER DESIGN PLOT TO UI
        self.filter_plot.clear()

        pen_response = pg.mkPen('m', width=2)

        self.filter_plot.plot(w, h, pen=pen_response)

        self.filter_plot.setLabel('left', 'Magnitude')
        self.filter_plot.setLabel('bottom', 'Frequency', units='Hz')
        self.filter_plot.showGrid(x=True, y=False)

        self.filter_plot.setXRange(0,150)


















