import sys

thismodule = sys.modules[__name__]

note = 0
for i in xrange(-1, 9):
    for j in ['C', 'C#', 'D', 'D#',  'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']:
        setattr(thismodule, j+str(i), note)
        note += 1

C8 = 99
