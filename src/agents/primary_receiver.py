from .base_agent import WaspAgent
from src.utils.helpers import hex_distance

class PrimaryReceiver(WaspAgent):
    """Manage PrimReceiver Behaviour: Receive Food Units from Forager, Distribute to SecFeeder."""
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.agent_type = "primary_receiver"
        self.load = 0.0

    def step(self):
        
        # Distribute Food to Secondary Feeders
        if self.load > 0.1:
            feeders = [a for a in self.model.ui_agents if a.agent_type == "secondary_feeder" and a.load < 2.0]
            if feeders:
                target = min(feeders, key = lambda f: hex_distance(self.pos, f.pos))
                
                dist_to_target = hex_distance(self.pos, target.pos)
                if dist_to_target == 0: 
                    give = min(1.0, self.load)
                    self.load -= give
                    target.load += give
                    self.model.start_new_bout(self.model.ui.last_realtime_check)
                    return
                
                self.move_toward(target.pos)
                return

        # Get Food from Foragers
        if self.load < 5.0:
            
            # Proactive Exchange Check
            for n_pos in self.get_neighbors(include_center=True):
                shifted_pos = self.model._shift_pos(n_pos)
                agents_here = self.model.grid.get_cell_list_contents(shifted_pos)
                for agent in agents_here:
                    if agent.agent_type == "forager" and agent.load > 0.1:
                        give = min(0.5, agent.load)
                        self.load += give
                        agent.load -= give
                        return

            # Movement Logic
            foragers = [a for a in self.model.ui_agents if a.agent_type == "forager" and a.load > 0.1]
            if foragers:
                target = min(foragers, key=lambda f: hex_distance(self.pos, f.pos))
                self.move_toward(target.pos)
                return