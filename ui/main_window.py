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


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Biosignal DSP Studio")

        self.graph = pg.PlotWidget()

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
        self.duration = 5
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
        chain.add_filter(ButterworthFilter("low", 80))

        filtered = chain.apply(self.signal, self.fs)

        t = np.arange(len(self.signal)) / self.fs

        self.graph.clear()

        self.graph.plot(self.signal, pen='b')
        self.graph.plot(filtered, pen='r')
