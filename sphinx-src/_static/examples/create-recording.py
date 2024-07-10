#!/usr/bin/env python
"""\
Creates a DMX Recording file based on user input

MIT License

Copyright (c) 2024 Pharos Controls

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import math
import json
import tempfile
import os
import datetime
import tarfile
import uuid

# Create a DMX recording component file with sinewave data
# Fixed sample rate of 50Hz
# filename - the filename to use
# length - the total length of the recording (seconds)
# freq - the frequency of the sinewave in Hz
def create_sine_file(filepath, length, freq):
    sampleCount = 50 * length

    with open(filepath, 'w') as file:
        for sample in range(sampleCount):
            time = sample / 50 # Timestamp in seconds
            angle = time * math.pi * 2 * freq
            value = math.floor(128 + math.sin(angle) * 128)

            file.write(f'{math.floor(time * (10**9))}') # Timestamp as nanoseconds
            file.write('\n')
            for i in range(512): # Write out 512 addresses
                file.write(f'{value:02x}')
            file.write('\n')

# Create a DMX recording metadata file
def create_metadata_file(filepath, metadata):
    data = json.dumps(metadata, indent=4)
    with open(filepath, 'w') as file:
        file.write(data)

# Write the DMX recording header to an output file
def write_recording_header(outputFile):
    outputFile.write(b'Cage') # Magic header for DMX recordings
    outputFile.write(b'\0\0') # Version number, currently 0
    fileUuid = uuid.uuid4()
    outputFile.write(fileUuid.bytes)


def main():
    print("Creating a Sinewave DMX Recording File")
    description = input("Enter recording description: ")
    protocol = 'sACN' # Default to sACN, can be sACN or ArtNet
    universes = int(input("Enter number of Universes: "))
    length = int(input("Enter recording length, in seconds: "))
    frequency = int(input("Enter sinewave frequency, in Hz: "))

    timestamp = math.floor(datetime.datetime.now().timestamp())
    outputFileName = f'generated_recording_{timestamp}.pdrec'

    with tempfile.TemporaryDirectory() as tempDirPath:
        os.mkdir(os.path.join(tempDirPath, 'recording'))

        metadata = {}
        metadata['description'] = description
        metadata['duration'] = math.floor(length * 1000) # Duration in millisec
        metadata['protocol'] = protocol
        metadata['start_timestamp'] = timestamp # Epoch timestamp
        metadata['universes'] = []

        for universe in range(universes):
            print(f'Creating Universe {universe+1}')
            create_sine_file(os.path.join(tempDirPath, 'recording', f'{universe}'), length, frequency)
            metadata['universes'].append({'frame_rate': 50, 'number': universe})

        create_metadata_file(os.path.join(tempDirPath, 'metadata'), metadata)

        with tempfile.TemporaryFile(suffix='.tar.gz') as f:
            with tarfile.open(fileobj=f, mode='w:gz') as tar:
                tar.add(tempDirPath, arcname=os.path.sep)

            f.flush()
            f.seek(0)

            with open(outputFileName, 'wb') as outputFile:
                write_recording_header(outputFile)
                outputFile.write(f.read())

        print(f'Saved archive to {outputFileName}')

if __name__ == "__main__":
    main()