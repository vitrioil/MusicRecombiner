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

    def __init__(self, stems:int, chunk_size=2):
        """
            Args:
                stems (int): total files to generate (2/3/5).
                chunk_size (int): chunk size (in seconds) indicates
                    duration size of individual chunk before splitting.
                NOTE: Longer audio file takes more memory. Hence, splitting
                    the audio is a workaround.
        """

        # specified stem loads a specific model
        # hence, it should be specified which model
        # to load.
        self.stems = stems
        #in minutes
        self.chunk_size = int(chunk_size*60)

        self._separator = Separator(f"spleeter:{self.stems}stems")

        # spleeter specific config
        self._audio_adapter = get_default_audio_adapter()

    def _chunk(self, waveform, sr):
        chunks = []
        length = len(waveform) // sr
        remainder = len(waveform) % sr
        print(len(waveform), len(waveform) / sr)
        for c in range(0, length, self.chunk_size):
            print(c)
            chunk = waveform[c*sr: (c+self.chunk_size)*sr]
            print(len(chunk))
            yield chunk
        """
        if remainder:
            chunk = waveform[(c + 1)*sr + remainder:]
            print(len(chunk), "remainder")
            yield chunk
        """

    def separate(self, audio: Union[str, np.ndarray], sample_rate=44_100):
        """Separate audio into specified stems.

            Note: Spleeter uses tensorflow backend. Hence, corresponding
            installed device will automatically be used (CPU/GPU).
            Minimum VRAM/RAM requirement: 4GB (for small audio, <6 minutes).

            Args:
                audio_file (str, array): path to the original signal or the signal itself.
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

        print(waveform.shape)
        #predict in chunks
        prediction = {}
        for chunk in self._chunk(waveform, sample_rate):
            chunk_prediction = self._separator.separate(chunk)

            for chunk_key, chunk_value in chunk_prediction.items():
                if chunk_key not in prediction:
                    prediction[chunk_key] = []
                prediction.get(chunk_key).append(chunk_value)

        #merge chunk prediction
        prediction = {k: np.vstack(v) for k, v in prediction.items()}
        print(list(v.shape for v in prediction.values()))
        signal = Signal(prediction.keys(), prediction.values())

        return signal

