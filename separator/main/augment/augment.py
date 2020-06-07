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

    def augment_one(self, interval: Tuple[float, float], sample_rate: int, modify: callable):
        """Change amplitude of the signal.

            Args:
                interval tuple(float, float): time interval to modify.
                gain (float): (1>gain>0) float to indicate volume change.
                sample_rate (int): sampling rate of audio.
                modify (callable): modify the signal with custom logic.

            Returns:
                self.
        """
        start, end = self._preprocess_interval(interval, sample_rate)

        def _apply(signal: Iterable[float]):
            nonlocal start, end
            start, end, length = self._interval_check(signal, start, end)
            if not (start < end < length):
                raise ValueError(f"Interval: ({start}, {end}) out of range for (0, {length})")

            signal = modify(signal, start, end)
            return signal

        self.command.append(_apply)
        return self

    def augment_two(self, interval: Tuple[float, float], new_start: float, sample_rate: int,
                   modify: callable):
        """Copy a signal in the interval to a new location.

            Args:
                interval tuple(float, float): time interval to copy.
                new_start float: new location start.
                sample_rate int: sampling rate of signal.
                modify (callable): modify the signal with custom logic.

            Returns:
                self.
        """
        start, end = interval
        new_end = new_start + (end - start)

        start, end = self._preprocess_interval((start, end), sample_rate)
        new_start, new_end = self._preprocess_interval((new_start, new_end), sample_rate)

        def _apply(signal: Iterable[float]):
            nonlocal start, end, new_start, new_end
            start, end, length = self._interval_check(signal, start, end)
            new_start, new_end = self._bound_check(new_start, new_end, length)
            if not (start < end < length) or not (new_start < new_end < length):
                raise ValueError(f"Interval: ({start}, {end}) or ({new_start}, {new_end}) out of range for (0, {length})")

            signal = modify(signal, start, end, new_start, new_end)
            return signal

        self.command.append(_apply)
        return self

    def amplitude(self, interval: Tuple[float, float], gain: float, sample_rate: int):
        """Change amplitude of the signal.

            Args:
                interval tuple(float, float): time interval to modify.
                gain (float): (1>gain>0) float to indicate volume change.
                sample_rate (int): sampling rate of audio.

            Returns:
                self.
        """
        def _amplitude(signal, start, end):
            signal[start: end] *= gain
            return signal

        if not (0 <= gain <= 1):
            raise ValueError(f"gain: {gain} should be in [0, 1]")

        return self.augment_one(interval, sample_rate, _amplitude)

    def copy(self, interval: Tuple[float, float], copy_start: float, sample_rate: int):
        """Copy a signal in the interval to a new location.

            Args:
                interval tuple(float, float): time interval to copy.
                copy_start float: new location start.
                sample_rate int: sampling rate of signal.

            Returns:
                self.
        """
        def _copy(signal, start, end, new_start, new_end):
            signal[new_start: new_end] = signal[start:end]
            return signal

        return self.augment_two(interval, copy_start, sample_rate, _copy)

    def overlay(self, interval: Tuple[float, float], overlay_start: float, sample_rate: int):
        """Overlay an interval to another.

            Args:
                interval tuple(float, float): time interval to copy.
                overlay_start float: overlay start.
                sample_rate int: sampling rate of signal.

            Returns:
                self.
        """
        def _overlay(signal, start, end, new_start, new_end):
            signal[new_start: new_end] += signal[start:end]
            signal[new_start: new_end] /= 2
            return signal

        return self.augment_two(interval, overlay_start, sample_rate, _overlay)

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

