# 6-String Bass Reading Exercises

Algorithmic generator of sight-reading exercises for **6-string electric bass** (low B – high C).  
Each run produces a fresh set of pieces exported as MusicXML (and optionally PDF via MuseScore).

## Algorithmic model

| Step | What happens |
|---|---|
| **Pseudo-modal scale** | Strictly upward brownian walk: random steps of 1–3 semitones from a random offset, covering the full instrument range |
| **Melody** | Bidirectional brownian walk over scale *indices* (jumps ±1–3, boundary reflection), mirrored into a palindrome |
| **Harmonisation** | Each 4/4 measure auto-harmonised by chord detection on its pitched notes |
| **Enharmonics** | Accidentals are randomly spelled as sharps or flats — intentionally mixed, as a reading challenge |
| **Clef** | Bass clef throughout by default; `_apply_bass_treble_clefs` can insert treble-8vb changes (adjust `TREBLE_THRESHOLD_MIDI`) |

### Rhythm variants

| Generator | Rhythm | Rests |
|---|---|---|
| `gen_quarter` | quarter notes | none |
| `gen_eighth` | eighth notes | ~25 % per slot |
| `gen_16th` | mixed 16th / 8th / dotted-8th / quarter | ~25 % per slot |

For `gen_16th`, notes crossing beat boundaries are split and tied by the [TECORCO](https://github.com/vanderaalle/comune) algorithm.

## Files

| File | Purpose |
|---|---|
| `generators.py` | All generator functions and helpers |
| `6-string exercise.ipynb` | Interactive notebook: explore, tweak, preview single pieces |
| `generate_books.py` | Batch script: 10 books × 3 processes → 30 PDFs |

## Dependencies

```
pip install music21 showscore
```

Also requires:
- `numpy` (`pip install numpy`)
- [MuseScore 4](https://musescore.org) AppImage for PDF export (path configured in `generate_books.py`)

`harmonizer.py` and `tecorco.py` are bundled in this repo.

## Usage

**Interactive (notebook):**
```
jupyter lab "6-string exercise.ipynb"
```

**Batch generation (30 PDFs):**
```
python3 generate_books.py
```
Output goes to `books/book_01_quarter.pdf` … `books/book_10_16th.pdf`.
