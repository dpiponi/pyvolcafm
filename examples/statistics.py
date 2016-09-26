import tempfile
import mido
import os
import filecmp
import numpy

from pyvolcafm import *
from pyvolcafm.notes import *
from pyvolcafm.operator import *

def statistics():
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

    if 0:
        files.remove('atsu_4.syx')
        files.remove('dxmik2.syx')
        files.remove('dxoc14.syx')
        files.remove('dxoc16.syx')
        files.remove('dxoc19.syx')
        files.remove('dxoc23.syx')
        files.remove('int.syx')
        files.remove('ortega14.syx')
        files.remove('ortega17.syx')
        files.remove('ortega19.syx')
        files.remove('ortega2.syx')
        files.remove('ortega4.syx')
        files.remove('ortega5.syx')
        files.remove('ortega6.syx')
        files.remove('ortega7.syx')
        files.remove('ortega8.syx')
        files.remove('sjsu-g.syx')
        files.remove('solange5.syx')

    operator_count = 0
    counts = {attr: numpy.zeros(range, dtype=numpy.int32)
              for attr, range in OPERATOR_ATTR_RANGES}
    for file in files:
        # print file
        data = read_sysex_file('data/'+file)
        strm = iter(data)
        voices = bank_from_packed_stream(strm)
        for voice in voices:
            for operator in voice.operators:
                integrity = operator.test_integrity()
                if integrity:
                    operator_count += 1
                    for attr, _ in OPERATOR_ATTR_RANGES:
                        counts[attr][getattr(operator, attr)] += 1
                else:
                    print "Rejecting", file, voice.name
                    break
    print counts
    print "operator_count =", operator_count

statistics()

