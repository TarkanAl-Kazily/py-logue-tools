# Copyright 2024 Tarkan Al-Kazily

import mido


def get_midi_ports(verbose: bool = False) -> list[str]:
    """
    Optionally print and return detected MIDI ports.

    Args:
        verbose: Print detected ports

    Returns:
    - list of the ioports detected
    """
    if verbose:
        print("  Available Ports:")

    ioports = []
    for i, p in enumerate(mido.get_ioport_names()):
        ioports.append(p)
        if verbose:
            print(f"    port {i}: {p}")

    return ioports


def get_inout_port(index) -> mido.ports.IOPort | None:
    """
    Args:
        index: Port index to use

    Returns:
    - mido IOPort or None on error
    """
    ioport_names = get_midi_ports()

    try:
        io_name = ioport_names[index]
    except KeyError:
        print(f"{index} port not found")
        return None

    return mido.open_ioport(io_name)
