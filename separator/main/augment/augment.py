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

    def _preprocess_interval(self, interval, sample_rate):
        interval = map(lambda x: int(x*sample_rate), interval)
        start, end = tuple(interval)
        return start, end

    def _bound_check(self, start, end, length):
        if start < 0:
            start = 0
        if end >= length:
            end = length - 1
        return start, end

    def _interval_check(self, signal, start, end):
        length = len(signal)
        start, end = self._bound_check(start, end, length)
        return start, end, length

    def amplitude(self, interval: Tuple[float, float], gain: float, sample_rate: int):
        """Change amplitude of the signal.

            Args:
                interval tuple(float, float): time interval to modify.
                gain (float): (1>gain>0) float to indicate volume change.
                sample_rate (int): sampling rate of audio.

            Returns:
                self.
        """
        start, end = self._preprocess_interval(interval, sample_rate)

        if not (0 <= gain <= 1):
            raise ValueError(f"gain: {gain} should be in [0, 1]")

        def _apply(signal: Iterable[float]):
            nonlocal start, end
            start, end, length = self._interval_check(signal, start, end)
            if not (start < end < length):
                raise ValueError(f"Interval: ({start}, {end}) out of range for (0, {length})")

            signal[start: end] *= gain
            return signal

        self.command.append(_apply)
        return self

    def copy(self, interval: Tuple[float, float], copy_start: float, sample_rate: int):
        """Copy a signal in the interval to a new location.

            Args:
                interval tuple(float, float): time interval to copy.
                copy_start float: new location start.

            Returns:
                self.
        """
        start, end = interval
        copy_end = copy_start + (end - start)

        start, end = self._preprocess_interval((start, end), sample_rate)
        copy_start, copy_end = self._preprocess_interval((copy_start, copy_end), sample_rate)

        def _apply(signal: Iterable[float]):
            nonlocal start, end, copy_start, copy_end
            start, end, length = self._interval_check(signal, start, end)
            copy_start, copy_end = self._bound_check(copy_start, copy_end, length)
            if not (start < end < length) or not (copy_start < copy_end < length):
                raise ValueError(f"Interval: ({start}, {end}) or ({copy_start}, {copy_end}) out of range for (0, {length})")

            signal[copy_start: copy_end] = signal[start: end]
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
        audio_signal = signal.get(signal_name)

        for command in self.command:
            audio_signal = command(audio_signal)

        signal.set(signal_name, audio_signal)

    def clear(self):
        """Clears all command.
        """
        self.command = []

