# Pitch

Version: 0.1.0  
Last updated: 2026-01-31

This document defines pitch-related concepts and establishes canonical representations used throughout the project.

---

## 1. Conceptual Model

Pitch is treated as an abstract quantity independent of instrument, timbre, or notation. Multiple representations coexist and must be explicitly mapped.

Key assumptions:
- Octave equivalence holds unless stated otherwise
- Enharmonic equivalence may or may not hold, depending on context
- Representation choice is contextual (notation vs computation)

---

## 2. Note Names

Western pitch notation uses seven letter names:

A B C D E F G

These define **generic pitch identity** without accidentals or octave.

---

## 3. Accidentals

Accidentals modify a note’s pitch by chromatic alteration:

- Sharp (♯): +1 semitone
- Flat (♭): −1 semitone
- Double sharp (𝄪): +2 semitones
- Double flat (𝄫): −2 semitones
- Natural (♮): cancels prior alteration

Accidentals affect spelling and interval identity, not just pitch height.

---

## 4. Pitch Class (PC)

A **pitch class** represents all pitches related by octave equivalence.

Canonical computational representation:

- Integer modulo 12
- Domain: ℤ₁₂ = {0,…,11}

Reference mapping:

| PC | Note Name |
|----|-----------|
| 0  | C         |
| 1  | C♯ / D♭   |
| 2  | D         |
| 3  | D♯ / E♭   |
| 4  | E         |
| 5  | F         |
| 6  | F♯ / G♭   |
| 7  | G         |
| 8  | G♯ / A♭   |
| 9  | A         |
| 10 | A♯ / B♭   |
| 11 | B         |

This mapping is **conventional**, not theoretical necessity.

---

## 5. Octaves

An octave represents doubling of frequency.

Notation:
- Scientific pitch notation (e.g., C4)
- Octave number increments at C

Octave number is ignored in pitch-class contexts.

---

## 6. MIDI Representation

MIDI encodes pitch as integers:

- Range: 0–127
- Semitone resolution

Standard reference:

- MIDI 60 = C4

Mapping:

```
MIDI = 12 × (octave) + pitch_class + 12
```

Examples:
- C4: 12×4 + 0 + 12 = 60
- A4: 12×4 + 9 + 12 = 69

This mapping is assumed unless overridden.

---

## 7. Enharmonic Equivalence

Two notes are enharmonically equivalent if they map to the same pitch class.

Musical consequences:
- Same sound
- Different spelling
- Different interval identity

Enharmonic equivalence **must not** be assumed in harmonic or interval analysis.

---

## 8. Transposition

Transposition is defined as addition in ℤ₁₂ (or ℤ for MIDI):

```
PC' = (PC + n) mod 12
```

Properties:
- Structure-preserving
- Invertible
- Key-agnostic

---

## 9. Invariance

Pitch-class sets are invariant under:
- Transposition
- Octave displacement

They are **not** invariant under:
- Inversion (unless explicitly defined)
- Spelling changes

---

## 10. Canonical Data Types (Abstract)

- Note: {letter, accidental, octave}
- Pitch class: int ∈ ℤ₁₂
- MIDI pitch: int ∈ [0,127]

Conversions must be explicit and loss-aware.

