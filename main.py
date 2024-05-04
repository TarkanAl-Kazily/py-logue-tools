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
    parser.add_argument("-i", type=int, help="Input port index")
    parser.add_argument("-o", type=int, help="Output port index")

    subparsers = parser.add_subparsers(title="subcommands")
    probe_parser = subparsers.add_parser(
        "probe", description="Query loaded logue programs"
    )

    return parser.parse_args()


def main(args):
    # List connected devices
    inputs, outputs = utils.midi.get_midi_ports(verbose=args.l)


if __name__ == "__main__":
    main(parse_args())
