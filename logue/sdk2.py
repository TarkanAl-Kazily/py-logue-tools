# Copyright 2024 Tarkan Al-Kazily

import logue.target


class InquiryCommand(logue.target.LogueMessage):
    """
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

    def __init__(self, channel: int):
        """
        Args:
            channel: 1-16 MIDI channel ID
        """
        super().__init__(data=[0x7E, channel - 1, 0x06, 0x01])
        self.channel = channel

    @classmethod
    def from_message(message):
        channel = message.data[1] + 1
        return InquiryCommand(channel)


class InquiryResponse(logue.target.LogueMessage):
    """
     DEVICE INQUIRY REPLY
    +---------+------------------------------------------------+
    | Byte[H] |                Description                     |
    +---------+------------------------------------------------+
    |   F0    | Exclusive Status                               |
    |   7E    | Non Realtime Message                           |
    |   00    | MIDI Global Channel        ( Device ID )       |
    |   06    | General Information                            |
    |   02    | Identity Reply                                 |
    |   42    | KORG ID                    ( Manufacturers ID )|
    |   73    | NTS-1 digital kit mk II ID ( Family ID   (LSB))|
    |   01    |                            ( Family ID   (MSB))|
    |   01    |                            ( Member ID   (LSB))|
    |   00    |                            ( Member ID   (MSB))|
    |   xx    |                            ( Minor Ver.  (LSB))|
    |   xx    |                            ( Minor Ver.  (MSB))|
    |   xx    |                            ( Major Ver.  (LSB))|
    |   xx    |                            ( Major Ver.  (MSB))|
    |   F7    | END OF EXCLUSIVE                               |
    +---------+------------------------------------------------+
    """

    def __init__(self, minor_ver: int, major_ver: int):
        """
        Args:
            minor_ver: SDK version number
            major_ver: SDK version number
        """
        super().__init__(
            data=[
                0x7E,
                0x00,
                0x06,
                0x02,
                0x42,
                0x73,
                0x01,
                0x01,
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
        return InquiryResponse(minor_ver, major_ver)


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
        """

        cmd = InquiryCommand(self.channel)
        rsp = self.write_cmd(cmd.to_message())
        rsp = InquiryResponse.from_message(rsp)
        print(f"Device SDK version {rsp.major_ver}.{rsp.minor_ver}")


class NTS1Mk2(SDK2):
    """
    Supports interacting with the nts-1 mk2 logue device.
    """

    def __init__(self, ioport, channel=1):
        super().__init__(ioport=ioport, channel=1)
