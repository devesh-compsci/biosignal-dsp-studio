class Signal:
    def __init__(self, data, fs, name="signal"):
        self.data = data
        self.fs = fs
        self.name = name

        self.filtered = None
        self.peaks = None
        self.features = {}
