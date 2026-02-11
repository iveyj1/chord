# Intervals

Version: 0.1.0  
Last updated: 2026-01-31

This document defines musical intervals and their computational representations.

---

## 1. Interval Definition

An **interval** is the relationship between two pitches, defined by:
- Generic size (letter distance)
- Specific quality (chromatic alteration)

Intervals are directional unless explicitly reduced.

---

## 2. Generic Intervals

Generic interval size counts letter names inclusively.

Examples:
- C → E = third
- D → A = fifth

Generic intervals ignore accidentals and octave displacement.

---

## 3. Specific Intervals

A **specific interval** combines:
- Generic size
- Interval quality

Qualities:
- Perfect (P)
- Major (M)
- Minor (m)
- Augmented (A)
- Diminished (d)

Example:
- C → E = major third
- C → E♭ = minor third

---

## 4. Semitone Distance

In computational contexts, intervals may be represented as semitone distance:

```
Δ = (PC₂ − PC₁) mod 12
```

This representation:
- Loses spelling information
- Preserves transpositional structure

---

## 5. Interval Class

An **interval class (IC)** is the smallest distance between two pitch classes under inversion.

Definition:

```
IC = min(Δ, 12 − Δ)
```

Range:
- IC ∈ {0,…,6}

Used primarily in set-theoretic contexts.

---

## 6. Inversion

### 6.1 Interval Inversion

Interval inversion maps an interval to its complement:

```
size₁ + size₂ = 9
```

Quality inversion:
- Perfect ↔ Perfect
- Major ↔ Minor
- Augmented ↔ Diminished

Example:
- M3 ↔ m6

---

## 7. Direction

Intervals may be:
- Ascending
- Descending

Direction matters for:
- Melodic motion
- Voice leading

Direction is ignored in pitch-class and interval-class contexts.

---

## 8. Compound Intervals

Intervals larger than an octave are **compound intervals**.

Reduction:
- Compound intervals reduce to simple intervals modulo octave

Example:
- 10th → third

---

## 9. Enharmonic vs Functional Identity

Intervals with identical semitone distance may differ functionally:

- C → F♯ (A4)
- C → G♭ (d5)

These are **not equivalent** in tonal contexts.

---

## 10. Canonical Data Types (Abstract)

- Generic interval: int (2–8)
- Specific interval: {generic, quality}
- Semitone interval: int ∈ ℤ₁₂
- Interval class: int ∈ {0,…,6}

All representations must declare which model is in use.

