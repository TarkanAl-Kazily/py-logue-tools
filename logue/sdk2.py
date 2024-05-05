# Copyright 2024 Tarkan Al-Kazily

import logue.target

KORG_ID = 0x42
EXCLUSIVE_HEADER = [KORG_ID, 0x30, 0x00, 0x01, 0x73]


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
                KORG_ID,
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
        if message.data[4] != KORG_ID:
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
        super().__init__(data=[KORG_ID, 0x50, 0x00, echo_id])
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
                KORG_ID,
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
        if message.data[0] != KORG_ID:
            raise Exception("Invalid message")

        echo_id = message.data[4]
        minor_ver = message.data[10] << 7 | message.data[9]
        major_ver = message.data[12] << 7 | message.data[11]
        return SearchDeviceResponse(echo_id, major_ver, minor_ver)


class CurrentProgramDataDumpCommand(logue.target.LogueMessage):
    """
    (1) CURRENT PROGRAM DATA DUMP REQUEST                               R
    +----------------+--------------------------------------------------+
    |     Byte       |             Description                          |
    +----------------+--------------------------------------------------+
    | F0,42,3g,      | EXCLUSIVE HEADER                                 |
    |    00,01,73    |                                                  |
    | 0001 0000 (10) | CURRENT PROGRAM DATA DUMP REQUEST      10H       |
    | 1111 0111 (F7) | EOX                                              |
    +----------------+--------------------------------------------------+
    """

    def __init__(self):
        super().__init__(data=EXCLUSIVE_HEADER + [0x10])

    @classmethod
    def from_message(cls, message):
        return CurrentProgramDataDumpCommand()


class CurrentProgramDataDump(logue.target.LogueMessage):
    """
    (3) CURRENT PROGRAM DATA DUMP                                     R/T
    +----------------+--------------------------------------------------+
    |     Byte       |             Description                          |
    +----------------+--------------------------------------------------+
    | F0,42,3g,      | EXCLUSIVE HEADER                                 |
    |    00,01,73    |                                                  |
    | 0100 0000 (40) | CURRENT PROGRAM DATA DUMP              40H       |
    | 0ddd dddd (dd) | Data                                             |
    | 0ddd dddd (dd) |  :         Data Size         Conv. Size          |
    | 0ddd dddd (dd) |  :      576Bytes (7bit) -> 505Bytes (8bit)       |
    | 0ddd dddd (dd) |  :                                               |
    | 1111 0111 (F7) | EOX                        (See NOTE 1, TABLE 2) |
    +----------------+--------------------------------------------------+
    """

    DATA_CONV_SIZE = 505

    def __init__(self, data: bytes):
        if len(data) != CurrentProgramDataDump.DATA_CONV_SIZE:
            raise Exception("Incorrect data length")

        super().__init__(data=EXCLUSIVE_HEADER + [0x40] + logue.host_to_midi(data))

    @classmethod
    def from_message(cls, message):
        return CurrentProgramDataDumpCommand()


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

    def search(self):
        cmd = SearchDeviceCommand(0x55)
        rsp = self.write_cmd(cmd.to_message())
        rsp = SearchDeviceResponse.from_message(rsp)
        print(f"{rsp.echo_id} Device SDK version {rsp.major_ver}.{rsp.minor_ver}")


class NTS1Mk2(SDK2):
    """
    Supports interacting with the nts-1 mk2 logue device.
    """

    def __init__(self, ioport, channel=1):
        super().__init__(ioport=ioport, channel=1)
