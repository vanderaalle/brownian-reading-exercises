# This a harmonizator that starts from melody and tries to
# match the notes in the melody by finding a chord
# it does not assume any key

import numpy as np
from music21 import *
import copy

# see Haruspex list
# this could be natively in music21 using Chord obj
symbolsTo7 = {}
chordStr = ("""C	{0, 4, 7}
Cm	{0, 3, 7}
C+	{0, 4, 8}
Cdim	{0, 3, 6}
C7	{0, 4, 7, 10}
CM7	{0, 4, 7, 11}
CmM7	{0, 3, 7, 11}
Cm7	{0, 3, 7, 10}
C+M7	{0, 4, 8, 11}
C+7	{0, 4, 8, 10}
Cmin7b5	{0, 3, 6, 10}
Cdim7	{0, 3, 6, 9}
C7b5	{0, 4, 6, 10}
Csus4	{0, 5, 7}
Csus2	{0, 2, 7}
Cadd2	{0, 2, 4, 7}
Cadd4	{0, 4, 5, 7}
Cmadd2	{0, 2, 3, 7}
Cmadd4	{0, 3, 5, 7}""")

chs = [[x[0].replace("C", ""), eval(x[1])] for x in (c.split("\t")
                                                     for c in chordStr.replace("{", "[").replace("}", "]").split("\n"))]

for x in chs:
    symbolsTo7[x[0]] = x[1]

# you pass a stream obj


def extractFormsFromList(pitch_list):
    stru = [x for x in pitch_list]
    conc = [stru for x in range(len(stru))]
    conc = np.array(conc).flatten()
    forms = []
    for x in range(len(stru)):
        co = np.array(conc[x:(x+len(stru))])
        base = (co[0] % 12)
        com = co % 12
        form = com-(com[0])
        form = [el if el >= 0 else (el+12) for el in form]
        form = sorted(list(set(form)))
        forms.append([base, form])
    return forms

# stream2 = stream.Stream()
# n3 = note.Note('E4')  # octave values can be included in creation arguments
# stream2.append(n3)
# n3 = note.Note('G4')  # octave values can be included in creation arguments
# stream2.append(n3)
# n3 = note.Note('B4')  # octave values can be included in creation arguments
# stream2.append(n3)
# n3 = note.Note('D#4')  # octave values can be included in creation arguments
# stream2.append(n3)
# n3 = note.Note('F#4')  # octave values can be included in creation arguments
# stream2.append(n3)
# stream2.show()
# forms = extractFormsFromMeasure(stream2)
# forms

# rewritten as a recursive func


def chordMatch(forms, symbols, matched, cnt=0):
    #var fm, ch
    ch = []
    dict = {}
    if matched is None:
        matched = len(forms)
    for ann in forms:
        form = ann[1]
        p = [x for x in symbols if len(
            set(symbols[x]).intersection(set(form))) == matched]
        if p != []:
            fm = ann
            ch = p
            dict[str(fm)] = ch
    if (len(ch) == 0) and (cnt < 100):
        #print("AGAIN")
        cnt = cnt + 1
        dict = chordMatch(forms, symbols, matched-1, cnt)
        return dict
    else:
        return dict

# m = chordMatch(forms, symbolsTo7, None)
# print(m)


# priority for choosing chord, max to min
priority = ['', 'm', '7', 'm7', 'M7', '+', 'mM7', '+7', '+M7', '7b5', 'min7b5',
            'sus4', 'sus2', 'add4', 'add2', 'madd4', 'madd2', 'dim', 'dim7']
# if you want more
# priority2 = ['', 'm', 'M9', '9', 'm9', 'mM9', '7', 'm7', 'M7', '+', 'mM7', '+7', '+M7', '7b5', 'o','o7', '0', 'sus4', 'sus2', 'add4', 'add2', 'madd4', 'madd2', '+M9', '+9', 'Ø9', 'Øb9', 'o9', 'ob9']


def creditAssign(pdict, priority):
    newD = {}
    for x in pdict:
        pr = min([priority.index(c) for c in pdict[x]])
        newD[x] = pr
    newD = {v: k for k, v in newD.items()}
    sel = min(newD.keys())
    p = pitch.Pitch(pitchClass = eval(newD[sel])[0])
    return (p.name, priority[sel])


def getChord(pitch_list, scramblePriority=False):
    forms = extractFormsFromList(pitch_list)
    matches = chordMatch(forms, symbolsTo7, None)
    if scramblePriority == True:
        pr = copy.deepcopy(priority)
        random.shuffle(pr)
        cr = creditAssign(matches, pr)
    else:
        cr = creditAssign(matches, priority)
    return cr
