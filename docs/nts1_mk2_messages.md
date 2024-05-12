# NTS-1 mkII MIDI messages notes

All important messages are MIDI sysex type messages (beginning with 0xf0)

Categories:
1. Universal Sysex (Device Inquiry)
- DEVICE INQUIRY MESSAGE REQUEST
- DEVICE INQUIRY REPLY

2. System Exclusive (KORG Logue Messages)
All begin with common header, followed by id value, followed by message specific data payload.
+-------------+-------------------------------------+------+
|     40      | CURRENT PROGRAM DATA DUMP           | R    |
|     51      | GLOBAL DATA DUMP                    | R    |
|             |                                     |      |
|     47      | USER API VERSION                    | R    |
|     48      | USER MODULE INFO                    | R    |
|     49      | USER SLOT STATUS                    | R    |
|     4A      | USER SLOT DATA                      | R    |
|             |                                     |      |
|     7E      | CURRENT PROGRAM CHANGED             | C    |
|             |                                     |      |
|    23-2F    | STATUS (ACK/NAK)                    | E    |
+-------------+-------------------------------------+------+

+-------------+-------------------------------------+------+
|     10      | CURRENT PROGRAM DATA DUMP REQUEST          |
|     0E      | GLOBAL DATA DUMP REQUEST                   |
|             |                                            |
|     40      | ^^CURRENT PROGRAM DATA DUMP                |
|     51      | ^^GLOBAL DATA DUMP                         |
|             |                                            |
|     17      | USER API VERSION REQUEST                   |
|     18      | USER MODULE INFO REQUEST                   |
|     19      | USER SLOT STATUS REQUEST                   |
|     1A      | USER SLOT DATA REQUEST                     |
|     1B      | CLEAR USER SLOT                            |
|     1D      | CLEAR USER MODULE                          |
|     1E      | SWAP USER DATA                             |
|             |                                            |
|     47      | ^^USER API VERSION                         |
|     48      | ^^USER MODULE INFO                         |
|     49      | ^^USER SLOT STATUS                         |
|     4A      | ^^USER SLOT DATA                           |
+-------------+-------------------------------------+------+

3. Search Device
- SEARCH DEVICE REQUEST
- SEARCH DEVICE REPLY

## Receivable
* 2-3 UNIVERSAL SYSTEM EXCLUSIVE MESSAGE ( NON REALTIME ) DEVICE INQUIRY MESSAGE REQUEST
* 2-4 SYSTEM EXCLUSIVE MESSAGE
* 2-5 SEARCH DEVICE REQUEST
* (1) CURRENT PROGRAM DATA DUMP REQUEST
* (2) GLOBAL DATA DUMP REQUEST
* (3) CURRENT PROGRAM DATA DUMP
* (4) GLOBAL DATA DUMP
* (5) USER API VERSION REQUEST
* (6) USER MODULE INFO REQUEST
* (7) USER SLOT STATUS REQUEST
* (8) USER SLOT DATA REQUEST
* (9) CLEAR USER SLOT
* (10) CLEAR USER MODULE
* (11) SWAP USER DATA
* (14) USER SLOT STATUS
* (15) USER SLOT DATA

## Transmittable
* 1-3 UNIVERSAL SYSTEM EXCLUSIVE MESSAGES DEVICE INQUIRY REPLY
* 1-4 SYSTEM EXCLUSIVE MESSAGES
* 1-5 SEARCH DEVICE REPLY
* (3) CURRENT PROGRAM DATA DUMP
* (4) GLOBAL DATA DUMP
* (12) USER API VERSION
* (13) USER MODULE INFO
* (14) USER SLOT STATUS
* (15) USER SLOT DATA
* (16) STATUS (ACK/NAK)


---

# (15) USER SLOT DATA                                              R/T
From the docs:
```
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

 When this message is received, the data is saved to the specified
 module's slot, then then STATUS is transmitted (see NOTE 2).

 This message is transmitted after USER SLOT DATA REQUEST is received.
```

Believe it or not, this is not complete documentation.

Better documentation follows:
```
+----------------+--------------------------------------------------+
|     Byte       |             Description                          |
+----------------+--------------------------------------------------+
| F0,42,3g,      | EXCLUSIVE HEADER                                 |
|    00,01,73    |                                                  |
| 0100 1010 (4A) | USER SLOT DATA                         4AH       |
| 0ddd dddd (dd) | MODULE ID                                        |
| 0ddd dddd (dd) | SLOT NUMBER                                      |
| 0ddd dddd (dd) | SEQUENCE NUM                                     |
| 0000 0001 (01) | ? MAX SEQUENCE NUM ? <ONE IN EXPERIMENTS>        |
| 0ddd dddd (dd) |  :         Data Size         Conv. Size          |
| 0ddd dddd (dd) |  :     Variable (7bit) -> Variable (8bit)        |
|     :          |  :                                               |
| 1111 0111 (F7) | EOX                        (see NOTE 1, TABLE 5) |
+----------------+--------------------------------------------------+

THE TOTAL MESSAGE SIZE CANNOT EXCEED 4096 BYTES.

If the user data is too large, the message will be split over multiple packets.

Message contents are the contents of the .unit file directly (the ELF).
```
