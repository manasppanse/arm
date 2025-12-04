from mesa import Agent
from src.utils.helpers import hex_distance
import random

class WaspAgent(Agent):
    """Base for ALl Wasp Agents (Foragers, Primary Receivers, Secondary Feeders)."""
    def __init__(self, unique_id: int, model, pos):
        object.__init__(self) 
        self.unique_id = unique_id
        self.model = model
        self.pos = None 
        self.agent_type = "wasp"
        self.load = 0.0
        self.max_hunger = 10.0 
        self.hunger = 0.0 

    # Increase Agent Hunger Over Time.
    def decay_hunger(self, dt):
        increase_rate_per_sec = 0.01
        self.hunger = min(self.max_hunger, self.hunger + increase_rate_per_sec * dt)
    
    # Returns List of Valid Adj. Hex CoOrds within Boudnaries of Nest Grid.
    def get_neighbors(self, include_center = False):
        neighbors = []
        directions = [(1,0), (1,-1), (0,-1), (-1,0), (-1,1), (0,1)]
        
        for d in directions:
            n_pos = (self.pos[0] + d[0], self.pos[1] + d[1])
            if n_pos in self.model.ui.grid.cells:
                neighbors.append(n_pos)
            
        if include_center:
            neighbors.append(self.pos)
        return neighbors

    # Hex CoOrds -> MESA Positive Grid CoOrds Converter.
    def _shift_pos(self, pos):
        return (pos[0] + self.model.OFFSET, pos[1] + self.model.OFFSET)

    # Agent Movement Handler.
    def move_to_pos(self, pos):
        if pos == self.pos: return
        new_shifted_pos = self.model._shift_pos(pos)
        current_shifted_pos = self.model._shift_pos(self.pos)
        original_pos = self.pos
        self.pos = current_shifted_pos 
        self.model.grid.move_agent(self, new_shifted_pos)
        self.pos = pos

    # Moves Agent 1 Step Towards a Hex Position.
    def move_toward(self, target):
        if not target: return
        
        candidates = self.get_neighbors()
        if not candidates: return

        best = self.pos
        best_dist = hex_distance(self.pos, target)

        for n_pos in candidates:
            dist = hex_distance(n_pos, target)
            if dist < best_dist:
                cell = self.model.ui.grid.cells.get(n_pos) 
                
                is_exchange_agent = self.agent_type in ["forager", "primary_receiver"]
                if cell and (cell.stage != "border" or is_exchange_agent):
                    best_dist = dist
                    best = n_pos
                elif cell and n_pos == target: 
                    best_dist = dist
                    best = n_pos
        
        if best != self.pos:
            self.move_to_pos(best)