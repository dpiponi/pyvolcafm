import tempfile
import mido
import os
import filecmp
import numpy

from pyvolcafm import *
from pyvolcafm.notes import *
from pyvolcafm.operator import *

def generate_from_counts(counts):
    cdf = numpy.cumsum(counts)
    i = random.randrange(cdf[-1])
    return numpy.searchsorted(cdf,i,side='right')

def compute_operator_statistics():
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

    operator_count = 0
    voice_counts = {attr: numpy.zeros(range, dtype=numpy.int32)
                    for attr, range in VOICE_ATTR_RANGES}
    operator_counts = {attr: numpy.zeros(range, dtype=numpy.int32)
                       for attr, range in OPERATOR_ATTR_RANGES}
    operator_counts['egr1'] = numpy.zeros(100, dtype=numpy.int32)
    operator_counts['egr2'] = numpy.zeros(100, dtype=numpy.int32)
    operator_counts['egr3'] = numpy.zeros(100, dtype=numpy.int32)
    operator_counts['egr4'] = numpy.zeros(100, dtype=numpy.int32)
    operator_counts['egl1'] = numpy.zeros(100, dtype=numpy.int32)
    operator_counts['egl2'] = numpy.zeros(100, dtype=numpy.int32)
    operator_counts['egl3'] = numpy.zeros(100, dtype=numpy.int32)
    operator_counts['egl4'] = numpy.zeros(100, dtype=numpy.int32)
    voice_counts['ptr1'] = numpy.zeros(100, dtype=numpy.int32)
    voice_counts['ptr2'] = numpy.zeros(100, dtype=numpy.int32)
    voice_counts['ptr3'] = numpy.zeros(100, dtype=numpy.int32)
    voice_counts['ptr4'] = numpy.zeros(100, dtype=numpy.int32)
    voice_counts['ptl1'] = numpy.zeros(100, dtype=numpy.int32)
    voice_counts['ptl2'] = numpy.zeros(100, dtype=numpy.int32)
    voice_counts['ptl3'] = numpy.zeros(100, dtype=numpy.int32)
    voice_counts['ptl4'] = numpy.zeros(100, dtype=numpy.int32)
    for file in files:
        # print file
        data = read_sysex_file('data/'+file)
        strm = iter(data)
        voices = bank_from_packed_stream(strm)
        for voice in voices:
            has_integrity = voice.test_integrity()
            if has_integrity:
                for attr, _ in VOICE_ATTR_RANGES:
                    voice_counts[attr][getattr(voice, attr)] += 1
                voice_counts['ptr1'][voice.ptr[0]] += 1
                voice_counts['ptr2'][voice.ptr[1]] += 1
                voice_counts['ptr3'][voice.ptr[2]] += 1
                voice_counts['ptr4'][voice.ptr[3]] += 1
                voice_counts['ptl1'][voice.ptl[0]] += 1
                voice_counts['ptl2'][voice.ptl[1]] += 1
                voice_counts['ptl3'][voice.ptl[2]] += 1
                voice_counts['ptl4'][voice.ptl[3]] += 1
                for operator in voice.operators:
                    operator_count += 1
                    for attr, _ in OPERATOR_ATTR_RANGES:
                        operator_counts[attr][getattr(operator, attr)] += 1
                    operator_counts['egr1'][operator.egr[0]] += 1
                    operator_counts['egr2'][operator.egr[1]] += 1
                    operator_counts['egr3'][operator.egr[2]] += 1
                    operator_counts['egr4'][operator.egr[3]] += 1
                    operator_counts['egl1'][operator.egl[0]] += 1
                    operator_counts['egl2'][operator.egl[1]] += 1
                    operator_counts['egl3'][operator.egl[2]] += 1
                    operator_counts['egl4'][operator.egl[3]] += 1
            else:
                print "Rejecting", file, voice.name
                break
    print operator_counts
    print voice_counts

    # Generate a new voice bank based on these statistics
    voices = []
    for i in xrange(32):
        voice = Voice()
        for attr, _ in VOICE_ATTR_RANGES:
            value = generate_from_counts(voice_counts[attr])
            print attr, value
            setattr(voice, attr, value)
        voice.ptr = [generate_from_counts(voice_counts['ptr1']),
                     generate_from_counts(voice_counts['ptr2']),
                     generate_from_counts(voice_counts['ptr3']),
                     generate_from_counts(voice_counts['ptr4'])]
        voice.ptl = [generate_from_counts(voice_counts['ptl1']),
                     generate_from_counts(voice_counts['ptl2']),
                     generate_from_counts(voice_counts['ptl3']),
                     generate_from_counts(voice_counts['ptl4'])]
        for operator in voice.operators:
            for attr, _ in OPERATOR_ATTR_RANGES:
                value = generate_from_counts(operator_counts[attr])
                print attr, value
                setattr(operator, attr, value)
            operator.egr = [generate_from_counts(operator_counts['egr1']),
                            generate_from_counts(operator_counts['egr2']),
                            generate_from_counts(operator_counts['egr3']),
                            generate_from_counts(operator_counts['egr4'])]
            operator.egl = [generate_from_counts(operator_counts['egl1']),
                            generate_from_counts(operator_counts['egl2']),
                            generate_from_counts(operator_counts['egl3']),
                            generate_from_counts(operator_counts['egl4'])]
        voice.dump()
        voices.append(voice)

    write_sysex_file('random.syx', packed_stream_from_bank(voices))

compute_operator_statistics()

