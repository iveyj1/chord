"""
Configuration constants for the piano learning game.

Display settings, colors, and MIDI configuration.
"""

# =============================================================================
# Display Settings
# =============================================================================

WIDTH, HEIGHT = 1680, 1000
FPS = 30

# Colors
WHITE = (200, 200, 200)
BLACK = (0, 0, 0)
NOTE_COLOR = (25, 25, 25)
GREEN = (0, 128, 0)
RED = (200, 0, 0)
GRAY = (100, 100, 100)

# Staff image
CLEF_IMAGE = "grand_staff.svg"

# =============================================================================
# Staff Geometry (in pixels)
# =============================================================================

CENTER_Y_PX = HEIGHT // 2
HALF_LINE_SPACING = 20.6  # Half the distance between staff lines (pixels)

NOTE_WIDTH_PX = HALF_LINE_SPACING * 3
NOTE_HEIGHT_PX = HALF_LINE_SPACING * 2

# =============================================================================
# Mathematical Staff Mapping Parameters
# =============================================================================

# Core spacing (in half-line units) - each semitone moves this many positions
SEMITONE_TO_STAFF_POSITION = 7 / 12  # One semitone = 7/12 staff positions (lines+spaces per octave)

# Clef reference points (MIDI note numbers for bottom staff line)
BASS_CLEF_REFERENCE_MIDI = 43    # G2 (bottom line of bass clef)
TREBLE_CLEF_REFERENCE_MIDI = 64   # E4 (bottom line of treble clef)

# Clef reference positions (half-line units relative to screen center)
BASS_CLEF_REFERENCE_POSITION = -13  # Where G2 sits relative to center
TREBLE_CLEF_REFERENCE_POSITION = 5   # Where E4 sits relative to center

# Range limits (MIDI note numbers)
MIN_MIDI_NOTE = 21  # A0
MAX_MIDI_NOTE = 108  # C8

# =============================================================================
# Legacy Constants (for backward compatibility)
# =============================================================================

# These define where each clef's bottom line sits relative to screen center
BASS_CLEF_BOTTOM_Y = BASS_CLEF_REFERENCE_POSITION
TREBLE_CLEF_BOTTOM_Y = TREBLE_CLEF_REFERENCE_POSITION

# =============================================================================
# MIDI Configuration
# =============================================================================

TRY_MIDI = True
MIDI_PORT_NAME = "Roland Digital Piano MIDI 1"
MIDI_OUT_PORT_NAME = "Roland Digital Piano MIDI 1"

# To find your MIDI port name, run:
#   import mido
#   print(mido.get_input_names())
#   print(mido.get_output_names())
