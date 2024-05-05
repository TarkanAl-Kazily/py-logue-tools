# Copyright 2024 Tarkan Al-Kazily

from .utils import host_to_midi, midi_to_host
from .sdk2 import NTS1Mk2
from .sdk1 import NTS1

LOGUE_TARGET_CLASSES = [
    NTS1Mk2,
    NTS1,
]

KORG_ID = 0x42


def get_logue_target_types() -> list[str]:
    """
    Returns:
      - List of supported class names
    """
    return [target.__name__ for target in LOGUE_TARGET_CLASSES]
