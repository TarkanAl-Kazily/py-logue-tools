# Copyright 2024 Tarkan Al-Kazily

import logue
import unittest


class TestLogueUtils(unittest.TestCase):
    def test_host_to_midi_case1(self):
        # 7 host bytes -> 8 midi bytes, simple case
        host_data = [0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6]
        midi_data = [0x0, 0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6]
        self.assertEqual(midi_data, logue.host_to_midi(host_data))

        self.assertEqual(host_data, logue.midi_to_host(midi_data))

    def test_host_to_midi_case2(self):
        # 7 host bytes -> 8 midi bytes, all bits set
        host_data = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        midi_data = [0x7F, 0x7F, 0x7F, 0x7F, 0x7F, 0x7F, 0x7F, 0x7F]
        self.assertEqual(midi_data, logue.host_to_midi(host_data))

        self.assertEqual(host_data, logue.midi_to_host(midi_data))

    def test_host_to_midi_case3(self):
        # 4 host bytes -> 5 midi bytes, all bits set but leading 3
        host_data = [0xFF, 0xFF, 0xFF, 0xFF]
        midi_data = [0x0F, 0x7F, 0x7F, 0x7F, 0x7F]
        self.assertEqual(midi_data, logue.host_to_midi(host_data))

        self.assertEqual(host_data, logue.midi_to_host(midi_data))

    def test_host_to_midi_case_null(self):
        # 0 host bytes -> 0 midi bytes
        host_data = []
        midi_data = []
        self.assertEqual(midi_data, logue.host_to_midi(host_data))

        self.assertEqual(host_data, logue.midi_to_host(midi_data))
