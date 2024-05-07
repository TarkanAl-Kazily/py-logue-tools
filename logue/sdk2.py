# Copyright 2024 Tarkan Al-Kazily

import typing
import json
import logue
import logue.target
import mido
from logue.common import InquiryRequest, SearchDeviceRequest


def id_only_from_message(cls, message):
    if SystemExclusiveMessage.id_from_message(message) != cls.ID:
        raise logue.LogueError("Incorrect message type")

    if len(SystemExclusiveMessage.payload_from_message(message)) != 0:
        raise logue.LogueError("Incorrect message with non-empty payload")

    return cls()


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
                logue.KORG_ID,
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
        if message.data[4] != logue.KORG_ID:
            raise logue.LogueError("Not a KORG device")

        minor_ver = message.data[10] << 7 | message.data[9]
        major_ver = message.data[12] << 7 | message.data[11]
        return InquiryResponse(major_ver, minor_ver)


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
                logue.KORG_ID,
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
        if message.data[0] != logue.KORG_ID:
            raise logue.LogueError("Invalid message")

        echo_id = message.data[4]
        minor_ver = message.data[10] << 7 | message.data[9]
        major_ver = message.data[12] << 7 | message.data[11]
        return SearchDeviceResponse(echo_id, major_ver, minor_ver)


class SystemExclusiveMessage(logue.target.LogueMessage):
    """
    Common class for all SDK2 System Exclusive messages which share a common header format.
    """

    HEADER = [logue.KORG_ID, 0x30, 0x00, 0x01, 0x73]

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
        if list(message_header) != SystemExclusiveMessage.HEADER:
            raise logue.LogueError(f"{message} is not a SystemExclusiveMessage")

        # Search for a supported message type based on the exclusive id
        for subcls in SystemExclusiveMessage.__subclasses__():
            if subcls.ID == message_id:
                return subcls.from_message(message)

        raise logue.LogueError(
            f"Received system exclusive message with unknown id {message_id}"
        )


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
        return id_only_from_message(cls, message)


class GlobalDataDumpRequest(SystemExclusiveMessage):
    """
    (2) GLOBAL DATA DUMP REQUEST                                        R
    +----------------+--------------------------------------------------+
    |     Byte       |             Description                          |
    +----------------+--------------------------------------------------+
    | F0,42,3g,      | EXCLUSIVE HEADER                                 |
    |    00,01,73    |                                                  |
    | 0000 1110 (0E) | GLOBAL DATA DUMP REQUEST               0EH       |
    | 1111 0111 (F7) | EOX                                              |
    +----------------+--------------------------------------------------+
    """

    ID = 0x0E

    def __init__(self):
        super().__init__(id=GlobalDataDumpRequest.ID, payload=[])

    @classmethod
    def from_message(cls, message):
        return id_only_from_message(cls, message)


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

    NOTE: Actual host size is 504 bytes long
    """

    ID = 0x40
    HOST_PAYLOAD_SIZE = 504
    MIDI_PAYLOAD_SIZE = 576

    def __init__(self, program_data: list[int]):
        if len(program_data) != CurrentProgramDataDump.HOST_PAYLOAD_SIZE:
            raise logue.LogueError(f"Incorrect data length {len(program_data)}")

        super().__init__(
            id=CurrentProgramDataDump.ID, payload=logue.host_to_midi(program_data)
        )
        self.program_data = program_data

        if bytes(program_data[0:4]) != "PROG".encode("ascii") or bytes(
            program_data[-4:]
        ) != "PRED".encode("ascii"):
            raise logue.LogueError(
                f"Incorrect program_data format - {program_data[0:4]} {program_data[-4:]}"
            )

    @classmethod
    def from_message(cls, message):
        if SystemExclusiveMessage.id_from_message(message) != CurrentProgramDataDump.ID:
            raise logue.LogueError("Incorrect message id")

        payload = SystemExclusiveMessage.payload_from_message(message)
        if len(payload) != CurrentProgramDataDump.MIDI_PAYLOAD_SIZE:
            raise logue.LogueError("Incorrect payload")

        return CurrentProgramDataDump(program_data=logue.midi_to_host(payload))

    def __repr__(self):
        result = ""
        maj_ver = (self.program_data[4] << 8) | self.program_data[5]
        min_ver = self.program_data[6]
        patch = self.program_data[7]
        result += f"ver {maj_ver}.{min_ver}.{patch}"

        prog_name = bytes(self.program_data[12:28]).decode("ascii")
        osc_name = bytes(self.program_data[40:60]).decode("ascii")
        mod_name = bytes(self.program_data[124:144]).decode("ascii")
        delay_name = bytes(self.program_data[180:200]).decode("ascii")
        rvb_name = bytes(self.program_data[236:256]).decode("ascii")

        result += f" {prog_name}: osc {osc_name} mod {mod_name} delay {delay_name} reverb {rvb_name}"
        return result


class GlobalDataDump(SystemExclusiveMessage):
    """
    (4) GLOBAL DATA DUMP                                              R/T
    +----------------+--------------------------------------------------+
    |     Byte       |             Description                          |
    +----------------+--------------------------------------------------+
    | F0,42,3g,      | EXCLUSIVE HEADER                                 |
    |    00,01,73    |                                                  |
    | 0101 0001 (51) | GLOBAL DATA DUMP                       51H       |
    | 0ddd dddd (dd) | Data                                             |
    | 0ddd dddd (dd) |  :         Data Size         Conv. Size          |
    | 0ddd dddd (dd) |  :       37Bytes (7bit) -> 32Bytes (8bit)        |
    |     :          |  :                                               |
    | 1111 0111 (F7) | EOX                        (See NOTE 1, TABLE 1) |
    +----------------+--------------------------------------------------+
    """

    ID = 0x51
    HOST_PAYLOAD_SIZE = 32
    MIDI_PAYLOAD_SIZE = 37

    def __init__(self, program_data: list[int]):
        if len(program_data) != GlobalDataDump.HOST_PAYLOAD_SIZE:
            raise logue.LogueError("Incorrect data length")

        super().__init__(id=GlobalDataDump.ID, payload=logue.host_to_midi(program_data))
        self.program_data = program_data

    @classmethod
    def from_message(cls, message):
        if SystemExclusiveMessage.id_from_message(message) != GlobalDataDump.ID:
            raise logue.LogueError("Incorrect message id")

        payload = SystemExclusiveMessage.payload_from_message(message)
        if len(payload) != GlobalDataDump.MIDI_PAYLOAD_SIZE:
            raise logue.LogueError("Incorrect payload")

        return GlobalDataDump(program_data=logue.midi_to_host(payload))


class UserApiVersionRequest(SystemExclusiveMessage):
    """
    (5) USER API VERSION REQUEST                                       R
    +----------------+--------------------------------------------------+
    |     Byte       |             Description                          |
    +----------------+--------------------------------------------------+
    | F0,42,3g,      | EXCLUSIVE HEADER                                 |
    |    00,01,73    |                                                  |
    | 0001 0111 (17) | USER API VERSION REQUEST               17H       |
    | 1111 0111 (F7) | EOX                                              |
    +----------------+--------------------------------------------------+
    """

    ID = 0x17

    def __init__(self):
        super().__init__(id=UserApiVersionRequest.ID, payload=[])

    @classmethod
    def from_message(cls, message):
        return id_only_from_message(cls, message)


class UserModuleInfoRequest(SystemExclusiveMessage):
    """
    (6) USER MODULE INFO REQUEST                                       R
    +----------------+--------------------------------------------------+
    |     Byte       |             Description                          |
    +----------------+--------------------------------------------------+
    | F0,42,3g,      | EXCLUSIVE HEADER                                 |
    |    00,01,73    |                                                  |
    | 0001 1000 (18) | USER MODULE INFO REQUEST               18H       |
    | 0ddd dddd      | USER MODULE ID (modfx:1,delfx:2,revfx:3,osc:4)   |
    | 1111 0111 (F7) | EOX                                              |
    +----------------+--------------------------------------------------+
    """

    ID = 0x18

    def __init__(self, module_id: int):
        super().__init__(id=UserModuleInfoRequest.ID, payload=[module_id])
        self.module_id = module_id

    @classmethod
    def from_message(cls, message):
        if SystemExclusiveMessage.id_from_message(message) != UserModuleInfoRequest.ID:
            raise logue.LogueError("Incorrect message id")

        payload = SystemExclusiveMessage.payload_from_message(message)
        if len(payload) != 1:
            raise logue.LogueError("Incorrect payload")

        return UserModuleInfoRequest(module_id=payload[0])


class UserSlotStatusRequest(SystemExclusiveMessage):
    """
    (7) USER SLOT STATUS REQUEST                                       R
    +----------------+--------------------------------------------------+
    |     Byte       |             Description                          |
    +----------------+--------------------------------------------------+
    | F0,42,3g,      | EXCLUSIVE HEADER                                 |
    |    00,01,73    |                                                  |
    | 0001 1001 (19) | USER SLOT STATUS REQUEST               19H       |
    | 0ddd dddd      | USER MODULE ID (modfx:1,delfx:2,revfx:3,osc:4)   |
    | 0ddd dddd      | USER SLOT ID   (modfx/osc:0-15, delfx/revfx:0-7) |
    | 1111 0111 (F7) | EOX                                              |
    +----------------+--------------------------------------------------+
    """

    ID = 0x19

    def __init__(self, module_id: int, slot_id: int):
        super().__init__(id=UserSlotStatusRequest.ID, payload=[module_id, slot_id])
        self.module_id = module_id
        self.slot_it = slot_id

    @classmethod
    def from_message(cls, message):
        if SystemExclusiveMessage.id_from_message(message) != UserSlotStatusRequest.ID:
            raise logue.LogueError("Incorrect message id")

        payload = SystemExclusiveMessage.payload_from_message(message)
        if len(payload) != 2:
            raise logue.LogueError("Incorrect payload")

        return UserSlotStatusRequest(module_id=payload[0], slot_id=payload[1])


class UserSlotDataRequest(SystemExclusiveMessage):
    """
    (8) USER SLOT DATA REQUEST                                         R
    +----------------+--------------------------------------------------+
    |     Byte       |             Description                          |
    +----------------+--------------------------------------------------+
    | F0,42,3g,      | EXCLUSIVE HEADER                                 |
    |    00,01,73    |                                                  |
    | 0001 1010 (1A) | USER SLOT DATA REQUEST                 1AH       |
    | 0ddd dddd      | USER MODULE ID (modfx:1,delfx:2,revfx:3,osc:4)   |
    | 0ddd dddd      | USER SLOT ID   (modfx/osc:0-15, delfx/revfx:0-7) |
    | 1111 0111 (F7) | EOX                                              |
    +----------------+--------------------------------------------------+
    """

    ID = 0x1A

    def __init__(self, module_id: int, slot_id: int):
        super().__init__(id=UserSlotDataRequest.ID, payload=[module_id, slot_id])
        self.module_id = module_id
        self.slot_it = slot_id

    @classmethod
    def from_message(cls, message):
        if SystemExclusiveMessage.id_from_message(message) != UserSlotDataRequest.ID:
            raise logue.LogueError("Incorrect message id")

        payload = SystemExclusiveMessage.payload_from_message(message)
        if len(payload) != 2:
            raise logue.LogueError("Incorrect payload")

        return UserSlotDataRequest(module_id=payload[0], slot_id=payload[1])


class ClearUserSlot(SystemExclusiveMessage):
    """
    (9) CLEAR USER SLOT                                                R
    +----------------+--------------------------------------------------+
    |     Byte       |             Description                          |
    +----------------+--------------------------------------------------+
    | F0,42,3g,      | EXCLUSIVE HEADER                                 |
    |    00,01,73    |                                                  |
    | 0001 1011 (1B) | CLEAR USER SLOT                        1BH       |
    | 0ddd dddd      | USER MODULE ID (modfx:1,delfx:2,revfx:3,osc:4)   |
    | 0ddd dddd      | USER SLOT ID   (modfx/osc:0-15, delfx/revfx:0-7) |
    | 1111 0111 (F7) | EOX                                              |
    +----------------+--------------------------------------------------+
    """

    ID = 0x1B

    def __init__(self, module_id: int, slot_id: int):
        super().__init__(id=ClearUserSlot.ID, payload=[module_id, slot_id])
        self.module_id = module_id
        self.slot_id = slot_id

    @classmethod
    def from_message(cls, message):
        if SystemExclusiveMessage.id_from_message(message) != ClearUserSlot.ID:
            raise logue.LogueError("Incorrect message id")

        payload = SystemExclusiveMessage.payload_from_message(message)
        if len(payload) != 2:
            raise logue.LogueError("Incorrect payload")

        return ClearUserSlot(module_id=payload[0], slot_id=payload[1])


class ClearUserModule(SystemExclusiveMessage):
    """
    (10) CLEAR USER MODULE                                              R
    +----------------+--------------------------------------------------+
    |     Byte       |             Description                          |
    +----------------+--------------------------------------------------+
    | F0,42,3g,      | EXCLUSIVE HEADER                                 |
    |    00,01,73    |                                                  |
    | 0001 1101 (1D) | CLEAR USER MODULE                      1DH       |
    | 0ddd dddd      | USER MODULE ID (modfx:1,delfx:2,revfx:3,osc:4)   |
    | 1111 0111 (F7) | EOX                                              |
    +----------------+--------------------------------------------------+
    """

    ID = 0x1D

    def __init__(self, module_id: int):
        super().__init__(id=ClearUserModule.ID, payload=[module_id])
        self.module_id = module_id

    @classmethod
    def from_message(cls, message):
        if SystemExclusiveMessage.id_from_message(message) != ClearUserModule.ID:
            raise logue.LogueError("Incorrect message id")

        payload = SystemExclusiveMessage.payload_from_message(message)
        if len(payload) != 1:
            raise logue.LogueError("Incorrect payload")

        return ClearUserModule(module_id=payload[0])


class SwapUserData(SystemExclusiveMessage):
    """
    (11) SWAP USER DATA                                                 R
    +----------------+--------------------------------------------------+
    |     Byte       |             Description                          |
    +----------------+--------------------------------------------------+
    | F0,42,3g,      | EXCLUSIVE HEADER                                 |
    |    00,01,73    |                                                  |
    | 0001 1110 (1E) | SWAP USER DATA                         1EH       |
    | 0ddd dddd      | USER MODULE ID (modfx:1,delfx:2,revfx:3,osc:4)   |
    | 0ddd dddd      | USER SLOT ID   (modfx/osc:0-15, delfx/revfx:0-7) |
    | 0ddd dddd      | USER SLOT ID   (modfx/osc:0-15, delfx/revfx:0-7) |
    | 1111 0111 (F7) | EOX                                              |
    +----------------+--------------------------------------------------+
    """

    ID = 0x1E

    def __init__(self, module_id: int, slot1: int, slot2: int):
        super().__init__(id=SwapUserData.ID, payload=[module_id, slot1, slot2])
        self.module_id = module_id
        self.slot1 = slot1
        self.slot2 = slot2

    @classmethod
    def from_message(cls, message):
        if SystemExclusiveMessage.id_from_message(message) != SwapUserData.ID:
            raise logue.LogueError("Incorrect message id")

        payload = SystemExclusiveMessage.payload_from_message(message)
        if len(payload) != 3:
            raise logue.LogueError("Incorrect payload")

        return SwapUserData(module_id=payload[0], slot1=payload[1], slot2=payload[2])


class UserApiVersion(SystemExclusiveMessage):
    """
    (12) USER API VERSION                                               T
    +----------------+--------------------------------------------------+
    |     Byte       |             Description                          |
    +----------------+--------------------------------------------------+
    | F0,42,3g,      | EXCLUSIVE HEADER                                 |
    |    00,01,73    |                                                  |
    | 0100 0111 (47) | USER API VERSION                       47H       |
    | 0000 1010 (dd) | PLATFORM ID          (NTS-1 digital kit mkII: 5) |
    | 0ddd dddd (dd) | MAJOR                           (0-99)           |
    | 0ddd dddd (dd) | MINOR                           (0-99)           |
    | 0ddd dddd (dd) | PATCH                           (0-99)           |
    | 1111 0111 (F7) | EOX                                              |
    +----------------+--------------------------------------------------+
    """

    ID = 0x47

    def __init__(self, platform_id: int, major: int, minor: int, patch: int):
        super().__init__(
            id=UserApiVersion.ID, payload=[platform_id, major, minor, patch]
        )
        self.platform_id = platform_id
        self.major = major
        self.minor = minor
        self.patch = patch

    @classmethod
    def from_message(cls, message):
        if SystemExclusiveMessage.id_from_message(message) != UserApiVersion.ID:
            raise logue.LogueError("Incorrect message id")

        payload = SystemExclusiveMessage.payload_from_message(message)
        if len(payload) != 4:
            raise logue.LogueError("Incorrect payload")

        return UserApiVersion(
            platform_id=payload[0], major=payload[1], minor=payload[2], patch=payload[3]
        )


class UserModuleInfo(SystemExclusiveMessage):
    """
    (13) USER MODULE INFO                                               T
    +----------------+--------------------------------------------------+
    |     Byte       |             Description                          |
    +----------------+--------------------------------------------------+
    | F0,42,3g,      | EXCLUSIVE HEADER                                 |
    |    00,01,73    |                                                  |
    | 0100 1000 (48) | USER MODULE INFO                       48H       |
    | 0ddd dddd (dd) | Data1                                            |
    | 0ddd dddd (dd) | Data2                                            |
    | 0ddd dddd (dd) |  :         Data Size         Conv. Size          |
    | 0ddd dddd (dd) |  :       11Bytes (7bit) ->  9Bytes (8bit)        |
    |     :          |  :                                               |
    | 1111 0111 (F7) | EOX                        (see NOTE 1, TABLE 3) |
    +----------------+--------------------------------------------------+
    """

    ID = 0x48
    HOST_PAYLOAD_SIZE = 9
    MIDI_PAYLOAD_SIZE = 11

    def __init__(self, program_data: list[int]):
        if len(program_data) != UserModuleInfo.HOST_PAYLOAD_SIZE:
            raise logue.LogueError("Incorrect program_data size")

        super().__init__(id=UserModuleInfo.ID, payload=logue.host_to_midi(program_data))
        self.program_data = program_data

    @classmethod
    def from_message(cls, message):
        if SystemExclusiveMessage.id_from_message(message) != UserModuleInfo.ID:
            raise logue.LogueError("Incorrect message id")

        payload = SystemExclusiveMessage.payload_from_message(message)
        if len(payload) != UserModuleInfo.MIDI_PAYLOAD_SIZE:
            raise logue.LogueError("Incorrect payload")

        return UserModuleInfo(program_data=logue.midi_to_host(payload))


class UserSlotStatus(SystemExclusiveMessage):
    """
    (14) USER SLOT STATUS                                            R/T
    +----------------+--------------------------------------------------+
    |     Byte       |             Description                          |
    +----------------+--------------------------------------------------+
    | F0,42,3g,      | EXCLUSIVE HEADER                                 |
    |    00,01,73    |                                                  |
    | 0100 1001 (49) | USER SLOT STATUS                       49H       |
    | 0ddd dddd (dd) | USER MODULE ID (modfx:1,delfx:2,revfx:3,osc:4)   |
    | 0ddd dddd (dd) | USER SLOT ID   (modfx/osc:0-15, delfx/revfx:0-7) |
    | 0ddd dddd (dd) | Data1                                            |
    | 0ddd dddd (dd) | Data2                                            |
    | 0ddd dddd (dd) |  :         Data Size         Conv. Size          |
    | 0ddd dddd (dd) |  :       37Bytes (7bit) -> 32Bytes (8bit)        |
    |     :          |  :                                               |
    | 1111 0111 (F7) | EOX                        (see NOTE 1, TABLE 4) |
    +----------------+--------------------------------------------------+
    """

    ID = 0x49
    HOST_PAYLOAD_SIZE = 32
    MIDI_PAYLOAD_SIZE = 37

    def __init__(self, module_id: int, slot_id: int, program_data: list[int]):
        if len(program_data) != UserSlotStatus.HOST_PAYLOAD_SIZE:
            raise logue.LogueError("Incorrect program_data size")
        super().__init__(
            id=UserSlotStatus.ID,
            payload=[module_id, slot_id] + logue.host_to_midi(program_data),
        )
        self.module_id = module_id
        self.slot_id = slot_id
        self.program_data = program_data

    @classmethod
    def from_message(cls, message):
        if SystemExclusiveMessage.id_from_message(message) != UserSlotStatus.ID:
            raise logue.LogueError("Incorrect message id")

        payload = SystemExclusiveMessage.payload_from_message(message)
        if len(payload) != 2 + UserSlotStatus.MIDI_PAYLOAD_SIZE:
            raise logue.LogueError("Incorrect payload")

        return UserSlotStatus(
            module_id=payload[0],
            slot_id=payload[1],
            program_data=logue.midi_to_host(payload[2:]),
        )


class UserSlotData(SystemExclusiveMessage):
    """
    (15) USER SLOT DATA                                              R/T
    +----------------+--------------------------------------------------+
    |     Byte       |             Description                          |
    +----------------+--------------------------------------------------+
    | F0,42,3g,      | EXCLUSIVE HEADER                                 |
    |    00,01,73    |                                                  |
    | 0100 1010 (4A) | USER SLOT DATA                         4AH       |
    | 0ddd dddd (dd) | Data1                                            |
    | 0ddd dddd (dd) | Data2                                            |
    | 0ddd dddd (dd) |  :         Data Size         Conv. Size          |
    | 0ddd dddd (dd) |  :     Variable (7bit) -> Variable (8bit)        |
    |     :          |  :                                               |
    | 1111 0111 (F7) | EOX                        (see NOTE 1, TABLE 5) |
    +----------------+--------------------------------------------------+
    """

    ID = 0x4A

    def __init__(self, program_data: list[int]):
        super().__init__(id=UserSlotData.ID, payload=logue.host_to_midi(program_data))
        self.program_data = program_data

    @classmethod
    def from_message(cls, message):
        if SystemExclusiveMessage.id_from_message(message) != UserSlotData.ID:
            raise logue.LogueError("Incorrect message id")

        payload = SystemExclusiveMessage.payload_from_message(message)
        return UserSlotData(program_data=logue.midi_to_host(payload))


class StatusOperationCompleted(SystemExclusiveMessage):
    ID = 0x23

    def __init__(self):
        super().__init__(id=StatusOperationCompleted.ID, payload=[])

    @classmethod
    def from_message(cls, message):
        return id_only_from_message(cls, message)


class StatusOperationError(SystemExclusiveMessage):
    ID = 0x24

    def __init__(self):
        super().__init__(id=StatusOperationError.ID, payload=[])

    @classmethod
    def from_message(cls, message):
        return id_only_from_message(cls, message)


class StatusDataFormatError(SystemExclusiveMessage):
    ID = 0x26

    def __init__(self):
        super().__init__(id=StatusDataFormatError.ID, payload=[])

    @classmethod
    def from_message(cls, message):
        return id_only_from_message(cls, message)


class StatusUserDataSizeError(SystemExclusiveMessage):
    ID = 0x27

    def __init__(self):
        super().__init__(id=StatusUserDataSizeError.ID, payload=[])

    @classmethod
    def from_message(cls, message):
        return id_only_from_message(cls, message)


class StatusUserDataCrcError(SystemExclusiveMessage):
    ID = 0x28

    def __init__(self):
        super().__init__(id=StatusUserDataCrcError.ID, payload=[])

    @classmethod
    def from_message(cls, message):
        return id_only_from_message(cls, message)


class StatusUserTargetError(SystemExclusiveMessage):
    ID = 0x29

    def __init__(self):
        super().__init__(id=StatusUserTargetError.ID, payload=[])

    @classmethod
    def from_message(cls, message):
        return id_only_from_message(cls, message)


class StatusUserApiError(SystemExclusiveMessage):
    ID = 0x2A

    def __init__(self):
        super().__init__(id=StatusUserApiError.ID, payload=[])

    @classmethod
    def from_message(cls, message):
        return id_only_from_message(cls, message)


class StatusUserLoadSizeError(SystemExclusiveMessage):
    ID = 0x2B

    def __init__(self):
        super().__init__(id=StatusUserLoadSizeError.ID, payload=[])

    @classmethod
    def from_message(cls, message):
        return id_only_from_message(cls, message)


class StatusUserModuleError(SystemExclusiveMessage):
    ID = 0x2C

    def __init__(self):
        super().__init__(id=StatusUserModuleError.ID, payload=[])

    @classmethod
    def from_message(cls, message):
        return id_only_from_message(cls, message)


class StatusUserSlotError(SystemExclusiveMessage):
    ID = 0x2D

    def __init__(self):
        super().__init__(id=StatusUserSlotError.ID, payload=[])

    @classmethod
    def from_message(cls, message):
        return id_only_from_message(cls, message)


class StatusUserFormatError(SystemExclusiveMessage):
    ID = 0x2E

    def __init__(self):
        super().__init__(id=StatusUserFormatError.ID, payload=[])

    @classmethod
    def from_message(cls, message):
        return id_only_from_message(cls, message)


class StatusUserInternalError(SystemExclusiveMessage):
    ID = 0x2F

    def __init__(self):
        super().__init__(id=StatusUserInternalError.ID, payload=[])

    @classmethod
    def from_message(cls, message):
        return id_only_from_message(cls, message)


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
        cmd = SearchDeviceRequest(0x55)
        rsp = self.write_cmd(cmd.to_message())
        rsp = SearchDeviceResponse.from_message(rsp)
        print(f"Device SDK version {rsp.major_ver}.{rsp.minor_ver}")

    def save_data(self, file: typing.IO):
        save_data = {}
        cmd = CurrentProgramDataDumpRequest()
        rsp = self.write_cmd(cmd.to_message())
        save_data["CurrentProgramDataDump"] = str(rsp)
        rsp = CurrentProgramDataDump.from_message(rsp)
        print(rsp)
        save_data["description"] = str(rsp)

        cmd = GlobalDataDumpRequest()
        rsp = self.write_cmd(cmd.to_message())
        save_data["GlobalDataDump"] = str(rsp)
        rsp = GlobalDataDump.from_message(rsp)

        json.dump(save_data, file)

    def load_data(self, file: typing.IO):
        load_data = json.load(file)
        print(load_data["description"])
        cmd = CurrentProgramDataDump.from_message(
            mido.parse_string(load_data["CurrentProgramDataDump"])
        )
        rsp = self.write_cmd(cmd.to_message())
        rsp = SystemExclusiveMessage.from_message(rsp)
        if not isinstance(rsp, StatusOperationCompleted):
            print(f"An error occurred - {type(rsp)}")
            return

        cmd = GlobalDataDump.from_message(
            mido.parse_string(load_data["GlobalDataDump"])
        )
        rsp = self.write_cmd(cmd.to_message())
        rsp = SystemExclusiveMessage.from_message(rsp)
        if not isinstance(rsp, StatusOperationCompleted):
            print(f"An error occurred - {type(rsp)}")
            return


class NTS1Mk2(SDK2):
    """
    Supports interacting with the nts-1 mk2 logue device.
    """

    def __init__(self, ioport, channel=1):
        super().__init__(ioport=ioport, channel=1)
