import pytest

from separator.main import Signal


def test_create():
    signal = Signal(["test"], [[1, 2]])
    assert signal is not None

def test_diff_len():
    with pytest.raises(Exception) as pe:
        signal = Signal(["test"], [[1], [2, 3]])

def test_n_stem():
    signal = Signal(["test", "test2"], [[1, 2], [3, 4]])
    stem = signal.stems
    assert stem==2

def test_get():
    signal = Signal(["test", "test2"], [[1, 2], [3, 4]])
    audio = signal.get("test")
    assert audio == [1, 2]

    with pytest.raises(ValueError) as pe:
        audio = signal.get("test3")

def test_set():
    signal = Signal(["test", "test2"], [[1, 2], [3, 4]])
    signal.set("test", [1, 2.5])

    with pytest.raises(ValueError) as pe:
        signal.set("test3", [1, 2.5])

    signal.set("tesT2", [3, 4.5])

    with pytest.raises(ValueError) as pe:
        signal.set("tesT2", [3, 4.5, 4])

def test_len():
    signal = Signal(["test", "test2"], [[1, 2, 3], [4, 5, 6]])
    assert len(signal) == 2
    assert signal.get_signal_length() == 3

