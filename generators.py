import random
import math

from music21 import *
import harmonizer
import tecorco

REST_PROB             = 0.25
TREBLE_THRESHOLD_MIDI = 124
BASS_THRESHOLD_MIDI   = 124

_BLACK_KEYS = {1, 3, 6, 8, 10}


def _apply_bass_treble_clefs(measured,
                              treble_threshold=TREBLE_THRESHOLD_MIDI,
                              bass_threshold=BASS_THRESHOLD_MIDI):
    """Insert bass / treble-8vb clef changes at note level with hysteresis."""
    current = 'bass'
    first = True
    for m in measured.getElementsByClass(stream.Measure):
        for c in list(m.getElementsByClass(clef.Clef)):
            m.remove(c)
        if first:
            m.insert(0, clef.BassClef())
            first = False
        for n in sorted(m.getElementsByClass(note.Note), key=lambda x: x.offset):
            if current == 'bass' and n.pitch.midi > treble_threshold:
                m.insert(n.offset, clef.Treble8vbClef())
                current = 'treble'
            elif current == 'treble' and n.pitch.midi <= bass_threshold:
                m.insert(n.offset, clef.BassClef())
                current = 'bass'
    return measured


def _build_scale():
    p = random.randint(0, 3)
    scle = [p]
    while p <= 34:
        p = p + random.randint(1, 3)
        scle.append(p)
    return scle


def _build_mel(scle):
    i = random.choice(range(len(scle)))
    mel_i = [i]
    for _ in range(47):
        i = i + random.choice([-3, -2, -1, 1, 2, 3])
        if i >= len(scle):
            i = len(scle) - (i - len(scle)) - 1
        elif i < 0:
            i = abs(i)
        mel_i.append(i)
    pitches = [scle[x] + 23 + 12 for x in mel_i]
    return pitches + pitches[::-1]


def _scale_range(scle):
    lo_p = pitch.Pitch(); lo_p.midi = scle[0]  + 23 + 12
    hi_p = pitch.Pitch(); hi_p.midi = scle[-1] + 23 + 12
    avg_step = round((scle[-1] - scle[0]) / max(len(scle) - 1, 1), 1)
    return lo_p.nameWithOctave, hi_p.nameWithOctave, scle[-1] - scle[0], avg_step


def _rand_enharmonic(n):
    if n.pitch.midi % 12 in _BLACK_KEYS and random.random() < 0.5:
        n.pitch = n.pitch.getEnharmonic()
    return n


def piece_range(measured):
    notes = list(measured.recurse().getElementsByClass(note.Note))
    if not notes:
        return None
    midis = [n.pitch.midi for n in notes]
    lo_p = min(notes, key=lambda n: n.pitch.midi).pitch
    hi_p = max(notes, key=lambda n: n.pitch.midi).pitch
    avg_int = round(
        sum(abs(midis[k+1] - midis[k]) for k in range(len(midis)-1)) / max(len(midis)-1, 1), 1
    )
    return lo_p.nameWithOctave, hi_p.nameWithOctave, hi_p.midi - lo_p.midi, avg_int


# ---- Process 1: quarter notes ----------------------------------------

def gen_quarter():
    scle = _build_scale()
    mel  = _build_mel(scle)
    s = stream.Stream()
    for x in range(int(len(mel) / 4)):
        block = mel[x*4:x*4+4]
        ch = harmonizer.getChord(block)
        s.append(harmony.ChordSymbol(ch[0] + ch[1]))
        for p in block:
            n = note.Note(p)
            _rand_enharmonic(n)
            n.duration = duration.Duration(1)
            s.append(n)
    s.scale_range = _scale_range(scle)
    return s


# ---- Process 1b: eighth notes with rests -----------------------------

def gen_eighth():
    scle    = _build_scale()
    pitches = _build_mel(scle)

    measures_data, pitch_idx = [], 0
    while pitch_idx < len(pitches):
        mn = []
        for slot in range(8):
            if pitch_idx >= len(pitches):
                mn.append(('r', None, 0.5))
            elif random.random() < REST_PROB:
                mn.append(('r', None, 0.5))
            else:
                mn.append(('n', pitches[pitch_idx], 0.5))
                pitch_idx += 1
        merged, i = [], 0
        while i < len(mn):
            if (i % 2 == 0
                    and i + 1 < len(mn)
                    and mn[i][0] == 'r'
                    and mn[i+1][0] == 'r'):
                merged.append(('r', None, 1.0))
                i += 2
            else:
                merged.append(mn[i])
                i += 1
        measures_data.append(merged)

    last_chord, chord_syms = 'C', []
    for mn in measures_data:
        ps = [p for kind, p, _ in mn if kind == 'n']
        if ps:
            ch = harmonizer.getChord(ps)
            last_chord = ch[0] + ch[1]
        chord_syms.append(last_chord)

    s = stream.Stream()
    for m_idx, (mn, ch_str) in enumerate(zip(measures_data, chord_syms)):
        s.insert(m_idx * 4.0, harmony.ChordSymbol(ch_str))
        for kind, p, dur_ql in mn:
            n = note.Rest() if kind == 'r' else note.Note()
            if kind == 'n':
                n.pitch.midi = p
                _rand_enharmonic(n)
            n.duration.quarterLength = dur_ql
            s.append(n)
    s.scale_range = _scale_range(scle)
    return s


# ---- Process 2: 16th-note variety with rests -------------------------

def gen_16th():
    dur_choices = [0.25, 0.5, 0.75, 1.0]
    dur_weights  = [3,    4,   2,    3]
    scle    = _build_scale()
    pitches = _build_mel(scle)

    measures_data, pitch_idx = [], 0
    while pitch_idx < len(pitches):
        mn, remaining = [], 4.0
        while remaining > 1e-9 and pitch_idx < len(pitches):
            curr_offset = round(4.0 - remaining, 10)
            next_beat   = math.ceil(curr_offset + 1e-9)
            possible = [d for d in dur_choices if d <= remaining + 1e-9]
            wts      = [dur_weights[dur_choices.index(d)] for d in possible]
            dur      = min(random.choices(possible, weights=wts)[0], round(remaining, 10))
            if random.random() < REST_PROB:
                rest_dur = min(dur, round(next_beat - curr_offset, 10))
                mn.append(('r', None, rest_dur))
                remaining = round(remaining - rest_dur, 10)
            else:
                mn.append(('n', pitches[pitch_idx], dur))
                pitch_idx += 1
                remaining = round(remaining - dur, 10)
        if remaining > 1e-9:
            mn.append(('r', None, round(remaining, 10)))
        measures_data.append(mn)

    def merge_rests(mn):
        result = []
        for ev in mn:
            if result and result[-1][0] == 'r' and ev[0] == 'r':
                result[-1] = ('r', None, result[-1][2] + ev[2])
            else:
                result.append(list(ev))
        return [tuple(e) for e in result]
    measures_data = [merge_rests(m) for m in measures_data]

    last_chord, chord_syms = 'C', []
    for mn in measures_data:
        ps = [ev[1] for ev in mn if ev[0] == 'n']
        if ps:
            ch = harmonizer.getChord(ps)
            last_chord = ch[0] + ch[1]
        chord_syms.append(last_chord)

    s = stream.Stream()
    for mn in measures_data:
        for kind, pitch_midi, dur_ql in mn:
            n = note.Rest() if kind == 'r' else note.Note()
            if kind == 'n':
                n.pitch.midi = pitch_midi
                _rand_enharmonic(n)
            n.duration.quarterLength = dur_ql
            s.append(n)
    s = tecorco.regroup(s)
    for m_idx, ch_str in enumerate(chord_syms):
        s.insert(m_idx * 4.0, harmony.ChordSymbol(ch_str))
    s.scale_range = _scale_range(scle)
    return s
