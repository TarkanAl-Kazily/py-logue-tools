# Copyright 2024 Tarkan Al-Kazily

import mido.ports


class LogueTarget:
    """
    Base class defining a Logue-SDK compatible device.

    Sub-classes of this class define specific MIDI implementations and additional functions for
    working with different device types.

    Attributes:
        port: Bi-directional MIDI port for communicating with target
    """

    def __init__(self, ioport: mido.ports.IOPort):
        self.port = ioport

    def inquiry(self):
        """
        Perform an inquiry request reply handshake with the device.
        """
        raise NotImplemented()
