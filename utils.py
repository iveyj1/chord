"""
Utility functions for the piano learning game.

This module contains:
- Note manipulation functions (strip_accidental, compare_notes, etc.)
- MIDI input helpers
- SVG loading
"""

import pygame
import cairosvg
import io
from music import note_to_mnote, mnote_to_note


def strip_accidental(note):
    """Return note without accidental (e.g., 'C#4' -> 'C4')."""
    return note.replace("b", "").replace("#", "")


def compare_notes(note1, comparison, note2):
    """Compare two notes by pitch.
    
    Args:
        note1: First note (e.g., "C4")
        comparison: One of '<', '<=', '>', '>=', '==', '!='
        note2: Second note (e.g., "D4")
    
    Returns:
        bool: Result of the comparison
    """
    mnote1 = note_to_mnote[note1]
    mnote2 = note_to_mnote[note2]
    
    if comparison == '<':
        return mnote1 < mnote2
    elif comparison == '<=':
        return mnote1 <= mnote2
    elif comparison == '>':
        return mnote1 > mnote2
    elif comparison == '>=':
        return mnote1 >= mnote2
    elif comparison == '==':
        return mnote1 == mnote2
    elif comparison == '!=':
        return mnote1 != mnote2
    else:
        raise ValueError(f"Unknown comparison operator: {comparison}")


def get_note_from_midi(midi_num, chord_notes):
    """Convert MIDI number to note name, preferring notes in the current chord.
    
    Args:
        midi_num: MIDI note number (e.g., 60 for middle C)
        chord_notes: List of note names in the current chord
    
    Returns:
        str: Note name (e.g., "C4" or "C#4")
    """
    candidate_notes = mnote_to_note[midi_num]
    
    # Prefer note that's in the chord
    for note in candidate_notes:
        if note in chord_notes:
            return note
    
    # Otherwise prefer sharp notation
    for note in candidate_notes:
        if "#" in note:
            return note
    
    # Fall back to first option
    return candidate_notes[0]


def load_svg_as_surface(svg_path, width, height):
    """Load an SVG file and convert to a Pygame surface.
    
    Args:
        svg_path: Path to the SVG file
        width: Target width in pixels
        height: Target height in pixels
    
    Returns:
        pygame.Surface: The rendered image
    """
    with open(svg_path, "rb") as f:
        svg_data = f.read()
    png_data = cairosvg.svg2png(
        bytestring=svg_data,
        output_width=width,
        output_height=height
    )
    return pygame.image.load(io.BytesIO(png_data))
