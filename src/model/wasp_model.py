from mesa import Model
from mesa.space import MultiGrid
from src.agents.forager import Forager
from src.agents.primary_receiver import PrimaryReceiver
from src.agents.secondary_feeder import SecondaryFeeder
from src.nest.grid import NestGrid
from src.utils.helpers import hex_distance
import random

class WaspModel(Model):
    """Main Simulation Model for Grid, Agents & Bout Cycles"""
    def __init__(self, ui, n_for: int, n_rec: int, n_fed: int, max_bouts: int, food_scarcity: float):
        super().__init__()
        self.ui = ui
        self.schedule = []
        
        # Sim Params
        self.n_for = n_for
        self.n_rec = n_rec
        self.n_fed = n_fed
        self.max_bouts = max_bouts
        self.food_scarcity = food_scarcity
        self.ui_agents = []
        
        # Metrics & Bout Management
        self.food_in_system = 0.0
        self.current_bout = False
        self.current_bout_steps = 0
        self.current_bout_larvae_fed = 0.0 
        self.bout_count = 0

        # 1 Bout = 15 Seconds (in milliseconds) (Only for Simulation Purposes.)
        self.bout_duration_ms = 15 * 1000 
        self.bout_start_time = None
        self.MESA_GRID_SIZE = 100 
        self.OFFSET = 50 
        self.grid = MultiGrid(self.MESA_GRID_SIZE, self.MESA_GRID_SIZE, False)
        self.setup()

    # Hex CoOrds -> Positive MESA Grid CoOrds Converter.
    def _shift_pos(self, pos):
        return (pos[0] + self.OFFSET, pos[1] + self.OFFSET)

    # Initalize Nest Grid & Place All Agents
    def setup(self):
        radius = int(self.ui.controls.sliders["Nest Radius"].value)
        self.ui.grid = NestGrid(radius)
        self.nest_grid = self.ui.grid 
        for agent in list(self.ui_agents): 
            self.grid.remove_agent(agent)
        self.schedule.clear()
        self.ui_agents.clear()
        
        # Unique ID Counter
        uid = 0
        
        valid_cells = [
            p for p, c in self.ui.grid.cells.items() 
            if c.stage != "border"
        ]
        
        internal_cells = [
             p for p, c in self.ui.grid.cells.items() 
             if c.stage.startswith("larva")
        ]
        
        forager_launch_cells = [
            p for p, c in self.ui.grid.cells.items() 
            if hex_distance(p, (0, 0)) == radius + 1
        ]
        
        # Foragers
        if forager_launch_cells:
            for _ in range(self.n_for):
                pos = random.choice(forager_launch_cells) if forager_launch_cells else random.choice(valid_cells)
                a = Forager(uid, self, pos) 
                self.grid.place_agent(a, self._shift_pos(pos))
                a.pos = pos
                self.schedule.append(a)
                self.ui_agents.append(a)
                uid += 1
        
        # Primary Receivers
        if internal_cells:
            for _ in range(self.n_rec):
                pos = random.choice(internal_cells)
                a = PrimaryReceiver(uid, self, pos) 
                self.grid.place_agent(a, self._shift_pos(pos)) 
                a.pos = pos
                self.schedule.append(a)
                self.ui_agents.append(a)
                uid += 1

        # Secondary Feeders
        if internal_cells:
            for _ in range(self.n_fed):
                pos = random.choice(internal_cells)
                a = SecondaryFeeder(uid, self, pos) 
                self.grid.place_agent(a, self._shift_pos(pos)) 
                a.pos = pos
                self.schedule.append(a)
                self.ui_agents.append(a)
                uid += 1

    # Termination Check & Run Agent Steps
    def step(self):
        if self.bout_count >= self.max_bouts:
            self.ui.sim_running = False
            return
        
        for agent in self.schedule:
            agent.step()
        
        self.current_bout_steps += 1
        
    # Called by Agent on 1st Food Delivery
    def start_new_bout(self, current_time_ms):
        if not self.current_bout:
            self.current_bout = True
            self.bout_start_time = current_time_ms
            self.current_bout_steps = 0
            self.current_bout_larvae_fed = 0.0
    
    # Called by UI/Frame to Check if TIme Limit has Reached.
    def check_bout_end_time(self, current_time_ms):
        if self.current_bout and self.bout_start_time is not None:
            elapsed_time = current_time_ms - self.bout_start_time
            
            if elapsed_time >= self.bout_duration_ms:
                self.bout_count += 1
                self.food_in_system = 0.0
                self.current_bout = False
                self.bout_start_time = current_time_ms 
                self.current_bout_steps = 0
                self.current_bout_larvae_fed = 0.0
                self.current_bout_steps = 0
                self.current_bout_larvae_fed = 0.0
                # print(f"Bout {self.bout_count} ended by TIME limit (1 minute).") DEBUG LINE
                return True
        return False