# Copyright 2024 Tarkan Al-Kazily

import logue.target
from logue.common import InquiryRequest


class InquiryResponse(logue.target.LogueMessage):
    """
     DEVICE INQUIRY REPLY
    +---------+------------------------------------------------+
    | Byte[H] |                Description                     |
    +---------+------------------------------------------------+
    |   F0    | Exclusive Status                               |
    |   7E    | Non Realtime Message                           |
    |   0g    | MIDI Global Channel  ( Device ID )             |
    |   06    | General Information                            |
    |   02    | Identity Reply                                 |
    |   42    | KORG ID              ( Manufacturers ID )      |
    |   57    | NTS-1 digital kit ID ( Family ID   (LSB))      |
    |   01    |                      ( Family ID   (MSB))      |
    |   00    |                      ( Member ID   (LSB))      |
    |   00    |                      ( Member ID   (MSB))      |
    |   xx    |                      ( Minor Ver.  (LSB))      |
    |   xx    |                      ( Minor Ver.  (MSB))      |
    |   xx    |                      ( Major Ver.  (LSB))      |
    |   xx    |                      ( Major Ver.  (MSB))      |
    |   F7    | END OF EXCLUSIVE                               |
    +---------+------------------------------------------------+

    NOTE: The minor and major versions are reported incorrectly
    """

    def __init__(self, major_ver: int, minor_ver: int):
        """
        Args:
            major_ver: SDK version number
            minor_ver: SDK version number
        """
        super().__init__(
            data=[
                0x7E,
                0x00,
                0x06,
                0x02,
                0x42,
                0x57,
                0x01,
                0x00,
                0x00,
                minor_ver & 0x7F,
                (minor_ver >> 7) & 0x7F,
                major_ver & 0x7F,
                (major_ver >> 7) & 0x7F,
            ]
        )
        self.minor_ver = minor_ver
        self.major_ver = major_ver

    @classmethod
    def from_message(cls, message):
        if message.data[4] != 0x42:
            raise Exception("Not a KORG device")

        minor_ver = message.data[10] << 7 | message.data[9]
        major_ver = message.data[12] << 7 | message.data[11]
        return InquiryResponse(major_ver, minor_ver)


class SearchDeviceCommand(logue.target.LogueMessage):
    """
    2-5 SEARCH DEVICE REQUEST
    +---------+------------------------------------------------+
    | Byte[H] |                Description                     |
    +---------+------------------------------------------------+
    |   F0    | Exclusive Status                               |
    |   42    | KORG ID              ( Manufacturers ID )      |
    |   50    | Search Device                                  |
    |   00    | Request                                        |
    |   dd    | Echo Back ID                                   |
    |   F7    | END OF EXCLUSIVE                               |
    +---------+------------------------------------------------
    """

    def __init__(self, echo_id: int):
        """
        Args:
            echo_id: 0-127 ID
        """
        super().__init__(data=[0x42, 0x50, 0x00, echo_id])
        self.echo_id = echo_id

    @classmethod
    def from_message(cls, message):
        echo_id = message.data[3]
        return SearchDeviceCommand(echo_id)


class SearchDeviceResponse(logue.target.LogueMessage):
    """
    1-5 SEARCH DEVICE REPLY
    +---------+------------------------------------------------+
    | Byte[H] |                Description                     |
    +---------+------------------------------------------------+
    |   F0    | Exclusive Status                               |
    |   42    | KORG ID              ( Manufacturers ID )      |
    |   50    | Search Device                                  |
    |   01    | Reply                                          |
    |   0g    | g:MIDI Global Channel  ( Device ID )           |
    |   dd    | Echo Back ID                                   |
    |   57    | NTS-1 digital kit ID ( Family ID   (LSB))      |
    |   01    |                      ( Family ID   (MSB))      |
    |   00    |                      ( Member ID   (LSB))      |
    |   00    |                      ( Member ID   (MSB))      |
    |   xx    |                      ( Minor Ver.  (LSB))      |
    |   xx    |                      ( Minor Ver.  (MSB))      |
    |   xx    |                      ( Major Ver.  (LSB))      |
    |   xx    |                      ( Major Ver.  (MSB))      |
    |   F7    | END OF EXCLUSIVE                               |
    +---------+------------------------------------------------+

    NOTE: The minor and major versions are reported incorrectly
    """

    def __init__(self, echo_id: int, major_ver: int, minor_ver: int):
        """

        Args:
            echo_id: 0-127 ID
            major_ver: SDK version
            minor_ver: SDK version
        """
        super().__init__(
            data=[
                0x42,
                0x50,
                0x01,
                0x00,
                echo_id,
                0x57,
                0x01,
                0x00,
                0x00,
                minor_ver & 0x7F,
                (minor_ver >> 7) & 0x7F,
                major_ver & 0x7F,
                (major_ver >> 7) & 0x7F,
            ]
        )
        self.echo_id = echo_id
        self.major_ver = major_ver
        self.minor_ver = minor_ver

    @classmethod
    def from_message(cls, message):
        if message.data[0] != 0x42:
            raise Exception("Invalid message")

        echo_id = message.data[4]
        minor_ver = message.data[10] << 7 | message.data[9]
        major_ver = message.data[12] << 7 | message.data[11]
        return SearchDeviceResponse(echo_id, major_ver, minor_ver)


class SDK1(logue.target.LogueTarget):
    """
    Sub-class category of LogueTarget for logue devices using the version 1 SDK and MIDI
    implementations.

    Where possible, multiple logue devices that share the same MIDI functions for the SDK version
    can implement those functions here.
    """

    def __init__(self, ioport, channel=1):
        super().__init__(ioport=ioport, channel=channel)

    def inquiry(self):
        cmd = InquiryRequest(self.channel)
        rsp = self.write_cmd(cmd.to_message())
        rsp = InquiryResponse.from_message(rsp)
        # The NTS-1 seems to swap Major and Minor versions
        print(f"Device SDK version {rsp.major_ver}.{rsp.minor_ver}")

    def search(self):
        cmd = SearchDeviceCommand(33)
        rsp = self.write_cmd(cmd.to_message())
        rsp = SearchDeviceResponse.from_message(rsp)
        print(f"{rsp.echo_id} Device SDK version {rsp.major_ver}.{rsp.minor_ver}")


class NTS1(SDK1):
    """
    Supports interacting with the nts-1 logue device.
    """

    def __init__(self, ioport, channel=1):
        super().__init__(ioport=ioport, channel=1)
