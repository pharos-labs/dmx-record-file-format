DMX Recording File Format
#########################

This documentation describes the file format for `DMX Recording Files <https://www.pharoscontrols.com/designer/software/dmx-record/>`_ from `Pharos Controls <https://www.pharoscontrols.com/>`_.

If you are a user of the Pharos system and wish to create or import DMX recordings, you do not need to read this documentation - you can simply use the `DMX recording application <https://www.pharoscontrols.com/designer/software/dmx-record/>`_.

This documentation is intended for third party developers who wish to generate a DMX recording file for import into Pharos Designer directly from their products.

DMX Recording Files
===================

DMX recording files contain between one and sixteen universes of DMX data recorded over time. These recordings can be imported into Pharos Designer for playback from a Pharos controller.

DMX recording files are a binary format and have a file extension of .PDREC

Overall File Format
===================

The file consists of tarred gzip data prefixed by a file header

File Header
===========

The file starts with a header which has a length of 22 bytes. The content of the header is as follows:

.. list-table:: File Header
   :widths: 15 15 15 55
   :header-rows: 1

   * - Field
     - Length (Bytes)
     - Expected Content
     - Notes
   * - Identifier
     - 4
     - ``Cage``
     - Magic header to identify file type
   * - Version
     - 2
     - ``0`` (16 bit unsigned integer)
     - File version number. Currently only version 0 is supported
   * - UUID
     - 16
     - UUID encoded according to RFC 4122
     - A Unique Identifier for the file

File Body
=========

The body of the file is a gzip compressed TAR file which can be written or read with standard utilities and libraries for your platform.

The contents of the body might look something like this for a recording containing 4 universes of data::

    Root of tar file
    ├── recording
    │ ├── 0
    │ ├── 1
    │ ├── 2
    │ └── 3
    └── metadata

The body contains a directory called "recording" which contains a file for each universe. The files have numbers for titles, where the number corresponds to universe number as described below.

The body also contains a metadata file, which is JSON-encoded data about the recording.


Metadata File
=============

The Metadata file contains information about the recording. A typical example might look like this:

.. code-block:: json

    {
        "description": "Example DMX Recording",
        "duration": 10000,
        "name": "ExampleRecording",
        "protocol": "sACN",
        "start_timestamp": 1711400171,
        "universes": [
            {
                "frame_rate": 50,
                "number": 0
            }
        ]
    }

The JSON contains the following fields:


.. list-table:: Metadata
   :widths: 20 80
   :header-rows: 1

   * - Field
     - Notes
   * - ``description``
     - A text description of the file - can be multiline
   * - ``duration``
     - The total length of the recording, in milliseconds
   * - ``protocol``
     - The protocol used for the recording, ``sACN`` or ``Artnet``
   * - ``start_timestamp``
     - The time at which the recording was started, as a Unix Epoch start_timestamp
   * - ``universes``
     - An array of universes - each universe must specify a ``frame_rate`` and a ``number``
   * - ``frame_rate``
     - The rate at which the universe data should be played back. Supported rates are up to 50 frames per second
   * - ``number``
     - The universe number - see below

Universes are numbered depending on the protocol type:

For sACN, they are the sACN universe number minus one. So for example sACN universe 1 is shown as universe 0, universe 38 would be numbered 37.

For Art-Net, the Art-Net Net, Subnet and Universe values are combined to a single number combined as::

  Net << 8 | Subnet << 4 | Universe

So for example, Net 1, subnet 3, universe 4 would be 308.

Universe Data File
==================

The universe data files contain the actual timed DMX data for output.

The universe file has a format broken across two lines: The first line includes an ascending timestamp in nanoseconds, the second line includes the DMX data encoded in hexadecimal format.

An example pair might look like::

    60000000
    afafafafafafafafafafafafafafafafafafafafafafafafafafafafafafafafafafaf[...]

In this example, the timestamp is 60000000 nanoseconds (that is, 0.06 seconds through the capture), and the DMX levels are all at level 0xaf, that is 175.

If say DMX address 3 was at 255 and all other channels were at zero, it might look like::

    60000000
    0000FF0000000000000000000000000000000000000000000000000000000000000000[...]

Example Code
============

In order to assist with interpreting the format, a some examples of reading and writing DMX recording files have been prepared. You can find those at the links below.

These examples are written in Python. To use them, you will need a 3.x version of Python available from https://www.python.org/

Creating a Recording
--------------------

You can find this example here :
:download:`Create Recording <_static/examples/create-recording.py>`

This sample will create a DMX recording file. When you run it you are prompted for some information about the recording, and it will generate a recording file in the directory you run it in.

A sample run might look like::

  > python create-recording.py
  Creating a Sinewave DMX Recording File
  Enter recording description: My sample Sinewave
  Enter recording name: Sine
  Enter number of Universes: 3
  Enter recording length, in seconds: 60
  Enter sinewave frequency, in Hz: 1
  Creating Universe 1
  Creating Universe 2
  Creating Universe 3
  Saved archive to generated_recording_1720526422.pdrec


Reading a Recording
-------------------

You can find this example here:
:download:`Read Recording <_static/examples/read-recording.py>`

This sample will read a DMX recording file. It takes the file as a command line argument, so you might for example enter::

  python.exe read_recording.py my_example_file.pdrec

It will output the metadata and information about the data encoded in the file::

  > python read-recording.py generated_recording_1720531694.pdrec
  File UUID is 36dcb2c4-3611-db90-f94d-6c0d704587c2
  Description: My sample Sinewave
  Duration: 60000 milliseconds
  Name: Sine
  Protocol: sACN
  Recording started at: 2024-07-09 14:28:14
  Contains 3 universes
