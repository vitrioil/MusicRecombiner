from typing import Iterable, Tuple

# package import
from separator.main import Signal

class Augment:
    """Augment will try to augment the audio signal.

        Examples:
            Chain commands first specifying parameters. Then apply to a
            particular signal.

            >>>signal = Signal(...)
            >>>augment = Augment()
            >>>augment.amplitude(interval=(3, 10), gain=0, sample_rate=44_100)
                      .amplitude(interval=(15, 20), gain=0.5, sample_rate=44_100)
            >>>augment.augment(signal, signal_name="vocals")
    """

    def __init__(self):
        self.command = []

    def amplitude(self, interval: Tuple[int, int], gain: float, sample_rate: int):
        """Change amplitude of the signal.

            Args:
                interval tuple(int, int): time interval to modify.
                gain (float): (1>gain>0) float to indicate volume change.
                sample_rate (int): sampling rate of audio.

            Returns:
                self.
        """
        interval = map(lambda x: x*sample_rate, interval)
        start, end = tuple(interval)

        if not (0 <= gain < 1):
            raise ValueError(f"gain: {gain} should be in [0, 1)")

        def _apply(signal: Iterable[float, float]):
            length = len(signal)
            if not (start < end < length):
                raise ValueError(f"Interval: ({start}, {end}) out of range for (0, {length})")

            signal[start: end] *= gain
            return signal

        self.command.append(_apply)
        return self

    def augment(self, signal: Signal, signal_name: str):
        """Augment the signal specified by the name.

            Args:
                signal (Signal): signal to augment.
                signal_name (str): signal stem.

            Returns:
                None
        """
        audio_signal = self.signal.get(signal_name)

        for command in self.command:
            audio_signal = command(audio_signal)

        self.signal.set(signal_name, audio_signal)

    def clear(self):
        """Clears all command.
        """
        self.command = []

