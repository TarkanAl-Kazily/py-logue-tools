# Copyright 2024 Tarkan Al-Kazily

import mido


def get_midi_ports():
    """
    Print and return detected MIDI ports.

    Returns:
    - two lists of the input and output port names
    """
    inputs = []
    print("  Available MIDI inputs:")
    for i, p in enumerate(mido.get_input_names()):
        print(f"    in  {i}: {p}")
        inputs.append(p)
    print()

    outputs = []
    print("  Available MIDI outputs:")
    for i, p in enumerate(mido.get_output_names()):
        print(f"    out {i}: {p}")
        outputs.append(p)
    print()

    return inputs, outputs
