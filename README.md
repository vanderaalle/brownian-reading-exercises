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

## Ready-to-use exercise books

30 PDFs are included in [`books/`](books/) — 10 independent books per rhythm variant, 10 pieces each.

| Book | Quarter notes | Eighth notes + rests | 16th notes + rests |
|:---:|:---:|:---:|:---:|
| 01 | [book_01_quarter.pdf](books/book_01_quarter.pdf) | [book_01_eighth.pdf](books/book_01_eighth.pdf) | [book_01_16th.pdf](books/book_01_16th.pdf) |
| 02 | [book_02_quarter.pdf](books/book_02_quarter.pdf) | [book_02_eighth.pdf](books/book_02_eighth.pdf) | [book_02_16th.pdf](books/book_02_16th.pdf) |
| 03 | [book_03_quarter.pdf](books/book_03_quarter.pdf) | [book_03_eighth.pdf](books/book_03_eighth.pdf) | [book_03_16th.pdf](books/book_03_16th.pdf) |
| 04 | [book_04_quarter.pdf](books/book_04_quarter.pdf) | [book_04_eighth.pdf](books/book_04_eighth.pdf) | [book_04_16th.pdf](books/book_04_16th.pdf) |
| 05 | [book_05_quarter.pdf](books/book_05_quarter.pdf) | [book_05_eighth.pdf](books/book_05_eighth.pdf) | [book_05_16th.pdf](books/book_05_16th.pdf) |
| 06 | [book_06_quarter.pdf](books/book_06_quarter.pdf) | [book_06_eighth.pdf](books/book_06_eighth.pdf) | [book_06_16th.pdf](books/book_06_16th.pdf) |
| 07 | [book_07_quarter.pdf](books/book_07_quarter.pdf) | [book_07_eighth.pdf](books/book_07_eighth.pdf) | [book_07_16th.pdf](books/book_07_16th.pdf) |
| 08 | [book_08_quarter.pdf](books/book_08_quarter.pdf) | [book_08_eighth.pdf](books/book_08_eighth.pdf) | [book_08_16th.pdf](books/book_08_16th.pdf) |
| 09 | [book_09_quarter.pdf](books/book_09_quarter.pdf) | [book_09_eighth.pdf](books/book_09_eighth.pdf) | [book_09_16th.pdf](books/book_09_16th.pdf) |
| 10 | [book_10_quarter.pdf](books/book_10_quarter.pdf) | [book_10_eighth.pdf](books/book_10_eighth.pdf) | [book_10_16th.pdf](books/book_10_16th.pdf) |

Run `generate_books.py` to regenerate a fresh set at any time.

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
