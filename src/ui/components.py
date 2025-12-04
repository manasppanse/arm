import pygame
from src.utils.helpers import UI_COLORS

class TerminalComponent:
    """All UI Panels w/ Consistent Terminal Style."""
    def __init__(self, rect, bg_color = UI_COLORS["panel_bg"],
                 border_color = UI_COLORS["border"], text_color = UI_COLORS["text"]):
        self.rect = rect
        self.bg_color = bg_color
        self.border_color = border_color
        self.text_color = text_color
        self.font = pygame.font.SysFont('monospace', 18)

    # Border around Component
    def draw_border(self, surface):
        pygame.draw.rect(surface, self.border_color, self.rect, 1)

    # Component BG Fill
    def draw_bg(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)

class TextChip(TerminalComponent):
    """Small Panel Display Label w/ Dynamic Value."""
    def __init__(self, rect, label, value):
        super().__init__(rect)
        self.label = label
        self.value = value

    def draw(self, surface):
        self.draw_bg(surface)
        self.draw_border(surface)
        label_surf = self.font.render(self.label, True, self.text_color)
        surface.blit(label_surf, (self.rect.x + 5, self.rect.y + 5))
        value_surf = self.font.render(self.value, True, self.text_color)
        surface.blit(value_surf, (self.rect.x + self.rect.width - value_surf.get_width() - 5, self.rect.y + 5))


class Button(TerminalComponent):
    """Clickable Button w/ hover Effect."""
    def __init__(self, rect, label, font, bg_color, text_color, callback):
        super().__init__(rect, bg_color=bg_color, text_color=text_color)
        self.label = label
        self.font = font
        self.original_color = bg_color
        self.hover_color = tuple(min(255, c + 30) for c in self.original_color)
        self.current_color = self.original_color

    # Click Detection & Hover State Update.
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.current_color = self.hover_color
            else:
                self.current_color = self.original_color
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect)
        self.draw_border(surface)
        text_surf = self.font.render(self.label, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class Slider(TerminalComponent):
    """Horizontal Slider for Params Tuning."""
    def __init__(self, rect, label, min_val, max_val, start_val, font):
        super().__init__(rect)
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.font = font
        self.is_dragging = False
        self.track_rect = pygame.Rect(rect.x, rect.y + rect.height // 2 - 2, rect.width, 4)
        self.knob_radius = 8
        self.update_knob_pos()

    # Visual Knob Movement b.o Current Value.
    def update_knob_pos(self):
        norm_val = (self.value - self.min_val) / (self.max_val - self.min_val)
        self.knob_x = int(self.track_rect.x + norm_val * self.track_rect.width)

    # Slider Dragging & Clicking Detection.
    def handle_event(self, event, scroll_y):
        draw_rect = self.rect.move(0, -scroll_y)
        knob_area = pygame.Rect(self.knob_x - self.knob_radius, self.track_rect.y - self.knob_radius, 2 * self.knob_radius, 2 * self.knob_radius)
        knob_area = knob_area.move(0, -scroll_y)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if knob_area.collidepoint(event.pos):
                self.is_dragging = True
            elif draw_rect.collidepoint(event.pos):
                self.update_value_from_pos(event.pos[0])
                self.is_dragging = True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            self.update_value_from_pos(event.pos[0])

    # Mouse X Position -> Slider Value Conversion.
    def update_value_from_pos(self, mouse_x):
        x = max(self.track_rect.x, min(self.track_rect.right, mouse_x))
        norm_val = (x - self.track_rect.x) / self.track_rect.width
        new_value = self.min_val + norm_val * (self.max_val - self.min_val)
        if isinstance(self.min_val, int) and isinstance(self.max_val, int):
            self.value = int(round(new_value))
        else:
            self.value = new_value
            
        self.update_knob_pos()

    # Label, Track, Knob Rendering w/ Vertical Scrolling Support.
    def draw(self, surface, scroll_y):
        draw_rect = self.rect.move(0, -scroll_y)
        if isinstance(self.min_val, int) and isinstance(self.max_val, int):
            value_str = f"{self.value:.0f}"
        else:
            value_str = f"{self.value:.1f}"

        label_surf = self.font.render(f"{self.label}: {value_str}", True, UI_COLORS["text"])
        surface.blit(label_surf, (draw_rect.x, draw_rect.y - self.font.get_height() - 5))
        bar_rect = pygame.Rect(draw_rect.x + 5, draw_rect.y, draw_rect.width - 10, 5)
        pygame.draw.rect(surface, UI_COLORS["border"], bar_rect)
        pos = (self.value - self.min_val) / (self.max_val - self.min_val)
        knob_x = bar_rect.x + int(pos * bar_rect.width)
        pygame.draw.circle(surface, UI_COLORS["text"], (knob_x, bar_rect.centery), 5)

class Dropdown(TerminalComponent):
    """Simple Dropdown Selector."""
    def __init__(self, rect, label, options, font):
        super().__init__(rect)
        self.label = label
        self.options = options
        self.selected = options[0]
        self.font = font
        self.is_open = False
        self.text_color = UI_COLORS["text"]
        self.item_height = 30
        h = len(self.options) * self.item_height
        self.dropdown_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, h)

    # Toggle Menu & Option Selection.
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
            elif self.is_open:
                x, y = event.pos
                if self.dropdown_rect.collidepoint(x, y):
                    index = (y - self.dropdown_rect.y) // self.item_height
                    if 0 <= index < len(self.options):
                        self.selected = self.options[index]
                    self.is_open = False
    
    # Draw Current Selection & Menu Expander.
    def draw(self, surface, scroll_y):
        draw_rect = self.rect.move(0, -scroll_y)
        label_surf = self.font.render(f"{self.label}: {self.selected}", True, self.text_color)
        surface.blit(label_surf, (draw_rect.x, draw_rect.y + 5))
        self.draw_border(surface)

        if self.is_open:
            h = len(self.options) * self.item_height
            self.dropdown_rect = pygame.Rect(draw_rect.x, draw_rect.bottom, draw_rect.width, h)
            pygame.draw.rect(surface, UI_COLORS["panel_bg"], self.dropdown_rect)
            pygame.draw.rect(surface, self.border_color, self.dropdown_rect, 1)

            for i, option in enumerate(self.options):
                item_rect = pygame.Rect(self.dropdown_rect.x, self.dropdown_rect.y + i * self.item_height, self.dropdown_rect.width, self.item_height)
                item_surf = self.font.render(option, True, self.text_color)

                if option == self.selected:
                    pygame.draw.rect(surface, UI_COLORS["border"], item_rect)
                    
                surface.blit(item_surf, (item_rect.x + 5, item_rect.y + 5))