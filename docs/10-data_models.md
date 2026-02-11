# Data Models

Version: 0.1.0  
Last updated: 2026-01-31

This document defines canonical data structures for representing pitch, scales, chords, harmony tokens, voicings, and time in software. The goal is to make conversions explicit and loss-aware.

---

## 1. Design Principles

- Prefer **explicit types** over implicit conventions.
- Separate **symbolic** (spelling) from **numeric** (PC/MIDI).
- Make **lossy conversions** explicit.
- Keep real-time operations bounded (avoid unbounded search).

---

## 2. Core Numeric Types

### 2.1 Pitch Class

- Type: int
- Domain: 0..11
- Meaning: ℤ₁₂ pitch class, using the canonical mapping in pitch.md

### 2.2 MIDI Pitch

- Type: int
- Domain: 0..127
- Meaning: semitone-indexed absolute pitch

### 2.3 Semitone Interval

- Type: int
- Domain: integers (use mod 12 only when explicitly PC-based)

---

## 3. Symbolic Types

### 3.1 Note Spelling

Represents staff-level spelling.

Fields:
- letter: one of {A,B,C,D,E,F,G}
- accidental: integer offset in semitones (e.g. -2..+2)
- octave: int (scientific pitch notation)

This representation is required for:
- correct interval naming
- notation-aware analysis

It is not required for:
- most generation/detection tasks

---

## 4. Scales

### 4.1 Step Pattern

- Type: list[int]
- Constraint: sum == 12

### 4.2 Ordered Scale (Pitch-Class)

- Type: list[int]
- Constraint: each element in 0..11
- Interpretation: cyclic order, root at index 0

### 4.3 Pitch-Class Set

- Type: set[int]
- Interpretation: unordered membership

Recommended helper operations:
- transpose_scale(scale, n)
- rotate_scale(scale, k)
- scale_to_pcs(scale)

---

## 5. Chords

### 5.1 Chord (Pitch-Class Set)

- Type: frozenset[int]
- Interpretation: abstract chord identity

### 5.2 Rooted Chord

- Type: struct

Fields:
- root_pc: int
- pcs: frozenset[int]

Root is optional; include it when analysis requires it.

### 5.3 Chord Quality

Represent chord quality as an enum independent of function:

- triad: {maj, min, dim, aug}
- seventh: {maj7, dom7, min7, hdim7, dim7}

If you need generality, store as interval vector relative to root.

---

## 6. Roman Numeral Token

Roman numerals are key-relative harmony tokens.

Canonical struct:

Fields:
- degree: int          # 1..7
- alterations: list[int]
  - Each alteration is applied to the degree’s scale pitch (e.g. ♭ = -1, ♯ = +1)
  - Multiple alterations allowed (rare)
- triad_quality: enum {maj, min, dim, aug}
- seventh: optional enum {maj7, dom7, min7, hdim7, dim7}
- inversion: optional enum
  - triads: {root, 6, 64}
  - sevenths: {7, 65, 43, 42}
- applied_to_degree: optional int
  - for secondary function (e.g. V/V => applied_to_degree=5)

Notes:
- This structure is a grammar token.
- It does not encode voicing or register.

---

## 7. Harmonic Function

Canonical representation:

- function: enum {T, PD, D}
- strength: float in [0,1] (optional)
- scope: enum {global, local}
- resolution_target_degree: optional int

Function labeling is often inferred; treat it as metadata.

---

## 8. Progression Token

A progression token is RN + function + time.

Fields:
- rn: RomanNumeralToken
- func: optional FunctionToken
- dur: Duration

---

## 9. Voicing and Voice Leading

### 9.1 Voicing

- Type: tuple[int, ...]  # MIDI pitches, low → high
- Constraint: strictly increasing (no unisons within a single voicing) unless allowed

### 9.2 Voice Assignment

When moving voicing V to W:
- Keep length equal where possible
- If lengths differ, define an explicit policy:
  - drop inner voices
  - prioritize guide tones (3rd, 7th)

### 9.3 Voice-Leading Cost

Store cost parameters separately:

Fields:
- voice_weights: list[float]
- leap_penalty_threshold: int
- hysteresis_epsilon: float

---

## 10. Time and Events

### 10.1 Clock

Real-time systems need a canonical time base. Recommended options:

- tick-based: integer ticks at fixed PPQ
- time-based: seconds (float)

Prefer tick-based for quantized practice tasks.

### 10.2 Event

Fields:
- onset: int (ticks) or float (seconds)
- duration: int/float
- pitches: tuple[int, ...] (MIDI)
- velocity: optional int
- channel: optional int

Events are the bridge between MIDI streams and harmonic interpretation.

---

## 11. Loss-Aware Conversions (Required)

Conversions must declare what is lost.

Examples:
- NoteSpelling -> PC loses spelling
- MIDI -> PC loses octave/register
- PC set -> RN requires key context
- RN -> PC set requires key context and scale model

Prefer function signatures that force context to be provided.

---

## 12. Minimal Interfaces (Suggested)

These are the minimal pure functions implied by the above types:

- pc_from_midi(midi) -> pc
- midi_from_pc_oct(pc, octave) -> midi
- transpose_pcs(pcs, n) -> pcs
- build_scale_from_steps(root_pc, steps) -> ordered_scale
- rotate_scale(scale, k) -> scale
- build_tertian_chord(scale, degree, n_tones) -> pcs
- realize_rn_to_pcs(rn, key, mode) -> pcs
- choose_voicing(next_pcs, prev_voicing, constraints, cost) -> voicing

Real-time orchestration is layered on top.

