from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QFileDialog,
    QVBoxLayout, QWidget, QTabWidget, QHBoxLayout,
    QLabel, QComboBox, QSpinBox, QListWidget
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
        self.signal_type.currentTextChanged.connect(self._on_signal_type_changed)

        self.sample_rate_input = QSpinBox()
        self.sample_rate_input.setRange(1, 10000)
        self.sample_rate_input.setValue(1000)

        self.filter_type = QComboBox()
        self.filter_type.addItems(["Lowpass", "Highpass", "Notch", "BandPass"])

        self.cutoff_input = QSpinBox()
        self.cutoff_input.setRange(1, 500)
        self.cutoff_input.setValue(50)

        self.apply_btn = QPushButton("Apply")
        self.reset_btn = QPushButton("Reset")

        self.hr_label = QLabel("Heart Rate: -- BPM")

        # Filter chain display list
        self.chain_list = QListWidget()
        self.chain_list.setMaximumHeight(100)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.time_plot, 3)
        left_layout.addWidget(tabs, 2)

        left_panel = QWidget()
        left_panel.setLayout(left_layout)

        right_layout = QVBoxLayout()

        right_layout.addWidget(QLabel("INPUT CONFIGURATION"))
        right_layout.addWidget(self.load_btn)
        right_layout.addWidget(QLabel("Sample Rate"))
        right_layout.addWidget(self.sample_rate_input)
        right_layout.addWidget(QLabel("Signal Type"))
        right_layout.addWidget(self.signal_type)

        right_layout.addWidget(self.hr_label)

        right_layout.addSpacing(20)

        right_layout.addWidget(QLabel("DSP Pipeline"))
        right_layout.addWidget(QLabel("Filter Type"))
        right_layout.addWidget(self.filter_type)

        right_layout.addWidget(QLabel("Cutoff Frequency (Hz)"))
        right_layout.addWidget(self.cutoff_input)

        right_layout.addWidget(self.apply_btn)
        right_layout.addWidget(self.reset_btn)

        right_layout.addSpacing(10)
        right_layout.addWidget(QLabel("Active Filter Chain"))
        right_layout.addWidget(self.chain_list)

        right_layout.addStretch()

        right_panel = QWidget()
        right_panel.setLayout(right_layout)

        self.apply_btn.clicked.connect(self.apply_pipeline)
        self.reset_btn.clicked.connect(self.reset_pipeline)

        main_layout = QHBoxLayout()
        main_layout.addWidget(left_panel, 4)
        main_layout.addWidget(right_panel, 1)

        container = QWidget()
        container.setLayout(main_layout)

        self.setCentralWidget(container)

        self.signal = None
        self.start_time = 0
        self.duration = 2
        self.fs = 1000
        self.channel_index = 0
        self.active_chain = None  # track last applied chain

    def _build_ecg_chain(self):
        chain = FilterChain()
        chain.add_filter(NotchFilter(50))
        chain.add_filter(ButterworthFilter("low", 40))
        chain.add_filter(ButterworthFilter("high", cutoff=0.5, order=2))
        return chain

    def _on_signal_type_changed(self, signal_type):
        # Only show HR label for ECG
        self.hr_label.setVisible(signal_type == "ECG")

    def _update_chain_list(self, chain):
        self.chain_list.clear()
        for f in chain.filters:
            name = type(f).__name__
            
            cutoff = getattr(f, 'cutoff', None) or getattr(f, 'freq', None) or getattr(f, 'w0', None)
            label = f"{name} : {cutoff} Hz" if cutoff is not None else name
            self.chain_list.addItem(label)

    def apply_pipeline(self):
        if self.signal is None:
            return

        self.fs = self.sample_rate_input.value()
        ftype = self.filter_type.currentText()
        cutoff = self.cutoff_input.value()

        if self.signal_type.currentText() == "ECG":
            chain = self._build_ecg_chain()
        else:
            chain = FilterChain()

        if ftype == "Lowpass":
            chain.add_filter(ButterworthFilter("low", cutoff))
        elif ftype == "Highpass":
            chain.add_filter(ButterworthFilter("high", cutoff))
        elif ftype == "Notch":
            chain.add_filter(NotchFilter(cutoff))
        elif ftype == "BandPass":
            chain.add_filter(ButterworthFilter("band", (5, cutoff)))

        self.active_chain = chain
        filtered = chain.apply(self.signal, self.fs)

        self._update_chain_list(chain)

        t = np.arange(len(self.signal)) / self.fs

        # Time Plot
        self.time_plot.clear()
        self.time_plot.plot(t, self.signal, pen=pg.mkPen('b', width=1))
        self.time_plot.plot(t, filtered, pen=pg.mkPen('r', width=2))

        # FREQUENCY DOMAIN
        freq, raw_fft = compute_fft(self.signal, self.fs)
        freq, filtered_fft = compute_fft(filtered, self.fs)

        self.freq_plot.clear()
        self.freq_plot.plot(freq, raw_fft, pen=pg.mkPen('b', width=1))
        self.freq_plot.plot(freq, filtered_fft, pen=pg.mkPen('r', width=2))
        self.freq_plot.setLabel('left', 'Magnitude')
        self.freq_plot.setLabel('bottom', 'Frequency', units='Hz')
        self.freq_plot.showGrid(x=True, y=False, alpha=0.3)
        self.freq_plot.setXRange(0, 150)

        # FILTER RESPONSE
        w, h = chain.frequency_response(self.fs)

        self.filter_plot.clear()
        self.filter_plot.plot(w, h, pen=pg.mkPen('m', width=2))
        self.filter_plot.setLabel('left', 'Magnitude')
        self.filter_plot.setLabel('bottom', 'Frequency', units='Hz')
        self.filter_plot.showGrid(x=True, y=False)
        self.filter_plot.setXRange(0, 150)

    def reset_pipeline(self):
        self.filter_type.setCurrentIndex(0)
        self.cutoff_input.setValue(50)
        self.sample_rate_input.setValue(1000)

        if self.signal is not None:
            self.apply_pipeline()

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

        chain = self._build_ecg_chain()
        filtered = chain.apply(self.signal, self.fs)

        freq, raw_fft = compute_fft(self.signal, self.fs)
        freq, filtered_fft = compute_fft(filtered, self.fs)

        w, h = chain.frequency_response(self.fs)

        t = np.arange(len(self.signal)) / self.fs

        # HR — only computed and shown for ECG
        if self.signal_type.currentText() == "ECG":
            peaks = detect_r_peaks(filtered, self.fs)
            if len(peaks) > 1:
                rr = np.diff(peaks) / self.fs
                hr = 60 / np.mean(rr)
            else:
                hr = 0
            self.hr_label.setText(f"Heart Rate: {hr:.1f} BPM")
            self.hr_label.setVisible(True)
        else:
            peaks = []
            self.hr_label.setVisible(False)

        self._update_chain_list(chain)

        # TIME DOMAIN
        self.time_plot.clear()
        self.time_plot.plot(t, self.signal, pen=pg.mkPen('b', width=1))
        self.time_plot.plot(t, filtered, pen=pg.mkPen('r', width=2))

        if len(peaks) > 1:
            self.time_plot.plot(
                t[peaks], filtered[peaks],
                pen=None, symbol='o', symbolBrush='g', symbolSize=8
            )

        # FREQUENCY DOMAIN
        self.freq_plot.clear()
        self.freq_plot.plot(freq, raw_fft, pen=pg.mkPen('b', width=1))
        self.freq_plot.plot(freq, filtered_fft, pen=pg.mkPen('r', width=2))
        self.freq_plot.setLabel('left', 'Magnitude')
        self.freq_plot.setLabel('bottom', 'Frequency', units='Hz')
        self.freq_plot.showGrid(x=True, y=False, alpha=0.3)
        self.freq_plot.setXRange(0, 150)

        # FILTER RESPONSE
        self.filter_plot.clear()
        self.filter_plot.plot(w, h, pen=pg.mkPen('m', width=2))
        self.filter_plot.setLabel('left', 'Magnitude')
        self.filter_plot.setLabel('bottom', 'Frequency', units='Hz')
        self.filter_plot.showGrid(x=True, y=False)
        self.filter_plot.setXRange(0, 150)
