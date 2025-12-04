import math

# NEST Cell Color Palette
COLORS = {
    "empty": (5, 5, 5), # Almost Black
    "border": (100, 80, 60), # Dark Brown
    "egg": (255, 248, 235), # Cream White
    "larva1": (255, 245, 200), # Pale Yellow
    "larva2": (255, 225, 140), # Warm Yellow
    "larva3": (255, 190, 80), # Golden Yellow
    "pupa": (230, 210, 170), # Light Tan
}

# Agent Role & Behaviour Color Palatte
AGENT_COLORS = {
    "forager_empty": (180, 90, 40), # Rust Brown
    "forager_full": (220, 140, 50), # Amber Orange
    "primary_receiver": (180, 120, 60), # Honey Brown
    "secondary_feeder": (200, 160, 100), # Soft Sand
    "idle": (140, 140, 140), # Medium Gray
    "prey": (0, 255, 255) # Aqua Cyan
}

# UI Color Palette
UI_COLORS = {
    "bg": (5, 5, 5), # Almost Black
    "panel_bg": (20, 20, 40), # Dark Navy
    "border": (0, 180, 180), # Teal Cyan
    "text": (0, 255, 255), # Bright Cyan
    "highlight": (50, 50, 50), # Dark Gray
    "rec": (255, 50, 50), # Alert Red
    "error": (255, 0, 0), # Pure Red
}

# Grid Calculation
def hex_distance(a, b):
    return (abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[0] - b[0] + a[1] - b[1])) // 2