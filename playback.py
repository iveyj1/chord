"""
Piano Learning Game - Main Entry Point

A game for learning to read music notation by playing notes on a MIDI keyboard
or simulating with computer keyboard.

Controls:
    SPACE       - Advance to next chord
    P           - Toggle pause/auto-advance mode  
    R           - Reset to start of sequence
    A-G         - Simulate playing a note
    SHIFT+A-G   - Simulate playing a sharp note
    1-6         - Set octave for simulated notes
    ESC         - Quit
"""

import pygame
import mido
import time
import argparse

from constants import WIDTH, HEIGHT, WHITE, BLACK, FPS, TRY_MIDI, MIDI_PORT_NAME
from music import note_to_mnote
from chords import generate_chord, reset_chord_sequence, start_new_line_generation
from utils import get_note_from_midi, strip_accidental
from game import screen, clock, font, staff_img, present_frame
from draw import (
    draw_chord,
    draw_info_overlay,
    draw_start_screen,
    get_sequence_layout,
    draw_sequence_staff,
    draw_sequence_bars,
    draw_next_chord_indicator,
)

# =============================================================================
# Game State
# =============================================================================

state = "start"
current_chord = None
current_clef = None
current_notes = []

user_hit_set = set()
user_miss_set = set()

time_of_chord_display = None
chord_time = 2  # seconds before auto-advance

paused = True  # start paused for testing

current_octave = 4
current_difficulty = 1

# CLI options
show_start_reference_chords = False
sequence_mode = False

# Sequence mode settings/state
SEQUENCE_BARS = 3
CHORDS_PER_BAR = 4
CHORDS_PER_LINE = SEQUENCE_BARS * CHORDS_PER_BAR

sequence_chords = []
sequence_hits = []
sequence_misses = []
active_sequence_index = 0
RELEASE_ADVANCE_DELAY_SEC = 0.10

pressed_keyboard_notes = {}
active_midi_notes = set()
all_inputs_released_since = time.time()
pending_advance_action = None

# =============================================================================
# Keyboard Simulation
# =============================================================================

KEY_TO_NOTE = {
    pygame.K_a: "A",
    pygame.K_b: "B",
    pygame.K_c: "C",
    pygame.K_d: "D",
    pygame.K_e: "E",
    pygame.K_f: "F",
    pygame.K_g: "G",
}


def is_sequence_line_complete():
    """Return True when sequence mode reached end of current line."""
    return sequence_mode and bool(sequence_chords) and active_sequence_index >= len(sequence_chords)


def _has_active_input() -> bool:
    return bool(pressed_keyboard_notes) or bool(active_midi_notes)


def _mark_input_pressed():
    global all_inputs_released_since
    all_inputs_released_since = None


def _mark_input_released_if_all():
    global all_inputs_released_since
    if _has_active_input():
        return
    if all_inputs_released_since is None:
        all_inputs_released_since = time.time()


def _queue_advance(action: str):
    global pending_advance_action
    if pending_advance_action is None:
        pending_advance_action = action


def _consume_ready_advance_action() -> str | None:
    global pending_advance_action

    if pending_advance_action is None:
        return None
    if RELEASE_ADVANCE_DELAY_SEC < 0:
        action = pending_advance_action
        pending_advance_action = None
        return action
    if _has_active_input() or all_inputs_released_since is None:
        return None
    if time.time() < all_inputs_released_since + RELEASE_ADVANCE_DELAY_SEC:
        return None

    action = pending_advance_action
    pending_advance_action = None
    return action


def _display_notes_without_accidentals(notes):
    return {strip_accidental(note) for note in notes}


def _clear_active_misses_on_input():
    """Clear visible wrong-note marks for the active chord on any new note input."""
    if sequence_mode:
        if sequence_chords and not is_sequence_line_complete():
            sequence_misses[active_sequence_index].clear()
    else:
        user_miss_set.clear()


def set_active_sequence_chord():
    """Load the active chord from sequence arrays into current chord globals."""
    global current_chord, current_clef, current_notes, time_of_chord_display

    if not sequence_chords or active_sequence_index >= len(sequence_chords):
        current_chord = sequence_chords[-1] if sequence_chords else None
        current_clef = current_chord["clef"] if current_chord else None
        current_notes = []
        return

    current_chord = sequence_chords[active_sequence_index]
    current_clef = current_chord["clef"]
    current_notes = current_chord["notes"]
    time_of_chord_display = time.time()


def load_sequence_line(regenerate=True):
    """Initialize sequence mode line data (new line or repeat line)."""
    global sequence_chords, sequence_hits, sequence_misses, active_sequence_index

    if regenerate or not sequence_chords:
        start_new_line_generation()
        sequence_chords = [generate_chord(current_difficulty) for _ in range(CHORDS_PER_LINE)]

    sequence_hits = [set() for _ in sequence_chords]
    sequence_misses = [set() for _ in sequence_chords]
    active_sequence_index = 0
    set_active_sequence_chord()


def advance_sequence_chord():
    """Advance sequence mode to next chord, or to line-complete state."""
    global active_sequence_index

    if is_sequence_line_complete():
        return

    active_sequence_index += 1
    set_active_sequence_chord()

# =============================================================================
# MIDI Setup
# =============================================================================

midi_in = None

if TRY_MIDI:
    try:
        midi_in = mido.open_input(MIDI_PORT_NAME)
        print(f"MIDI connected: {MIDI_PORT_NAME}")
    except (OSError, AttributeError) as e:
        print(f"MIDI not available: {e}")
        midi_in = None

# =============================================================================
# Event Handlers
# =============================================================================

def handle_keydown(event):
    """Process a keydown event. Returns new state if changed, else None."""
    global paused, current_octave, state, user_hit_set, user_miss_set
    
    key = event.key
    
    # Global controls (work in any state)
    if key == pygame.K_ESCAPE:
        return "quit"
    
    if key == pygame.K_p:
        paused = not paused
        return None

    # Sequence control: allow immediate new line at any point
    if sequence_mode and key == pygame.K_n:
        return "sequence_new_line"
    
    if key == pygame.K_r:
        if sequence_mode:
            return "sequence_repeat_line"
        reset_chord_sequence()
        return "show_chord"
    

    # Difficulty selection (number keys 1-6 with CTRL)
    if key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6):
        num = key - pygame.K_0  # pygame.K_1 is 49, so 49-48=1
        if 1 <= num <= 6:
            if pygame.key.get_mods() & pygame.KMOD_CTRL:
                # Set difficulty
                global current_difficulty
                current_difficulty = num
                print(f"Difficulty set to {current_difficulty}")
            else:
                # Set octave
                current_octave = num
        return None
    
    # State-specific handling
    if state == "start":
        # Any other key starts the game
        return "show_chord"
    
    if state == "wait_for_notes":
        # Space advances
        if key == pygame.K_SPACE:
            if sequence_mode and is_sequence_line_complete():
                return None
            if sequence_mode:
                return "queue_sequence_advance"
            return "queue_show_chord"
        
        # Note simulation
        if key in KEY_TO_NOTE:
            note_letter = KEY_TO_NOTE[key]
            mods = pygame.key.get_mods()
            if mods & pygame.KMOD_SHIFT:
                note_letter += "#"
            elif mods & pygame.KMOD_CTRL:
                note_letter += "b"
            simulated_note = f"{note_letter}{current_octave}"
            if simulated_note in note_to_mnote:
                pressed_keyboard_notes[key] = simulated_note
                _mark_input_pressed()
                _clear_active_misses_on_input()

                if sequence_mode:
                    if simulated_note in current_notes:
                        sequence_hits[active_sequence_index].add(simulated_note)
                    else:
                        sequence_misses[active_sequence_index].add(simulated_note)
                else:
                    if simulated_note in current_notes:
                        user_hit_set.add(simulated_note)
                    else:
                        user_miss_set.add(simulated_note)
    
    return None


def handle_keyup(event):
    """Process key release for keyboard input hold tracking."""
    key = event.key
    if key in pressed_keyboard_notes:
        del pressed_keyboard_notes[key]
        _mark_input_released_if_all()


def process_midi():
    """Process pending MIDI messages and return note_on MIDI numbers this frame."""
    global user_hit_set, user_miss_set

    note_on_midi = []

    if not midi_in:
        return note_on_midi

    for msg in midi_in.iter_pending():
        if msg.type == "note_on" and msg.velocity > 0:
            active_midi_notes.add(msg.note)
            _mark_input_pressed()
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity <= 0):
            if msg.note in active_midi_notes:
                active_midi_notes.remove(msg.note)
            _mark_input_released_if_all()
            continue

        note_on_midi.append(msg.note)

        if state != "wait_for_notes":
            continue
        if sequence_mode and is_sequence_line_complete():
            continue

        _clear_active_misses_on_input()

        note = get_note_from_midi(msg.note, current_notes)
        if sequence_mode:
            if note in current_notes:
                sequence_hits[active_sequence_index].add(note)
            else:
                sequence_misses[active_sequence_index].add(note)
        else:
            if note in current_notes:
                user_hit_set.add(note)
            else:
                user_miss_set.add(note)

    return note_on_midi


def check_chord_complete():
    """Check if current chord has been completed."""
    if sequence_mode:
        if is_sequence_line_complete():
            return False

        hits = sequence_hits[active_sequence_index]
        misses = sequence_misses[active_sequence_index]
        if hits.issuperset(set(current_notes)):
            if not misses:
                chord_name = current_chord["chord_name"] if current_chord else "Chord"
                print(f"✓ {chord_name}")
            return True
        return False

    if user_hit_set.issuperset(set(current_notes)):
        if not user_miss_set:
            chord_name = current_chord["chord_name"] if current_chord else "Chord"
            print(f"✓ {chord_name}")
        return True
    return False


def parse_args():
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description="Piano learning game")
    parser.add_argument(
        "--show-start-reference-chords",
        "--show-reference",
        action="store_true",
        dest="show_start_reference_chords",
        help="show C2-C3-C4 (bass) and C4-C5-C6 (treble) on the start screen",
    )
    parser.add_argument(
        "--sequence",
        action="store_true",
        help="show 3 bars x 4 chords line and progress through the full line",
    )
    return parser.parse_args()

# =============================================================================
# Main Game Loop
# =============================================================================

def main():
    global state, current_chord, current_clef, current_notes
    global show_start_reference_chords, sequence_mode
    global user_hit_set, user_miss_set, time_of_chord_display
    global pending_advance_action

    args = parse_args()
    show_start_reference_chords = args.show_start_reference_chords
    sequence_mode = args.sequence
    
    running = True
    
    while running:
        # --- Event Processing ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                new_state = handle_keydown(event)
                if new_state == "quit":
                    running = False
                elif new_state == "queue_sequence_advance":
                    if sequence_mode and state == "wait_for_notes" and not is_sequence_line_complete():
                        _queue_advance("sequence_advance")
                elif new_state == "queue_show_chord":
                    if state == "wait_for_notes":
                        _queue_advance("show_chord")
                elif new_state == "sequence_new_line":
                    if sequence_mode:
                        pending_advance_action = None
                        load_sequence_line(regenerate=True)
                        state = "wait_for_notes"
                elif new_state == "sequence_repeat_line":
                    if sequence_mode:
                        pending_advance_action = None
                        load_sequence_line(regenerate=False)
                        state = "wait_for_notes"
                elif new_state:
                    if new_state == "show_chord":
                        pending_advance_action = None
                    state = new_state

            if event.type == pygame.KEYUP:
                handle_keyup(event)
        
        # --- Clear Screen ---
        screen.fill(WHITE)
        if staff_img and not sequence_mode:
            screen.blit(staff_img, (0, 0))
        
        # --- State Machine ---
        if state == "start":
            draw_start_screen(screen, font)
            if show_start_reference_chords:
                draw_chord(screen, ["C2", "C3", "C4"], "half", "F")
                draw_chord(screen, ["C4", "C5", "C6"], "half", "G")
        

        elif state == "show_chord":
            pending_advance_action = None
            if sequence_mode:
                if not sequence_chords:
                    load_sequence_line(regenerate=True)
                else:
                    set_active_sequence_chord()
            else:
                # Get next chord with current difficulty
                current_chord = generate_chord(current_difficulty)
                current_clef = current_chord['clef']
                current_notes = current_chord['notes']
                # Reset tracking
                user_hit_set.clear()
                user_miss_set.clear()
                time_of_chord_display = time.time()
            state = "wait_for_notes"
        
        elif state == "wait_for_notes":
            process_midi()

            if sequence_mode:
                if is_sequence_line_complete():
                    load_sequence_line(regenerate=True)
                else:
                    if (
                        not paused
                        and time_of_chord_display is not None
                        and time.time() > time_of_chord_display + chord_time
                    ):
                        _queue_advance("sequence_advance")
                    elif check_chord_complete():
                        _queue_advance("sequence_advance")

                    ready_action = _consume_ready_advance_action()
                    if ready_action == "sequence_advance":
                        advance_sequence_chord()

                layout = get_sequence_layout(SEQUENCE_BARS, CHORDS_PER_BAR)
                draw_sequence_staff(screen, layout)
                draw_sequence_bars(screen, layout)

                for idx, chord in enumerate(sequence_chords):
                    x_center = layout["chord_centers"][idx]
                    draw_chord(
                        screen,
                        chord["notes"],
                        "half",
                        chord["clef"],
                        x_center=x_center,
                        scale=layout["note_scale"],
                    )
                    draw_chord(
                        screen,
                        sequence_hits[idx],
                        "whole",
                        chord["clef"],
                        x_center=x_center,
                        scale=layout["note_scale"],
                    )
                    draw_chord(
                        screen,
                        _display_notes_without_accidentals(sequence_misses[idx]),
                        "x",
                        chord["clef"],
                        x_center=x_center,
                        scale=layout["note_scale"],
                    )

                if not is_sequence_line_complete() and sequence_chords:
                    draw_next_chord_indicator(screen, layout["chord_centers"][active_sequence_index])

                info_chord = current_chord if current_chord else {
                    "chord_name": "-",
                    "notes": [],
                    "clef": "-",
                }
                active_hits = set()
                active_misses = set()
                if not is_sequence_line_complete() and sequence_chords:
                    active_hits = sequence_hits[active_sequence_index]
                    active_misses = _display_notes_without_accidentals(sequence_misses[active_sequence_index])

                draw_info_overlay(screen, info_chord, active_hits, active_misses, paused, current_octave)

                status_font = pygame.font.SysFont(None, 28)
                if not is_sequence_line_complete():
                    current_bar = (active_sequence_index // CHORDS_PER_BAR) + 1
                    line_status = f"Line {active_sequence_index + 1}/{CHORDS_PER_LINE}  Bar {current_bar}/{SEQUENCE_BARS}"
                else:
                    line_status = "Loading next line..."
                line_status_surf = status_font.render(line_status, True, BLACK)
                screen.blit(line_status_surf, (20, HEIGHT - 135))
            else:
                # Auto-advance if not paused
                if (
                    not paused
                    and time_of_chord_display is not None
                    and time.time() > time_of_chord_display + chord_time
                ):
                    _queue_advance("show_chord")

                # Check completion
                if check_chord_complete():
                    _queue_advance("show_chord")

                ready_action = _consume_ready_advance_action()
                if ready_action == "show_chord":
                    state = "show_chord"
                    continue

                # Draw current state
                draw_clef = current_clef if current_clef else "G"
                draw_chord(screen, current_notes, "half", draw_clef)
                draw_chord(screen, user_hit_set, "whole", draw_clef)
                draw_chord(screen, _display_notes_without_accidentals(user_miss_set), "x", draw_clef)
                info_chord = current_chord if current_chord else {
                    "chord_name": "-",
                    "notes": [],
                    "clef": draw_clef,
                }
                draw_info_overlay(
                    screen,
                    info_chord,
                    user_hit_set,
                    _display_notes_without_accidentals(user_miss_set),
                    paused,
                    current_octave,
                )

            # Show difficulty in overlay (move up to avoid overlap)
            diff_font = pygame.font.SysFont(None, 32)
            diff_surf = diff_font.render(f"Difficulty: {current_difficulty} (CTRL+1-6)", True, (0,0,0))
            screen.blit(diff_surf, (20, HEIGHT-105))
        
        # --- Update Display ---
        present_frame(screen)
        clock.tick(FPS)
    
    # Cleanup
    pygame.quit()


if __name__ == "__main__":
    main()
