from .base_agent import WaspAgent
from src.utils.helpers import hex_distance

class SecondaryFeeder(WaspAgent):
    """Manage SecFeeder Behaviour: Receive Food Units from PrimReceiver, Target Hungriest Larva for Delivery."""
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.agent_type = "secondary_feeder"
        self.load = 0.0

    def step(self):
        
        # Feed Larvae
        if self.load > 0.1:
            larvae = [
                (p, c) for p, c in self.model.ui.grid.cells.items() 
                if c.type == "larva" and c.hunger > 0.1
            ]
            if larvae:
                target_pos, target_cell = max(larvae, key = lambda x: x[1].hunger)
                dist_to_target = hex_distance(self.pos, target_pos)
                if dist_to_target <= 1:
                    fed = target_cell.feed(min(0.5, self.load)) 
                    self.load -= fed
                    if fed > 0:
                        self.model.current_bout_larvae_fed += fed 
                        self.model.food_in_system -= fed
                    return
                
                self.move_toward(target_pos)
                return

        # Get Food Units from Primary Receiver
        if self.load < 0.1:
            receivers = [a for a in self.model.ui_agents if a.agent_type == "primary_receiver" and a.load > 0.1]
            if receivers:
                target = min(receivers, key = lambda a: hex_distance(self.pos, a.pos))
                dist_to_target = hex_distance(self.pos, target.pos)
                if dist_to_target <= 1:
                    give = min(1.0, target.load) 
                    self.load += give
                    target.load -= give
                    return
                
                self.move_toward(target.pos)
                return