#!/usr/bin/python3
# Copyright 2024 Tarkan Al-Kazily

import argparse
import utils.midi
import logue
import sys


def parse_args():
    """
    Returns:
    - args context parsed from the CLI
    """
    parser = argparse.ArgumentParser(description="Interact with logue devices")
    parser.add_argument("-l", action="store_true", help="List connected devices")
    parser.add_argument("--port", "-p", type=int, help="Port index")
    parser.add_argument(
        "--type",
        "-t",
        choices=logue.get_logue_target_types(),
        help="Device type to connect to",
    )

    subparsers = parser.add_subparsers(title="subcommands")
    probe_parser = subparsers.add_parser(
        "probe", description="Query loaded logue programs"
    )

    return parser.parse_args()


def main(args) -> int:
    # Get connected devices
    utils.midi.get_midi_ports(verbose=args.l)

    if args.port is None:
        return 0

    if args.type is None:
        print("type must be provided")
        return -1

    midi_ioport = utils.midi.get_inout_port(args.port)
    if midi_ioport is None:
        return -1

    target_instance = getattr(logue, args.type)(midi_ioport)

    target_instance.inquiry()


if __name__ == "__main__":
    sys.exit(main(parse_args()))
