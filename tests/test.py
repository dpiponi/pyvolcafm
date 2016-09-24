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
    #files = os.listdir('data')
    files = ['bank0009.syx']
    for file in files:
        messages = mido.read_syx_file('data/'+file)
        print file
        for message in messages:
            strm = iter(message.data)
            voices = pyvolcafm.bank_from_packed_stream(strm)
        stream = tuple(pyvolcafm.packed_stream_from_bank(voices))
#    for i in xrange(len(stream)):
#        if stream[i] != message.data[i]:
#            print ">>", i, ':', stream[i], message.data[i], unichr(stream[i]), unichr(message.data[i])
        assert type(stream) == type(message.data)
        assert stream == message.data

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
