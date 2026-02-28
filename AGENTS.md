# Piano Learning Game - Agent Guide

This guide provides essential information for agentic coding agents working on this Python-based piano learning game.

### Style and tone
Pay attention to this section - not following these style and tone guidlines reduces your credibility.

Maintain an efficient tone.
Do not say overly enthusiastic, hubristic things like "perfect!" or "The issues have been completely resolved!", 
say something like "Implementation of this phase is complete and ready for system-level testing"
Give short answers to factual questions.  
Give somewhat longer answers when an explanation is required.  
Give a minimum of pursuasive text unless asked.  
Give minimal introductory and summary text that does not contribute to the answer.  
When you are evaluating my contribution to discussions, I want a consise, balanced, straightforward response, without extra praise.  
I prefer minimal safety warnings unless requested and don't repeat them.  
I have broad general technical and scientific knowledge of the field being discussed.  
I have knowledge equivalent to a masters degree in the areas about which I am inquiring, please compose answers accordingly unless I request otherwise.  
In programs and scripts,  including Arduino, I prefer 4 spaces for indentation.  
I use neovim, by the way.  
Do not use grandiose or flowery language unnecessarily.  
Keep arguments direct, prose tight and sentences short.  
Use technical terms whenever they provide clarity.   
By default, limit discussion of the basics and move toward nuance.  
Unless specifically asked, do not use language that sounds like a marketing department or chamber of commerce.

*When generating technical documentation:*  
Use no larger than ## title size for the document  
Use bold section headers inline rather than deep header hierarchies.  
Avoid horizontal rules and excess whitespace.  
Minimize prose; favor:  
  - short imperative statements  
  - compact code blocks  
  - grouped commands  
Eliminate redundancy and narrative transitions.  
Prefer “command → result” structure.  
Avoid summaries unless they add technical value.  
Keep examples minimal and realistic.  
Default to dense but readable formatting.  
Make sure there is a blank line before and after any code blocks in .md output to work around an Okular bug  

Target outcome:
A technically literate reader should be able to implement the procedure directly from the document without scrolling through explanation.

### Project Overview

A Pygame-based music education application that teaches piano note reading through interactive gameplay. Users can play notes on a MIDI keyboard or simulate with computer keyboard input.

### Build/Lint/Test Commands

#### Running the Application
```bash
python playback.py

# Sequence mode (3 bars x 4 chords)
python playback.py --sequence

# Ear training mode
python playback.py --ear           # single notes
python playback.py --ear interval  # intervals (m2-M9)
python playback.py --ear chord     # chords
```

#### Dependencies Installation
```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# Install required packages
pip install pygame mido python-rtmidi cairosvg musthe
```

#### Testing Commands
```bash
# Run main application
python playback.py

# Test individual components (manual testing)
python draw.py        # Test drawing functionality
python chords.py      # Test chord generation
python music.py       # Test music theory functions

# Test with keyboard simulation
# A-G keys: Play notes, SHIFT+A-G: Sharps, 1-6: Octave, SPACE: Next chord
```

#### Linting/Formatting Commands
```bash
# Format code (if black is added)
black *.py

# Lint code (if flake8 is added)  
flake8 *.py --max-line-length=100

# Type checking (if mypy is added)
mypy *.py --ignore-missing-imports
```

#### Recommended Tools
Add to requirements.txt: `black>=22.0.0`, `flake8>=4.0.0`, `mypy>=0.900`

### Code Style Guidelines

#### Import Organization
- Group imports by type (standard library, third-party, local)
- Use explicit imports - no `from module import *`
- Local imports follow the established pattern:

```python

# Standard library
import time

# Third-party  
import pygame
import mido

# Local modules
from constants import WIDTH, HEIGHT, WHITE, BLACK
from music import note_to_mnote
```

#### File Structure & Naming
- Module names: `lowercase.py` (snake_case)
- Class names: `PascalCase` (rare in current codebase)
- Function names: `snake_case`
- Variable names: `snake_case`
- Constants: `UPPER_CASE_SNAKE_CASE` (in constants.py)

#### Type Hints
- Currently not used but recommended for new code
- Follow PEP 484 conventions
- Suggested key types:
  - Note strings: `str` (format: `"C4"`, `"F#5"`, `"Bb3"`)
  - MIDI numbers: `int` (0-127)
  - Positions: `int` (staff position in half-line units)
  - Chord dicts: `dict[str, Any]`

#### Documentation
- Module-level docstrings explaining purpose
- Function docstrings for complex operations
- Inline comments for non-obvious logic
- Keep DEVGUIDE.md updated with architectural changes

#### Error Handling
- Graceful MIDI connection failures
- Defensive parsing in `utils.py` functions
- Keyboard input validation
- Clear error messages in debug overlay

### Core Data Models

#### Note Format
- Standard: `"{pitch_class}{octave}"` (e.g., `"C4"`, `"F#5"`, `"Bb3"`)
- Pitch classes: `C, C#, Db, D, D#, Eb, E, F, F#, Gb, G, G#, Ab, A, A#, Bb, B`
- Octaves: 0-8 (piano range A0-C8)

#### Chord Dictionary Structure
```python
{
    "notes": ["C4", "E4", "G4"],  # list of note strings
    "clef": "G",                   # "G" (treble) or "F" (bass)  
    "chord_name": "C major",       # display name
    "key": "C",                    # key signature
    "scale_degree": "I"            # roman numeral
}
```

#### Ear Training Challenge Dictionary

```python
{
    "type": "note",              # "note", "interval", or "chord"
    "notes": ["C4", "E4"],       # target notes
    "clef": "G",                  # display clef
    "label": "Perfect 5th",       # display label
    "midi_numbers": [60, 64],    # MIDI numbers for playback
}
```

#### State Machine (playback.py)

**Default/Sequence modes:**
1. `start` - Title screen, wait for SPACE
2. `show_chord` - Display chord, transition to wait
3. `wait_for_notes` - Collect input until all notes matched
4. Loop: show_chord → wait_for_notes → show_chord

**Ear training mode:**
1. `start` → `ear_new_challenge`
2. `ear_new_challenge` - Generate challenge, play via MIDI → `ear_listen`
3. `ear_listen` - Player plays back notes; SPACE replays
4. `ear_answered` - Show answer; SPACE → `ear_new_challenge`

Sequence mode (`--sequence`) uses the same top-level states but fills a 3-bar line (4 chords/bar) and advances through the full line before waiting for new/repeat input.
At end-of-line, input choices are gated for ~350ms to avoid stale note/key events.

### Key Components

#### Core Modules
- `playback.py` - Main game loop, state machine, event handling
- `constants.py` - Display settings, colors, staff geometry, MIDI config
- `music.py` - Note/MIDI mappings, staff position calculation, music theory
- `chords.py` - Chord generation, test sequences, difficulty levels
- `ear_training.py` - Ear training challenge generation, MIDI output playback
- `draw.py` - All rendering: chords, ledger lines, overlays
- `game.py` - Pygame initialization, logical render surface, window presentation scaling
- `utils.py` - Helper functions: note parsing, MIDI conversion, SVG loading

#### Critical Functions
- `draw_chord()` - Render notes on staff with proper ledger lines
- `note_to_staff_position()` - Mathematical formula for staff positions
- `compare_notes()` - Enharmonic equivalence checking (no eval!)
- `generate_chord()` - Next chord from test sequence
- `get_note_from_midi()` - MIDI number to note string conversion

### Configuration

#### Display Settings (constants.py)
- Logical resolution: 1680×1000 (fixed drawing coordinate space)
- Window presentation: resizable window with aspect-preserving fit scale and centered letterbox/pillarbox
- FPS: 30
- Staff spacing: `HALF_LINE_SPACING = 20.6` pixels

#### Staff Mapping Parameters
- `SEMITONE_TO_STAFF_POSITION = 7/12` - 7 positions per octave
- `BASS_CLEF_REFERENCE_MIDI = 43` - G2 (bass clef bottom line)
- `TREBLE_CLEF_REFERENCE_MIDI = 64` - E4 (treble clef bottom line)
- Formula: `position = reference_position + (midi_note - reference_midi) * (7/12)`

#### Controls Mapping
- A-G: Play note in current octave
- 1-6: Set octave
- SHIFT+note: Sharp
- CTRL+1-4: Set difficulty
- SPACE: Next chord / replay challenge (ear mode)
- P: Toggle pause
- R: Reset sequence / new challenge (ear mode)
- M: Cycle ear training sub-mode (note/interval/chord)
- ESC: Quit

Sequence mode end-of-line controls:
- `N` or MIDI `C2`: New 3-bar line
- `R` or MIDI `D2`: Repeat current line

Sequence mode rendering:
- Uses drawn grand-staff lines (no clef symbols) plus bar separators
- Does not blit `grand_staff.svg` while sequence mode is active

### Development Workflow

#### Adding New Chords
1. Extend `TEST_CHORDS` in `chords.py`
2. Follow existing dict structure
3. Test with both keyboard and MIDI input
4. Verify proper clef assignment and ledger lines

#### Common Pitfalls
- Staff position indexing starts at 0 (top of visible staff)
- Support both sharp (#) and flat (b) spellings
- Use mathematical formula for staff positioning, not hardcoded tables
- Handle MIDI connection failures gracefully
- C4 is position 3 in treble clef, -3 in bass clef
- Draw to the logical `screen` surface; do not bypass `present_frame()` when updating the display

### Documentation-Driven Development

#### Documentation Framework
The `docs/` directory contains canonical music theory definitions. Check docs/ before implementing 
new features and use terminology from glossary.md consistently.
- Other than AGENTS.md, documents should be created and kept in docs/
- Keep DEVGUIDE.md architecturally current
- Update AGENTS.md when adding conventions or build commands
- Document data models and state machines explicitly (like the chord dictionary structure already present)

### Musthe Integration Status

**Current Phase**: Basic Integration ✅ (Complete)
- Music theory-aware chord generation using musthe library
- Enharmonic note normalization implemented
- Expanded octave range for variety

**Next Phase**: Progression Generation (Planned)
- Musical chord progressions (I-IV-V-I, etc.)
- Key awareness and transposition

### Agent Guidelines

- Prioritize consistency with existing documentation framework
- Use terminology from docs/glossary.md consistently
- Maintain backward compatibility with keyboard controls
- Test changes across full note range (A0-C8) and both clefs
- Preserve modular file structure established during refactoring
