from typing import Iterable


class Signal:
    """Signal object holds individual separated signals.
    """

    def __init__(self, signal_names: Iterable[str], signal: Iterable[Iterable[float]]):
        """
            Args:
                signal_names (list[str]): names of individual signals.
                signal list[iterable[float, float]]: 2 channel,
                    individual signals of equal length.

        """
        self.signal_names = list(map(lambda x: x.lower(), signal_names))
        self.signal = list(signal)

        length = set([len(i) for i in self.signal])
        assert len(length) == 1, "All audio should be of equal length."
        self.length = length.pop()

        self.sig_dict = {n: s for n, s in zip(self.signal_names, self.signal)}
        self.stems = len(self.sig_dict)

    def get(self, name: str):
        """Get a particular signal. Lowercase names are used.

            Args:
                name (str): name of signal.
        """
        name = name.lower()
        if name not in self.sig_dict.keys():
            raise ValueError(f"""Signal does not exist.
Perhaps used an incorrect stem? Current stem: {self.stems}""")
        return self.sig_dict.get(name)

    def set(self, signal_name: str, signal: Iterable[float]):
        """Update a particular existing signal.

           Args:
                signal_name (str): Signal name to update.
                signal (iterable[float, float]): Updated signal.

           Raises:
                ValueError: when signal name does not match or
                            if the length of the signal does not match.
        """
        signal_name = signal_name.lower()

        if signal_name not in self.sig_dict.keys():
           raise ValueError("Cannot add new signal. New signal should pre-exist.")

        length = len(signal)
        if length != self.get_signal_length():
            print(length, self.length)
            raise ValueError("New audio signal is not of the same duration.")

        self.sig_dict[signal_name] = signal

    def get_signal_length(self):
        return self.length

    def get_names(self):
        return list(self.sig_dict.keys())

    def get_items(self):
        yield from self.sig_dict.items()

    def __len__(self):
        return self.stems

