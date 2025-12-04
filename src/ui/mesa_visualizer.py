import pygame
import math
from src.utils.helpers import AGENT_COLORS, COLORS

class HexRenderer:
    """Hex Grid & Agents Rendering using Pygame."""
    def __init__(self, rect, margin, ui):
        self.rect = rect
        self.margin = margin
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.hex_size = 30
        self.ui = ui
        self.model = None

    # Hex CoOrds -> Screen Pixel CoOrds Converter.
    def axial_to_pixel(self, pos):
        q, r = pos
        x = self.hex_size * (math.sqrt(3) * q + math.sqrt(3)/2 * r) * self.zoom
        y = self.hex_size * (3/2 * r) * self.zoom
        return (
            self.rect.centerx + x + self.offset_x,
            self.rect.centery + y + self.offset_y
        )

    # Single Hexagon Cell Corner Points Calculation.
    def hex_points(self, cx, cy):
        points = []
        for i in range(6):
            angle_deg = 60 * i + 30
            angle_rad = math.pi / 180 * angle_deg
            x = cx + self.hex_size * math.cos(angle_rad) * self.zoom
            y = cy + self.hex_size * math.sin(angle_rad) * self.zoom
            points.append((x, y))
        return points

    # Draws Nest Cells.
    def draw_grid(self, surface, grid):
        for pos, cell in grid.cells.items():
            cx, cy = self.axial_to_pixel(pos)
            color = COLORS.get(cell.stage, COLORS["empty"])
            points = self.hex_points(cx, cy)
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, COLORS["border"], points, 1)

    # Draws Prey.
    def draw_preys(self, surface, preys):
        for pos, load in preys:
            px, py = self.axial_to_pixel(pos)
            size = int(self.hex_size * self.zoom * 0.35)
            pygame.draw.circle(surface, AGENT_COLORS["prey"], (int(px), int(py)), size)
            pygame.draw.circle(surface, (255, 255, 255), (int(px), int(py)), size, 2)

    # Draws WaspAgents -> Loop Iterates over self.ui.model.ui_agents (Aliased to 'agents' in Function Signature).
    def draw_agents(self, surface, agents):
        for agent in self.ui.model.ui_agents:
            px, py = self.axial_to_pixel(agent.pos)
            size = int(self.hex_size * self.zoom * 0.3)

            if agent.agent_type == "forager":
                color = AGENT_COLORS["forager_full"] if agent.load > 0.1 else AGENT_COLORS["forager_empty"]
            elif agent.agent_type == "primary_receiver":
                color = AGENT_COLORS["primary_receiver"] if agent.load > 0.1 else tuple(c // 2 for c in AGENT_COLORS["primary_receiver"])
            elif agent.agent_type == "secondary_feeder":
                color = AGENT_COLORS["secondary_feeder"] if agent.load > 0.1 else tuple(c // 2 for c in AGENT_COLORS["secondary_feeder"])
            else:
                color = (180, 180, 180)

            pygame.draw.circle(surface, color, (int(px), int(py)), size)
            pygame.draw.circle(surface, (255, 255, 255), (int(px), int(py)), size, 2)

    # Screen Pixel CoOrds -> Hex CoOrds COnverter.
    def mouse_to_axial(self, mouse_pos):
        px, py = mouse_pos
        x = (px - self.rect.centerx - self.offset_x) / (self.hex_size * self.zoom)
        y = (py - self.rect.centery - self.offset_y) / (self.hex_size * self.zoom)
        q = (math.sqrt(3)/3 * x - 1./3 * y)
        r = (2./3 * y)
        return self._round_axial(q, r)

    # Floating-Point Hex CoOrds -> Nearest Int Hex CoOrds Converter.
    def _round_axial(self, q, r):
        s = -q - r
        q_round = round(q)
        r_round = round(r)
        s_round = round(s)
        q_diff = abs(q_round - q)
        r_diff = abs(r_round - r)
        s_diff = abs(s_round - s)
        if q_diff > r_diff and q_diff > s_diff:
            q_round = -r_round - s_round
        elif r_diff > s_diff:
            r_round = -q_round - s_round
        return (q_round, r_round)

    # Zoom In/Out Function.
    def zoom_in(self):
        self.zoom = min(2.5, self.zoom + 0.10)
    def zoom_out(self):
        self.zoom = max(0.5, self.zoom - 0.10)

    # Hoverstate Text Information Generator.
    def get_hover_info(self, pos, grid):
        if not grid or pos not in grid.cells:
            return "Outside Nest"
        cell = grid.cells[pos]
        lines = [f"Pos: {pos}", f"Cell: {cell.type}"]

        # For Larvae
        if cell.type == "larva":
            lines.append(f"Hunger: {cell.hunger:.1f}/{cell.max_hunger} Units")

        # For Prey
        prey_here = [load for p_pos, load in self.ui.preys if p_pos == pos]
        if prey_here:
            lines.append(f"Prey: {prey_here[0]:.1f} Units")

        # For Agents
        agents_here = [a for a in self.ui.model.ui_agents if a.pos == pos]
        if agents_here:
            lines.append("--- Agents ---")
            for a in agents_here:
                load_info = f"Load: {a.load:.1f}"
                hunger_info = f" | Hunger: {a.hunger:.1f}" if hasattr(a, 'hunger') else ""
                lines.append(f"{a.agent_type.title()} #{a.unique_id} → {load_info}{hunger_info}")

        return "\n".join(lines)