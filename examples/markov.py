import tempfile
import mido
import os
import filecmp
import re
import numpy

from pyvolcafm import *
from pyvolcafm.notes import *
from pyvolcafm.operator import *

def generate_from_counts(counts):
    cdf = numpy.cumsum(counts)
    i = random.randrange(cdf[-1])
    return numpy.searchsorted(cdf,i,side='right')

def collect_operator_statistics(voice, op, counts, previous=None):
    operator = voice.operators[op]
    if previous:
        for attr, _ in OPERATOR_ATTR_RANGES:
            counts[attr][getattr(previous, attr)][getattr(operator, attr)] += 1
        counts['egr1'][previous.egr[0]][operator.egr[0]] += 1
        counts['egr2'][previous.egr[1]][operator.egr[1]] += 1
        counts['egr3'][previous.egr[2]][operator.egr[2]] += 1
        counts['egr4'][previous.egr[3]][operator.egr[3]] += 1
        counts['egl1'][previous.egl[0]][operator.egl[0]] += 1
        counts['egl2'][previous.egl[1]][operator.egl[1]] += 1
        counts['egl3'][previous.egl[2]][operator.egl[2]] += 1
        counts['egl4'][previous.egl[3]][operator.egl[3]] += 1
    else:
        for attr, _ in OPERATOR_ATTR_RANGES:
            counts[attr][getattr(operator, attr)] += 1
        counts['egr1'][operator.egr[0]] += 1
        counts['egr2'][operator.egr[1]] += 1
        counts['egr3'][operator.egr[2]] += 1
        counts['egr4'][operator.egr[3]] += 1
        counts['egl1'][operator.egl[0]] += 1
        counts['egl2'][operator.egl[1]] += 1
        counts['egl3'][operator.egl[2]] += 1
        counts['egl4'][operator.egl[3]] += 1

    if algorithm.ALGORITHMS[voice.algo].has_key(op):
        for parent_op in algorithm.ALGORITHMS[voice.algo][op]:
            if parent_op > op:
                collect_operator_statistics(voice, parent_op, operator_counts_step, operator)

def generate_operator_from_statistics(voice, op, counts, previous=None):
    operator = voice.operators[op]
    if previous:
        for attr, _ in OPERATOR_ATTR_RANGES:
            value = generate_from_counts(counts[attr][getattr(previous, attr)])
            print attr, value
            setattr(operator, attr, value)
        operator.egr = [generate_from_counts(counts['egr1'][previous.egr[0]]),
                        generate_from_counts(counts['egr2'][previous.egr[1]]),
                        generate_from_counts(counts['egr3'][previous.egr[2]]),
                        generate_from_counts(counts['egr4'][previous.egr[3]])]
        operator.egl = [generate_from_counts(counts['egl1'][previous.egl[0]]),
                        generate_from_counts(counts['egl2'][previous.egl[1]]),
                        generate_from_counts(counts['egl3'][previous.egl[2]]),
                        generate_from_counts(counts['egl4'][previous.egl[3]])]
    else:
        for attr, _ in OPERATOR_ATTR_RANGES:
            value = generate_from_counts(counts[attr])
            print attr, value
            setattr(operator, attr, value)
        operator.egr = [generate_from_counts(counts['egr1']),
                        generate_from_counts(counts['egr2']),
                        generate_from_counts(counts['egr3']),
                        generate_from_counts(counts['egr4'])]
        operator.egl = [generate_from_counts(counts['egl1']),
                        generate_from_counts(counts['egl2']),
                        generate_from_counts(counts['egl3']),
                        generate_from_counts(counts['egl4'])]

    if algorithm.ALGORITHMS[voice.algo].has_key(op):
        for parent_op in algorithm.ALGORITHMS[voice.algo][op]:
            if parent_op > op:
                generate_operator_from_statistics(voice, parent_op, operator_counts_step, operator)

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

    voice_counts = {attr: numpy.zeros(range, dtype=numpy.int32)
                    for attr, range in VOICE_ATTR_RANGES}

    global operator_counts_step # XXX Fix!!

    operator_counts_init = {attr: numpy.zeros(range, dtype=numpy.int32)
                            for attr, range in OPERATOR_ATTR_RANGES}
    operator_counts_step  = {attr: numpy.zeros((range, range), dtype=numpy.int32)
                             for attr, range in OPERATOR_ATTR_RANGES}

    operator_counts_init['egr1'] = numpy.zeros(100, dtype=numpy.int32)
    operator_counts_init['egr2'] = numpy.zeros(100, dtype=numpy.int32)
    operator_counts_init['egr3'] = numpy.zeros(100, dtype=numpy.int32)
    operator_counts_init['egr4'] = numpy.zeros(100, dtype=numpy.int32)
    operator_counts_init['egl1'] = numpy.zeros(100, dtype=numpy.int32)
    operator_counts_init['egl2'] = numpy.zeros(100, dtype=numpy.int32)
    operator_counts_init['egl3'] = numpy.zeros(100, dtype=numpy.int32)
    operator_counts_init['egl4'] = numpy.zeros(100, dtype=numpy.int32)

    operator_counts_step['egr1'] = numpy.zeros((100, 100), dtype=numpy.int32)
    operator_counts_step['egr2'] = numpy.zeros((100, 100), dtype=numpy.int32)
    operator_counts_step['egr3'] = numpy.zeros((100, 100), dtype=numpy.int32)
    operator_counts_step['egr4'] = numpy.zeros((100, 100), dtype=numpy.int32)
    operator_counts_step['egl1'] = numpy.zeros((100, 100), dtype=numpy.int32)
    operator_counts_step['egl2'] = numpy.zeros((100, 100), dtype=numpy.int32)
    operator_counts_step['egl3'] = numpy.zeros((100, 100), dtype=numpy.int32)
    operator_counts_step['egl4'] = numpy.zeros((100, 100), dtype=numpy.int32)

    voice_counts['ptr1'] = numpy.zeros(100, dtype=numpy.int32)
    voice_counts['ptr2'] = numpy.zeros(100, dtype=numpy.int32)
    voice_counts['ptr3'] = numpy.zeros(100, dtype=numpy.int32)
    voice_counts['ptr4'] = numpy.zeros(100, dtype=numpy.int32)
    voice_counts['ptl1'] = numpy.zeros(100, dtype=numpy.int32)
    voice_counts['ptl2'] = numpy.zeros(100, dtype=numpy.int32)
    voice_counts['ptl3'] = numpy.zeros(100, dtype=numpy.int32)
    voice_counts['ptl4'] = numpy.zeros(100, dtype=numpy.int32)

#    file_re = re.compile('.*(string|viol|cello)', re.IGNORECASE)
#    voice_re = re.compile('.*(string|viol|cello)', re.IGNORECASE)
#    file_re = re.compile('.*bass', re.IGNORECASE)
#    voice_re = re.compile('.*bass', re.IGNORECASE)
#    file_re = re.compile('.*(wind|sax|clarinet|flute|oboe)', re.IGNORECASE)
#    voice_re = re.compile('.*(wind|sax|clarinet|flute|oboe)', re.IGNORECASE)
#    file_re = re.compile('.*syn', re.IGNORECASE)
#    voice_re = re.compile('.*syn', re.IGNORECASE)
    file_re = re.compile('.', re.IGNORECASE)
    voice_re = re.compile('.', re.IGNORECASE)

    for file in files:
        doall = False
        if file_re.match(file):
            doall = True
        # print file
        data = read_sysex_file('data/'+file)
        strm = iter(data)
        voices = bank_from_packed_stream(strm)
        for voice in voices:
            has_integrity = voice.test_integrity()
            if has_integrity and (doall or voice_re.match(voice.name)):
                print voice.name
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

                for op in algorithm.ALGORITHMS[voice.algo]['out']:
                    collect_operator_statistics(voice, op, operator_counts_init)

            else:
                # print "Rejecting", file, voice.name
                break
    #print operator_counts
    #print voice_counts

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
        voice.name = "markov "+str(i+1)

        for op in algorithm.ALGORITHMS[voice.algo]['out']:
            generate_operator_from_statistics(voice, op, operator_counts_init)

        voice.dump()
        voices.append(voice)

    write_sysex_file('markov.syx', packed_stream_from_bank(voices))

compute_operator_statistics()

