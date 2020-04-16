from abc import ABC, abstractmethod


class Augment(ABC):
    """Augment will try to augment the audio signal.
    """

    def __init__(self):
        pass

    def augment(self, signal: Signal, signal_name: str, *args, **kwargs):
        audio_signal = self.signal.get(signal_name)
        audio_signal = self._augment(audio_signal, *args, **kwargs)
        self.signal.set(signal_name, audio_signal)

    @abstractmethod
    def _augment(self, signal, *args, **kwargs):
        """Abstract method to augment an individual audio.""""

