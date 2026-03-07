from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QFileDialog,
    QVBoxLayout, QWidget
)

import numpy as np
import pyqtgraph as pg

from data.loader import load_txt

from dsp.filter_chain import FilterChain
from dsp.filters.notch import NotchFilter
from dsp.filters.butterworth import ButterworthFilter

from dsp.features.ecg import detect_r_peaks


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()


        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')


        self.setWindowTitle("Biosignal DSP Studio")

        self.graph = pg.PlotWidget()
        self.graph.setLabel('left', 'Amplitude')
        self.graph.setLabel('bottom', 'Time', units='s')
        self.graph.getAxis('bottom').enableAutoSIPrefix(False)
        self.graph.showGrid(x=True, y=True, alpha=0.3)

        self.load_btn = QPushButton("Load Signal")
        self.load_btn.clicked.connect(self.load_signal)

        layout = QVBoxLayout()
        layout.addWidget(self.load_btn)
        layout.addWidget(self.graph)

        container = QWidget()
        container.setLayout(layout)

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
        
        t = np.arange(len(self.signal)) / self.fs

        peaks = detect_r_peaks(filtered, self.fs)

        self.graph.clear()
        
        pen_raw = pg.mkPen('b',width=1)
        pen_filtered = pg.mkPen('r',width=2)
        
        self.graph.plot(t, self.signal, pen=pen_raw)
        self.graph.plot(t, filtered, pen=pen_filtered)

        self.graph.plot(
            t[peaks],
            filtered[peaks],
            pen=None,
            symbol='o',
            symbolBrush='g',
            symbolSize=8
        )
