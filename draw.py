"""
Drawing functions for the piano learning game.

All Pygame rendering code lives here.
"""

import pygame
from constants import (
    WIDTH, HEIGHT, BLACK, NOTE_COLOR, GREEN, RED, GRAY,
    CENTER_Y_PX, HALF_LINE_SPACING, NOTE_WIDTH_PX, NOTE_HEIGHT_PX
)
from music import note_to_mnote, note_to_position
from utils import strip_accidental, compare_notes

# =============================================================================
# Module-level font cache (initialized on first use)
# =============================================================================

_fonts = {}

def _get_font(name, size):
    """Get or create a cached font."""
    key = (name, size)
    if key not in _fonts:
        if name is None:
            _fonts[key] = pygame.font.SysFont(None, size)
        else:
            _fonts[key] = pygame.font.Font(name, size)
    return _fonts[key]


# =============================================================================
# Position Conversion
# =============================================================================

def note_y_pos(note, clef):
    """Get the y position of a note in half-line units."""
    return note_to_position[clef][strip_accidental(note)]


def y_pos_to_pixel(pos):
    """Convert half-line position to pixel y-coordinate."""
    return CENTER_Y_PX - pos * HALF_LINE_SPACING


# =============================================================================
# Drawing Primitives
# =============================================================================

def draw_accidental(screen, note, y_pix, x_center=None, x_shift=0.0, scale=1.0):
    """Draw sharp or flat symbol next to a note."""
    font_size = max(20, int(80 * scale))
    font = _get_font("fonts/BravuraText.otf", font_size)
    accidental_offset = int(60 * scale)
    if x_center is None:
        x_center = WIDTH // 2
    x = int(x_center - accidental_offset + x_shift)
    
    if "#" in note:
        surf = font.render("♯", True, BLACK)
        screen.blit(surf, (x, y_pix - surf.get_height() // 2))
    elif "b" in note:
        surf = font.render("♭", True, BLACK)
        screen.blit(surf, (x, y_pix - surf.get_height() // 2))


def draw_ledger_line(screen, ledger_pos, x_center=None, note_width=None, thickness=5):
    """Draw a single ledger line at the given staff position."""
    if x_center is None:
        x_center = WIDTH // 2
    if note_width is None:
        note_width = NOTE_WIDTH_PX

    y_pix = y_pos_to_pixel(ledger_pos)
    half_length = int(1.5 * note_width / 2)
    pygame.draw.line(
        screen, BLACK,
        (int(x_center - half_length), y_pix),
        (int(x_center + half_length), y_pix),
        max(1, int(thickness))
    )


def draw_ledger_lines(screen, note, clef, x_center=None, note_width=None, scale=1.0):
    """Draw all required ledger lines for a note."""
    # Set top and bottom line positions for each clef
    if clef == 'G':
        top_line_pos = note_to_position[clef]["F5"]
        bottom_line_pos = note_to_position[clef]["E4"]
    else:
        top_line_pos = note_to_position[clef]["A3"]
        bottom_line_pos = note_to_position[clef]["G2"]

    pos = note_to_position[clef][strip_accidental(note)]

    # Above the staff: ledger lines at top_line_pos+2, +4, ...
    if pos > top_line_pos:
        for ledger_pos in range(top_line_pos + 2, pos + 1, 2):
            draw_ledger_line(
                screen,
                ledger_pos,
                x_center=x_center,
                note_width=note_width,
                thickness=max(1, int(5 * scale)),
            )
    # Below the staff: ledger lines at bottom_line_pos-2, -4, ...
    if pos < bottom_line_pos:
        for ledger_pos in range(bottom_line_pos - 2, pos - 1, -2):
            draw_ledger_line(
                screen,
                ledger_pos,
                x_center=x_center,
                note_width=note_width,
                thickness=max(1, int(5 * scale)),
            )

def draw_chord(screen, notes, duration="half", clef="G", x_center=None, scale=1.0):
    """Draw a chord (set of notes) on the staff.
    
    Args:
        screen: Pygame surface to draw on
        notes: Iterable of note names (e.g., ["C4", "E4", "G4"])
        duration: "half" (hollow), "whole" (filled), or "x" (wrong note marker)
        clef: "G" (treble) or "F" (bass)
    """
    if not notes:
        return

    # Sort notes by pitch for proper stacking
    notes_list = sorted(notes, key=lambda x: note_to_mnote[x])

    if x_center is None:
        x_center = WIDTH // 2

    note_width = max(2, int(NOTE_WIDTH_PX * scale))
    note_height = max(2, int(NOTE_HEIGHT_PX * scale))

    y_last = None
    x_shift_mult = 0

    for note in notes_list:
        stripped_note = strip_accidental(note)
        if stripped_note not in note_to_position[clef]:
            print(f"[WARN] Note '{note}' (note '{stripped_note}') not in staff mapping for clef '{clef}'. Skipping.")
            # Optionally, print bounds for debugging
            all_notes = list(note_to_position[clef].keys())
            print(f"         {clef} clef range: {all_notes[0]} to {all_notes[-1]}")
            continue
        y = note_y_pos(note, clef)
        y_pix = y_pos_to_pixel(y)

        # Offset notes that are adjacent (seconds) to avoid overlap
        if y_last is not None and abs(y - y_last) < 2:
            x_shift_mult = 1 - x_shift_mult
        else:
            x_shift_mult = 0
        y_last = y
        x_shift = int(x_shift_mult * -note_width / 1.2)

        # Draw accidental (not shown for wrong-note X markers)
        if duration != "x":
            draw_accidental(screen, note, y_pix, x_center=x_center, x_shift=x_shift, scale=scale)

        # Draw note head
        if duration in ("half", "whole"):
            line_width = max(1, int(6 * scale)) if duration == "half" else 0  # hollow vs filled
            pygame.draw.ellipse(
                screen, NOTE_COLOR,
                (int(x_center - note_width / 2 + x_shift),
                 int(y_pix - note_height / 2),
                 note_width, note_height),
                line_width
            )
        elif duration == "x":
            # Draw X for wrong notes
            x_width = max(6, int(20 * scale))
            x_mark_center = int(x_center + note_width)
            pygame.draw.line(screen, BLACK,
                (x_mark_center - x_width, y_pix - x_width),
                (x_mark_center + x_width, y_pix + x_width),
                max(1, int(10 * scale)),
            )
            pygame.draw.line(screen, BLACK,
                (x_mark_center - x_width, y_pix + x_width),
                (x_mark_center + x_width, y_pix - x_width),
                max(1, int(10 * scale)),
            )

        # Draw ledger lines
        draw_ledger_lines(screen, note, clef, x_center=x_center, note_width=note_width, scale=scale)


def get_sequence_layout(num_bars=4, chords_per_bar=4):
    """Return layout geometry for sequence mode bars/chord slots."""
    total_chords = num_bars * chords_per_bar
    left_x = int(WIDTH * 0.06)
    right_x = int(WIDTH * 0.94)
    lane_width = right_x - left_x
    slot_width = lane_width / total_chords

    chord_centers = [left_x + slot_width * (i + 0.5) for i in range(total_chords)]
    bar_edges = [left_x + slot_width * chords_per_bar * i for i in range(num_bars + 1)]

    note_scale = min(1.0, max(0.9, slot_width / (NOTE_WIDTH_PX * 1.05)))

    return {
        "chord_centers": chord_centers,
        "bar_edges": bar_edges,
        "staff_left": left_x,
        "staff_right": right_x,
        "note_scale": note_scale,
    }


def draw_sequence_staff(screen, layout):
    """Draw a full-width grand staff overlay (no clef symbols)."""
    left_x = int(layout["staff_left"])
    right_x = int(layout["staff_right"])

    treble_line_notes = ["E4", "G4", "B4", "D5", "F5"]
    bass_line_notes = ["G2", "B2", "D3", "F3", "A3"]
    line_positions = [note_to_position["G"][n] for n in treble_line_notes]
    line_positions.extend(note_to_position["F"][n] for n in bass_line_notes)

    line_thickness = 8
    for pos in line_positions:
        y = int(y_pos_to_pixel(pos))
        pygame.draw.line(screen, BLACK, (left_x, y), (right_x, y), line_thickness)


def draw_sequence_bars(screen, layout):
    """Draw simple equal-width bar separators for sequence mode."""
    top_line_pos = note_to_position["G"]["F5"]
    bottom_line_pos = note_to_position["F"]["G2"]
    top_y = int(y_pos_to_pixel(top_line_pos) - HALF_LINE_SPACING * 3)
    bottom_y = int(y_pos_to_pixel(bottom_line_pos) + HALF_LINE_SPACING * 3)

    for i, x in enumerate(layout["bar_edges"]):
        thickness = 3 if i in (0, len(layout["bar_edges"]) - 1) else 2
        pygame.draw.line(screen, GRAY, (int(x), top_y), (int(x), bottom_y), thickness)


def draw_next_chord_indicator(screen, x_center):
    """Draw a small dot above the next chord slot."""
    top_line_pos = note_to_position["G"]["F5"]
    y = int(y_pos_to_pixel(top_line_pos) - HALF_LINE_SPACING * 4.2)
    radius = max(4, int(HALF_LINE_SPACING * 0.35))
    pygame.draw.circle(screen, RED, (int(x_center), y), radius)


def draw_info_overlay(screen, chord_dict, user_hits, user_misses, paused, octave):
    """Draw chord info and status overlay on screen.
    
    Args:
        screen: Pygame surface
        chord_dict: Current chord dictionary with 'chord_name', 'notes', 'clef'
        user_hits: Set of correctly hit notes
        user_misses: Set of incorrectly hit notes
        paused: Whether game is paused
        octave: Current octave for keyboard simulation
    """
    # Ensure we don't go off screen
    max_y = HEIGHT - 120  # Leave room for status bar and help
    info_font = _get_font(None, 32)
    small_font = _get_font(None, 24)
    y = 20
    
    # Chord info
    if y < max_y:
        text = info_font.render(f"Chord: {chord_dict['chord_name']}", True, BLACK)
        screen.blit(text, (20, y))
        y += 35
    
    if y < max_y:
        text = info_font.render(f"Notes: {', '.join(chord_dict['notes'])}  Clef: {chord_dict['clef']}", True, BLACK)
        screen.blit(text, (20, y))
        y += 35
    
    # Hits and misses
    if user_hits and y < max_y:
        text = info_font.render(f"Hits: {', '.join(sorted(user_hits))}", True, GREEN)
        screen.blit(text, (20, y))
        y += 35
    
    if user_misses and y < max_y:
        text = info_font.render(f"Misses: {', '.join(sorted(user_misses))}", True, RED)
        screen.blit(text, (20, y))
        y += 35
    
    # Status bar at bottom - ensure no cutoff
    status = "PAUSED" if paused else "AUTO"
    text = info_font.render(f"Mode: {status}  |  Octave: {octave}", True, BLACK)
    screen.blit(text, (20, HEIGHT - 70))
    
    help_text = small_font.render(
        "SPACE=next  P=pause/auto  R=reset  A-G=notes  1-6=octave  SHIFT=sharp  CTRL=flat",
        True, GRAY
    )
    screen.blit(help_text, (20, HEIGHT - 35))


def draw_start_screen(screen, font):
    """Draw the start screen."""
    text = font.render("Press any key to start", True, BLACK)
    screen.blit(text, (50, 50))
    
    help_text = font.render("Controls: SPACE=next, P=pause/auto, A-G=notes, 1-6=octave", True, GRAY)
    screen.blit(help_text, (50, 100))


def draw_ear_training_overlay(screen, challenge, sub_mode,
                              player_hits, player_misses,
                              score_correct, score_total,
                              difficulty, octave,
                              show_answer=False,
                              playing_midi=False):
    """Draw ear training mode overlay.

    Args:
        screen: Pygame surface.
        challenge: Current ear training challenge dict (or None).
        sub_mode: "note", "interval", or "chord".
        player_hits: Set of correctly matched notes.
        player_misses: Set of incorrect notes.
        score_correct: Running correct count.
        score_total: Running total count.
        difficulty: Current difficulty level.
        octave: Current keyboard octave.
        show_answer: If True, reveal the answer label and notes.
        playing_midi: If True, MIDI playback is in progress.
    """
    info_font = _get_font(None, 32)
    small_font = _get_font(None, 24)
    big_font = _get_font(None, 48)
    max_y = HEIGHT - 120
    y = 20

    # Mode header
    mode_label = f"Ear Training: {sub_mode.capitalize()}"
    text = big_font.render(mode_label, True, BLACK)
    screen.blit(text, (20, y))
    y += 55

    # Score
    if score_total > 0:
        pct = int(100 * score_correct / score_total)
        score_str = f"Score: {score_correct}/{score_total} ({pct}%)"
    else:
        score_str = "Score: 0/0"
    text = info_font.render(score_str, True, BLACK)
    screen.blit(text, (20, y))
    y += 35

    # Playing indicator
    if playing_midi:
        text = info_font.render("♪ Playing...", True, (0, 0, 180))
        screen.blit(text, (20, y))
        y += 35

    # Hits
    if player_hits and y < max_y:
        text = info_font.render(f"Hits: {', '.join(sorted(player_hits))}", True, GREEN)
        screen.blit(text, (20, y))
        y += 35

    # Misses
    if player_misses and y < max_y:
        text = info_font.render(f"Misses: {', '.join(sorted(player_misses))}", True, RED)
        screen.blit(text, (20, y))
        y += 35

    # Answer reveal
    if show_answer and challenge and y < max_y:
        answer_text = f"Answer: {challenge['label']}  ({', '.join(challenge['notes'])})"
        text = info_font.render(answer_text, True, (0, 100, 0))
        screen.blit(text, (20, y))
        y += 35

    # Bottom status
    diff_text = f"Difficulty: {difficulty} (CTRL+1-4)  |  Octave: {octave}"
    text = info_font.render(diff_text, True, BLACK)
    screen.blit(text, (20, HEIGHT - 105))

    help_text = small_font.render(
        "SPACE=replay  R=new  M=cycle mode  P=pause/auto  A-G=notes  1-6=octave  SHIFT=sharp  CTRL+1-4=diff",
        True, GRAY,
    )
    screen.blit(help_text, (20, HEIGHT - 35))
