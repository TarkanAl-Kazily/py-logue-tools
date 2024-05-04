# Copyright 2024 Tarkan Al-Kazily

import mido.ports
import time


class LogueTarget:
    """
    Base class defining a Logue-SDK compatible device.

    Sub-classes of this class define specific MIDI implementations and additional functions for
    working with different device types.

    Attributes:
        port: Bi-directional MIDI port for communicating with target
        channel: MIDI channel [1-16] for the target
    """

    def __init__(self, ioport: mido.ports.IOPort, channel: int = 1):
        self.port = ioport
        self.channel = channel

    def write_cmd(self, command: mido.Message) -> mido.Message:
        """
        Write a message and wait for its response from the target.
        Blocks.

        Args:
            command: command to write on the port

        Returns:
            Received message from the device.
        """
        self.port.send(command)

        for _ in range(10):
            response = self.port.receive(block=False)
            if response:
                return response
            time.sleep(0.01)

        raise Exception("Timeout")

    def inquiry(self):
        """
        Perform an inquiry request reply handshake with the device.
        """
        raise NotImplemented()
