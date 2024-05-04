#!/usr/bin/python3
# Copyright 2024 Tarkan Al-Kazily

import argparse
import utils.midi


def parse_args():
    """
    Returns:
    - args context parsed from the CLI
    """
    parser = argparse.ArgumentParser(description="Interact with logue devices")
    parser.add_argument("-l", action="store_true", help="List connected devices")

    subparsers = parser.add_subparsers(title="subcommands")
    probe_parser = subparsers.add_parser(
        "probe", description="Query loaded logue programs"
    )

    return parser.parse_args()


def main(args):
    if args.l:
        # List connected devices
        utils.midi.get_midi_ports()


if __name__ == "__main__":
    main(parse_args())
