import mido
import pyvolcafm
import os
from pyvolcafm import notes

def test():
    assert True

TEST_DATA = 'data/b1.syx'
def test_1():
    messages = mido.read_syx_file(TEST_DATA)
    for message in messages:
        strm = iter(message.data)
        voices = pyvolcafm.bank_from_packed_stream(strm)

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
        data = pyvolcafm.read_sysex_file('data/'+file)
        strm = iter(data)
        voices = pyvolcafm.bank_from_packed_stream(strm)
        stream = tuple(pyvolcafm.packed_stream_from_bank(voices))
        for i in xrange(len(stream)):
            if stream[i] != data[i]:
                print ">>", i, ':', stream[i], data[i]#, unichr(stream[i]), unichr(message.data[i])
        assert type(stream) == type(data)
        assert stream == data

def test_3():
        messages = mido.read_syx_file(TEST_DATA)
        for message in messages:
            strm = iter(message.data)
            voices = pyvolcafm.bank_from_packed_stream(strm)
        op1 = voices[0].operators[0]
        s = pyvolcafm.packed_stream_from_operator(op1)
        op2 = pyvolcafm.operator_from_packed_stream(iter(s))

        # pyvolcafm.dump_operator(op1)
        # pyvolcafm.dump_operator(op2)
        print op1 == op2

        voice1 = voices[0]
        # pyvolcafm.dump_voice(voice1)
        s = pyvolcafm.packed_stream_from_voice(voice1)
        voice2 = pyvolcafm.voice_from_packed_stream(iter(s))
        # pyvolcafm.dump_voice(voice2)
        print voice1 == voice2

        voice = pyvolcafm.Voice()
        # pyvolcafm.dump_voice(voice)
