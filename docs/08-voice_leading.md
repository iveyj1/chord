# Voice Leading

Version: 0.1.0  
Last updated: 2026-01-31

This document defines voice leading as constraints and optimization criteria for moving between chords. It bridges harmonic abstractions (chords/functions) and concrete realizations (voicings on piano / MIDI streams).

---

## 1. Definition

**Voice leading** is the mapping of voices from one sonority to the next such that:
- Each voice moves in a controlled way
- Harmonic identity is preserved
- Musical goals (smoothness, clarity, style) are satisfied

Voice leading is defined over **voicings**, not abstract chords.

---

## 2. Voices and Registers

A **voice** is a continuous melodic strand. On piano, voices are conceptual but can be modeled as ordered note streams.

A **voicing** assigns chord tones to specific registers.

Canonical computational model:

- Voicing: ordered list of pitches (MIDI integers)
- Voice i corresponds to index i (low → high)

---

## 3. Chord Tones vs Non-Chord Tones

Voice leading typically treats:
- **Chord tones** as structural targets
- **Non-chord tones** (passing, neighbor, suspension) as controlled deviations

This document defines chord-tone voice leading first; non-chord tones are an extension.

---

## 4. Basic Constraints (Tonal/Common-Practice)

These are constraints often used in classical-style four-part writing. They may be relaxed for pop/piano textures.

- Avoid parallel perfect fifths and octaves between voices
- Avoid voice crossing (unless intentional)
- Maintain reasonable spacing (outer voices wider than inner voices)
- Prefer contrary/oblique motion where possible
- Resolve tendency tones (e.g., leading tone)

These are best treated as **soft constraints** in algorithmic contexts.

---

## 5. Smoothness (Parsimony)

A common objective is minimizing total motion.

Given two voicings V and W of equal length n:

```
cost(V→W) = Σ |W[i] − V[i]|
```

Variants:
- Weighted voices (e.g., penalize soprano leaps more)
- Squared cost for large jumps

Smoothness is style-neutral and useful for real-time generation.

---

## 6. Voice Assignment Problem

When moving from chord A to chord B:
- chord tones differ
- voices must be mapped to new targets

This is a matching problem.

Approach:
1. Enumerate candidate voicings for B (within register limits)
2. Compute mapping cost from current voicing
3. Choose minimum-cost candidate subject to constraints

Cost Function Components:
- Voice motion cost (see Section 5)
- Constraint violation penalties
- Style-specific preferences

In real-time systems, candidate enumeration must be bounded (e.g., limit to 8-12 candidates).

---

## 7. Inversions and Bass Motion

Bass motion strongly influences perceived function and smoothness.

Principles:
- Stepwise bass motion strengthens continuity
- Root motion by 5th reinforces function (D→T)
- Inversion choice is a primary control knob

Algorithmic control:
- Treat inversion as a discrete state variable
- Penalize bass leaps > threshold

---

## 8. Doubling and Omission (Piano/Pop Practicalities)

In keyboard textures, chords are often incomplete or doubled.

Rules of thumb:
- Prefer including 3rd and 7th for functional identity
- Root may be omitted if implied (context or bass instrument)
- Doubling root is typically safe
- Avoid doubling tendency tones in strict styles

This motivates “shell voicings” as a first-class target.

---

## 9. Tendency Tones and Resolutions

Some scale degrees have directional tendencies in tonal contexts:
- 7 → 1 (leading tone resolution)
- 4 → 3 (in dominant-tonic contexts)

These can be encoded as constraints:

```
if tone == leading_tone:
    prefer next_tone == tonic (same octave proximity)
```

Additional tendency patterns:
- 6 → 5 (subdominant to dominant)
- 2 → 1 (supertonic resolution)

Tendency rules improve realism beyond pure smoothness.

---

## 10. Computational Representation

### 10.1 Core types

- Pitch: MIDI int
- Voicing: list[MIDI]
- Chord target set: set[PC] (from chords.md)

### 10.2 Mapping

Given current voicing V:
- Reduce to PCs for chord identity checking
- Generate candidate next voicings W satisfying chord target PCs
- Choose W minimizing a cost under constraints

---

## 11. Real-Time Considerations

Constraints for real-time operation:
- Bounded search
- Stable behavior (avoid jitter between near-equal solutions)
- Latency-aware updates

Practical strategies:
- Cache best voicing per (RN, inversion, register window)
- Add hysteresis: change only if improvement exceeds ε
- Limit candidate count per frame

---

## 12. Scope and Limitations

This document defines a minimal, composable voice-leading layer suitable for:
- Classical-style reductions
- Pop piano comping
- Algorithmic accompaniment

Counterpoint and ornamentation are separate layers.

