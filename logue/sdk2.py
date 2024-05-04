# Copyright 2024 Tarkan Al-Kazily

import logue.target


class SDK2(logue.target.LogueTarget):
    """
    Sub-class category of LogueTarget for logue devices using the version 2 SDK and MIDI
    implementations.

    Where possible, multiple logue devices that share the same MIDI functions for the SDK version
    can implement those functions here.
    """

    def __init__(self, ioport):
        super().__init__(ioport=ioport)

    def inquiry(self):
        pass


class NTS1Mk2(SDK2):
    """
    Supports interacting with the nts-1 mk2 logue device.
    """

    def __init__(self, ioport):
        super().__init__(ioport=ioport)
