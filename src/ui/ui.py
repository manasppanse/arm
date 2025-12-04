import pygame
import datetime
import random
from src.utils.helpers import COLORS, AGENT_COLORS, UI_COLORS, hex_distance
from src.ui.components import TextChip, Button
from src.ui.controls import ControlsPanel
from src.nest.grid import NestGrid 
from src.ui.mesa_visualizer import HexRenderer
from src.model.wasp_model import WaspModel

class WaspSimUI:
    """Pygame Custom Terminal-style UI."""
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("ARM Simulation Tool") 
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()
        self.margin = min(self.width, self.height) * 0.01
        self.font_size = 18
        self.font = pygame.font.SysFont('monospace', self.font_size, bold = True)
        self.small_font = pygame.font.SysFont('monospace', 16)
        self.bg_color = UI_COLORS["bg"]
        self.border_color = UI_COLORS["border"]
        self.text_color = UI_COLORS["text"]
        self.rec_color = UI_COLORS["rec"]
        self.grid = None
        self.agents = []
        self.sim_running = False
        self.recording = False
        self.hover_info = ""
        self.scroll_y = 0
        self.last_realtime_check = pygame.time.get_ticks()
        self.start_time = None
        self.preys = []
        self.prey_respawn_timer = 0.0
        self.prey_respawn_interval = 5.0
        self.max_prey_on_map = 3
        self.setup_layout()
        self.renderer = HexRenderer(self.playground_rect, self.margin, self)
        self.model = None

    # UI Sections Placement & Initializes Controls/Buttons.
    def setup_layout(self):
        inner_w = self.width - 2 * self.margin
        inner_h = self.height - 2 * self.margin
        left_w = inner_w * 0.7
        right_w = inner_w * 0.3

        # PLAYGROUND (MESA Map)
        self.playground_rect = pygame.Rect(self.margin, self.margin, left_w, inner_h)
        right_x = self.margin + left_w + self.margin
        panel_w = right_w
        btn_h = self.font_size + 12
        gap = self.margin

        # PLAYGROUND - LEGEND Box.
        self.legend_rect = pygame.Rect(self.playground_rect.x + 20, self.playground_rect.y + 20, 220, 295)

        # Right Panel STATUS Bar
        top_h = self.font_size + 12
        self.top_bar_rect = pygame.Rect(right_x, self.margin, panel_w, top_h)

        # Right Panel RECORDING Buttons
        rec_y = self.margin + top_h + self.margin
        btn_w = (panel_w - gap) // 2
        button_bg = UI_COLORS["panel_bg"]
        
        self.start_rec_btn = Button(
            pygame.Rect(right_x, rec_y, btn_w, btn_h), 
            'START RECORDING', 
            self.font, 
            button_bg, 
            self.text_color, 
            self.start_recording
        )
        self.stop_rec_btn = Button(
            pygame.Rect(right_x + btn_w + gap, rec_y, btn_w, btn_h), 
            'STOP RECORDING', 
            self.font, 
            button_bg,
            self.text_color, 
            self.stop_recording
        )

        # Right Panel - METRICS Display (Text Chips)
        met_y = rec_y + btn_h + self.margin
        met_h = (self.font_size + 12) * 3 + self.margin * 4
        self.metrics_rect = pygame.Rect(right_x, met_y, panel_w, met_h)
        self.metrics = []
        chip_w = (panel_w - 3 * gap) / 2
        chip_h = self.font_size + 12
        labels = ["Route Eff.", "Unfed L%", "L1:2:3 %", "Redundancy", "Hunger Peeps", "Radial Bias"]
        for i, label in enumerate(labels):
            col = i % 2
            row = i // 2
            x = right_x + gap + col * (chip_w + gap)
            y = met_y + self.margin + row * (chip_h + gap)
            self.metrics.append(TextChip(pygame.Rect(x, y, chip_w, chip_h), label, "—"))

        # Right Panel - HOVERSTATE
        hover_y = met_y + met_h + self.margin
        self.hover_rect = pygame.Rect(right_x, hover_y, panel_w, 90)

        # Right Panel - SIMULATION & EXIT Buttons.
        exit_y = self.height - self.margin - btn_h
        sim_y = exit_y - btn_h - self.margin
        
        self.start_sim_btn = Button(
            pygame.Rect(right_x, sim_y, btn_w, btn_h), 
            'START SIM', 
            self.font, 
            button_bg,
            self.text_color, 
            self.start_sim
        )
        self.stop_sim_btn = Button(
            pygame.Rect(right_x + btn_w + gap, sim_y, btn_w, btn_h), 
            'STOP SIM', 
            self.font, 
            button_bg,
            self.text_color, 
            self.stop_sim
        )
        self.exit_btn = Button(
            pygame.Rect(right_x, exit_y, panel_w, btn_h), 
            'EXIT PROGRAM', 
            self.font, 
            button_bg,
            self.text_color, 
            pygame.quit
        )

        # Right Panel - PARAMETERS Box
        params_y = hover_y + 90 + self.margin
        params_bottom = sim_y - self.margin
        self.params_rect = pygame.Rect(right_x, params_y, panel_w, params_bottom - params_y)
        
        ctrl_rect = self.params_rect.inflate(-self.margin * 2, -self.margin * 2)
        ctrl_rect.y += self.margin
        ctrl_rect.height -= self.margin
        self.controls = ControlsPanel(ctrl_rect, self.font_size, self.margin)
        self.max_scroll = max(0, self.controls.content_height - ctrl_rect.height)
        
    # Draws Standard Bordered Panel w/ Title.
    def draw_titled_border(self, surf, rect, title):
        color = self.border_color
        title_surf = self.font.render(title, True, color)
        tw, th = title_surf.get_width(), title_surf.get_height()
        pygame.draw.line(surf, color, (rect.x, rect.y), (rect.x + 5, rect.y), 1)
        surf.blit(title_surf, (rect.x + 10, rect.y - th // 2))
        pygame.draw.line(surf, color, (rect.x + 15 + tw, rect.y), (rect.right, rect.y), 1)
        pygame.draw.line(surf, color, (rect.x, rect.y), (rect.x, rect.bottom), 1)
        pygame.draw.line(surf, color, (rect.right, rect.y), (rect.right, rect.bottom), 1)
        pygame.draw.line(surf, color, (rect.x, rect.bottom), (rect.right, rect.bottom), 1)

    # Recording Logic.
    def start_recording(self):
        self.recording = True
        self.start_time = pygame.time.get_ticks()
    def stop_recording(self):
        self.recording = False
        self.start_time = None

    # Spawn Preys in a Random, Unoccupied Cell @ Launch Ring.
    def spawn_prey(self):
        if not self.grid: return
        r = self.grid.visible_radius + 1
        launch_ring_cells = [p for p in self.grid.cells if hex_distance(p, (0,0)) == r]
        occupied_cells = {p for p, _ in self.preys}
        available_cells = [p for p in launch_ring_cells if p not in occupied_cells]
        if available_cells:
            pos = random.choice(available_cells)
            self.preys.append((pos, 10.0))

    # Initiates a New Sim w/ Params b.o Slider Values.
    def start_sim(self):
        if self.sim_running: return
        
        controls = self.controls.sliders
        n_for = int(controls["Forager %"].value)
        n_rec = int(controls["Primary Receiver %"].value)
        max_bouts = int(controls["Max Bouts"].value)
        food_scarcity = controls["Food Scarcity"].value
        n_fed = n_rec // 2 if n_rec > 0 else 10 

        self.model = WaspModel(
            self,
            n_for=n_for,
            n_rec=n_rec,
            n_fed=n_fed,
            max_bouts=max_bouts,
            food_scarcity=food_scarcity
        )
        self.renderer.model = self.model
        self.grid = self.model.ui.grid
        self.agents = self.model.ui_agents 
        self.sim_running = True
        self.preys.clear()
        self.spawn_prey()
        self.prey_respawn_timer = 0.0
        self.last_realtime_check = pygame.time.get_ticks()
        self.model.start_new_bout(self.last_realtime_check)

    # Stops Simulation Run & Resets State.
    def stop_sim(self):
        self.sim_running = False
        self.grid = None
        self.agents = []
        self.model = None

    # Calculate & Update Metric Display Chips.
    def update_metrics(self):
        if not self.grid or not self.model: 
            for m in self.metrics: m.value = "—"
            return
        
        larvae = [c for c in self.grid.cells.values() if c.type == "larva"]
        total = len(larvae)
        
        # Metric 01: Route Efficiency
        total_steps = self.model.current_bout_steps
        larvae_fed = self.model.current_bout_larvae_fed
        efficiency = (larvae_fed / total_steps) * 100 if total_steps else 0
        self.metrics[0].value = f"{efficiency:.2f}"

        # Metric 02: Unfed Larvae %
        unfed = sum(1 for c in larvae if c.hunger > 0.1)
        self.metrics[1].value = f"{(unfed/total * 100 if total else 0):.1f}%"
        
        # Metric 03: L1:L2:L3 Larval Stage Ratio %
        larvae_data = {'larva1': 0, 'larva2': 0, 'larva3': 0}
        total_larvae_in_ratio = 0
        
        for cell in self.grid.cells.values():
            if cell.type == "larva":
                stage = cell.stage
                if stage in larvae_data:
                    larvae_data[stage] += 1
                total_larvae_in_ratio += 1
        
        if total_larvae_in_ratio > 0:
            l1_pc = (larvae_data.get('larva1', 0) / total_larvae_in_ratio) * 100
            l2_pc = (larvae_data.get('larva2', 0) / total_larvae_in_ratio) * 100
            l3_pc = (larvae_data.get('larva3', 0) / total_larvae_in_ratio) * 100
            
            raw_percentages = [l1_pc, l2_pc, l3_pc]
            rounded_percentages = [int(p) for p in raw_percentages]
            error = 100 - sum(rounded_percentages)
            fractions = [p - int(p) for p in raw_percentages]
            sorted_fractions = sorted([(f, i) for i, f in enumerate(fractions)], reverse = True)
            
            for i in range(error):
                original_index = sorted_fractions[i][1]
                rounded_percentages[original_index] += 1
                
            l_ratio = f"{rounded_percentages[0]}:{rounded_percentages[1]}:{rounded_percentages[2]}"
        else:
            l_ratio = "0:0:0"

        self.metrics[2].value = l_ratio
        
        # Metric 04: Bout Count
        self.metrics[3].label = "Bout Count"
        self.metrics[3].value = str(self.model.bout_count)

        # Metric 05: Hungry Receivers
        hungry_receivers = sum(1 for a in self.agents if a.agent_type == "primary_receiver" and a.load < 0.1)
        self.metrics[4].value = str(hungry_receivers)
        
        # Metric 06: Radial Bias
        foragers_total = 0
        periphery_radius = self.grid.visible_radius + 1 
        foragers_on_periphery = 0
        
        for agent in self.agents:
            if agent.agent_type == "forager":
                foragers_total += 1
                if hex_distance(agent.pos, (0, 0)) == periphery_radius: 
                    foragers_on_periphery += 1
        
        radial_bias = (foragers_on_periphery / foragers_total) * 100 if foragers_total > 0 else 0.0
        self.metrics[5].value = f"{radial_bias:.1f}%"

    # Draw all UI Components Onscreen.
    def draw(self):
        self.screen.fill(self.bg_color)
        
        # Draw PLAYGROUND & Nest Grid
        self.draw_titled_border(self.screen, self.playground_rect, "PLAYGROUND")
        inner = self.playground_rect.inflate(-self.margin * 2, -self.margin * 2)
        pygame.draw.rect(self.screen, self.border_color, inner, 1)
        
        old_clip = self.screen.get_clip()
        self.screen.set_clip(inner)
        if self.grid:
            self.renderer.draw_grid(self.screen, self.grid)
            self.renderer.draw_preys(self.screen, self.preys) 
            self.renderer.draw_agents(self.screen, self.agents)
        self.screen.set_clip(old_clip)

        # Draw LEGEND
        pygame.draw.rect(self.screen, UI_COLORS["panel_bg"], self.legend_rect)
        self.draw_titled_border(self.screen, self.legend_rect, "LEGEND")
        lx, ly = self.legend_rect.x + 15, self.legend_rect.y + 15
        items = [("Egg", COLORS["egg"]), ("Pupa", COLORS["pupa"]), ("Larva L1", COLORS["larva1"]),
                 ("Larva L2", COLORS["larva2"]), ("Larva L3", COLORS["larva3"]),
                 ("Forager (Full)", AGENT_COLORS["forager_full"]), ("Forager (Empty)", AGENT_COLORS["forager_empty"]), 
                 ("Receiver", AGENT_COLORS["primary_receiver"]), ("Feeder", AGENT_COLORS["secondary_feeder"]),
                 ("Prey", AGENT_COLORS["prey"]),
                 ("Foraging Env", COLORS["empty"])]
        for lbl, col in items:
            pygame.draw.rect(self.screen, col, (lx, ly, 20, 20))
            pygame.draw.rect(self.screen, UI_COLORS["border"], (lx, ly, 20, 20), 1)
            self.screen.blit(self.small_font.render(lbl, True, UI_COLORS["text"]), (lx + 30, ly + 2))
            ly += 25

        # Draw STATUS
        self.draw_titled_border(self.screen, self.top_bar_rect, "STATUS")
        
        if self.recording and self.start_time:
            dur = (pygame.time.get_ticks() - self.start_time) // 1000
            rec_text = f"REC {dur//3600:02d}:{(dur%3600)//60:02d}:{dur%60:02d}"
        else:
            rec_text = "RECORDING: OFF"
        rec_surf = self.font.render(rec_text, True, self.rec_color if self.recording else self.text_color)
        self.screen.blit(rec_surf, (self.top_bar_rect.x + 15, self.top_bar_rect.y + 8))
        
        utc = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S UTC")
        utc_surf = self.font.render(utc, True, self.text_color)
        self.screen.blit(utc_surf, (self.top_bar_rect.right - utc_surf.get_width() - 15, self.top_bar_rect.y + 8))

        # Draw METRICS
        self.draw_titled_border(self.screen, self.metrics_rect, "METRICS")
        for m in self.metrics: m.draw(self.screen)
        
        # Draw HOVERSTATE
        self.draw_titled_border(self.screen, self.hover_rect, "HOVERSTATE")
        if self.hover_info:
            lines = self.hover_info.split('\n')
            for i, l in enumerate(lines):
                self.screen.blit(self.small_font.render(l, True, (255, 255, 200)), (self.hover_rect.x + 10, self.hover_rect.y + 10 + i * 15))

        # Draw PARAMETERS
        self.draw_titled_border(self.screen, self.params_rect, "PARAMETERS")
        old_clip = self.screen.get_clip()
        self.screen.set_clip(self.params_rect.inflate(-5, -5))
        self.controls.draw(self.screen, self.scroll_y)
        self.screen.set_clip(old_clip)

        # Draw Buttons.
        self.start_rec_btn.draw(self.screen)
        self.stop_rec_btn.draw(self.screen)
        self.start_sim_btn.draw(self.screen)
        self.stop_sim_btn.draw(self.screen)
        self.exit_btn.draw(self.screen)

        pygame.display.flip()

    # Pygame Event Processing.
    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return False
            
            if self.start_rec_btn.handle_event(e): self.start_recording()
            if self.stop_rec_btn.handle_event(e): self.stop_recording()
            if self.start_sim_btn.handle_event(e): self.start_sim()
            if self.stop_sim_btn.handle_event(e): self.stop_sim()
            if self.exit_btn.handle_event(e): return False
            
            if e.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                adj_e = pygame.event.Event(e.type, {'pos': (e.pos[0], e.pos[1] + self.scroll_y), 'button': getattr(e,'button',1)})
                if self.params_rect.collidepoint(e.pos):
                    self.controls.handle_event(adj_e, self.scroll_y) 
            
            if e.type == pygame.MOUSEWHEEL and self.params_rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_y = max(0, min(self.max_scroll, self.scroll_y - e.y * 20))

            if self.sim_running and self.playground_rect.collidepoint(pygame.mouse.get_pos()):
                if e.type == pygame.MOUSEMOTION:
                    ax = self.renderer.mouse_to_axial(e.pos)
                    self.hover_info = self.renderer.get_hover_info(ax, self.grid)
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if e.button == 4: self.renderer.zoom_in()
                    if e.button == 5: self.renderer.zoom_out()
                    
        return True

    # Main Sim & Rendering Loop
    def run(self):
        clock = pygame.time.Clock()
        while self.handle_events():
            if self.sim_running and self.model:
                now = pygame.time.get_ticks()
                dt = (now - self.last_realtime_check) / 1000.0 
                
                # Prey Respawn Logic
                self.prey_respawn_timer += dt
                if self.prey_respawn_timer > self.prey_respawn_interval and len(self.preys) < self.max_prey_on_map: 
                    self.spawn_prey()
                    self.prey_respawn_timer = 0.0
                    
                # Hunger Decay Logic
                if self.grid:
                    self.grid.decay_hunger(dt)
                    for agent in self.model.ui_agents:
                        if hasattr(agent, 'decay_hunger'):
                            agent.decay_hunger(dt)
                            
                self.last_realtime_check = now
                self.model.check_bout_end_time(now)
                self.model.step()
                
                # Slowing Down Sim Update Rate -> Wait 200ms betn. Model Steps (~5steps/s)
                pygame.time.wait(200) 
                self.update_metrics()
            
            self.draw()
            clock.tick(60)
        pygame.quit()