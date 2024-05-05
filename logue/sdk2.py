# Copyright 2024 Tarkan Al-Kazily

import logue.target
from logue.common import InquiryRequest

KORG_ID = 0x42


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


class SystemExclusiveMessage(logue.target.LogueMessage):
    """
    Common class for all SDK2 System Exclusive messages which share a common header format.
    """

    HEADER = [KORG_ID, 0x30, 0x00, 0x01, 0x73]

    def __init__(self, id, payload):
        super().__init__(data=SystemExclusiveMessage.HEADER + [id] + payload)
        self.id = id
        self.payload = payload

    @classmethod
    def header_from_message(cls, message):
        return message.data[: len(SystemExclusiveMessage.HEADER)]

    @classmethod
    def id_from_message(cls, message):
        return message.data[len(SystemExclusiveMessage.HEADER)]

    @classmethod
    def payload_from_message(cls, message):
        return message.data[len(SystemExclusiveMessage.HEADER) + 1 :]

    @classmethod
    def from_message(cls, message):
        message_header = SystemExclusiveMessage.header_from_message(message)
        message_id = SystemExclusiveMessage.id_from_message(message)
        if message_header != SystemExclusiveMessage.HEADER:
            raise Exception(f"{message} is not a SystemExclusiveMessage")

        # TODO key off message_id and return appropriate class type
        raise NotImplementedException()


class CurrentProgramDataDumpRequest(SystemExclusiveMessage):
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

    ID = 0x10

    def __init__(self):
        super().__init__(id=CurrentProgramDataDumpRequest.ID, payload=[])

    @classmethod
    def from_message(cls, message):
        if (
            SystemExclusiveMessage.id_from_message(message)
            != CurrentProgramDataDumpRequest.ID
        ):
            raise Exception("Incorrect message id")

        if SystemExclusiveMessage.payload_from_message(message) != []:
            raise Exception("Incorrect payload")

        return CurrentProgramDataDumpRequest()


class CurrentProgramDataDump(SystemExclusiveMessage):
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

    ID = 0x40
    DATA_CONV_SIZE = 505
    PAYLOAD_SIZE = 576

    def __init__(self, program_data: bytes):
        if len(program_data) != CurrentProgramDataDump.DATA_CONV_SIZE:
            raise Exception("Incorrect data length")

        super().__init__(
            id=CurrentProgramDataDump.ID, payload=logue.host_to_midi(program_data)
        )
        self.program_data = program_data

    @classmethod
    def from_message(cls, message):
        if SystemExclusiveMessage.id_from_message(message) != CurrentProgramDataDump.ID:
            raise Exception("Incorrect message id")

        payload = SystemExclusiveMessage.payload_from_message(message)
        if len(payload) != CurrentProgramDataDump.PAYLOAD_SIZE:
            raise Exception("Incorrect payload")

        return CurrentProgramDataDump(program_data=logue.midi_to_host(payload))


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
        cmd = InquiryRequest(self.channel)
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
