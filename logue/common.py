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
