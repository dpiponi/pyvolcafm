import notes
import random

_LIN = 0
_EXP = 1
EXP = 2
LIN = 3

OPERATOR_ATTR_RANGES = [
#    ('egr', 100), ('egl', 100),
    ('lsbp', 100),
    ('lsld', 100), ('lsrd', 100),
    ('lslc', 4), ('lsrc', 4),
    ('ors', 8), ('ams', 4), ('kvs', 8),
    ('olvl', 100), ('oscm', 2),
    ('frec', 32), ('fref', 100), ('detu', 15)
]

class Operator:
    def __init__(self):
        # Default voice according to DX7
        for attr, value in [
                ('ams', 0), ('oscm', 0),
                ('frec', 1), ('fref', 0), ('detu', 7),
                ('egr', 4*[99]), ('egl', 3*[99]+[0]),
                ('lsbp', getattr(notes, 'A-1')),
                ('lslc', _LIN), ('lsrc', _LIN),
                ('lsld', 0), ('lsrd', 0),
                ('olvl', 0), ('ors', 0), ('kvs', 0)
            ]:
            setattr(self, attr, value)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def test_integrity(self):
        for o in self.egr:
            if o < 0 or o > 99:
                return False
        for o in self.egl:
            if o < 0 or o > 99:
                return False
        for attr, limit in OPERATOR_ATTR_RANGES:
            value = getattr(self, attr)
            if value < 0 or value >= limit:
                print attr, "value =", value, "limit =", limit
                return False
        return True

    @classmethod
    def random(cls):
        operator = Operator()

        operator.egr = [random.randrange(100) for i in xrange(4)]
        operator.egl = [random.randrange(100) for i in xrange(4)]

        for attr, limit in OPERATOR_ATTR_RANGES:
            setattr(operator, attr, random.randrange(limit))

        return operator

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
