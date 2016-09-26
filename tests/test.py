import tempfile
import mido
import os
import filecmp

from pyvolcafm import *
from pyvolcafm.notes import *
from pyvolcafm.operator import *

def test():
    assert True

TEST_DATA = 'data/b1.syx'
def test_1():
    messages = mido.read_syx_file(TEST_DATA)
    for message in messages:
        strm = iter(message.data)
        voices = bank_from_packed_stream(strm)

# Read in a bunch of sysexes.
# Convert back to stream.
# Compare stream for equality with original.
# Removed some examples because there are badly formed sysex files out there.
def test_2():
    files = os.listdir('data')
    files.remove('bank0009.syx')
    files.remove('bank0043.syx')
    files.remove('bank0054.syx')
    files.remove('guitar1.syx')
    files.remove('mark.syx')
    files.remove('rm0001.syx')
    files.remove('road1.syx')
    files.remove('road2.syx')
    files.remove('rom3a.syx')
    files.remove('rom3b.syx')
    files.remove('sjsu-f.syx')
    files.remove('splitsbn.syx')
    files.remove('steph2.syx')
    files.remove('steph4.syx')
    files.remove('steve1.syx')
    files.remove('steph3.syx')
    files.remove('string1.syx')
    files.remove('strings.syx')
    files.remove('syn_plus.syx')
    files.remove('synplus.syx')
    files.remove('xylos.syx')
    files.remove('yamaha.syx')
    files.remove('zone3.syx')
    #files = ['bank0009.syx']
    #files = ['bank0009.syx']
    #files = ['bank0043.syx']
    #files = ['guitar1.syx']
    for file in files:
        print file
        data = read_sysex_file('data/'+file)
        strm = iter(data)
        voices = bank_from_packed_stream(strm)
        stream = tuple(packed_stream_from_bank(voices))
        for i in xrange(len(stream)):
            if stream[i] != data[i]:
                print ">>", i, ':', stream[i], data[i]#, unichr(stream[i]), unichr(message.data[i])
        assert type(stream) == type(data)
        assert stream == data

def test_3():
        messages = mido.read_syx_file(TEST_DATA)
        for message in messages:
            strm = iter(message.data)
            voices = bank_from_packed_stream(strm)
        op1 = voices[0].operators[0]
        s = op1.to_packed_stream()
        op2 = Operator.from_packed_stream(iter(s))

        # dump_operator(op1)
        # dump_operator(op2)
        print op1 == op2

        voice1 = voices[0]
        # dump_voice(voice1)
        s = voice1.to_packed_stream()
        voice2 = Voice.from_packed_stream(iter(s))
        # dump_voice(voice2)
        print voice1 == voice2

        voice = Voice()
        # dump_voice(voice)

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
