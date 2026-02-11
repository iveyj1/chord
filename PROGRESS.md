# Piano Learning Game - Progress & Plans

## Completed

### Phase 1: Cleanup & Stabilization
- Fixed `compare_notes()` - removed unsafe `eval()`, now uses direct comparison
- Fixed `limit_note_range()` - corrected off-by-one bug (`chord_notes[1]` → `chord_notes[0]`)
- Fixed bass clef ledger lines - was checking wrong clef
- Removed dead code: `test_note` global, unused `mnote_to_staff_position`, duplicate chord definitions
- Replaced random chord generation with fixed test sequence

### Phase 2: Testing Without Keyboard
- Added keyboard simulation (A-G keys, 1-6 for octave, SHIFT for sharps)
- Added on-screen display: chord name, notes, clef, hits/misses
- Added controls: SPACE=next, P=pause/auto, R=reset, ESC=quit
- Fixed event handling bug in start state

### Phase 2.5: Refactoring
- Split code into focused modules (was 5 files with mixed concerns, now 7 clean files)
- Removed `from x import *` - all imports explicit
- Added font caching in draw.py
- Functions now take `screen` parameter instead of using globals

### Phase 3: Data Model Documentation
- Documented note format, MIDI mapping, staff positions, chord dictionary
- Added planned difficulty levels to chords.py

## Current State
- Game runs, displays notes/chords on grand staff
- Both clefs work with correct ledger lines
- Can test with computer keyboard or MIDI keyboard
- 29 test chords covering single notes, triads, accidentals, ledger lines

## Future Plans

### Phase 4: Chord Generation
- Difficulty levels:
  1. Single notes (white keys)
  2. Single notes (with accidentals)
  3. Intervals (2 notes)
  4. Triads
  5. Seventh chords
  6. Both clefs
- Configurable key and note range
- Musical progressions (I-IV-V-I, etc.)

### Phase 5: Gamification
- Scoring system
- Timing feedback
- Visual hit/miss indicators
- Progress tracking
- Adaptive difficulty
