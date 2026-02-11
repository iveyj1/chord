# Chords

Version: 0.1.0  
Last updated: 2026-01-31

This document defines chords as pitch-class structures derived from scales and establishes canonical representations for analysis, generation, and performance.

---

## 1. Definition

A **chord** is a finite set of pitches perceived as a harmonic unit.

Properties:
- Order-independent as a set
- Order-dependent as a voicing
- Context-dependent function

Unless stated otherwise, chords are defined at the pitch-class level.

---

## 2. Chords vs Voicings

- **Chord**: abstract pitch-class structure
- **Voicing**: concrete ordering, spacing, and register assignment

A single chord admits many voicings.

---

## 3. Tertian Construction

Most tonal harmony uses **tertian chords**, constructed by stacking thirds within a scale.

Formal rule:

```
chord = {scale[i], scale[i+2], scale[i+4], ...}
```

Indexing is modulo scale cardinality.

---

## 4. Triads

Triads consist of three stacked thirds.

| Quality      | Interval Structure | Example (PCs) | Data Model |
|--------------|--------------------|---------------|------------|
| Major        | M3 + m3            | frozenset{0,4,7} | triad_quality: "maj" |
| Minor        | m3 + M3            | frozenset{0,3,7} | triad_quality: "min" |
| Diminished   | m3 + m3            | frozenset{0,3,6} | triad_quality: "dim" |
| Augmented    | M3 + M3            | frozenset{0,4,8} | triad_quality: "aug" |

Triad quality is invariant under transposition.

---

## 5. Seventh Chords

Seventh chords extend triads by one additional third.

| Quality              | Intervals           | Example (PCs) | Data Model |
|----------------------|---------------------|---------------|------------|
| Major 7              | M3 m3 M3            | frozenset{0,4,7,11} | seventh: "maj7" |
| Dominant 7           | M3 m3 m3            | frozenset{0,4,7,10} | seventh: "dom7" |
| Minor 7              | m3 M3 m3            | frozenset{0,3,7,10} | seventh: "min7" |
| Half-diminished 7    | m3 m3 M3            | frozenset{0,3,6,10} | seventh: "hdim7" |
| Fully diminished 7   | m3 m3 m3            | frozenset{0,3,6,9}  | seventh: "dim7" |

---

## 6. Extensions

Extensions are chord tones above the seventh, typically derived from the parent scale:

- 9th
- 11th
- 13th

Extensions do not imply inclusion of all intermediate tones.

---

## 7. Scale-Degree Chords

Given a scale, chords may be built on each degree.

Example: diatonic triads in major

| Degree | Quality |
|--------|---------|
| I      | Major   |
| ii     | Minor   |
| iii    | Minor   |
| IV     | Major   |
| V      | Major   |
| vi     | Minor   |
| vii°   | Dimin.  |

This table is **derived**, not axiomatic.

---

## 8. Inversions

A chord inversion places a non-root chord tone in the bass.

Triad inversions:
- Root position
- First inversion
- Second inversion

Inversion affects:
- Bass motion
- Voice leading
- Function perception

---

## 9. Root, Quality, Function

These are orthogonal concepts:

- **Root**: pitch-class reference
- **Quality**: internal interval structure
- **Function**: contextual role

No one-to-one mapping exists between quality and function.

---

## 10. Enharmonic and Set-Theoretic Views

At the pitch-class set level:

- C°7 = {0,3,6,9}
- Symmetric under transposition

Set-theoretic equivalence may obscure tonal function.

---

## 11. Canonical Data Types (Abstract)

- Chord (PCS): set[int] ∈ ℤ₁₂
- Chord with root: {root_pc, pcs}
- Voicing: ordered list[int] (MIDI or PC + octave)

Operations:
- Transpose
- Invert
- Voice
- Reduce to PCS

All higher-level harmony and progression logic depends on these primitives.

