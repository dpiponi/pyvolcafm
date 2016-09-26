"""Class representing one voice on Yamaha DX7 or Korg Volca FM"""

import notes
from operator import *

class Voice:
    def __init__(self):
        # Default voice according to DX7
        self.operators = [Operator() for i in xrange(5, -1, -1)]
        self.operators[0].olvl = 99
        self.algo = 0
        self.fdbk = 0
        self.lfow = 0 # Triangle
        self.lfor = 35
        self.lfod = 0
        self.lpmd = 0
        self.lamd = 0
        self.lfok = 1
        self.msp = 3
        self.oks = 1
        self.ptr = [99, 99, 99, 99]
        self.ptl = [50, 50, 50, 50]
        self.trsp = notes.C3-notes.C1
        self.name = 'INIT VOICE'
        pass

    @classmethod
    def random(cls):
        voice = Voice()
        # unfinished
        voice.operators = [Operator.random() for i in xrange(0, 6)]
        return voice

    @classmethod
    def from_packed_stream(cls, strm):
        voice = Voice()
        # print "Starting a voice"
        voice.operators = [Operator.from_packed_stream(strm)
                           for i in xrange(6)]
        voice.operators.reverse()
        voice.ptr = [strm.next() for i in xrange(4)]
        voice.ptl = [strm.next() for i in xrange(4)]
        # print "Reading algo"
        voice.algo = strm.next()
        packed_data = strm.next()
        voice.fdbk = packed_data & 0x7
        voice.oks = (packed_data >> 3) & 0x1
        voice.lfor = strm.next()
        voice.lfod = strm.next()
        voice.lpmd = strm.next() # I think
        voice.lamd = strm.next()
        packed_data = strm.next()
        voice.lfok = packed_data & 0x1
        voice.lfow = (packed_data >> 1) & 0x7
        voice.msp = (packed_data >> 4) & 0x7
        voice.trsp = strm.next()
        bytes = [strm.next() for i in xrange(10)]
        chars = [chr(i) for i in bytes]
        voice.name = str("".join(chars))

        return voice

    def to_packed_stream(self):
        for i in xrange(5, -1, -1):
            for b in self.operators[i].to_packed_stream():
                yield b

        for r in self.ptr:
            yield r
        for l in self.ptl:
            yield l

        yield self.algo
        yield self.fdbk | self.oks << 3 # Top bits may be set?
        for attr in ['lfor', 'lfod', 'lpmd', 'lamd']:
            yield getattr(self, attr)
        yield self.lfok | self.lfow << 1 | self.msp << 4
        yield self.trsp

        for i in self.name:
            yield ord(i)
        for i in xrange(10-len(self.name)):
            yield 32

    def dump(self):
        print "========================"
        print "Voice:", self.name
        for i in range(6):
            print "+------------------------------"
            print "Operator", i
            self.operators[i].dump()
            print "+------------------------------"
        for attr in ['ptr', 'ptl', 'fdbk', 'oks',
                     'lfod', 'lamd', 'lfok', 'lfow',
                     'msp', 'trsp', 'lfor', 'lpmd',
                     'algo']:
            print attr, "=", getattr(self, attr)
        print "========================"

        def __eq__(self, other):
            return self.__dict__ == other.__dict__

# Untested
def voice_from_stream(strm):
    voice = Voice()
    # print "Starting a voice"
    voice.operators = [operator_from_stream(strm)
                       for i in xrange(6)]
    voice.operators.reverse()
    voice.ptr = [strm.next() for i in xrange(4)]
    voice.ptl = [strm.next() for i in xrange(4)]
    voice.algo = strm.next()
    voice.fdbk = strm.next()
    voice.oks = strm.next()
    for attr in ['algo', 'fdbk', 'oks', 'lfospeed',
                 'lfod', 'lfopitchmoddepth', 'lamd', 'lfok',
                 'lfow', 'msp', 'trsp']:
        setattr(voice, attr, strm.next())
    # print "Reading name"
    voice.name = str("".join([chr(strm.next())
                              for i in xrange(10)]))
    ons = strm.next()
    voice.on = [1 if (ons & 1<<i) else 0 for i in range(6)]
    return voice
