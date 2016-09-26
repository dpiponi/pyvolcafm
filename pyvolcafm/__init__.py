"""A small library to manipulate MIDI sysex files containing
banks of 32 Yamaha DX7/Korg Volca FM voices."""

import sys
import mido
import itertools

from notes import *
from operator import *
from voice import *

# See https://github.com/rogerallen/dxsyx/blob/master/dx7-sysex-format.txt
# Also http://synthify.com/ChromaticArchive/MIDI/DX7-II-SYSEX.pdf

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
        voice = Voice.from_packed_stream(strm2)
        voices.append(voice)
        # dump_voice(voice)
        # print "Voice", i, "read."
    # print "Data read"
    checksum = strm.next()
    s = -sum(bytes) & 0x7f
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
        voice_gen = voices[i].to_packed_stream()
        for b in voice_gen:
            s += b
            yield b
    yield -s & 0x7f

def expect_byte(strm, b, e):
    n = strm.next()
    if n != b:
        print e
        sys.exit(1)

def parse_voice(stream):
    for i in xrange(128):
        strm.next()

def read_sysex_file(filename):
    f = open(filename, 'rb')
    d = tuple(map(ord, list(f.read())))
    assert d[0] == 0xf0
    assert d[-1] == 0xf7
    return d[1:-1]

def write_sysex_file(filename, strm):
    file = open(filename,'wb')
    file.write(b'\xf0')
    data = bytearray(strm)
    file.write(data)
    file.write(b'\xf7')
    file.close()
