import notes

_LIN = 0
_EXP = 1
EXP = 2
LIN = 3

class Operator:
    def __init__(self):
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
        self.olvl = 0
        self.ors = 0 # ???
        self.kvs = 0

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @classmethod
    def from_packed_stream(cls, strm):
        operator = Operator()
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

    def to_packed_stream(self):
        for i in xrange(4):
            yield self.egr[i]
        for i in xrange(4):
            yield self.egl[i]
        for attr in ['lsbp', 'lsld', 'lsrd']:
            yield getattr(self, attr)
        yield self.lslc | self.lsrc << 2
        yield self.ors | self.detu << 3
        yield self.ams | self.kvs << 2 # top bit may be set?
        yield self.olvl
        yield self.oscm | self.frec << 1
        yield self.fref

# Untested
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

def dump_operator(operator):
    for attr in ['egr', 'egl', 'lsbp', 'lsld',
                 'lsrd', 'lslc', 'lsrc', 'ors',
                 'ams', 'kvs', 'olvl', 'oscm',
                 'frec', 'fref', 'detu']:
        print attr, "=", getattr(operator, attr)
