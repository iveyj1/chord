"""
Music theory data and note/MIDI mappings.

=============================================================================
DATA MODEL DOCUMENTATION
=============================================================================

Note Representation:
    A note is a string in the format: "{pitch_class}{octave}"
    - pitch_class: One of C, D, E, F, G, A, B (optionally with # or b)
    - octave: Integer 0-8 (Middle C is C4, A440 is A4)
    
    Examples: "C4", "F#5", "Bb3", "A0"
    
    Note: Both sharp (#) and flat (b) spellings are supported for the same pitch.
    For example, "C#4" and "Db4" both map to MIDI note 61.

MIDI Number (mnote):
    Integer 0-127 representing absolute pitch.
    - A0 = 21, C4 (middle C) = 60, A4 (440Hz) = 69, C8 = 108
    
Staff Position:
    Integer representing vertical position on staff in half-line units.
    - 0 = center of grand staff (between treble and bass)
    - Positive = upward, Negative = downward
    - Each staff line or space is 1 unit apart
    
Clef:
    String "G" (treble) or "F" (bass)
    - Treble clef: typically C4-C6, staff lines E4-F5
    - Bass clef: typically C2-C4, staff lines G2-A3

Chord (as returned by generate_chord()):
    Dictionary with keys:
    - notes: List[str] - Note names (e.g., ["C4", "E4", "G4"])
    - clef: str - "G" or "F"  
    - chord_name: str - Display name (e.g., "C major")
    - key: str - Musical key (e.g., "C", "G", "Am") [placeholder]
    - scale_degree: str - Roman numeral (e.g., "I", "V") [placeholder]

=============================================================================
MODULE CONTENTS
=============================================================================

This module contains:
- note_to_mnote: Map note names (e.g., "C4") to MIDI numbers
- mnote_to_note: Reverse mapping (MIDI number to list of note names)
- note_to_position: Map notes to staff positions for each clef
- Music theory constants for future chord generation
"""

from constants import (
    BASS_CLEF_BOTTOM_Y, TREBLE_CLEF_BOTTOM_Y,
    BASS_CLEF_REFERENCE_MIDI, TREBLE_CLEF_REFERENCE_MIDI,
    BASS_CLEF_REFERENCE_POSITION, TREBLE_CLEF_REFERENCE_POSITION,
    SEMITONE_TO_STAFF_POSITION, MIN_MIDI_NOTE, MAX_MIDI_NOTE
)

# Try to import musthe, but handle gracefully if not available
try:
    import musthe
    MUSTHE_AVAILABLE = True
except ImportError:
    MUSTHE_AVAILABLE = False
    print("Warning: musthe library not available. Install with: pip install musthe")

# =============================================================================
# Note <-> MIDI Number Mappings
# =============================================================================

note_to_mnote = {
    # A0 to B0 (MIDI 21–23)
    "A0": 21,
    "A#0": 22, "Bb0": 22,
    "B0": 23,
    
    # C1 to B1 (MIDI 24–35)
    "C1": 24,
    "C#1": 25, "Db1": 25,
    "D1": 26,
    "D#1": 27, "Eb1": 27,
    "E1": 28,
    "F1": 29,
    "F#1": 30, "Gb1": 30,
    "G1": 31,
    "G#1": 32, "Ab1": 32,
    "A1": 33,
    "A#1": 34, "Bb1": 34,
    "B1": 35,
    
    # C2 to B2 (MIDI 36–47)
    "C2": 36,
    "C#2": 37, "Db2": 37,
    "D2": 38,
    "D#2": 39, "Eb2": 39,
    "E2": 40,
    "F2": 41,
    "F#2": 42, "Gb2": 42,
    "G2": 43,
    "G#2": 44, "Ab2": 44,
    "A2": 45,
    "A#2": 46, "Bb2": 46,
    "B2": 47,
    
    # C3 to B3 (MIDI 48–59)
    "C3": 48,
    "C#3": 49, "Db3": 49,
    "D3": 50,
    "D#3": 51, "Eb3": 51,
    "E3": 52,
    "F3": 53,
    "F#3": 54, "Gb3": 54,
    "G3": 55,
    "G#3": 56, "Ab3": 56,
    "A3": 57,
    "A#3": 58, "Bb3": 58,
    "B3": 59,
    
    # C4 to B4 (MIDI 60–71)
    "C4": 60,
    "C#4": 61, "Db4": 61,
    "D4": 62,
    "D#4": 63, "Eb4": 63,
    "E4": 64,
    "F4": 65,
    "F#4": 66, "Gb4": 66,
    "G4": 67,
    "G#4": 68, "Ab4": 68,
    "A4": 69,
    "A#4": 70, "Bb4": 70,
    "B4": 71,
    
    # C5 to B5 (MIDI 72–83)
    "C5": 72,
    "C#5": 73, "Db5": 73,
    "D5": 74,
    "D#5": 75, "Eb5": 75,
    "E5": 76,
    "F5": 77,
    "F#5": 78, "Gb5": 78,
    "G5": 79,
    "G#5": 80, "Ab5": 80,
    "A5": 81,
    "A#5": 82, "Bb5": 82,
    "B5": 83,
    
    # C6 to B6 (MIDI 84–95)
    "C6": 84,
    "C#6": 85, "Db6": 85,
    "D6": 86,
    "D#6": 87, "Eb6": 87,
    "E6": 88,
    "F6": 89,
    "F#6": 90, "Gb6": 90,
    "G6": 91,
    "G#6": 92, "Ab6": 92,
    "A6": 93,
    "A#6": 94, "Bb6": 94,
    "B6": 95,
    
    # C7 to B7 (MIDI 96–107)
    "C7": 96,
    "C#7": 97, "Db7": 97,
    "D7": 98,
    "D#7": 99, "Eb7": 99,
    "E7": 100,
    "F7": 101,
    "F#7": 102, "Gb7": 102,
    "G7": 103,
    "G#7": 104, "Ab7": 104,
    "A7": 105,
    "A#7": 106, "Bb7": 106,
    "B7": 107,
    
    # C8 (MIDI 108)
    "C8": 108
}

# Reverse mapping: MIDI number -> list of note names (e.g., 61 -> ["C#4", "Db4"])
mnote_to_note = {}
for note, keynum in note_to_mnote.items():
    mnote_to_note.setdefault(keynum, []).append(note)

# =============================================================================
# Enharmonic Mapping (for musthe integration)
# =============================================================================

# Maps enharmonic equivalents that musthe generates but we don't have in our main mapping
ENHARMONIC_EQUIVALENTS = {
    # Double flats to flats
    'Cbb': 'Bb',
    'Dbb': 'C', 
    'Ebb': 'Db',
    'Fbb': 'Eb',
    'Gbb': 'F',
    'Abb': 'G',
    'Bbb': 'A',
    
    # Double sharps to sharps  
    'C##': 'D',
    'D##': 'E',
    'E##': 'F#',
    'F##': 'G',
    'G##': 'A',
    'A##': 'B',
    'B##': 'C#',
    
    # Rare flats that map to our preferred spelling
    'Cb': 'B',
    'Fb': 'E', 
    'Eb': 'Eb',  # Already in mapping
    'Ab': 'Ab',  # Already in mapping
    'Db': 'Db',  # Already in mapping
    'Gb': 'F#',  # Map to sharp spelling
    'Bb': 'Bb',  # Already in mapping
    
    # Other enharmonic equivalents
    'D#': 'D#',  # Already in mapping
    'A#': 'A#',  # Already in mapping
    'E#': 'F',
    'B#': 'C',
}

def normalize_note(note_str: str) -> str:
    """
    Normalize note string to our preferred spelling for MIDI mapping.
    
    Args:
        note_str: Note string like "Cb4", "E#", "Gbb5"
        
    Returns:
        Normalized note string that exists in note_to_mnote
    """
    if note_str in note_to_mnote:
        return note_str
    
    # Extract pitch class and octave
    if len(note_str) >= 2:
        # Handle cases like "Cb4", "E#5", "Gbb3"
        if note_str[-1].isdigit():
            octave = note_str[-1]
            pitch_class = note_str[:-1]
        else:
            octave = ''
            pitch_class = note_str
    else:
        return note_str  # Invalid format, return as-is
    
    # Map enharmonic equivalents
    normalized_pitch = ENHARMONIC_EQUIVALENTS.get(pitch_class, pitch_class)
    
    normalized_note = f"{normalized_pitch}{octave}"
    
    # If still not found, try more mappings
    if normalized_note not in note_to_mnote:
        # Special case: map Gb to F#
        if normalized_pitch == 'Gb':
            normalized_note = f"F#{octave}"
        elif normalized_pitch == 'Cb':
            normalized_note = f"B{int(octave)-1}" if octave.isdigit() else f"B{octave}"
    
    return normalized_note if normalized_note in note_to_mnote else note_str

# =============================================================================
# Mathematical Staff Position Mapping
# =============================================================================

def note_to_staff_position(note: str, clef: str) -> int:
    """
    Calculate staff position for a note using a mathematical formula.
    
    Args:
        note: Note string (e.g., "C4", "F#5", "Bb3")
        clef: Either "F" (bass) or "G" (treble)
        
    Returns:
        Integer representing vertical position on staff in half-line units
        (relative to screen center)
        
    Formula:
        position = reference_position + (midi_note - reference_midi) * (7/12)
        
    Where:
        - reference_position: where the clef's bottom line sits relative to center
        - reference_midi: MIDI note number for the clef's bottom line  
        - 7/12: conversion factor (7 staff positions per 12 semitones/octave)
        
    Musical Intuition:
        - One octave (12 semitones) spans 7 staff positions (lines and spaces)
        - This matches the diatonic scale: C-D-E-F-G-A-B occupies 7 positions
        - Each semitone moves 7/12 ≈ 0.583 staff positions
        - Accidentals (sharps/flats) fall between the natural note positions
    """
    # Get MIDI number for the note
    midi_note = note_to_mnote.get(note)
    if midi_note is None:
        raise ValueError(f"Unknown note: {note}")
    
    # Select appropriate reference points based on clef
    if clef == "F":  # Bass clef
        reference_midi = BASS_CLEF_REFERENCE_MIDI
        reference_position = BASS_CLEF_REFERENCE_POSITION
    elif clef == "G":  # Treble clef  
        reference_midi = TREBLE_CLEF_REFERENCE_MIDI
        reference_position = TREBLE_CLEF_REFERENCE_POSITION
    else:
        raise ValueError(f"Unknown clef: {clef}")
    
    # Calculate position using the formula: 7 staff positions per octave
    semitone_difference = midi_note - reference_midi
    position = reference_position + semitone_difference * (7 / 12)
    
    return int(round(position))

# Legacy compatibility wrapper - generates position table on demand
def get_note_to_position_map() -> dict:
    """
    Generate the traditional note_to_position mapping table using the formula.
    Maintains backward compatibility with existing code.
    """
    positions = {"F": {}, "G": {}}
    
    # Generate range of notes that are typically used
    for note, midi_num in note_to_mnote.items():
        if MIN_MIDI_NOTE <= midi_num <= MAX_MIDI_NOTE:
            # Calculate position for both clefs
            for clef in ["F", "G"]:
                try:
                    positions[clef][note] = note_to_staff_position(note, clef)
                except:
                    # Skip any problematic notes
                    pass
    
    return positions

# Create the traditional table for backward compatibility
note_to_position = get_note_to_position_map()

# =============================================================================
# Music Theory Data (for future chord generation)
# =============================================================================

# Chromatic scale using flats (for consistent indexing)
CHROMATIC_SCALE = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

# Enharmonic equivalents
SHARP_TO_FLAT = {"C#": "Db", "D#": "Eb", "F#": "Gb", "G#": "Ab", "A#": "Bb"}
FLAT_TO_SHARP = {v: k for k, v in SHARP_TO_FLAT.items()}

# Keys that prefer sharps vs flats
SHARP_KEYS = {"G", "D", "A", "E", "B", "F#", "C#m", "G#m", "D#m", "A#m"}
FLAT_KEYS = {"F", "Bb", "Eb", "Ab", "Db", "Gb", "Fm", "Cm", "Gm", "Dm"}

# Chord intervals (semitones from root)
CHORD_INTERVALS = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "diminished": [0, 3, 6],
    "augmented": [0, 4, 8],
    "dominant7": [0, 4, 7, 10],
    "major7": [0, 4, 7, 11],
    "minor7": [0, 3, 7, 10],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
}

# Diatonic chord qualities by scale degree
DIATONIC_MAJOR = {
    "I": "major", "ii": "minor", "iii": "minor", "IV": "major",
    "V": "major", "vi": "minor", "vii°": "diminished"
}

DIATONIC_MINOR = {
    "i": "minor", "ii°": "diminished", "III": "major", "iv": "minor",
    "v": "minor", "VI": "major", "VII": "major"
}

# Major scales
SCALES = {
    "C": ["C", "D", "E", "F", "G", "A", "B"],
    "G": ["G", "A", "B", "C", "D", "E", "F#"],
    "D": ["D", "E", "F#", "G", "A", "B", "C#"],
    "A": ["A", "B", "C#", "D", "E", "F#", "G#"],
    "E": ["E", "F#", "G#", "A", "B", "C#", "D#"],
    "B": ["B", "C#", "D#", "E", "F#", "G#", "A#"],
    "F": ["F", "G", "A", "Bb", "C", "D", "E"],
    "Bb": ["Bb", "C", "D", "Eb", "F", "G", "A"],
    "Eb": ["Eb", "F", "G", "Ab", "Bb", "C", "D"],
    "Ab": ["Ab", "Bb", "C", "Db", "Eb", "F", "G"],
}

# =============================================================================
# Musthe Integration Functions
# =============================================================================

def assign_clef(notes: list[str]) -> str:
    """Assign appropriate clef based on note range"""
    if not notes:
        return "G"
    
    # Get average position to determine best clef
    avg_midi = sum(note_to_mnote.get(note, 60) for note in notes) / len(notes)
    
    # Use treble clef for higher notes, bass for lower
    return "G" if avg_midi >= 60 else "F"

def extract_key_from_chord(musthe_chord) -> str:
    """Extract key from musthe chord (placeholder for now)"""
    # For Phase 1, return root note as key
    if hasattr(musthe_chord, 'notes') and musthe_chord.notes:
        return str(musthe_chord.notes[0])
    return "C"

def get_scale_degree(musthe_chord, key: str) -> str:
    """Get scale degree for chord (placeholder for now)"""
    # For Phase 1, return I as placeholder
    return "I"

def musthe_chord_to_dict(musthe_chord, octave: int = 4) -> dict:
    """Convert musthe.Chord to existing chord dict format"""
    if not MUSTHE_AVAILABLE:
        raise ImportError("musthe library not available")
    
    # Get notes from musthe chord - notes is a property, not method
    chord_notes = musthe_chord.notes
    notes = []
    for note in chord_notes:
        # Convert to string with our desired octave
        # Use string representation and modify octave
        note_str = str(note)  # This gives us something like "C", "Eb", etc.
        note_with_octave = f"{note_str}{octave}"
        # Normalize to our preferred spelling
        normalized_note = normalize_note(note_with_octave)
        notes.append(normalized_note)
    
    return {
        "notes": notes,
        "clef": assign_clef(notes),
        "chord_name": str(musthe_chord),
        "key": extract_key_from_chord(musthe_chord),
        "scale_degree": get_scale_degree(musthe_chord, extract_key_from_chord(musthe_chord))
    }

def chord_dict_to_musthe(chord_dict: dict):
    """Convert existing chord dict to musthe.Chord"""
    if not MUSTHE_AVAILABLE:
        raise ImportError("musthe library not available")
    
    if not chord_dict.get("notes"):
        return None
    
    # Extract root pitch class from first note
    first_note = chord_dict["notes"][0]
    pitch_class = first_note[:-1]  # Remove octave
    
    # Create basic chord (enhanced in later phases)
    try:
        return musthe.Chord(pitch_class)
    except:
        # Fallback to C major if chord creation fails
        return musthe.Chord('C')

def get_diatonic_quality(scale_degree: int) -> str:
    """Get diatonic chord quality for major scale degree"""
    qualities = ['', 'm', 'm', '', '', 'm', 'dim']  # I, ii, iii, IV, V, vi, vii°
    return qualities[scale_degree % 7]

def is_musthe_available() -> bool:
    """Check if musthe library is available"""
    return MUSTHE_AVAILABLE
