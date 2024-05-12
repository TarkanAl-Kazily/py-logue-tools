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
    parser.add_argument(
        "--full-inquiry",
        action="store_true",
        help="Query and print additional device info on startup",
    )

    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")
    save_parser = subparsers.add_parser(
        "save",
        description="Save presets to a file",
    )
    save_parser.add_argument("--file", "-f", type=str, help="File to save to")
    load_parser = subparsers.add_parser(
        "load",
        description="Load presets from a file",
    )
    load_parser.add_argument("--file", "-f", type=str, help="File to load from")
    install_parser = subparsers.add_parser(
        "install",
        description="Install a program to a user slot",
    )
    install_parser.add_argument("--file", "-f", type=str, help="Module to install")
    install_parser.add_argument(
        "--module-type",
        "-m",
        choices=["osc", "modfx", "delfx", "revfx"],
        help="Type of program",
    )
    install_parser.add_argument("--slot", "-s", type=int, help="Slot to load in")
    fetch_parser = subparsers.add_parser(
        "fetch",
        description="Fetch a program from a user slot",
    )
    fetch_parser.add_argument(
        "--file", "-f", type=str, help="Where to save the module to"
    )
    fetch_parser.add_argument(
        "--module-type",
        "-m",
        choices=["osc", "modfx", "delfx", "revfx"],
        help="Type of program",
    )
    fetch_parser.add_argument("--slot", "-s", type=int, help="Slot to fetch from")
    clear_parser = subparsers.add_parser(
        "clear",
        description="Clear a user slot",
    )
    clear_parser.add_argument(
        "--module-type",
        "-m",
        choices=["osc", "modfx", "delfx", "revfx"],
        help="Type of program",
    )
    clear_parser.add_argument("--slot", "-s", type=int, help="Slot to clear")

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

    target_instance.inquiry(full_inquiry=args.full_inquiry)

    if args.subcommand == "save":
        with open(args.file, "w") as f:
            target_instance.save_data(f)

    if args.subcommand == "load":
        with open(args.file, "r") as f:
            target_instance.load_data(f)

    if args.subcommand == "install":
        target_instance.install_program(args.module_type, args.slot, args.file)

    if args.subcommand == "fetch":
        target_instance.fetch_program(args.module_type, args.slot, args.file)

    if args.subcommand == "clear":
        target_instance.clear_program(args.module_type, args.slot)

    return 0


if __name__ == "__main__":
    sys.exit(main(parse_args()))
