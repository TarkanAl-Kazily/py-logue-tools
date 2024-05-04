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
    parser.add_argument("--port", "-p", type=int, help="Port index")
    parser.add_argument("--type", "-t", type=str, help="Device type to connect to")

    subparsers = parser.add_subparsers(title="subcommands")
    probe_parser = subparsers.add_parser(
        "probe", description="Query loaded logue programs"
    )

    return parser.parse_args()


def main(args):
    # Get connected devices
    utils.midi.get_midi_ports(verbose=args.l)

    if not hasattr(args, "port"):
        return

    midi_ioport = utils.midi.get_inout_port(args.port)
    if midi_ioport is None:
        return

    print(f"Opened midi_ioport {midi_ioport}")


if __name__ == "__main__":
    main(parse_args())
