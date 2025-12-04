import random
from src.utils.helpers import COLORS, hex_distance

class NestCell:
    """Represents a SINGULAR Hex Cell in Nest Capable of Holding Egg, Pupa, Larva."""
    def __init__(self, pos, stage = "empty"):
        self.pos = pos
        self.stage = stage
        self.type = "larva" if stage.startswith("larva") else stage
        if self.type == "larva":
            self.stage_num = int(stage[-1])
            self.max_hunger = self.stage_num
            self.hunger = 0.0
            self.fed = 0.0
        else:
            self.max_hunger = self.hunger = self.fed = 0.0
        self.visible = True

    # Reduces Larva Hunger Deficit by Given Amount (Capped by Current Hunger).
    def feed(self, amount):
        if self.type != "larva": return 0.0
        fed = min(amount, self.hunger)
        self.hunger -= fed
        self.fed += fed
        return fed
    
    # Increases Larva Hunger Deficit Over Time (dt is Time Delta in Seconds).
    def decay_hunger(self, dt):
        if self.type != "larva": return
        decay_rate_per_sec = 0.01
        self.hunger = min(self.max_hunger, self.hunger + decay_rate_per_sec * dt)

class NestGrid:
    """NestCell Collection in a Hexagonal Grid Layout Manager."""
    def __init__(self, radius):
        self.visible_radius = radius
        self.cells = {}
        self.setup_grid(radius)

    # Initiate All Cells in Grid 
    def setup_grid(self, visible_radius):
        self.cells.clear()
        center = (0, 0)
        for q in range(-visible_radius - 1, visible_radius + 2):
            for r in range(max(-visible_radius - 1, -q-visible_radius - 1),
                           min(visible_radius + 1, -q+visible_radius + 1) + 1):
                pos = (q, r)
                dist = hex_distance(pos, (0, 0))
                if dist > visible_radius + 2:
                    continue
                elif dist == visible_radius + 1:
                    cell = NestCell(pos, "empty")
                elif dist == visible_radius:
                    cell = NestCell(pos, "border")
                else:
                    rnd = random.random()
                    if rnd < 0.12: st = "egg"
                    elif rnd < 0.22: st = "pupa"
                    elif rnd < 0.97: st = f"larva{random.choices([1, 2, 3], weights = [40, 35, 25])[0]}"
                    else: st = "empty"
                    cell = NestCell(pos, st)
                self.cells[pos] = cell
    
    # Initiate Hunger Decay for All Cells in Grid
    def decay_hunger(self, dt):
        for cell in self.cells.values():
            cell.decay_hunger(dt)