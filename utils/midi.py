# Copyright 2024 Tarkan Al-Kazily

import mido


def get_midi_ports(verbose: bool = False):
    """
    Optionally print and return detected MIDI ports.

    Args:
        verbose: Print detected ports

    Returns:
    - two lists of the input and output port names
    """
    inputs = []
    for i, p in enumerate(mido.get_input_names()):
        inputs.append(p)

    outputs = []
    for i, p in enumerate(mido.get_output_names()):
        outputs.append(p)

    if verbose:
        print("  Available MIDI inputs:")
        for i, p in enumerate(inputs):
            print(f"    in  {i}: {p}")
        print()

        print("  Available MIDI outputs:")
        for i, p in enumerate(outputs):
            print(f"    out {i}: {p}")
        print()

    return inputs, outputs
