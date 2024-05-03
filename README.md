# Python tools for working with the Logue-SDK and devices

The `logue-sdk` from Korg is a cool way to get into DSP programming and building custom effects.
It's part of a line of synthesizers and effects modules that are hackable and sound great, but their
host tools to interact with the devices seem to be lacking in open source and bug fixes.

Fortunately, they adequately publish MIDI implementations for their devices, which includes the
programming and device interaction functions that their primary tool `logue-cli` normally would do.

This repository is experimentation in implementing a custom version of the `logue-cli` tool's
functionality based on these MIDI implementation specifications.

## Links

* [logue-sdk repo](https://github.com/korginc/logue-sdk)
* [NTS-1 Mk1 MIDI implementation](https://www.korg.com/us/support/download/manual/0/832/4831/)
* [NTS-1 Mk2 MIDI implementation](https://www.korg.com/us/support/download/manual/0/933/5210/)

## Tool goals

The objective of this work will be to create a tool initially matching the primary features of `logue-cli`, which are:
* `probe` connected devices to list their loaded programs
* `load` new units and presets
