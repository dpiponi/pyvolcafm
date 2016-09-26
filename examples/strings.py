from pyvolcafm import *

voice = Voice()
voices = []
for i in xrange(32):
    voice = Voice()
    voice.algo = 6
    for j in xrange(6):
        # voice.operators[j].detu = 
        pass
    for j in [1, 3, 5]:
        voice.operators[j].egl = [0, 15, 20, 0]
        voice.operators[j].egr = [10, 10, 10, 10]
        voice.operators[j].olvl = 75
        voice.operators[j].frec = 1
    for j in [0, 2, 4]:
        voice.operators[j].egl = [70, 90, 60, 0]
        voice.operators[j].egr = [50, 20, 20, 20]
        voice.operators[j].olvl = 99
        voice.operators[j].frec = 2
        voice.operators[j].detu = 7+(j-2)
    #voice.ptl = [70, 60, 50, 50]
    #voice.ptr = [98, 50, 50, 50]
    voice.name = 'VOICE '+str(i)
    voices.append(voice)
write_sysex_file('test.syx', packed_stream_from_bank(voices))
