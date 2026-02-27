# Piano Learning Game - Developer Guide

## File Structure

| File | Purpose |
|------|---------|
| `playback.py` | Main entry, game loop, state machine, event handling |
| `constants.py` | Configuration: display, colors, staff geometry, MIDI |
| `music.py` | Note/MIDI mappings, staff positions, music theory data |
| `chords.py` | Test chord sequence, `generate_chord()` |
| `draw.py` | All rendering: chord, ledger lines, overlays |
| `game.py` | Pygame init, global screen/clock/font/staff_img |
| `utils.py` | Helpers: note parsing, MIDI conversion, SVG loading |

## Data Structures

### Note Format
- String: `"{pitch_class}{octave}"` e.g., `"C4"`, `"F#5"`, `"Bb3"`
- Pitch classes: `C, C#, Db, D, D#, Eb, E, F, F#, Gb, G, G#, Ab, A, A#, Bb, B`
- Octaves: 0-8 (piano range A0-C8)

### MIDI Mapping (in `music.py`)
- `note_to_mnote`: dict, note string → MIDI number (21-108)
- `mnote_to_note`: dict, MIDI number → note string (flats only)
- Example: `"C4"` → 60, 60 → `"C4"`

### Staff Positions (in `music.py`)
- `note_to_position["G"]`: treble clef positions (F4=0 to A6=17)
- `note_to_position["F"]`: bass clef positions (A2=0 to C5=17)
- Position 0 = top of visible staff, increases downward
- Used with `HALF_LINE_SPACING` to calculate Y coordinate

### Chord Dictionary
```python
{
    "notes": ["C4", "E4", "G4"],  # list of note strings
    "clef": "G",                   # "G" (treble) or "F" (bass)
    "chord_name": "C major",       # display name
    "key": "C",                    # key signature
    "scale_degree": "I"            # roman numeral
}
```

## State Machine (playback.py)
1. `start` - Show title, wait for SPACE
2. `show_chord` - Render chord, transition immediately to wait
3. `wait_for_notes` - Collect input until all notes matched
4. Loop: show_chord → wait_for_notes → show_chord

## Key Functions

### music.py
- None currently called directly (data only)

### utils.py
- `strip_accidental(note)` → base note + accidental tuple
- `compare_notes(a, b)` → True if enharmonic equivalent
- `get_note_from_midi(midi_num)` → note string

### chords.py
- `generate_chord(clef)` → next chord dict from test sequence
- `reset_chord_sequence()` → restart from beginning

### draw.py
- `draw_chord(screen, chord_dict)` → render notes on staff
- `draw_info_overlay(screen, state_info)` → debug display
- `draw_start_screen(screen)` → title screen

## Configuration (constants.py)

### Display
- `WIDTH, HEIGHT`: 1680×1000
- `HALF_LINE_SPACING`: 20.6 (pixels between adjacent notes)
- `TREBLE_STAFF_TOP`, `BASS_STAFF_TOP`: Y positions

### Staff Bounds
- `TREBLE_STAFF_LINE_POSITIONS`: [0, 2, 4, 6, 8]
- `BASS_STAFF_LINE_POSITIONS`: [0, 2, 4, 6, 8]
- Ledger lines drawn for notes outside range

### MIDI
- `MIDI_PORT_NAME`: device name to connect
- `TRY_MIDI`: set False to disable MIDI, keyboard-only

## Controls
| Key | Action |
|-----|--------|
| A-G | Play note in current octave |
| 1-6 | Set octave |
| SHIFT+note | Sharp |
| SPACE | Next chord |
| P | Toggle pause/auto-advance |
| R | Reset sequence |
| ESC | Quit |

## Running
```bash
cd /home/user/dev/playback
source .venv/bin/activate
python playback.py
```

## Dependencies
- pygame
- mido
- python-rtmidi
- cairosvg
