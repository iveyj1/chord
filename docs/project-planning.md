## AI-Autonomous Development Best Practices

Practices for maximizing autonomous AI development capability on this project.

**1. Maintain Documentation Framework**

Current strength: `docs/glossary.md` provides canonical definitions. Continue this pattern:
- Keep `DEVGUIDE.md` architecturally current
- Update `AGENTS.md` when adding conventions or build commands
- Document data models and state machines explicitly (like chord dictionary structure)

**2. Establish Clear Constraints**

Already present:
- Type formats (`"C4"` string notation)
- Mathematical formulas (staff position calculation)
- Prohibited patterns ("no eval!" in compare_notes)

Expand to:
- Performance budgets (frame time limits)
- Acceptable dependency additions
- Breaking change policies

**3. Provide Verifiable Success Criteria**

Current gap: Manual testing only. Consider adding:

```python
# tests/test_music.py
def test_enharmonic_equivalence():
    assert compare_notes("C#4", "Db4")
    assert compare_notes("F4", "E#4")
```

Assertion-based tests enable autonomous verification.

**4. Use Structured Task Requests**

Effective patterns:
- "Add harmonic minor scale generation following the pattern in `chords.py`"
- "Implement pedal marking display using the staff geometry in `constants.py`"

Less effective:
- "Make the chords better"
- "Add more music theory"

**5. Configuration Over Code**

`constants.py` centralizes tunable parameters. Extend this for:
- Difficulty progression curves
- Visual themes
- Input timing windows

**6. Maintain Modular Boundaries**

Current strength: Clear separation (music.py, draw.py, playback.py). Preserve:
- One responsibility per module
- Explicit imports (no wildcards)
- Minimal cross-module state

Red flag: Utils modules becoming dumping grounds.

**7. Document Architectural Invariants**

From `AGENTS.md`:
- "Draw to logical `screen` surface; do not bypass `present_frame()`"
- "Use mathematical formula for staff positioning, not hardcoded tables"

Add similar invariants for:
- Event handling order
- State transition rules
- Rendering layer ordering

**8. Provide Incremental Milestones**

Instead of: "Add full MIDI recording and playback"

Break into:
1. Capture MIDI events to in-memory buffer
2. Serialize buffer to JSON format
3. Replay from buffer with timing preservation
4. Add UI controls for record/stop/play

Each step verifiable before proceeding.

**9. Use Type Hints Progressively**

Make type hints required for new code:
```python
def note_to_staff_position(note: str, clef: str) -> int:
    ...
```

**10. Maintain Known-Good State**

Critical practice:
- Tag working versions: `git tag v0.2-stable`
- Document what works: "Sequence mode fully functional as of commit abc123"
- Specify test procedure: "Run with `--sequence`, complete 3-bar line using MIDI keyboard"

Gives rollback target if experiments fail.

**Immediate Actionable Steps**

1. Add basic test suite (10-20 assertions for core functions)
2. Create `docs/architecture.md` documenting state machine and rendering pipeline
3. Establish feature request template:
```
Goal: [What capability to add]
Success criteria: [How to verify it works]
Constraints: [What not to break]
References: [Relevant docs/code]
```

The pattern started with `AGENTS.md` and `docs/glossary.md` extends well to architecture, testing, and configuration domains.
