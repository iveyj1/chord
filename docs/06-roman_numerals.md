# Roman Numeral Analysis

Version: 0.1.0  
Last updated: 2026-01-31

This document defines Roman numeral analysis as a functional, transposition-invariant representation of harmony.

---

## 1. Purpose

Roman numeral analysis represents chords **relative to a tonal center**, abstracting away absolute pitch.

Primary uses:
- Functional analysis
- Progression templates
- Transposition-invariant generation

Roman numerals encode **scale degree + chord quality**, not voicing.

---

## 2. Scale Degree Mapping

Given a key with tonic T and scale S:

```
Degree i ↔ S[i-1]
```

Degree numbering is relative to the tonic and assumes a reference scale (usually major or minor).

---

## 3. Numeral Case and Symbols

### 3.1 Case

- Uppercase: major-quality triad
- Lowercase: minor-quality triad
- Diminished: lowercase + °
- Augmented: uppercase + +

Examples:
- I   = major triad on degree 1
- ii  = minor triad on degree 2
- vii° = diminished triad on degree 7

---

## 4. Seventh Chords

Seventh chords are indicated by added figures or suffixes:

| Symbol | Meaning |
|-------|--------|
| 7     | dominant 7 |
| M7    | major 7 |
| m7    | minor 7 |
| ø7    | half-diminished 7 |
| °7    | fully diminished 7 |

Example:
- V7
- iiø7

---

## 5. Inversions and Figured Bass

Inversions are indicated using figured bass numerals.

| Inversion | Triad Notation | Seventh Notation | Example (C major) |
|-----------|----------------|------------------|-------------------|
| Root | (none) | 7 | I, I7 |
| First | 6 | 6/5 | I6, I6/5 |
| Second | 6/4 | 4/3 | I6/4, I4/3 |
| Third | (not applicable) | 4/2 | (not applicable), I4/2 |

Figured bass modifies **bass position**, not chord identity.

---

## 6. Applied and Secondary Chords

A **secondary (applied) chord** temporarily tonicizes a scale degree.

Notation:

```
V/V   = dominant of the dominant
```

Rules:
- Right-hand numeral defines temporary tonic
- Left-hand numeral defines function relative to it

---

## 7. Borrowed Chords

Chords borrowed from the parallel mode (major/minor):

| From Major | To Minor | Example |
|------------|----------|---------|
| IV | iv | minor subdominant |
| VI | ♭VI | lowered submediant |
| VII | ♭VII | lowered leading tone |

From Minor to Major (less common):
- iv → IV (Picardy third context)
- ♭VI → VI

Borrowing alters scale-degree quality without changing tonic.

---

## 8. Roman Numerals vs Pitch-Class Sets

Roman numerals encode:
- Relative scale degree
- Chord quality
- Function (implicitly)

They do **not** encode:
- Absolute pitch
- Voicing
- Register

Multiple pitch-class realizations may correspond to the same numeral.

---

## 9. Computational Representation

Canonical abstract form:

```
{
  degree: int,        // 1–7
  quality: enum,      // maj, min, dim, aug
  seventh: optional enum,
  inversion: optional enum,
  alterations: list   // e.g. ♭, ♯ applied to degree
}
```

Roman numerals form a **grammar**, not a set.

---

## 10. Limitations

Roman numeral analysis assumes:
- A tonal center
- A reference scale

It degrades in:
- Highly chromatic music
- Modal or post-tonal contexts

Use only where tonal function is meaningful.

