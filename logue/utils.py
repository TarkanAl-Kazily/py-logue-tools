# Copyright 2024 Tarkan Al-Kazily


def host_to_midi(data: bytes) -> bytes:
    """
    Convert host formatted 8-bit data to Korg's midi 7-bit data format

    NOTE 1: 7 bit data format conversion

      DATA ( 1Set = 8bit x 7Byte )
      b7     ~      b0   b7     ~      b0   b7   ~~    b0   b7     ~      b0
      +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+  +-+-+-~~-+-+-+  +-+-+-+-+-+-+-+-+
      | | | | | | | | |  | | | | | | | | |  | | |    | | |  | | | | | | | | |
      +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+  +-+-+-~~-+-+-+  +-+-+-+-+-+-+-+-+
            7n+0               7n+1          7n+2 ~~ 7n+5         7n+6

       MIDI DATA ( 1Set = 7bit x 8Byte )
         b7b7b7b7b7b7b7     b6    ~     b0     b6 ~~    b0     b6    ~     b0
      +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+  +-+-+-~~-+-+-+  +-+-+-+-+-+-+-+-+
      |0| | | | | | | |  |0| | | | | | | |  |0| |    | | |  |0| | | | | | | |
      +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+  +-+-+-~~-+-+-+  +-+-+-+-+-+-+-+-+
      7n+6,5,4,3,2,1,0         7n+0          7n+1 ~~ 7n+5         7n+6

    Args:
        data: host data

    Returns:
        bytes in range 0-127 suitable for sending over MIDI
    """
    raise NotImplementedException()


def midi_to_host(data: bytes) -> bytes:
    """
    Convert Kogs's midi 7-bit data format to host formatted 8-bit data

    NOTE 1: 7 bit data format conversion

      DATA ( 1Set = 8bit x 7Byte )
      b7     ~      b0   b7     ~      b0   b7   ~~    b0   b7     ~      b0
      +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+  +-+-+-~~-+-+-+  +-+-+-+-+-+-+-+-+
      | | | | | | | | |  | | | | | | | | |  | | |    | | |  | | | | | | | | |
      +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+  +-+-+-~~-+-+-+  +-+-+-+-+-+-+-+-+
            7n+0               7n+1          7n+2 ~~ 7n+5         7n+6

       MIDI DATA ( 1Set = 7bit x 8Byte )
         b7b7b7b7b7b7b7     b6    ~     b0     b6 ~~    b0     b6    ~     b0
      +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+  +-+-+-~~-+-+-+  +-+-+-+-+-+-+-+-+
      |0| | | | | | | |  |0| | | | | | | |  |0| |    | | |  |0| | | | | | | |
      +-+-+-+-+-+-+-+-+  +-+-+-+-+-+-+-+-+  +-+-+-~~-+-+-+  +-+-+-+-+-+-+-+-+
      7n+6,5,4,3,2,1,0         7n+0          7n+1 ~~ 7n+5         7n+6

    Args:
        data: 0-127 midi data

    Returns:
        8-bit host data
    """
    raise NotImplementedException()
