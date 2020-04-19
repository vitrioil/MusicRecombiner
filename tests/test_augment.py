import pytest
import numpy as np

from separator.main import Signal
from separator.main.augment import Augment

dummy_signal = Signal(["test"], [np.array(range(100), dtype=np.float32)])

def test_command():
    augment = Augment()

    augment.amplitude((3, 10), 0, 1)
    assert len(augment.command) == 1

    augment.augment(dummy_signal, "test")
    assert len(augment.command) == 1

    augment.amplitude((3, 10), 0, 1)
    assert len(augment.command) == 2

    augment.clear()
    assert len(augment.command) == 0

def test_amplitude():
    augment = Augment()
    augment.amplitude((3, 10), 0, 1)
    augment.augment(dummy_signal, "test")

    audio = dummy_signal.get("test")
    assert not any(audio[3: 10])

    augment.amplitude((25, 40), 0.5, 1)
    orig = audio[25: 40].copy()
    augment.augment(dummy_signal, "test")

    audio = dummy_signal.get("test")
    assert np.allclose(audio[25: 40], orig * 0.5)

    with pytest.raises(ValueError) as pe:
        augment.amplitude((1000, 1100), 0, 1)
        augment.augment(dummy_signal, "test")

    with pytest.raises(ValueError) as pe:
        augment.amplitude((1100, 1000), 0, 1)
        augment.augment(dummy_signal, "test")

    with pytest.raises(ValueError) as pe:
        augment.amplitude((10, 11), -1, 1)

    augment.amplitude((3, 4), 0, 10)

    with pytest.raises(ValueError) as pe:
        augment.amplitude((3, 4), 0, 100)
        augment.augment(dummy_signal, "test")
