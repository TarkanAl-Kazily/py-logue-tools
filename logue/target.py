# Copyright 2024 Tarkan Al-Kazily

import mido.ports
import time


class LogueError(Exception):
    """Base Logue Exception class"""


class LogueMessage:
    """Base LogueMessage class specific message types can be subclassed from."""

    def __init__(self, data: bytes):
        self.data = data

    def to_message(self):
        return mido.Message(type="sysex", data=self.data)

    @classmethod
    def from_message(cls, message):
        return LogueMessage(data=message.data)


class LogueTarget:
    """
    Base class defining a Logue-SDK compatible device.

    Sub-classes of this class define specific MIDI implementations and additional functions for
    working with different device types.

    Attributes:
        port: Bi-directional MIDI port for communicating with target
        channel: MIDI channel [1-16] for the target
    """

    RETRIES = 100
    DELAY_S = 0.01

    def __init__(self, ioport: mido.ports.IOPort, channel: int = 1):
        self.port = ioport
        self.channel = channel

    def write_cmd(self, command: mido.Message) -> mido.Message:
        """
        Write a message and wait for its response from the target.
        Raises an exception if no response is received quickly.

        Args:
            command: command to write on the port

        Returns:
            Next received message from the device.
        """
        self.write(command)

        return self.receive()

    def write(self, command: mido.Message):
        """
        Write a message.

        Args:
            command: command to write on the port
        """
        self.port.send(command)

    def receive(self) -> mido.Message:
        """
        Receive the next sysex message from the device.

        Raises:
            LogueError: When a message is not received within a short time interval.

        Returns:
            Next received message from the device.
        """
        for _ in range(LogueTarget.RETRIES):
            response = self.port.receive(block=False)
            if response and response.type == "sysex":
                return response
            time.sleep(LogueTarget.DELAY_S)

        raise LogueError("Did not receive a sysex message before timeout")

    # Device specific APIs

    def inquiry(self, full_inquiry: bool) -> bool:
        """
        Perform an inquiry request-reply handshake with the device.

        Args:
            full_inquiry: Set to true to print additional status information about the device.

        Returns:
            True on success, false otherwise
        """
        raise NotImplementedError()

    def search(self) -> bool:
        """
        Perform an search for available KORG devices.

        Returns:
            True on success, false otherwise
        """
        raise NotImplementedError()

    def save_data(self, file: typing.IO) -> bool:
        """
        Save the device current settings to a file. File save formats are device specific.
        TODO: This should support additional user arguments to provide greater customization based on device capabilities.

        Args:
            file: File object to write save data to.

        Returns:
            True on success, false otherwise.
        """
        raise NotImplementedError()

    def load_data(self, file: typing.IO) -> bool:
        """
        Load settings from a file to the device. File save formats are device specific.
        TODO: This should support additional user arguments to provide greater customization based on device capabilities.

        Args:
            file: File object to load save data from.

        Returns:
            True on success, false otherwise.
        """
        raise NotImplementedError()

    def install_program(self, module: str, slot: int, filename: str) -> bool:
        """
        Install a user program to the device. Module program formats are device specific and should be built by the logue-sdk tools.

        Args:
            module: Module string ID, usually device specific.
            slot: Slot number for the program to be installed to.
            filename: Path to the program file to install.

        Returns:
            True on success, false otherwise.
        """
        raise NotImplementedError()

    def fetch_program(self, module: str, slot: int, filename: str) -> bool:
        """
        Receive a user program from the device, saving it to a file.

        Args:
            module: Module string ID, usually device specific.
            slot: Slot number for the program to be fetch from.
            filename: Path to write the program file to.

        Returns:
            True on success, false otherwise.
        """
        raise NotImplementedError()

    def clear_program(self, module: str, slot: int) -> bool:
        """
        Clear a user program from the device.

        Args:
            module: Type of the user program
            slot: Slot to clear the program from

        Returns:
            True on success, false otherwise.
        """
        raise NotImplementedError()
