from PyQt5.QtCore import Qt
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

        self.chain_list = QListWidget()
        self.chain_list.setMaximumHeight(100)

        # Time window controls
        self.start_time_input = QSpinBox()
        self.start_time_input.setRange(0, 9999)
        self.start_time_input.setValue(0)
        self.start_time_input.valueChanged.connect(self._render_pipeline)

        self.duration_input = QSpinBox()
        self.duration_input.setRange(1, 9999)
        self.duration_input.setValue(2)
        self.duration_input.valueChanged.connect(self._render_pipeline)

        left_layout = QVBoxLayout()

        left_header = QHBoxLayout()
        left_header.addWidget(QLabel("Start (s)"))
        left_header.addWidget(self.start_time_input)
        left_header.addWidget(QLabel("Length (s)"))
        left_header.addWidget(self.duration_input)

        left_layout.addLayout(left_header)
        left_layout.setAlignment(left_header, Qt.AlignRight)

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
        self.fs = 1000
        self.channel_index = 0
        self.active_chain = None

    def _build_ecg_chain(self):
        chain = FilterChain()
        chain.add_filter(NotchFilter(50))
        chain.add_filter(ButterworthFilter("low", 40))
        chain.add_filter(ButterworthFilter("high", cutoff=0.5, order=2))
        return chain

    def _on_signal_type_changed(self, signal_type):
        self.hr_label.setVisible(signal_type == "ECG")

        if self.signal is None:
            return

        if signal_type == "ECG":
            self.active_chain = self._build_ecg_chain()
        else:
            self.active_chain = FilterChain()

        self._render_pipeline()

    def _get_window(self):
        start = self.start_time_input.value()
        length = self.duration_input.value()
        i0 = int(start * self.fs)
        i1 = int((start + length) * self.fs)
        i1 = min(i1, len(self.signal))
        return i0, i1

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

        if self.active_chain is None:
            self.active_chain = FilterChain()

        if ftype == "Lowpass":
            self.active_chain.add_filter(ButterworthFilter("low", cutoff))
        elif ftype == "Highpass":
            self.active_chain.add_filter(ButterworthFilter("high", cutoff))
        elif ftype == "Notch":
            self.active_chain.add_filter(NotchFilter(cutoff))
        elif ftype == "BandPass":
            self.active_chain.add_filter(ButterworthFilter("band", (5, cutoff)))

        self._render_pipeline()

    def _render_pipeline(self):
        if self.signal is None or self.active_chain is None:
            return

        self.fs = self.sample_rate_input.value()

        filtered = self.active_chain.apply(self.signal, self.fs)

        self._update_chain_list(self.active_chain)

        i0, i1 = self._get_window()
        sig_window = self.signal[i0:i1]
        filtered_window = filtered[i0:i1]
        t = np.arange(i1 - i0) / self.fs + self.start_time_input.value()

        # TIME DOMAIN
        self.time_plot.clear()
        self.time_plot.plot(t, sig_window, pen=pg.mkPen(color='#0078D4', width=1))
        self.time_plot.plot(t, filtered_window, pen=pg.mkPen(color='#FA003F', width=2))

        if self.signal_type.currentText() == "ECG":
            peaks = detect_r_peaks(filtered, self.fs)
            if len(peaks) > 1:
                rr = np.diff(peaks) / self.fs
                hr = 60 / np.mean(rr)
            else:
                hr = 0
            self.hr_label.setText(f"Heart Rate: {hr:.1f} BPM")
            self.hr_label.setVisible(True)
            peaks_window = peaks[(peaks >= i0) & (peaks < i1)] - i0
            if len(peaks_window) > 0:
                self.time_plot.plot(
                    t[peaks_window], filtered_window[peaks_window],
                    pen=None, symbol='o', symbolBrush='g', symbolSize=8
                )
        else:
            self.hr_label.setVisible(False)

        # FREQUENCY DOMAIN
        freq, raw_fft = compute_fft(sig_window, self.fs)
        freq, filtered_fft = compute_fft(filtered_window, self.fs)

        self.freq_plot.clear()
        self.freq_plot.plot(freq, raw_fft, pen=pg.mkPen(color='#0078D4', width=1))
        self.freq_plot.plot(freq, filtered_fft, pen=pg.mkPen(color='#FA003F', width=2))
        self.freq_plot.setLabel('left', 'Magnitude')
        self.freq_plot.setLabel('bottom', 'Frequency', units='Hz')
        self.freq_plot.showGrid(x=True, y=False, alpha=0.3)
        self.freq_plot.setXRange(0, 150)

        # FILTER RESPONSE
        w, h = self.active_chain.frequency_response(self.fs)

        self.filter_plot.clear()
        self.filter_plot.plot(w, h, pen=pg.mkPen(color='#7719AA', width=2))
        self.filter_plot.setLabel('left', 'Magnitude')
        self.filter_plot.setLabel('bottom', 'Frequency', units='Hz')
        self.filter_plot.showGrid(x=True, y=False)
        self.filter_plot.setXRange(0, 150)

    def reset_pipeline(self):
        self.filter_type.setCurrentIndex(0)
        self.cutoff_input.setValue(50)
        self.sample_rate_input.setValue(1000)

        if self.signal_type.currentText() == "ECG":
            self.active_chain = self._build_ecg_chain()
        else:
            self.active_chain = FilterChain()

        self._render_pipeline()

    def load_signal(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Signal")

        if not path:
            return

        sig = load_txt(
            path,
            fs=self.fs,
            index=self.channel_index,
            start_time=self.start_time_input.value(),
            duration=self.duration_input.value()
        )

        self.signal = sig.data

        if self.signal_type.currentText() == "ECG":
            self.active_chain = self._build_ecg_chain()
        else:
            self.active_chain = FilterChain()

        self._render_pipeline()