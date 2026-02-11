# Harmonic Function

Version: 0.1.0  
Last updated: 2026-01-31

This document defines harmonic function as a contextual role played by chords within a tonal system, independent of absolute pitch and voicing.

---

## 1. Definition

**Harmonic function** describes how a chord behaves relative to a tonal center.

Function is:
- Contextual
- Relational
- Independent of chord quality alone

Function is not intrinsic to a chord; it emerges from tonal context.

---

## 2. Primary Functional Categories

Western tonal harmony is commonly described using three primary functions:

| Function | Abbrev | Role |
|--------|--------|------|
| Tonic | T | Stability, rest |
| Predominant | PD | Preparation |
| Dominant | D | Tension, resolution |

These form a directed functional flow.

---

## 3. Functional Flow

Canonical progression:

```
T → PD → D → T
```

Not all steps are required, but violations weaken tonal clarity.

---

## 4. Tonic Function

Tonic-function chords:
- Establish or reinforce the tonal center
- Exhibit minimal tendency to move

Common tonic-function chords (major key):
- I
- vi
- iii (weak)

---

## 5. Predominant Function

Predominant-function chords:
- Move away from tonic
- Prepare dominant

Common predominant-function chords:
- ii
- IV
- ii⁷
- IV⁷

Predominant rarely resolves directly to tonic.

---

## 6. Dominant Function

Dominant-function chords:
- Contain leading-tone tendency
- Generate instability

Common dominant-function chords:
- V
- V7
- vii°
- viiø7

Dominant typically resolves to tonic.

---

## 7. Cadences

A **cadence** is a harmonic gesture articulating closure.

| Cadence | Function Pattern | Examples |
|--------|------------------|----------|
| Perfect Authentic | D → T (V→I) | V-I, V7-I |
| Imperfect Authentic | D → T (inversion) | V6-I, V7-IA |
| Half | PD → D | I-V, IV-V |
| Plagal | PD → T | IV-I |
| Deceptive | D → T-substitute | V-vi |

Cadence strength depends on:
- Harmonic function
- Bass motion
- Metric placement

---

## 8. Functional Substitution

Chords may substitute for others sharing function.

Examples:
- vi for I (tonic substitute)
- ii for IV (predominant substitute)
- vii° for V (dominant substitute)

Substitution preserves function while altering color.

---

## 9. Secondary Function

Applied dominants temporarily assign dominant function to a non-tonic degree.

Example:
- V/V has dominant function relative to scale degree 5

Function is nested but remains directional.

---

## 10. Ambiguity and Context

Some chords admit multiple functional interpretations:
- iii
- vi
- IV in plagal contexts

Disambiguation depends on:
- Surrounding chords
- Bass motion
- Phrase position

---

## 11. Computational Representation

Canonical abstract form:

```
{
  function: enum {T, PD, D},
  strength: optional scalar,
  scope: enum {global, local},
  resolution_target: optional degree
}
```

Function may be inferred probabilistically.

---

## 12. Limitations

Functional harmony assumes:
- Tonal center
- Directed tension-resolution behavior

It degrades in:
- Modal harmony
- Extended chromaticism
- Non-functional progressions

Use where tonal motion is a design goal.

