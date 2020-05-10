import numpy as np

from typing import Union
from pathlib import Path

from spleeter.separator import Separator
from spleeter.audio.adapter import get_default_audio_adapter

# package import
from separator.main import Signal
from separator.main.separate import Separator as ABCSeparator


class SpleeterSeparator(ABCSeparator):
    """Spleeter separator uses the spleeter library
    to separate music sources.

    """

    def __init__(self, stems:int):
        """
            Args:
                stems (int): total files to generate (2/3/5).

        """

        # specified stem loads a specific model
        # hence, it should be specified which model
        # to load.
        self.stems = stems

        self._separator = Separator(f"spleeter:{self.stems}stems")

        # spleeter specific config
        self._audio_adapter = get_default_audio_adapter()

    def separate(self, audio: Union[str, np.ndarray], sample_rate=44_100):
        """Separate audio into specified stems.

            Note: Spleeter uses tensorflow backend. Hence, corresponding
            installed device will automatically be used (CPU/GPU).
            Minimum VRAM/RAM requirement: 4GB (for small audio, <6 minutes).

            Args:
                audio_file (Path): path to the original signal.
                sample_rate (int): sampling rate of the file.

            Returns:
                signal (Signal): separated signals.

            Raises:
                tf.errors.ResourceExhaustedError: When memory gets exhausted.

        """
        if isinstance(audio, np.ndarray):
            waveform = audio
        else:
            waveform, _ = self._audio_adapter.load(audio, sample_rate=sample_rate)

        prediction = self._separator.separate(waveform)

        signal = Signal(prediction.keys(), prediction.values())

        return signal

