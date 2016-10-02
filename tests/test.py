import tempfile
import mido
import os
import filecmp
from nose.tools import *

from pyvolcafm import *
from pyvolcafm.notes import *
from pyvolcafm.operator import *

def test():
    assert True

TEST_DATA = 'data/rom1a.syx'
def test_1():
    messages = mido.read_syx_file(TEST_DATA)
    for message in messages:
        gen = iter(message.data)
        voices = bank_from_packed_stream(gen)

# Read in a bunch of sysexes.
# Convert back to stream.
# Compare stream for equality with original.
# Removed some examples because there are badly formed sysex files out there.
def test_2():
    files = os.listdir('data')
    files.remove('rom3a.syx')
    files.remove('rom3b.syx')
    for file in files:
        print file
        data = read_sysex_file('data/'+file)
        gen = iter(data)
        voices = bank_from_packed_stream(gen)
        stream = tuple(packed_stream_from_bank(voices))
        assert stream == data

def test_3():
        messages = mido.read_syx_file(TEST_DATA)
        for message in messages:
            gen = iter(message.data)
            voices = bank_from_packed_stream(gen)
        op1 = voices[0].operators[0]
        s = op1.to_packed_stream()
        op2 = Operator.from_packed_stream(iter(s))

        print op1 == op2

        voice1 = voices[0]
        s = voice1.to_packed_stream()
        voice2 = Voice.from_packed_stream(iter(s))
        print voice1 == voice2

        voice = Voice()

# Test round trip
# File -> bank of 32 voices -> file
def test_4():
    data = iter(read_sysex_file(TEST_DATA))
    voices = bank_from_packed_stream(data)
    name = tempfile.mkdtemp()
    temp_file_name = os.path.join(name, 'test.syx')
    write_sysex_file(temp_file_name, packed_stream_from_bank(voices))
    assert filecmp.cmp(TEST_DATA, temp_file_name)
    os.remove(temp_file_name)
    os.rmdir(name)

@raises(OutOfRangeError)
def test_5():
    voice = Voice()
    voice.operators[0].egr[0] = 100
    voice.test_integrity()
