# Project Design

The project will be implemented in Python as an accessible language that has existing support for
interacting with MIDI and files.

## Outline

* A `logue` device will be present on a connected midi port with a preset channel. This will be the
  `LogueTarget`
* Communication with the `LogueTarget` must be bidirectional, so the input and output port for the
target will be combined together into one IOPort where messages will be sent and then we wait for
its response.
* Different kinds of `logue` devices have different MIDI implementations. Sub-classing the main
`LogueTarget` will support specifying these device differences. The type of attached devices will be
detected through a query operation.
