class Pipeline:

    def __init__(self, filters, features, feature_extractor):
        self.filters = filters
        self.feature_extractor = feature_extractor

    def run(self, signal):

        signal.filtered = self.filtered.apply(signal.data, signal.fs)

        signal.peaks = self.feature_extractor.detect_r_peaks(
            signal.filtered, signal.fs
        )

        return signal
