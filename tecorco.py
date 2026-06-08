from music21 import *

# The Infamous Testa Corpo Coda Algorithm (TECORCO)
# for note grouping
# three funcs to group notes


def makeHead(ev):
    return [ev]  # in list for homogeneity


def makeHeadTail(ev):
    headDur = int(ev[1])+1-ev[1]
    head = [ev[0], ev[1], headDur]
    tail = [ev[0], int(ev[1])+1, ev[2]-headDur]
    return [head, tail]


def makeHeadBodyTail(ev):
    end = ev[1]+ev[2]
    headDur = int(ev[1])+1-ev[1]
    head = [ev[0], ev[1], headDur]
    body = [ev[0], int(ev[1]+1), int(end)-int(ev[1]+1)]
    tail = [ev[0], int(end), end-int(end)]
    # tail can dur = 0, probably because of various int passages
    if (end-int(end)) == 0:
        return [head, body]
    else:
        return [head, body, tail]


# assembler for TECORCO
def tieChecker(ev):
    # multiple cases
    # ['r', 0.8, 0.53333332]
    if ((ev[1]+ev[2])-int(ev[1])) > 2:
        tiedEv = makeHeadBodyTail(ev)
    elif ((ev[1]+ev[2])-int(ev[1])) <= 2 and ((ev[1]+ev[2])-int(ev[1])) > 1:
        tiedEv = makeHeadTail(ev)
    else:
        tiedEv = makeHead(ev)
    return tiedEv


def regroup(meas):
    # was Stream. Should we make it selectable?
    newMeas = stream.Part()
    nts = []
    other = []
    for x in meas:
        if type(x) is note.Note:
            nts.append(['n', x.offset, x.duration.quarterLength, x.pitch.ps])
        elif type(x) is note.Rest:
            nts.append(['r', x.offset, x.duration.quarterLength, None])
        else:
            other.append(x)
    for x in nts:
        tied = tieChecker(x)
        if len(tied) == 1:
            n = makeNotedEv(x[0], x[2], x[3])
            newMeas.insert(x[1], n)
        elif len(tied) == 2:
            n = makeNotedEv(x[0], tied[0][2], x[3])
            if x[0] == 'n':
                n.tie = tie.Tie('start')
            newMeas.insert(tied[0][1], n)
            # tie start
            n = makeNotedEv(x[0], tied[1][2], x[3])
            newMeas.insert(tied[1][1], n)
            if x[0] == 'n':
                n.tie = tie.Tie('stop')
            # tie stop
        elif len(tied) == 3:
            n = makeNotedEv(x[0], tied[0][2], x[3])
            if x[0] == 'n':
                n.tie = tie.Tie('start')
            newMeas.insert(tied[0][1], n)
            # tie start
            n = makeNotedEv(x[0], tied[1][2], x[3])
            if x[0] == 'n':
                n.tie = tie.Tie('continue')
            newMeas.insert(tied[1][1], n)
            # tie continue
            n = makeNotedEv(x[0], tied[2][2], x[3])
            if x[0] == 'n':
                n.tie = tie.Tie('stop')
            newMeas.insert(tied[2][1], n)
            # tie stop
    for x in other:
        newMeas.insert(x.offset, x)
    return newMeas

def makeNotedEv(typ, dur, pitch = None):
    if typ == 'n':
        n = note.Note()
        n.pitch.ps = pitch
    else:
        n = note.Rest()
    n.duration.quarterLength = dur
    return n


