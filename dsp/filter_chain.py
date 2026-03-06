class FilterChain:
    def __init__(self):
        self.filters = []

    def add_filter(self, filter_obj):
        self.filters.append(filter_obj)

    def remove_filter(self, index):
        self.filters.pop(index)

    def clear(self):
        self.filters = []

    def apply(self, signal, fs):
        output = signal
        for f in self.filters:
            output = f.apply(output, fs)
        return output

    def frequency_response(self, fs):

        if len(self.filters) == 0:
            return None, None

        freqs = None
        total_response = None

        for f in self.filters:

            w, h = f.frequency_response(fs)

            if freqs is None:
                freqs = w
                total_response = h
            else:
                total_response = total_response * h

        return freqs, total_response

    def summary(self):
        return " -> ".join([f.__class__.__name__ for f in self.filters])
