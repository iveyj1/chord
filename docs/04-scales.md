# Scales

Version: 0.1.0  
Last updated: 2026-01-31

This document defines scales as ordered pitch-class structures and establishes their canonical representations for theory and computation.

---

## 1. Definition

A **scale** is an ordered collection of pitch classes spanning an octave.

Properties:
- Order matters
- Cardinality is finite
- Octave equivalence applies

A scale is distinct from a key, which assigns functional context.

---

## 2. Ordered vs Unordered Views

### Ordered Scale

An ordered scale is represented as a cyclic sequence:

```
S = [pc₀, pc₁, …, pcₙ₋₁]
```

- pc₀ is the scale’s reference pitch (not necessarily tonic)
- Order defines adjacency and step structure

### Unordered Pitch-Class Set

The same scale may be treated as an unordered set:

```
PCS = {pc₀, pc₁, …, pcₙ₋₁}
```

Used for:
- Transpositional equivalence
- Set-theoretic comparison

---

## 3. Step Patterns

A **step pattern** is the sequence of intervals between adjacent scale degrees.

Representation:

```
Δ = [d₀, d₁, …, dₙ₋₁]
```

where:

```
Σ dᵢ = 12
```

Example (major scale):

```
[2, 2, 1, 2, 2, 2, 1]
```

Step patterns are invariant under transposition.

---

## 4. Scale Degree Indexing

Scale degrees are indexed relative to the first element:

- Degree numbers: 1 … n
- Zero-based index: 0 … n−1

Degree numbering is contextual and not intrinsic to the scale itself.

---

## 5. Diatonic Scale

The **diatonic (major) scale** is defined by the step pattern:

```
[2, 2, 1, 2, 2, 2, 1]
```

Properties:
- Cardinality: 7
- Generates the modal system
- Asymmetric but maximally even

Pitch-class example (C major):

```
[0, 2, 4, 5, 7, 9, 11]
```

---

## 6. Modes as Rotations

A **mode** is a rotation of an ordered scale.

Formal definition:

```
mode_k(S) = rotate_left(S, k)
```

All modes:
- Share the same pitch-class set
- Differ in reference pitch and step ordering

Example (C major modes):

| Mode     | PC Sequence           |
|----------|-----------------------|
| Ionian   | 0 2 4 5 7 9 11         |
| Dorian   | 2 4 5 7 9 11 0         |
| Phrygian | 4 5 7 9 11 0 2         |
| Lydian   | 5 7 9 11 0 2 4         |
| Mixolyd. | 7 9 11 0 2 4 5         |
| Aeolian  | 9 11 0 2 4 5 7         |
| Locrian  | 11 0 2 4 5 7 9         |

---

## 7. Tonal Center vs Scale Root

The first element of an ordered scale is a **scale root**, not necessarily a tonic.

Tonic assignment requires:
- Harmonic context
- Functional interpretation

Modes do not imply tonality by themselves.

---

## 8. Minor Scale Systems

Three related step patterns are commonly used:

- Natural minor:   [2,1,2,2,1,2,2]
- Harmonic minor:  [2,1,2,2,1,3,1]
- Melodic minor:   [2,1,2,2,2,2,1] (ascending form)

These are **altered diatonic collections**, not separate modal systems.

---

## 9. Symmetry and Evenness

Scales may be analyzed by:
- Rotational symmetry
- Interval distribution
- Maximal evenness

The diatonic scale is maximally even but not symmetric.

---

## 10. Canonical Data Types (Abstract)

- Ordered scale: list[int] ∈ ℤ₁₂
- Step pattern: list[int] summing to 12
- Pitch-class set: set[int] ∈ ℤ₁₂

Operations:
- Transpose
- Rotate
- Reduce to PCS

All scale algorithms should be expressible in these terms.

