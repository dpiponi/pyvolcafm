"""
Generate a random patch based on a corpus of existing patches.
"""
import tempfile
import mido
import os
import filecmp
import re
import numpy

from pyvolcafm import *
from pyvolcafm.notes import *
from pyvolcafm.operator import *

def compute_operator_statistics():
    voices = []
    for i in xrange(32):
        voice = Voice.random()
        voice.name = "unifrm "+str(i+1)
        voice.dump()
        voices.append(voice)

    write_sysex_file('uniform.syx', packed_stream_from_bank(voices))

compute_operator_statistics()

