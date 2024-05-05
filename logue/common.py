# Copyright 2024 Tarkan Al-Kazily

import logue.target


class InquiryRequest(logue.target.LogueMessage):
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
    def from_message(cls, message):
        channel = message.data[1] + 1
        return InquiryRequest(channel)


class SearchDeviceRequest(logue.target.LogueMessage):
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
        return SearchDeviceRequest(echo_id)
