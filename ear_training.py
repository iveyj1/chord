"""
Ear training challenge generation and MIDI playback.

Generates single-note, interval, and chord challenges for ear training mode.
Plays target notes through MIDI output so the player hears them, then
the player reproduces them on their physical keyboard.

Challenge Dictionary Format:
    {
        "type": "note" | "interval" | "chord",
        "notes": ["C4", "E4"],          # target notes the player must play
        "clef": "G" | "F",              # display clef
        "label": "Perfect 5th",         # display label for the challenge
        "midi_numbers": [60, 64],       # MIDI note numbers to play back
    }

Difficulty controls the range of notes selected:
    1: Single octave, white keys  (C4-B4 treble, C3-B3 bass)
    2: Single octave, all keys
    3: Two octaves
    4: Full clef range
"""

import random
import time

import mido

from music import note_to_mnote, mnote_to_note, SCALES
from constants import MIDI_OUT_PORT_NAME

# ============================================================================
# MIDI Output
# ============================================================================

_midi_out = None


def open_midi_output(port_name: str | None = None) -> bool:
    """Open MIDI output port. Returns True on success."""
    global _midi_out
    if _midi_out is not None:
        return True
    target = port_name or MIDI_OUT_PORT_NAME
    try:
        _midi_out = mido.open_output(target)
        print(f"MIDI output opened: {target}")
        return True
    except (OSError, AttributeError, Exception) as e:
        print(f"MIDI output not available: {e}")
        _midi_out = None
        return False


def close_midi_output():
    """Close MIDI output port if open."""
    global _midi_out
    if _midi_out is not None:
        _midi_out.close()
        _midi_out = None


def play_notes(midi_numbers: list[int], duration: float = 0.6,
               velocity: int = 80, simultaneous: bool = True):
    """Play notes through MIDI output.

    Args:
        midi_numbers: MIDI note numbers to play.
        duration: Hold time in seconds.
        velocity: MIDI velocity (0-127).
        simultaneous: If True, all notes sound at once (chord).
                      If False, notes are arpeggiated with duration gap.
    """
    if _midi_out is None:
        return

    if simultaneous:
        for m in midi_numbers:
            _midi_out.send(mido.Message("note_on", note=m, velocity=velocity))
        time.sleep(duration)
        for m in midi_numbers:
            _midi_out.send(mido.Message("note_off", note=m, velocity=0))
    else:
        for m in midi_numbers:
            _midi_out.send(mido.Message("note_on", note=m, velocity=velocity))
            time.sleep(duration)
            _midi_out.send(mido.Message("note_off", note=m, velocity=0))
            time.sleep(0.05)  # tiny gap between arpeggiated notes


def play_challenge(challenge: dict, simultaneous: bool | None = None,
                   duration: float = 0.6):
    """Play a challenge's notes through MIDI output.

    For single notes, plays the note.
    For intervals, plays sequentially by default (ascending).
    For chords, plays simultaneously by default.
    """
    midi_numbers = challenge["midi_numbers"]
    if not midi_numbers:
        return

    if simultaneous is None:
        if challenge["type"] == "chord":
            simultaneous = True
        elif challenge["type"] == "interval":
            simultaneous = False
        else:
            simultaneous = True

    play_notes(midi_numbers, duration=duration, simultaneous=simultaneous)


# ============================================================================
# Range Definitions
# ============================================================================

# Difficulty -> (low_midi, high_midi) for each clef
# Treble clef ranges
_TREBLE_RANGES = {
    1: (60, 71),   # C4-B4  (single octave, white keys filtered separately)
    2: (60, 71),   # C4-B4  (single octave, all keys)
    3: (60, 83),   # C4-B5  (two octaves)
    4: (60, 86),   # C4-D6  (full treble range)
}

# Bass clef ranges
_BASS_RANGES = {
    1: (48, 59),   # C3-B3
    2: (48, 59),   # C3-B3
    3: (36, 59),   # C2-B3
    4: (30, 60),   # G1-C4
}

# White-key MIDI note numbers mod 12: C=0, D=2, E=4, F=5, G=7, A=9, B=11
_WHITE_KEY_PCS = {0, 2, 4, 5, 7, 9, 11}


def _midi_range_for(clef: str, difficulty: int) -> tuple[int, int]:
    """Return (low, high) MIDI range for clef and difficulty."""
    if clef == "G":
        return _TREBLE_RANGES.get(difficulty, _TREBLE_RANGES[4])
    return _BASS_RANGES.get(difficulty, _BASS_RANGES[4])


def _random_midi_in_range(low: int, high: int, white_only: bool = False) -> int:
    """Pick a random MIDI note within range, optionally white keys only."""
    candidates = list(range(low, high + 1))
    if white_only:
        candidates = [m for m in candidates if m % 12 in _WHITE_KEY_PCS]
    return random.choice(candidates)


def _note_name_for_midi(midi_num: int, prefer_sharp: bool = True) -> str:
    """Get a note name for a MIDI number."""
    candidates = mnote_to_note.get(midi_num, [])
    if not candidates:
        raise ValueError(f"No note name for MIDI {midi_num}")
    # Prefer natural
    for n in candidates:
        if len(n) >= 2 and n[-1].isdigit() and n[-2].isalpha() and n[-2].isupper():
            # Natural note like "C4"
            if len(n) == 2 or (len(n) == 3 and n[0].isalpha()):
                # Check it's truly natural (no accidental)
                pitch = n[:-1]
                if len(pitch) == 1:
                    return n
    if prefer_sharp:
        for n in candidates:
            if "#" in n:
                return n
    else:
        for n in candidates:
            if "b" in n:
                return n
    return candidates[0]


# ============================================================================
# Interval Definitions
# ============================================================================

# Semitone count -> interval name
INTERVAL_NAMES = {
    1: "Minor 2nd",
    2: "Major 2nd",
    3: "Minor 3rd",
    4: "Major 3rd",
    5: "Perfect 4th",
    6: "Tritone",
    7: "Perfect 5th",
    8: "Minor 6th",
    9: "Major 6th",
    10: "Minor 7th",
    11: "Major 7th",
    12: "Octave",
    13: "Minor 9th",
    14: "Major 9th",
}

# Which intervals are available at each difficulty
_INTERVAL_POOLS = {
    1: [3, 4, 5, 7],                              # m3, M3, P4, P5 (easy)
    2: [1, 2, 3, 4, 5, 6, 7],                     # up to P5 + tritone
    3: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],  # full octave
    4: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],  # through M9
}


# ============================================================================
# Challenge Generators
# ============================================================================

def _assign_clef_for_midi(midi_nums: list[int]) -> str:
    """Choose clef based on average pitch."""
    avg = sum(midi_nums) / len(midi_nums)
    return "G" if avg >= 60 else "F"


def generate_note_challenge(difficulty: int = 1,
                            prefer_clef: str | None = None) -> dict:
    """Generate a single-note ear training challenge.

    Args:
        difficulty: 1-4 controlling range and accidentals.
        prefer_clef: Force "G" or "F"; None picks randomly.
    """
    clef = prefer_clef or random.choice(["G", "F"])
    low, high = _midi_range_for(clef, difficulty)
    white_only = (difficulty <= 1)
    midi_num = _random_midi_in_range(low, high, white_only=white_only)
    note_name = _note_name_for_midi(midi_num)

    return {
        "type": "note",
        "notes": [note_name],
        "clef": clef,
        "label": note_name,
        "midi_numbers": [midi_num],
    }


def generate_interval_challenge(difficulty: int = 1,
                                prefer_clef: str | None = None) -> dict:
    """Generate an interval ear training challenge.

    The lower note is chosen randomly within range, then the interval
    is added upward. If the result exceeds range, the interval goes downward.

    Args:
        difficulty: 1-4 controlling interval pool and range.
        prefer_clef: Force "G" or "F"; None picks randomly.
    """
    clef = prefer_clef or random.choice(["G", "F"])
    low, high = _midi_range_for(clef, difficulty)
    white_only = (difficulty <= 1)

    pool = _INTERVAL_POOLS.get(difficulty, _INTERVAL_POOLS[4])
    semitones = random.choice(pool)

    # Pick root, ensuring interval fits in range
    max_root = high - semitones
    min_root = low
    if max_root < min_root:
        # Interval too large for range going up — go downward
        min_root = low + semitones
        max_root = high
        if min_root > max_root:
            # Fallback: just use the range boundaries
            min_root = low
            max_root = high

        root_midi = _random_midi_in_range(min_root, max_root, white_only=white_only)
        second_midi = root_midi - semitones
    else:
        root_midi = _random_midi_in_range(min_root, max_root, white_only=white_only)
        second_midi = root_midi + semitones

    midi_nums = sorted([root_midi, second_midi])
    notes = [_note_name_for_midi(m) for m in midi_nums]
    clef = _assign_clef_for_midi(midi_nums)

    interval_name = INTERVAL_NAMES.get(semitones, f"{semitones} semitones")

    return {
        "type": "interval",
        "notes": notes,
        "clef": clef,
        "label": interval_name,
        "midi_numbers": midi_nums,
    }


def generate_chord_challenge(difficulty: int = 1,
                             prefer_clef: str | None = None) -> dict:
    """Generate a chord ear training challenge.

    Uses triads at lower difficulties, seventh chords at higher.

    Args:
        difficulty: 1-4 controlling chord type and range.
        prefer_clef: Force "G" or "F"; None picks randomly.
    """
    clef = prefer_clef or random.choice(["G", "F"])
    low, high = _midi_range_for(clef, difficulty)
    white_only = (difficulty <= 1)

    # Choose chord quality
    if difficulty <= 2:
        intervals = random.choice([
            [0, 4, 7],   # major
            [0, 3, 7],   # minor
        ])
        quality_names = {(0, 4, 7): "Major", (0, 3, 7): "Minor"}
    else:
        intervals = random.choice([
            [0, 4, 7],       # major
            [0, 3, 7],       # minor
            [0, 3, 6],       # diminished
            [0, 4, 8],       # augmented
            [0, 4, 7, 10],   # dom7
            [0, 3, 7, 10],   # min7
        ])
        quality_names = {
            (0, 4, 7): "Major", (0, 3, 7): "Minor",
            (0, 3, 6): "Diminished", (0, 4, 8): "Augmented",
            (0, 4, 7, 10): "Dom 7th", (0, 3, 7, 10): "Min 7th",
        }

    max_span = intervals[-1]
    max_root = high - max_span
    if max_root < low:
        max_root = low

    root_midi = _random_midi_in_range(low, min(max_root, high), white_only=white_only)
    midi_nums = [root_midi + iv for iv in intervals]

    # Clamp any that exceed range
    midi_nums = [max(low, min(high, m)) for m in midi_nums]
    notes = [_note_name_for_midi(m) for m in midi_nums]
    clef = _assign_clef_for_midi(midi_nums)

    root_name = _note_name_for_midi(root_midi)
    root_pc = root_name[:-1]  # strip octave
    quality = quality_names.get(tuple(intervals), "Chord")
    label = f"{root_pc} {quality}"

    return {
        "type": "chord",
        "notes": notes,
        "clef": clef,
        "label": label,
        "midi_numbers": midi_nums,
    }


def generate_challenge(mode: str = "note", difficulty: int = 1,
                       prefer_clef: str | None = None) -> dict:
    """Generate an ear training challenge.

    Args:
        mode: "note", "interval", or "chord".
        difficulty: 1-4 controlling range and complexity.
        prefer_clef: Force "G" or "F"; None picks randomly.
    """
    if mode == "interval":
        return generate_interval_challenge(difficulty, prefer_clef)
    elif mode == "chord":
        return generate_chord_challenge(difficulty, prefer_clef)
    else:
        return generate_note_challenge(difficulty, prefer_clef)
