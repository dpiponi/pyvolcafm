import sys
import mido
import nose
import itertools

import notes

# See https://github.com/rogerallen/dxsyx/blob/master/dx7-sysex-format.txt
# Also http://synthify.com/ChromaticArchive/MIDI/DX7-II-SYSEX.pdf

#def stream(data):
#    for i in xrange(len(data)):
#        b = data[i]
#        # print i, len(data), b, str(unichr(b))
#        yield b

class Voice:
    def __init__(self):
        # Default voice according to DX7
        self.operators = [Operator(i) for i in xrange(5, -1, -1)]
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
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

DOCUMENTED_NAMES = {
    'egr': 'Envelope Rates',
    'egl': 'Envelope Levels',
    'lsbp': 'Level Scale Break Point',
    'ams': 'Amp Modulation Sensitivity 0-3. Per operator.',
    'pms': 'Amp Modulation Sensitivity 0-7. Per operator.',
    'lamd': 'Amp Modulation Depth 0-99. Controls LFO amplitude modulation depth for all operators.',
    'lpmd': 'Amp Modulation Depth 0-99. Controls LFO pich modulation depth for all operators.',
    'lfor': 'LFO Rate 0-99. 0 => ~0.1 Hz. 99 => ~60 Hz.',
    'lfod': 'LFO Delay',
    'lfok': 'LFO Key Sync.',
}

_LIN = 0
_EXP = 1
EXP = 2
LIN = 3

class Operator:
    def __init__(self, i):
        # Default voice according to DX7
        self.ams = 0
        self.oscm = 0
        self.frec = 1
        self.fref = 0
        self.detu = 7 # I think 0 offset by 7
        self.egr = [99, 99, 99, 99]
        self.egl = [99, 99, 99, 0]
        self.lsbp = getattr(notes, 'A-1') # 39?
        self.lslc = _LIN
        self.lsrc = _LIN
        self.lsld = 0
        self.lsrd = 0
        if i==0:
            self.olvl = 99
        else:
            self.olvl = 0
        self.ors = 0 # ???
        self.kvs = 0
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

def operator_from_stream(strm):
    operator = Operator()
    operator.egr = [strm.next() for i in xrange(4)]
    operator.egl = [strm.next() for i in xrange(4)]
    for attr in ['lsbp', 'lsld', 'lsrd', 'lslc',
                 'lsrc', 'ors', 'ams', 'kvs',
                 'olvl', 'oscm', 'frec', 'fref',
                 'detu']:
        setattr(operator, attr, strm.next())

    return operator

# Reasonably tested
def operator_from_packed_stream(strm):
    operator = Operator(0)
    operator.egr = [strm.next() for i in xrange(4)]
    operator.egl = [strm.next() for i in xrange(4)]
    # print "Break data"
    for attr in ['lsbp', 'lsld', 'lsrd']:
        setattr(operator, attr, strm.next())
    packed_data = strm.next()
    operator.lslc = packed_data & 0x3
    operator.lsrc = (packed_data >> 2) & 0x3
    packed_data = strm.next()
    operator.ors = packed_data & 0x7
    operator.detu = (packed_data >> 3) & 0xf
    packed_data = strm.next()
    operator.ams = packed_data & 0x3
    operator.kvs = (packed_data >> 2) & 0x7
    # print "Reading olvl"
    operator.olvl = strm.next()
    packed_data = strm.next()
    operator.oscm = packed_data & 0x1
    operator.frec = (packed_data >> 1) & 0x1f
    operator.fref = strm.next()

    return operator

def packed_stream_from_operator(operator):
    for i in xrange(4):
        yield operator.egr[i]
    for i in xrange(4):
        yield operator.egl[i]
    for attr in ['lsbp', 'lsld', 'lsrd']:
        yield getattr(operator, attr)
    yield operator.lslc | operator.lsrc << 2
    yield operator.ors | operator.detu << 3
    yield operator.ams | operator.kvs << 2 # top bit may be set?
    yield operator.olvl
    yield operator.oscm | operator.frec << 1
    yield operator.fref

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
    voice.name = str("".join([unichr(strm.next())
                              for i in xrange(10)]))
    ons = strm.next()
    voice.on = [1 if (ons & 1<<i) else 0 for i in range(6)]
    return voice

# Reasonably tested
def voice_from_packed_stream(strm):
    voice = Voice()
    # print "Starting a voice"
    voice.operators = [operator_from_packed_stream(strm)
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
    chars = [unichr(i) for i in bytes]
    voice.name = str("".join(chars))

    return voice

def bank_from_packed_stream(strm):
    expect_byte(strm, 67, "Not Yamaha")
    expect_byte(strm, 0, "sub_status != 0")
    expect_byte(strm, 9, "Not 32 voice format")
    expect_byte(strm, 32, "Not MSB of 4096 bytes")
    expect_byte(strm, 0, "Not LSB of 4096 bytes")
    voices = []
    bytes = list(itertools.islice(strm, 0, 32*128))
    strm2 = iter(bytes)
    for i in xrange(32):
        voice = voice_from_packed_stream(strm2)
        voices.append(voice)
        # dump_voice(voice)
        # print "Voice", i, "read."
    # print "Data read"
    checksum = strm.next()
    print "checksum =", hex(checksum)
    s = -sum(bytes) & 0x7f
    print "actual sum =", hex(s)
    assert s == checksum
    return voices

def packed_stream_from_bank(voices):
    yield 67
    yield 0
    yield 9
    yield 32
    yield 0
    s = 0
    for i in xrange(32):
        voice_gen = packed_stream_from_voice(voices[i])
        for b in voice_gen:
            s += b
            yield b
    yield -s & 0x7f

def packed_stream_from_voice(voice):
    for i in xrange(5, -1, -1):
        for b in packed_stream_from_operator(voice.operators[i]):
            yield b

    for r in voice.ptr:
        yield r
    for l in voice.ptl:
        yield l

    yield voice.algo
    yield voice.fdbk | voice.oks << 3 # Top bits may be set?
    for attr in ['lfor', 'lfod', 'lpmd', 'lamd']:
        yield getattr(voice, attr)
    yield voice.lfok | voice.lfow << 1 | voice.msp << 4
    yield voice.trsp

    for i in voice.name:
        yield ord(i)
    for i in xrange(10-len(voice.name)):
        yield 32

def dump_operator(operator):
    for attr in ['egr', 'egl', 'lsbp', 'lsld',
                 'lsrd', 'lslc', 'lsrc', 'ors',
                 'ams', 'kvs', 'olvl', 'oscm',
                 'frec', 'fref', 'detu']:
        print attr, "=", getattr(operator, attr)

def dump_voice(voice):
    print "========================"
    print "Voice:", voice.name
    for i in range(6):
        print "+------------------------------"
        print "Operator", i
        dump_operator(voice.operators[i])
        print "+------------------------------"
    for attr in ['ptr', 'ptl', 'fdbk', 'oks',
                 'lfod', 'lamd', 'lfok', 'lfow',
                 'msp', 'trsp', 'lfor', 'lpmd',
                 'algo']:
        print attr, "=", getattr(voice, attr)
    print "========================"

def expect_byte(strm, b, e):
    n = strm.next()
    if n != b:
        print e
        sys.exit(1)

def parse_voice(stream):
    for i in xrange(128):
        strm.next()
