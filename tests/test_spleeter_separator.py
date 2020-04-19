import pytest
import librosa
import numpy as np

from separator.main.augment import Augment
from separator.main.separate import SpleeterSeparator

#GLOBAL for memory reasons...
SEPARATOR = None
STEM = 2
AUDIO_FILE = "tests/test.mp3"
def test_create_separator():
    global SEPARATOR
    SEPARATOR = SpleeterSeparator(STEM)

def test_separate():
    signal = SEPARATOR.separate(AUDIO_FILE)
    assert len(signal) == STEM

    augment = Augment()
    augment.amplitude((0, 10), 0, 44_100)
    augment.augment(signal, "vocals")

    librosa.output.write_wav("tests/vocals.mp3", np.asfortranarray(signal.get("vocals")), sr=44_100)
