# Python tools for working with the Logue-SDK and devices

The `logue-sdk` from Korg is a cool way to get into DSP programming and building custom effects.
It's part of a line of synthesizers and effects modules that are hackable and sound great, but their
host tools to interact with the devices seem to be lacking in open source and bug fixes.

Fortunately, they adequately publish MIDI implementations for their devices, which includes the
programming and device interaction functions that their primary tool `logue-cli` normally would do.

This repository is experimentation in implementing a custom version of the `logue-cli` tool's
functionality based on these MIDI implementation specifications.

## Lint and Tests

Linting is enforced by the Python Black linter (through git pre-commit hooks).

Manually run the linter:
```
pre-commit run --all-files
```

Tests are implemented with Python's unittest framework. Manually run all tests:
```
python -m unittest discover tests/
```


## Links

* [logue-sdk repo](https://github.com/korginc/logue-sdk)
* [NTS-1 Mk1 MIDI implementation](https://www.korg.com/us/support/download/manual/0/832/4831/)
* [NTS-1 Mk2 MIDI implementation](https://www.korg.com/us/support/download/manual/0/933/5210/)

## Tool goals

The objective of this work will be to implement useful functions for interacting with `logue`
devices.

* `save` will save active settings or presets to a file.
* `load` will restore settings or presets from a file.
* `download` will install a user module to a slot.
