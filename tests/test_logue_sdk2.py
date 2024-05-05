# Copyright 2024 Tarkan Al-Kazily

import logue
import unittest
import json
import mido


class TestLogueSdk2(unittest.TestCase):
    def setUp(self):
        with open("tests/example_sdk2.json", "r") as f:
            self.example_messages = json.load(f)

    def test_current_program_data_dump(self):
        for msg in self.example_messages["CurrentProgramDataDump"]:
            mido_msg = mido.parse_string(msg)
            inst = logue.sdk2.CurrentProgramDataDump.from_message(mido_msg)
