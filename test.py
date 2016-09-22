import sys
import mido

# See https://github.com/rogerallen/dxsyx/blob/master/dx7-sysex-format.txt

def stream(data):
    for i in xrange(len(data)):
        b = data[i]
        # print i, len(data), b, str(unichr(b))
        yield b

class Voice:
    def __init__(self):
        # Default voice according to DX7
        self.operators = [Operator() for i in xrange(6)]
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
        pass
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class Operator:
    def __init__(self):
        # Default voice according to DX7
        self.ams = 0
        self.oscm = 0
        self.frec = 1
        self.fref = 0
        self.detu = 7 # I think offset by 7
        self.egr = [99, 99, 99, 99]
        self.egl = [99, 99, 99, 0]
        self.
        pass
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
    operator = Operator()
    operator.egr = [strm.next() for i in xrange(4)]
    operator.egl = [strm.next() for i in xrange(4)]
    # print "Break data"
    for attr in ['lsbp', 'lsld', 'lsrd']:
        setattr(operator, attr, strm.next())
    packed_data = strm.next()
    operator.lslc = packed_data & 3
    operator.lsrc = (packed_data >> 2) & 3
    packed_data = strm.next()
    operator.ors = packed_data & 0x7
    operator.detu = (packed_data >> 3) & 0xf
    packed_data = strm.next()
    operator.ams = packed_data & 0x3
    operator.kvs = (packed_data >> 2) & 0x7
    # print "Reading olvl"
    operator.olvl = strm.next()
    packed_data = strm.next()
    operator.oscm = packed_data & 1
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
    yield operator.ams | operator.kvs << 2
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

def packed_stream_from_voice(voice):
    for i in xrange(5, -1, -1):
        for b in packed_stream_from_operator(voice.operators[i]):
            yield b

    for r in voice.ptr:
        yield r
    for l in voice.ptl:
        yield l

    yield voice.algo
    yield voice.fdbk | voice.oks << 3
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

# messages = mido.read_syx_file('Syx/Dexed_01.syx')
messages = mido.read_syx_file('Syx/SynprezFM_11.syx')

def parse_voice(stream):
    for i in xrange(128):
        strm.next()

for message in messages:
    strm = stream(message.data)
    expect_byte(strm, 67, "Not Yamaha")
    expect_byte(strm, 0, "sub_status != 0")
    expect_byte(strm, 9, "Not 32 voice format")
    expect_byte(strm, 32, "Not MSB of 4096 bytes")
    expect_byte(strm, 0, "Not LSB of 4096 bytes")
    voices = []
    for i in xrange(32):
        voice = voice_from_packed_stream(strm)
        voices.append(voice)
        dump_voice(voice)
        # print "Voice", i, "read."
    # print "Data read"
    checksum = strm.next()
    print "checksum =", hex(checksum)
    s = sum(message.data[5:5+4096])
    print "actual sum =", hex((-s & 0x7f))
    # print vars(voice)

    op1 = voices[0].operators[0]
    s = packed_stream_from_operator(op1)
    op2 = operator_from_packed_stream(iter(s))

    dump_operator(op1)
    dump_operator(op2)
    print op1 == op2

    print "Testing voice/stream"
    voice1 = voices[0]
    print "Packing"
    dump_voice(voice1)
    s = packed_stream_from_voice(voice1)
    print "unpacking"
    voice2 = voice_from_packed_stream(iter(s))
    dump_voice(voice2)
    print "done"
    print voice1 == voice2
