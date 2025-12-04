import pygame
from src.utils.helpers import UI_COLORS
from src.ui.components import Slider, Dropdown

class ControlsPanel:
    """UI Elenent Manager for Adjusting Sim Params."""
    def __init__(self, rect, font_size, margin):
        self.rect = rect
        self.margin = margin
        self.font_size = font_size
        self.sliders = {}
        self.dropdowns = {}
        self.item_gap = 20
        self.slider_height = 10
        self.label_offset_y = self.font_size + 10
        self.setup_components()
        self.content_height = 0 

    # Define & Initialize All Interactive Controls.
    def setup_components(self):
        self.sliders.clear()
        self.dropdowns.clear()
        x = self.margin
        w = self.rect.width - 2 * self.margin
        y = self.margin
        
        # Slider Object Data: Label, Min, Max, Init Value.
        sliders_data = [
            ("Nest Radius", 2, 8, 5),
            ("Initial Wasp Count", 10, 40, 25),
            ("Forager %", 0, 10, 5),
            ("Primary Receiver %", 0, 20, 10),
            ("Max Bouts", 5, 25, 15),
            ("Food Scarcity", 0.0, 1.0, 0.5),
        ]
        
        current_y_pos = y
        for label, mn, mx, start in sliders_data:
            slider_rect = pygame.Rect(self.rect.x + x, self.rect.y + current_y_pos + self.label_offset_y, w, self.slider_height)
            self.sliders[label] = Slider(slider_rect, label, mn, mx, start, pygame.font.SysFont('monospace', self.font_size))
            current_y_pos += self.label_offset_y + self.slider_height + self.item_gap
            
        dropdown_rect = pygame.Rect(self.rect.x + x, self.rect.y + current_y_pos + self.label_offset_y, w, 30)
        self.dropdowns["Movement Algorithm"] = Dropdown(
            dropdown_rect, "Movement Algorithm", ["Random"], pygame.font.SysFont('monospace', self.font_size)
        )
        current_y_pos += self.label_offset_y + 30 + self.item_gap
        self.content_height = current_y_pos

    # Pass Pygame Events to All Contained Control Elements.
    def handle_event(self, event, scroll_y):
        for s in self.sliders.values():
            s.handle_event(event, scroll_y)
        for d in self.dropdowns.values():
            d.handle_event(event)
            
    def draw(self, surface, scroll_y):
        for s in self.sliders.values():
            s.draw(surface, scroll_y)
        for d in self.dropdowns.values():
            d.draw(surface, scroll_y)