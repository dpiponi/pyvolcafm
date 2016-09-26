from pyvolcafm import *

voices = []
for i in xrange(32):
    voice = Voice()
    voice.algo = 6
    for j in xrange(6):
        # voice.operators[j].detu = 
        pass
    for j in [1, 3, 5]:
        voice.operators[j].egl = [50, 80, 90, 50]
        voice.operators[j].egr = [40, 40, 40, 40]
        voice.operators[j].olvl = 65
        voice.operators[j].fref = j
    for j in [0, 2, 4]:
        voice.operators[j].egl = [99, 80, 60, 0]
        voice.operators[j].egr = [95, 40, 40, 40]
        voice.operators[j].olvl = 99
    voice.ptl = [70, 60, 50, 50]
    voice.ptr = [98, 50, 50, 50]
    voice.name = 'VOICE '+str(i)
    voices.append(voice)
write_sysex_file('test.syx', packed_stream_from_bank(voices))
