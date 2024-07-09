#!/usr/bin/env python
"""\
Reads a DMX recording file (specify file as command line argument)

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

import tarfile
import tempfile
import uuid
import sys
import os
import json
from time import strftime, localtime

if len(sys.argv) < 2:
    print('Syntax : python read-recording.py <Path to DMX recording file>')
    exit(-1)

recordingFilePath = sys.argv[1]


with open(recordingFilePath, 'rb') as pdRecFile:
    with tempfile.TemporaryDirectory() as tempDir:

        # Magic header should be "Cage"
        if pdRecFile.read(4) != b'Cage':
            raise Exception('Invalid Recording File')

        if pdRecFile.read(2) != b'\0\0':
            raise Exception('Only version 0 recording files are handled')

        uuidData = pdRecFile.read(16)
        uuidVal = uuid.UUID(int=int.from_bytes(uuidData, 'little'))

        print(f'File UUID is {uuidVal}')

        with open(os.path.join(tempDir, 'recording.tgz'), 'wb') as tempFile:
            tempFile.write(pdRecFile.read())
            tempFile.close()

        try:
            tar = tarfile.open(os.path.join(tempDir, 'recording.tgz'))
            tar.extractall(tempDir)
            tar.close()

            with open(os.path.join(tempDir, 'metadata')) as metaDataFile:
                metadata = json.load(metaDataFile)
                print(f'Description: {metadata['description']}')
                print(f'Duration: {metadata['duration']} milliseconds')
                print(f'Name: {metadata['name']}')
                print(f'Protocol: {metadata['protocol']}')
                print(f'Recording started at: {strftime('%Y-%m-%d %H:%M:%S', localtime(metadata['start_timestamp']))}')

                universeCount = len(metadata['universes'])
                print(f'Contains {universeCount} universes')

        except:
            print(f'Invalid DMX Recording File')
