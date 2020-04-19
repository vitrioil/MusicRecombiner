from pathlib import Path

from typing import Any
from abc import ABC, abstractmethod


class Separator(ABC):
    """ABC is the abstract base class for music
    separation.

    """

    # custom separator
    _separator: Any

    def __init__(self):
        pass

    @abstractmethod
    def separate(self, audio_file: Path):
        """ abstract method to separate signal."""

