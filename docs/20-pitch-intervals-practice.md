# Pitch and Intervals in Practice

*References core concepts from [pitch.md](02-pitch.md) and [intervals.md](03-intervals.md)*

## 1. Why This Matters for Software Development

Pitch and intervals are the atoms of music software. Every harmonic analysis, melody generation, or MIDI processing task reduces to manipulating these fundamental relationships. Understanding the distinction between **symbolic spelling** (C♯ vs D♭) and **numeric representation** (PC 1) is crucial - choose the right tool for each task.

**Core implementation questions:**
- Are you doing harmonic analysis? Use symbolic spellings to preserve interval identities.
- Generating transposable patterns? Use pitch classes for efficiency.
- Processing MIDI input? Convert to PC immediately for pattern matching.

## 2. Pitch Concepts in Code

### 2.1 Practical Pitch Conversion

```python
# From [pitch.md](02-pitch.md): MIDI = 12 × octave + pitch_class + 12
def midi_to_pc(midi_note: int) -> int:
    return midi_note % 12

def note_to_midi(note: str) -> int:  # e.g., "C4", "F#5"
    letter_to_pc = {'C':0, 'D':2, 'E':4, 'F':5, 'G':7, 'A':9, 'B':11}
    pc = letter_to_pc[note[0]]
    accidental = note[1:-1]  # extract accidental(s)
    octave = int(note[-1])
    
    if '#' in accidental:
        pc = (pc + len(accidental)) % 12
    elif 'b' in accidental:
        pc = (pc - len(accidental)) % 12
    
    return 12 * octave + pc + 12

# Examples:
assert midi_to_pc(60) == 0      # C4 -> PC 0
assert midi_to_pc(61) == 1      # C#4 -> PC 1  
assert note_to_midi("C4") == 60  # Verify formula works
assert note_to_midi("A4") == 69  # A440 reference
```

### 2.2 Enharmonic Handling

**Rule:** Use PC comparison for pitch equality, preserve spelling for interval analysis.

```python
def enharmonic_equivalent(note1: str, note2: str) -> bool:
    return midi_to_pc(note_to_midi(note1)) == midi_to_pc(note_to_midi(note2))

# Same sound, different spellings
assert enharmonic_equivalent("C#4", "Db4")  # True
assert enharmonic_equivalent("F#5", "Gb5")  # True

# But for interval analysis, spelling matters:
# C# → E = major third (3 semitones)
# Db → E = augmented third (4 semitones)
```

## 3. Interval Operations in Practice

### 3.1 Semitone Calculation

```python
def interval_semitones(note1: str, note2: str) -> int:
    """Positive = upward, negative = downward"""
    pc1, oct1 = midi_to_pc(note_to_midi(note1)), int(note1[-1])
    pc2, oct2 = midi_to_pc(note_to_midi(note2)), int(note2[-1])
    
    midi1, midi2 = note_to_midi(note1), note_to_midi(note2)
    return midi2 - midi1

# Examples:
assert interval_semitones("C4", "E4") == 4      # Major third
assert interval_semitones("C4", "Eb4") == 3      # Minor third  
assert interval_semitones("E4", "C4") == -4     # Descending major third
```

### 3.2 Interval Quality Detection

```python
def interval_quality(note1: str, note2: str) -> str:
    """Returns generic interval + quality"""
    # Generic interval from letter distance
    letter_order = ['C','D','E','F','G','A','B']
    generic = (letter_order.index(note2[0]) - letter_order.index(note1[0])) % 7 + 1
    
    semitones = abs(interval_semitones(note1, note2))
    
    # Quality determination by generic interval
    if generic in [1,4,5]:  # Unison, fourth, fifth
        if semitones in [0,5,7]:
            return f"perfect {generic}"
        elif semitones in [1,6,8]:
            return f"augmented {generic}"
        else:
            return f"diminished {generic}"
    else:  # Second, third, sixth, seventh
        if semitones in [2,4,9,11]:
            return f"major {generic}"
        elif semitones in [1,3,8,10]:
            return f"minor {generic}"
        elif semitones in [5,6]:
            return f"augmented {generic}"
        else:
            return f"diminished {generic}"

# Test cases:
assert interval_quality("C4", "E4") == "major 3"
assert interval_quality("C4", "Eb4") == "minor 3" 
assert interval_quality("C4", "F4") == "perfect 4"
```

### 3.3 Interval Inversion

```python
def invert_interval(generic: int, quality: str) -> tuple:
    """Returns (new_generic, new_quality) after inversion"""
    new_generic = 9 - generic
    
    inversion_map = {
        ('major', 'minor'), ('minor', 'major'),
        ('augmented', 'diminished'), ('diminished', 'augmented'),
        ('perfect', 'perfect')
    }
    
    for (q1, q2) in inversion_map:
        if quality == q1:
            new_quality = q2
            break
    
    return new_generic, new_quality

# Example: major 3rd inverts to minor 6th
assert invert_interval(3, 'major') == (6, 'minor')
```

## 4. Implementation Patterns

### 4.1 Efficient Data Structures

```python
# For fast PC set operations
from typing import FrozenSet

def chord_to_pc_set(chord_notes: list[str]) -> FrozenSet[int]:
    """Convert chord notes to pitch-class set for fast comparison"""
    return frozenset(midi_to_pc(note_to_midi(note)) for note in chord_notes)

# Fast harmonic analysis
def is_transpositionally_equivalent(chord1: list[str], chord2: list[str]) -> bool:
    """Check if chords are same type (transpositionally equivalent)"""
    pcs1, pcs2 = chord_to_pc_set(chord1), chord_to_pc_set(chord2)
    
    # Try all possible transpositions
    for transpose in range(12):
        transposed = frozenset((pc + transpose) % 12 for pc in pcs1)
        if transposed == pcs2:
            return True
    return False

# Test: C major and G major are transpositionally equivalent
assert is_transpositionally_equivalent(["C4","E4","G4"], ["G4","B4","D5"])
```

### 4.2 Real-Time Considerations

```python
# Pre-computed lookup tables for performance
PC_FROM_MIDI = [i % 12 for i in range(128)]
INTERVAL_CACHE = {}  # {(note1, note2): (generic, quality)}

def fast_interval_detection(midi1: int, midi2: int) -> tuple:
    """Optimized for real-time applications"""
    key = (midi1, midi2)
    if key not in INTERVAL_CACHE:
        # Compute and cache
        INTERVAL_CACHE[key] = compute_interval_quality(midi1, midi2)
    return INTERVAL_CACHE[key]
```

## 5. Worked Examples

### Example 1: Chord Type Detection
Given MIDI notes [60, 64, 67], determine chord quality:

```python
def detect_chord_quality(midi_notes: list[int]) -> str:
    """Return chord quality from MIDI notes"""
    if len(midi_notes) != 3: return "not a triad"
    
    pcs = sorted([PC_FROM_MIDI[n] for n in midi_notes])
    intervals = [(pcs[i+1] - pcs[i]) % 12 for i in range(2)]
    
    quality_map = {
        (4, 3): "major triad",
        (3, 4): "minor triad", 
        (3, 3): "diminished triad",
        (4, 4): "augmented triad"
    }
    
    return quality_map.get(tuple(intervals), "unknown")

assert detect_chord_quality([60, 64, 67]) == "major triad"  # C-E-G
assert detect_chord_quality([60, 63, 67]) == "minor triad"  # C-Eb-G
```

### Example 2: Voice Leading Smoothness
Calculate total voice leading motion between chords:

```python
def voice_leading_cost(chord1: list[int], chord2: list[int]) -> int:
    """Total semitone motion between voicings"""
    chord1, chord2 = sorted(chord1), sorted(chord2)
    return sum(abs(n2 - n1) for n1, n2 in zip(chord1, chord2))

# Compare different voice leading options
c_major = [60, 64, 67]  # C-E-G
g_major1 = [67, 71, 74]  # G-B-D (close position)
g_major2 = [55, 71, 74]  # G3-B-D (drop 2)

assert voice_leading_cost(c_major, g_major1) == 18  # 7+7+4
assert voice_leading_cost(c_major, g_major2) == 8   # 5+7+4 (smoother)
```

## 6. Progressive Exercises

### Exercise 1: Basic Pitch Conversion
Write functions to:
- Convert MIDI numbers to pitch classes
- Determine if two notes are enharmonically equivalent
- Convert between note names and MIDI numbers

**Implementation hint:** Use the formula from [pitch.md](02-pitch.md): `MIDI = 12 × octave + pitch_class + 12`

### Exercise 2: Interval Calculator
Implement `interval_analysis(note1, note2)` that returns:
- Generic interval number
- Quality (major/minor/perfect/etc.)
- Semitone distance
- Direction (up/down)

**Test:** "C4" → "Ab4" should return (6, augmented, 8, up)

### Exercise 3: Pattern Transposition
Create `transpose_pattern(pattern, target_note)` where:
- `pattern` is a list of MIDI intervals [0, 4, 7] (triad)
- `target_note` is starting MIDI note for the transposed pattern
- Return list of absolute MIDI notes

**Challenge:** Handle wraparound when pattern exceeds MIDI range (0-127)

### Exercise 4: Harmonic Analysis Algorithm
Given a melody line of MIDI notes, detect:
- Key (using pitch-class frequency analysis)
- Chord changes (simultaneous notes)
- Cadence patterns (V→I endings)

**Hint:** Use pitch-class set operations for fast pattern matching

### Exercise 5: Optimization Challenge
Implement a real-time interval detection system that:
- Processes MIDI input stream
- Detects chord types with <1ms latency
- Uses caching for common interval patterns
- Handles edge cases (notes outside range, invalid input)

**Performance target:** <100μs per interval calculation

---

## Quick Reference

| Concept | Data Structure | Key Operation |
|---------|----------------|---------------|
| Pitch Class | `int (0-11)` | `mod 12` arithmetic |
| Interval | `(generic, quality)` | `invert_interval()` |
| Chord | `FrozenSet[int]` | set equality/transposition |
| Voice Leading | `list[int]` | `sum(abs(diff))` |

**Remember:** Choose representations based on operation type - numeric for speed, symbolic for analysis.