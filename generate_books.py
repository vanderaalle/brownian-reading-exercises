"""
Generate 10 books × 3 processes (quarter, eighth, 16th) × 10 pieces each.
Outputs XML + PDF into books/ subdirectory.
"""
import os
import sys
import subprocess
import datetime

sys.path.append('/home/andrea/musica/muProj/comune')

from music21 import stream, instrument, metadata, tempo, expressions, layout, note
import generators

MUSESCORE = '/home/andrea/Applications/MuseScore-Studio-4.7.2.260525085-x86_64.AppImage'
OUT_DIR   = os.path.join(os.path.dirname(__file__), 'books')
N         = 10
TEMPO     = 60
PROCESSES = ['quarter', 'eighth', '16th']

GEN_MAP = {
    'quarter': generators.gen_quarter,
    'eighth':  generators.gen_eighth,
    '16th':    generators.gen_16th,
}

os.makedirs(OUT_DIR, exist_ok=True)


def _build_score(process, n, tempo_bpm):
    gen = GEN_MAP[process]
    raw_pieces   = [gen() for _ in range(n)]
    scale_ranges = [getattr(r, 'scale_range', None) for r in raw_pieces]
    pieces       = [generators._apply_bass_treble_clefs(r.makeMeasures()) for r in raw_pieces]

    part = stream.Part()
    part.insert(0, instrument.Instrument('Violoncello'))

    for p_idx, measured in enumerate(pieces):
        rng  = generators.piece_range(measured)
        srng = scale_ranges[p_idx]
        for m_idx, m in enumerate(measured.getElementsByClass(stream.Measure)):
            if p_idx == 0 and m_idx == 0:
                m.insert(0, tempo.MetronomeMark(number=tempo_bpm))
            if p_idx > 0 and m_idx == 0:
                m.insert(0, layout.PageLayout(isNew=True))
                m.insert(0, layout.SystemLayout(isNew=True))
            if m_idx == 0 and (rng or srng):
                parts = []
                if srng:
                    slo, shi, sspan, savg = srng
                    parts.append(f'scale: {slo}–{shi} ({sspan} st, avg step {savg} st)')
                if rng:
                    lo, hi, span, avg = rng
                    parts.append(f'melody: {lo}–{hi} ({span} st, avg jump {avg} st)')
                te = expressions.TextExpression('  |  '.join(parts))
                te.style.absoluteY = 15
                m.insert(0, te)
            part.append(m)

    score = stream.Score()
    score.insert(0, metadata.Metadata())
    score.metadata.title = f'{n}x {process}'
    score.append(part)
    return score


total = len(PROCESSES) * 10
done  = 0

for book_num in range(1, 11):
    for process in PROCESSES:
        label    = f'book_{book_num:02d}_{process}'
        xml_path = os.path.join(OUT_DIR, f'{label}.xml')
        pdf_path = os.path.join(OUT_DIR, f'{label}.pdf')

        score = _build_score(process, N, TEMPO)
        score.metadata.title = f'Book {book_num:02d} — {N}x {process} — {datetime.date.today()}'
        score.write('musicxml', xml_path)

        subprocess.run(
            [MUSESCORE, '-o', pdf_path, xml_path],
            check=True,
            env={**os.environ, 'QT_QPA_PLATFORM': 'offscreen'},
        )

        done += 1
        print(f'[{done}/{total}] {label}.pdf')

print(f'\nDone. Files in {OUT_DIR}')
