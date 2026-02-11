"""
Pygame initialization and global game objects.

This module initializes Pygame and provides shared objects:
- screen: The fixed logical drawing surface
- window: The resizable OS window surface
- clock: Frame rate controller
- font: Default font for text
- staff_img: The staff background image
"""

import pygame
from constants import WIDTH, HEIGHT, CLEF_IMAGE, WHITE
from utils import load_svg_as_surface

# Initialize Pygame
pygame.init()

# Create display window and fixed logical drawing surface
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
screen = pygame.Surface((WIDTH, HEIGHT))
pygame.display.set_caption("Chord Challenge")

# Frame rate controller
clock = pygame.time.Clock()

# Load staff background
try:
    staff_img = load_svg_as_surface(CLEF_IMAGE, WIDTH, HEIGHT)
except FileNotFoundError:
    print(f"Warning: Could not load {CLEF_IMAGE}")
    staff_img = None

# Default font
font = pygame.font.SysFont(None, 36)


def present_frame(logical_surface):
    """Scale logical surface into the window with preserved aspect ratio."""
    win_w, win_h = window.get_size()
    if win_w <= 0 or win_h <= 0:
        return

    scale = min(win_w / WIDTH, win_h / HEIGHT)
    draw_w = max(1, int(WIDTH * scale))
    draw_h = max(1, int(HEIGHT * scale))
    offset_x = (win_w - draw_w) // 2
    offset_y = (win_h - draw_h) // 2

    window.fill(WHITE)

    if draw_w == WIDTH and draw_h == HEIGHT:
        window.blit(logical_surface, (offset_x, offset_y))
    else:
        scaled_surface = pygame.transform.smoothscale(logical_surface, (draw_w, draw_h))
        window.blit(scaled_surface, (offset_x, offset_y))

    pygame.display.flip()
