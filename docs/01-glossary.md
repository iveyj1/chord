# Glossary

Version: 0.1.0  
Last updated: 2026-01-31

This glossary defines canonical terms used throughout the project. All other documents must either use these terms verbatim or explicitly reference them.

---

## Pitch and Notation

**Note**  
A symbolic representation of pitch using a letter name (A–G), optional accidental, and octave designation.

**Pitch**  
The perceived frequency of a sound, abstracted independently of timbre or loudness.

**Pitch Class (PC)**  
The equivalence class of pitches separated by octaves. Typically represented as integers modulo 12. (See: [pitch.md](02-pitch.md))

**Octave Equivalence**  
The assumption that pitches separated by a factor of two in frequency are functionally equivalent.

**Accidental**  
A symbol modifying a note’s pitch by a chromatic alteration (sharp, flat, natural, etc.).

**Enharmonic Equivalence**  
Different note spellings that correspond to the same pitch class (e.g., C♯ and D♭).

**Staff Notation**  
Standard five-line musical notation used to represent pitch and duration.

---

## Intervals

**Interval**  
The distance between two pitches, defined by both size (number) and quality.

**Generic Interval**  
An interval classified by letter-name distance only (e.g., third, fifth).

**Specific Interval**  
An interval defined by both generic size and quality (e.g., major third).

**Interval Quality**  
The classification of an interval (perfect, major, minor, augmented, diminished).

**Interval Class**  
The smallest distance between two pitch classes modulo octave and inversion symmetry.

**Inversion (Interval)**  
The transformation of an interval such that the lower pitch is raised by an octave, producing a complementary interval.

---

## Rhythm and Time

**Duration**  
The length of time a musical event occupies.

**Beat**  
The basic unit of perceived pulse in music.

**Meter**  
The hierarchical organization of beats into repeating patterns.

**Subdivision**  
The division of a beat into smaller rhythmic units.

**Tuplet**  
An irregular subdivision of time that deviates from the prevailing meter.

**Event**  
A discrete musical occurrence defined by onset time, duration, and content.

---

## Scales and Tonality

**Scale**  
An ordered collection of pitches or pitch classes within an octave. (See: [scales.md](04-scales.md))

**Step Pattern**  
The sequence of intervals between adjacent notes in a scale.

**Mode**  
A rotation of a scale that produces a different tonal center while preserving pitch content.

**Key**  
The contextual assignment of a tonic pitch and scale to a piece or passage.

**Tonic**  
The primary pitch or pitch class that functions as a point of rest.

**Scale Degree**  
The position of a pitch relative to the tonic, typically numbered 1–7.

---

## Chords and Harmony

**Chord**  
A set of pitches sounded simultaneously or perceived as a harmonic unit. (See: [chords.md](05-chords.md))

**Chord Quality**  
The classification of a chord based on its internal interval structure.

**Triad**  
A three-note chord built by stacking thirds.

**Seventh Chord**  
A four-note chord consisting of a triad plus a seventh above the root.

**Extension**  
A chord tone beyond the seventh, typically derived from the scale.

**Inversion (Chord)**  
A chord voicing where a pitch other than the root is in the bass.

**Voicing**  
The specific ordering and spacing of notes in a chord. (See: [voice_leading.md](08-voice_leading.md))

---

## Functional Harmony

**Function**  
The role a chord plays within a tonal context, independent of absolute pitch. (See: [harmony_function.md](07-harmony_function.md))

**Tonic Function**  
Harmony that provides stability and resolution.

**Predominant Function**  
Harmony that prepares dominant function.

**Dominant Function**  
Harmony that creates tension resolving to tonic.

**Cadence**  
A harmonic progression that articulates closure.

**Roman Numeral Analysis**  
A symbolic system for representing chord function relative to a key. (See: [roman_numerals.md](06-roman_numerals.md))

---

## Form and Structure

**Phrase**  
A musical unit analogous to a sentence, typically ending with a cadence.

**Period**  
A pair of related phrases forming a question–answer structure.

**Form**  
The large-scale organization of musical sections over time.

**Harmonic Rhythm**  
The rate at which chords change. (See: [progressions.md](09-progressions.md))

---

## Computational Concepts

**Pitch Representation**  
A formal encoding of pitch (e.g., MIDI number, pitch class integer).

**Time Representation**  
A formal encoding of musical time (e.g., ticks, seconds, frames).

**Pitch-Class Set**  
An unordered collection of pitch classes, typically represented modulo 12.

**Maximal Evenness**  
A property of pitch-class sets where intervals are as evenly distributed as possible within the octave.

**Cost Function**  
A mathematical function that evaluates voice leading quality by penalizing undesirable motion patterns.

**Voice Assignment**  
The process of mapping chord tones to specific voices when transitioning between voicings.

**Transposition**  
A uniform shift of all pitches by a fixed interval.

**Invariance**  
A property preserved under transformation (e.g., transposition invariance).

**Constraint**  
A rule limiting allowable musical structures or transformations.

---

## Performance and Practice

**Fingering**  
The assignment of fingers to notes on an instrument.

**Pattern**  
A repeatable musical or motor structure used for practice or generation.

**Transposition Practice**  
The systematic shifting of patterns through all keys.

**Shell Voicing**  
A reduced chord voicing emphasizing essential tones.

**Rootless Voicing**  
A chord voicing omitting the root, typically implied by context.

**Guide Tones**  
The third and seventh chord tones that define a chord's harmonic function and quality, prioritized in voice leading.

