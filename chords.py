"""
Chord generation for the piano learning game.

This module handles:
- Test chord sequences for development
- Future: intelligent chord/note generation with difficulty levels

Chord Dictionary Format:
    {
        "notes": ["C4", "E4", "G4"],  # List of note names to play
        "clef": "G",                   # "G" (treble) or "F" (bass)
        "chord_name": "C major",       # Display name for UI
        "key": "C",                    # Musical key (future use)
        "scale_degree": "I",           # Roman numeral (future use)
    }

Difficulty Levels (planned):
    1. Single notes (white keys only)
    2. Single notes (with accidentals)
    3. Intervals (2 notes)
    4. Triads (3 notes)
    5. Seventh chords (4 notes)
    6. Both clefs simultaneously
"""

import math
import random

from music import (
    SCALES,
    FLAT_KEYS,
    mnote_to_note,
    is_musthe_available,
)

# =============================================================================
# Test Chord Sequence
# =============================================================================

# Fixed test sequence for development/testing
# Each chord: {"notes": [...], "clef": "G"|"F", "name": "display name"}
TEST_CHORD_SEQUENCE = [
    # Single notes - treble clef
    {"notes": ["C4"], "clef": "G", "name": "Middle C (treble)"},
    {"notes": ["E4"], "clef": "G", "name": "E4"},
    {"notes": ["G4"], "clef": "G", "name": "G4"},
    {"notes": ["C5"], "clef": "G", "name": "C5"},
    # Basic triads - treble clef
    {"notes": ["C4", "E4", "G4"], "clef": "G", "name": "C major"},
    {"notes": ["D4", "F4", "A4"], "clef": "G", "name": "D minor"},
    {"notes": ["E4", "G4", "B4"], "clef": "G", "name": "E minor"},
    {"notes": ["F4", "A4", "C5"], "clef": "G", "name": "F major"},
    {"notes": ["G4", "B4", "D5"], "clef": "G", "name": "G major"},
    {"notes": ["A4", "C5", "E5"], "clef": "G", "name": "A minor"},
    # With accidentals
    {"notes": ["C4", "Eb4", "G4"], "clef": "G", "name": "C minor"},
    {"notes": ["F#4", "A4", "C#5"], "clef": "G", "name": "F# minor"},
    {"notes": ["Bb4", "D5", "F5"], "clef": "G", "name": "Bb major"},
    # Ledger lines - high treble
    {"notes": ["A5"], "clef": "G", "name": "A5 (1 ledger)"},
    {"notes": ["C6"], "clef": "G", "name": "C6 (2 ledgers)"},
    # Ledger lines - low treble
    {"notes": ["A3"], "clef": "G", "name": "A3 (2 ledgers)"},
    {"notes": ["C4"], "clef": "G", "name": "C4 (middle C ledger)"},
    # Bass clef - on staff
    {"notes": ["C3"], "clef": "F", "name": "C3 bass (on staff)"},
    {"notes": ["F2", "A2", "C3"], "clef": "F", "name": "F major bass"},
    {"notes": ["G2", "B2", "D3"], "clef": "F", "name": "G major bass"},
    # Bass clef - ledger lines above (toward middle C)
    {"notes": ["C4"], "clef": "F", "name": "Middle C (bass)"},
    {"notes": ["E4"], "clef": "F", "name": "E4 bass (2 ledgers)"},
    {"notes": ["G3", "C4", "E4"], "clef": "F", "name": "C major bass (ledgers above)"},
    # Bass clef - ledger lines below
    {"notes": ["E2"], "clef": "F", "name": "E2 bass (1 ledger below)"},
    {"notes": ["C2"], "clef": "F", "name": "C2 bass (2 ledgers below)"},
    {"notes": ["A1"], "clef": "F", "name": "A1 bass (3 ledgers below)"},
    {"notes": ["C2", "E2", "G2"], "clef": "F", "name": "C major low bass"},
]

# =============================================================================
# Chord Generator State
# =============================================================================

_chord_index = 0

# Musical range hard limits per clef (kept strict)
CLEF_MIDI_LIMITS = {
    "G": (60, 86),  # C4-E6
    "F": (30, 60),  # G1-C4
}

# Statistical tuning constants
CLEF_STAY_PROB = 0.90
ROOT_STEP_SIGMA = 3.5
ROOT_MEAN_REVERT_WEIGHT = 0.02
SOFTMAX_TEMP = 1.5
LEAP_PENALTY_WEIGHT = 1.0
EDGE_PENALTY_WEIGHT = 0.5

LINE_CHORD_COUNT = 12

FUNCTION_TRANSITIONS = {
    "T": [("T", 0.20), ("PD", 0.60), ("D", 0.20)],
    "PD": [("PD", 0.10), ("D", 0.75), ("T", 0.15)],
    "D": [("T", 0.80), ("D", 0.10), ("PD", 0.10)],
}

FUNCTION_DEGREES = {
    "T": [0, 5, 2],   # I, vi, iii
    "PD": [1, 3],     # ii, IV
    "D": [4, 6],      # V, vii
}

_PITCH_CLASS_TO_PC = {
    "C": 0,
    "B#": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "Fb": 4,
    "E#": 5,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
    "Cb": 11,
}

_generation_state = {
    "line_key": None,
    "line_position": 0,
    "last_function": None,
    "last_clef": None,
    "last_root_midi": None,
    "last_voicing_midis": None,
}

def _weighted_choice(weighted_items):
    total = sum(weight for _, weight in weighted_items)
    if total <= 0:
        return weighted_items[0][0]
    pick = random.random() * total
    run = 0.0
    for item, weight in weighted_items:
        run += weight
        if pick <= run:
            return item
    return weighted_items[-1][0]


def _sample_clef(prefer_clef: str | None = None) -> str:
    if prefer_clef in ("G", "F"):
        return prefer_clef

    last_clef = _generation_state["last_clef"]
    if last_clef not in ("G", "F"):
        return random.choice(["G", "F"])

    if random.random() < CLEF_STAY_PROB:
        return last_clef
    return "F" if last_clef == "G" else "G"


def _choose_line_key() -> str:
    # Keep to commonly taught keys to reduce accidental load.
    weighted_keys = [
        ("C", 0.24),
        ("G", 0.16),
        ("F", 0.16),
        ("D", 0.12),
        ("Bb", 0.12),
        ("A", 0.08),
        ("Eb", 0.07),
        ("E", 0.05),
    ]
    return _weighted_choice(weighted_keys)


def start_new_line_generation(key: str | None = None):
    """Reset phrase-level generation state and choose a new line key."""
    _generation_state["line_key"] = key if key in SCALES else _choose_line_key()
    _generation_state["line_position"] = 0
    _generation_state["last_function"] = None
    _generation_state["last_clef"] = None
    _generation_state["last_root_midi"] = None
    _generation_state["last_voicing_midis"] = None


def _ensure_line_state():
    if _generation_state["line_key"] is None:
        start_new_line_generation()


def _sample_function_for_step() -> str:
    step = _generation_state["line_position"]
    last_function = _generation_state["last_function"]

    if step == 0:
        return "T"
    if step == LINE_CHORD_COUNT - 2:
        return "D"
    if step == LINE_CHORD_COUNT - 1:
        return "T"

    if last_function is None:
        return _weighted_choice([("T", 0.45), ("PD", 0.35), ("D", 0.20)])

    return _weighted_choice(FUNCTION_TRANSITIONS[last_function])


def _choose_scale_degree(function_name: str) -> int:
    candidates = FUNCTION_DEGREES[function_name]
    # slight tonic/root preference
    if function_name == "T":
        return _weighted_choice([(0, 0.55), (5, 0.30), (2, 0.15)])
    if function_name == "PD":
        return _weighted_choice([(1, 0.60), (3, 0.40)])
    return _weighted_choice([(4, 0.70), (6, 0.30)])


def _preferred_note_name_for_midi(midi_note: int, key: str) -> str:
    candidates = mnote_to_note.get(midi_note)
    if not candidates:
        raise ValueError(f"No note name available for MIDI {midi_note}")

    prefer_flats = key in FLAT_KEYS
    natural = [n for n in candidates if len(n) >= 2 and n[1].isdigit()]
    if natural:
        return natural[0]

    if prefer_flats:
        flat_names = [n for n in candidates if "b" in n]
        if flat_names:
            return flat_names[0]
    else:
        sharp_names = [n for n in candidates if "#" in n]
        if sharp_names:
            return sharp_names[0]

    return candidates[0]


def _clamp_midi_to_clef(midi_note: int, clef: str) -> int:
    lower, upper = CLEF_MIDI_LIMITS[clef]
    while midi_note < lower:
        midi_note += 12
    while midi_note > upper:
        midi_note -= 12
    return max(lower, min(upper, midi_note))


def _candidate_roots_for_pitch_class(pitch_class: str, clef: str) -> list[int]:
    pc = _PITCH_CLASS_TO_PC[pitch_class]
    lower, upper = CLEF_MIDI_LIMITS[clef]
    return [m for m in range(lower, upper + 1) if m % 12 == pc]


def _sample_root_midi(pitch_class: str, clef: str) -> int:
    candidates = _candidate_roots_for_pitch_class(pitch_class, clef)
    if not candidates:
        lower, upper = CLEF_MIDI_LIMITS[clef]
        return (lower + upper) // 2

    lower, upper = CLEF_MIDI_LIMITS[clef]
    center = (lower + upper) / 2.0
    last_root = _generation_state["last_root_midi"]
    if last_root is None:
        mean = center
    else:
        mean = (1.0 - ROOT_MEAN_REVERT_WEIGHT) * last_root + ROOT_MEAN_REVERT_WEIGHT * center

    weighted = []
    for candidate in candidates:
        dist = candidate - mean
        weight = math.exp(-(dist * dist) / (2.0 * ROOT_STEP_SIGMA * ROOT_STEP_SIGMA))
        weighted.append((candidate, weight))
    return _weighted_choice(weighted)


def _build_interval_set(difficulty: int, quality: str | None = None) -> list[int]:
    if difficulty <= 1:
        return [0]
    if difficulty == 2:
        return [0]
    if difficulty == 3:
        return [0, random.choice([3, 4, 7, 8, 9])]

    if quality == "dim":
        triad = [0, 3, 6]
        seventh = [0, 3, 6, 10]
    elif quality == "min":
        triad = [0, 3, 7]
        seventh = [0, 3, 7, 10]
    else:
        triad = [0, 4, 7]
        seventh = [0, 4, 7, 10]

    if difficulty == 4:
        return triad

    if difficulty >= 5:
        if random.random() < 0.75:
            return seventh
        return triad

    return triad


def _generate_voicing_candidates(root_midi: int, intervals: list[int], clef: str) -> list[list[int]]:
    lower, upper = CLEF_MIDI_LIMITS[clef]
    base = [root_midi + interval for interval in intervals]
    candidates = []

    for inversion in range(len(base)):
        inv = base[:]
        for idx in range(inversion):
            inv[idx] += 12
        inv = sorted(inv)

        for octave_shift in (-24, -12, 0, 12, 24):
            shifted = [note + octave_shift for note in inv]
            if all(lower <= note <= upper for note in shifted):
                candidates.append(sorted(shifted))

    # De-duplicate while preserving order
    unique = []
    seen = set()
    for voicing in candidates:
        key = tuple(voicing)
        if key not in seen:
            seen.add(key)
            unique.append(voicing)
    return unique


def _voice_motion_cost(candidate: list[int], previous: list[int] | None) -> float:
    if not previous:
        return 0.0
    cost = 0.0
    for note in candidate:
        moves = [abs(note - prev_note) for prev_note in previous]
        best = min(moves) if moves else 0.0
        cost += best
        if best > 7:
            cost += (best - 7) * LEAP_PENALTY_WEIGHT
    return cost


def _edge_penalty(candidate: list[int], clef: str) -> float:
    lower, upper = CLEF_MIDI_LIMITS[clef]
    penalty = 0.0
    for note in candidate:
        dist_to_edge = min(note - lower, upper - note)
        if dist_to_edge < 4:
            penalty += (4 - dist_to_edge) * EDGE_PENALTY_WEIGHT
    return penalty


def _choose_voicing(root_midi: int, intervals: list[int], clef: str) -> list[int]:
    candidates = _generate_voicing_candidates(root_midi, intervals, clef)
    if not candidates:
        fallback = [_clamp_midi_to_clef(root_midi + interval, clef) for interval in intervals]
        return sorted(fallback)

    previous = _generation_state["last_voicing_midis"]
    weighted_candidates = []
    for candidate in candidates:
        cost = _voice_motion_cost(candidate, previous)
        cost += _edge_penalty(candidate, clef)
        if _generation_state["last_root_midi"] is not None:
            cost += abs(candidate[0] - _generation_state["last_root_midi"]) * 0.35
        weight = math.exp(-cost / max(0.01, SOFTMAX_TEMP))
        weighted_candidates.append((candidate, weight))
    return _weighted_choice(weighted_candidates)


def _quality_for_degree(scale_degree: int) -> str:
    # major-key diatonic quality
    if scale_degree in (0, 3, 4):
        return "maj"
    if scale_degree in (1, 2, 5):
        return "min"
    return "dim"


def _build_chord_name(key: str, scale_degree: int, quality: str, notes: list[str]) -> str:
    degree_labels = ["I", "ii", "iii", "IV", "V", "vi", "vii°"]
    quality_label = {
        "maj": "major",
        "min": "minor",
        "dim": "diminished",
    }.get(quality, quality)
    return f"{key} {degree_labels[scale_degree]} ({quality_label}) {'-'.join(notes)}"


def _advance_generation_state(clef: str, root_midi: int, voicing_midis: list[int], function_name: str):
    _generation_state["last_clef"] = clef
    _generation_state["last_root_midi"] = root_midi
    _generation_state["last_voicing_midis"] = sorted(voicing_midis)
    _generation_state["last_function"] = function_name
    _generation_state["line_position"] = (_generation_state["line_position"] + 1) % LINE_CHORD_COUNT
    if _generation_state["line_position"] == 0:
        _generation_state["line_key"] = _choose_line_key()
        _generation_state["last_function"] = None


def _generate_statistical_chord(difficulty: int = 1, prefer_clef: str | None = None):
    _ensure_line_state()

    line_key = _generation_state["line_key"]
    function_name = _sample_function_for_step()
    scale_degree = _choose_scale_degree(function_name)
    pitch_class = SCALES[line_key][scale_degree]
    quality = _quality_for_degree(scale_degree)

    clef = _sample_clef(prefer_clef)
    root_midi = _sample_root_midi(pitch_class, clef)
    intervals = _build_interval_set(difficulty, quality)
    voicing_midis = _choose_voicing(root_midi, intervals, clef)
    notes = [_preferred_note_name_for_midi(midi_note, line_key) for midi_note in voicing_midis]

    # difficulty 2 should expose more chromatic vocabulary
    if difficulty == 2 and random.random() < 0.35:
        chromatic = random.choice([-1, 1])
        chromatic_midi = _clamp_midi_to_clef(voicing_midis[0] + chromatic, clef)
        voicing_midis = [chromatic_midi]
        notes = [_preferred_note_name_for_midi(chromatic_midi, line_key)]

    chord_name = _build_chord_name(line_key, scale_degree, quality, notes)
    scale_degree_name = ["I", "ii", "iii", "IV", "V", "vi", "vii°"][scale_degree]

    _advance_generation_state(clef, root_midi, voicing_midis, function_name)

    return {
        "notes": notes,
        "clef": clef,
        "chord_name": chord_name,
        "key": line_key,
        "scale_degree": scale_degree_name,
    }

def generate_chord(difficulty=1, prefer_clef: str | None = None):
    """
    Generate a chord/note according to difficulty level.
    difficulty: 1-6
        1: Single notes (white keys)
        2: Single notes (with accidentals)
        3: Intervals (2 notes)
        4: Triads (3 notes)
        5: Seventh chords (4 notes)
        6: Both clefs (random)
    
    Phase 1 Integration: Uses musthe library when available for difficulty >= 2
    
    Args:
        difficulty: 1-6 difficulty level
        prefer_clef: If 'G' or 'F', biases toward that clef; None for equal probability
    """
    global _chord_index

    # For development/testing, use fixed test sequence if difficulty is None or 0
    if difficulty is None or difficulty == 0:
        chord = TEST_CHORD_SEQUENCE[_chord_index % len(TEST_CHORD_SEQUENCE)]
        _chord_index += 1
        return {
            "notes": chord["notes"],
            "clef": chord["clef"],
            "chord_name": chord["name"],
            "key": "C",
            "scale_degree": "I",
        }

    if should_use_musthe(difficulty):
        return generate_musthe_chord(difficulty, prefer_clef=prefer_clef)

    return _generate_statistical_chord(difficulty=difficulty, prefer_clef=prefer_clef)


def reset_chord_sequence():
    """Reset to the beginning of the test sequence."""
    global _chord_index
    _chord_index = 0
    start_new_line_generation()


def get_sequence_length():
    """Return the number of chords in the test sequence."""
    return len(TEST_CHORD_SEQUENCE)


def get_current_index():
    global _chord_index
    """Return the current position in sequence (0-based)."""
    return _chord_index % len(TEST_CHORD_SEQUENCE)


# =============================================================================
# Musthe Integration Functions (Phase 1)
# =============================================================================

def generate_musthe_chord(difficulty_level: int = 1, key: str = 'C', prefer_clef: str | None = None):
    """
    Generate single chords using musthe, respecting difficulty.
    
    Args:
        difficulty_level: 1-6 scale controlling chord complexity
        key: Musical key for generation (currently unused, placeholder)
        prefer_clef: If 'G' or 'F', biases toward that clef; None for equal probability
    
    Returns:
        Chord dictionary in existing format
    """
    del key
    # Use the same statistical generator. Musthe availability gates this path,
    # but generation behavior stays consistent across environments.
    return _generate_statistical_chord(difficulty=difficulty_level, prefer_clef=prefer_clef)

def generate_diatonic_chord(key: str = 'C', scale_degree: int | None = None, prefer_clef: str | None = None):
    """
    Generate a diatonic chord from a specific scale degree.
    
    Args:
        key: Key for scale (e.g., 'C', 'G', 'F')
        scale_degree: Scale degree (0-6, 0=root). If None, chooses randomly.
        prefer_clef: If 'G' or 'F', biases toward that clef; None for equal probability
    
    Returns:
        Chord dictionary in existing format
    """
    if key in SCALES:
        start_new_line_generation(key=key)
    else:
        start_new_line_generation()

    if scale_degree is None:
        return _generate_statistical_chord(difficulty=4, prefer_clef=prefer_clef)

    forced_degree = scale_degree % 7
    line_key = _generation_state["line_key"]
    clef = _sample_clef(prefer_clef)
    pitch_class = SCALES[line_key][forced_degree]
    quality = _quality_for_degree(forced_degree)
    root_midi = _sample_root_midi(pitch_class, clef)
    voicing_midis = _choose_voicing(root_midi, _build_interval_set(4, quality), clef)
    notes = [_preferred_note_name_for_midi(midi_note, line_key) for midi_note in voicing_midis]

    _advance_generation_state(clef, root_midi, voicing_midis, "T")

    return {
        "notes": notes,
        "clef": clef,
        "chord_name": _build_chord_name(line_key, forced_degree, quality, notes),
        "key": line_key,
        "scale_degree": ["I", "ii", "iii", "IV", "V", "vi", "vii°"][forced_degree],
    }

def should_use_musthe(difficulty: int | None = None) -> bool:
    """
    Determine whether to use musthe generation based on settings.
    
    Args:
        difficulty: Current difficulty level
    
    Returns:
        True if should use musthe, False for original generation
    """
    # For Phase 1, use musthe for all difficulties >= 2 when available
    return is_musthe_available() and difficulty is not None and difficulty >= 2
