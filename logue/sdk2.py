# Copyright 2024 Tarkan Al-Kazily

import mido
import logue.target


class SDK2(logue.target.LogueTarget):
    """
    Sub-class category of LogueTarget for logue devices using the version 2 SDK and MIDI
    implementations.

    Where possible, multiple logue devices that share the same MIDI functions for the SDK version
    can implement those functions here.
    """

    def __init__(self, ioport, channel=1):
        super().__init__(ioport=ioport, channel=channel)

    def inquiry(self):
        """
        From the NTS-1mkII_MIDIimp.txt:

         DEVICE INQUIRY MESSAGE REQUEST
        +---------+------------------------------------------------+
        | Byte[H] |    Description                                 |
        +---------+------------------------------------------------+
        |   F0    | Exclusive Status                               |
        |   7E    | Non Realtime Message                           |
        |   nn    | MIDI Channel (Device ID)                       |
        |   06    | General Information                            |
        |   01    | Identity Request                               |
        |   F7    | END OF EXCLUSIVE                               |
        +---------+------------------------------------------------+
        """

        cmd = mido.Message.from_bytes([0xF0, 0x7E, self.channel - 1, 0x06, 0x01, 0xF7])
        print(f"sent {cmd}")
        rsp = self.write_cmd(cmd)
        print(f"got {rsp}")


class NTS1Mk2(SDK2):
    """
    Supports interacting with the nts-1 mk2 logue device.
    """

    def __init__(self, ioport, channel=1):
        super().__init__(ioport=ioport, channel=1)
