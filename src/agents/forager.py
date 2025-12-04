from .base_agent import WaspAgent
from src.utils.helpers import hex_distance
import random

class Forager(WaspAgent):
    """Manage Forager Behaviour: Prey Searching, Hunting & Returning Food Units to a Primary Receiver."""
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.agent_type = "forager"
        self.load = 0.0
        self.target_prey = None
        self.state = "searching"
        self.last_dir = None

    def step(self):
        center = (0, 0)
        dist = hex_distance(self.pos, center)

        # Return With Food.
        if self.load > 0.1:
            self.state = "returning"
            receivers = [a for a in self.model.ui_agents if a.agent_type == "primary_receiver" and a.load < 5.0]
            if receivers:
                target = min(receivers, key = lambda a: hex_distance(self.pos, a.pos))
                dist_to_target = hex_distance(self.pos, target.pos)
                if dist_to_target == 0:
                    give = min(1.0, self.load)
                    self.load -= give
                    target.load += give
                    if not self.model.current_bout:
                        self.model.start_new_bout(self.model.ui.last_realtime_check)
                    return
                self.move_toward(target.pos)
                return
            if dist > self.model.ui.grid.visible_radius:
                self.move_toward(center)
            return

        # Hunt for Prey
        if self.target_prey is None or not any(p_pos == self.target_prey for p_pos, _ in self.model.ui.preys):
            self.target_prey = None
            available_prey = self.model.ui.preys
            if available_prey:
                nearest_prey_pos, _ = min(available_prey, key = lambda x: hex_distance(self.pos, x[0]))
                self.target_prey = nearest_prey_pos
                self.state = "hunting"

        if self.target_prey and self.target_prey in self.model.ui.grid.cells:
            self.state = "hunting"
            dist_to_prey = hex_distance(self.pos, self.target_prey)
            
            if dist_to_prey <= 1: 
                for i, (p, l) in enumerate(self.model.ui.preys):
                    if p == self.target_prey:
                        self.load = l
                        self.model.ui.preys.pop(i)
                        self.model.food_in_system += self.load 
                        
                        if not self.model.current_bout:
                            self.model.current_bout = True
                            self.model.current_bout_steps = 0
                            self.model.start_new_bout(self.model.ui.last_realtime_check)
                        break
                self.target_prey = None
                return
                
            self.move_toward(self.target_prey)
            return

        # Search for Prey
        self.state = "searching"
        launch_ring = self.model.ui.grid.visible_radius + 1
        if dist < launch_ring:
            neighbors = self.get_neighbors()
            if neighbors:
                outer = max(neighbors, key = lambda n: hex_distance(n, center))
                self.move_toward(outer)
        else:
            if not self.last_dir or self.pos == self.last_dir or hex_distance(self.pos, self.last_dir) <= 1:
                periphery = [p for p in self.model.ui.grid.cells if hex_distance(p, (0,0)) == launch_ring]
                if periphery:
                    self.last_dir = random.choice(periphery)
            if self.last_dir:
                self.move_toward(self.last_dir)