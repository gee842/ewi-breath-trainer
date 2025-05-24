import sys
import time
import numpy as np
import pygame
import pygame.midi
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
HISTORY_LENGTH = 300  # Number of velocity readings to keep
UPDATE_RATE = 30  # FPS
MIDI_POLL_RATE = 10  # ms
BG_COLOR = (25, 25, 25)
TEXT_COLOR = (230, 230, 230)
GRAPH_COLOR = (65, 156, 255)
DEBUG_COLOR = (255, 255, 100)
MAX_DEBUG_MESSAGES = 20

# Color palette for different notes
NOTE_COLORS = [
    (65, 156, 255),   # Blue
    (255, 100, 100),  # Red
    (100, 255, 100),  # Green
    (255, 255, 100),  # Yellow
    (255, 100, 255),  # Magenta
    (100, 255, 255),  # Cyan
    (255, 150, 100),  # Orange
    (150, 100, 255),  # Purple
    (255, 200, 150),  # Peach
    (150, 255, 150),  # Light Green
    (200, 150, 255),  # Lavender
    (255, 150, 200),  # Pink
]

class LongToneVisualizer:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.midi.init()
        
        # Set up the display
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("EWI Breath Trainer")
        self.font = pygame.font.SysFont("Arial", 24)
        self.small_font = pygame.font.SysFont("Arial", 16)
        self.large_font = pygame.font.SysFont("Arial", 48)
        self.clock = pygame.time.Clock()
        
        # Set up MIDI input
        self.setup_midi()
        
        # Data storage
        self.current_note = None
        self.current_velocity = 0
        self.note_name = "No note"
        self.velocity_history = np.zeros(HISTORY_LENGTH)
        self.note_history = np.full(HISTORY_LENGTH, -1)  # Track which note at each point (-1 = no note)
        self.note_colors = {}  # Map note numbers to colors
        self.color_index = 0  # For cycling through colors
        self.is_note_active = False
        self.time_held = 0
        self.start_time = 0
        self.current_note_start_idx = 0  # Where current note started in history
        self.stats = {
            "mean": 0,
            "std_dev": 0,
            "min": 0,
            "max": 0
        }
        
        # Debug mode
        self.debug_mode = False
        self.debug_messages = []
        self.cc_values = {}  # Store current CC values
        self.selected_cc = 7  # Default to CC7 (Volume) for breath controller
        
        # CC Controller button
        self.cc_button_rect = pygame.Rect(50, WINDOW_HEIGHT - 100, 200, 40)
        self.cc_dropdown_open = False
        
        # Create matplotlib figure for the graph
        self.fig, self.ax = plt.subplots(figsize=(8, 3), dpi=100)
        self.fig.patch.set_alpha(0.0)
        self.ax.set_facecolor((0.1, 0.1, 0.1, 0.8))
        
    def setup_midi(self):
        # List available MIDI devices
        device_count = pygame.midi.get_count()
        
        if device_count == 0:
            print("No MIDI devices found.")
            pygame.quit()
            sys.exit()
            
        # Print available devices
        print("Available MIDI devices:")
        input_device_ids = []
        for i in range(device_count):
            device_info = pygame.midi.get_device_info(i)
            is_input = device_info[2]
            if is_input:
                input_device_ids.append(i)
                print(f"{i}: {device_info[1].decode()}")
        
        # If no input devices found
        if not input_device_ids:
            print("No MIDI input devices found.")
            pygame.quit()
            sys.exit()
        
        # Use the first input device by default
        self.midi_input = pygame.midi.Input(input_device_ids[0])
        print(f"Using MIDI device: {pygame.midi.get_device_info(input_device_ids[0])[1].decode()}")
        
    def get_note_name(self, note_num):
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        note_name = notes[note_num % 12]
        octave = note_num // 12 - 1
        return f"{note_name}{octave}"
    
    def add_debug_message(self, message):
        """Add a message to the debug log"""
        timestamp = time.strftime("%H:%M:%S")
        self.debug_messages.append(f"[{timestamp}] {message}")
        if len(self.debug_messages) > MAX_DEBUG_MESSAGES:
            self.debug_messages.pop(0)
    
    def process_midi(self):
        if self.midi_input.poll():
            events = self.midi_input.read(10)
            for event in events:
                data = event[0]
                status = data[0] & 0xF0
                channel = data[0] & 0x0F
                
                # Note on event
                if status == 0x90 and data[2] > 0:
                    self.current_note = data[1]
                    self.current_velocity = data[2]
                    self.note_name = self.get_note_name(self.current_note)
                    self.is_note_active = True
                    self.start_time = time.time()
                    
                    # Assign color to new note if not already assigned
                    if self.current_note not in self.note_colors:
                        self.note_colors[self.current_note] = NOTE_COLORS[self.color_index % len(NOTE_COLORS)]
                        self.color_index += 1
                    
                    # Find current position in history for this note
                    current_idx = np.sum(self.velocity_history > 0)
                    self.current_note_start_idx = current_idx
                    
                    if self.debug_mode:
                        self.add_debug_message(f"Note ON: {self.note_name} (#{data[1]}) Vel:{data[2]} Ch:{channel}")
                    
                # Note off event
                elif (status == 0x80) or (status == 0x90 and data[2] == 0):
                    if self.current_note == data[1]:
                        self.is_note_active = False
                    
                    if self.debug_mode:
                        note_name = self.get_note_name(data[1])
                        self.add_debug_message(f"Note OFF: {note_name} (#{data[1]}) Ch:{channel}")
                
                # Continuous controller (for breath controllers)
                elif status == 0xB0:
                    cc_num = data[1]
                    cc_value = data[2]
                    self.cc_values[cc_num] = cc_value
                    
                    if self.debug_mode:
                        cc_names = {
                            1: "Modulation",
                            2: "Breath",
                            7: "Volume",
                            11: "Expression",
                            64: "Sustain",
                            74: "Filter Cutoff"
                        }
                        cc_name = cc_names.get(cc_num, f"CC{cc_num}")
                        self.add_debug_message(f"CC: {cc_name} ({cc_num}) = {cc_value} Ch:{channel}")
                    
                    # Use the selected CC for velocity
                    if cc_num == self.selected_cc:
                        self.current_velocity = cc_value
                
                # Other MIDI messages
                else:
                    if self.debug_mode:
                        self.add_debug_message(f"MIDI: Status:{status:02X} Data:{data[1]},{data[2]} Ch:{channel}")
        
        # Update velocity history
        if self.is_note_active:
            self.velocity_history = np.roll(self.velocity_history, -1)
            self.note_history = np.roll(self.note_history, -1)
            self.velocity_history[-1] = self.current_velocity
            self.note_history[-1] = self.current_note
            self.time_held = time.time() - self.start_time
            
            # Calculate statistics for current note only
            current_note_mask = self.note_history == self.current_note
            current_note_velocities = self.velocity_history[current_note_mask]
            current_note_velocities = current_note_velocities[current_note_velocities > 0]
            
            if len(current_note_velocities) > 0:
                self.stats["mean"] = np.mean(current_note_velocities)
                self.stats["std_dev"] = np.std(current_note_velocities)
                self.stats["min"] = np.min(current_note_velocities)
                self.stats["max"] = np.max(current_note_velocities)
        
    def update_graph(self):
        self.ax.clear()
        
        # Set up the plot
        self.ax.set_xlim(0, HISTORY_LENGTH)
        self.ax.set_ylim(0, 130)
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Velocity")
        self.ax.set_title("Velocity Consistency Across Notes")
        self.ax.grid(True, alpha=0.3)
        
        # Plot velocity history as one continuous line with color changes
        # First, identify segments and fill brief gaps for musical continuity
        velocity_smoothed = self.velocity_history.copy()
        note_history_smoothed = self.note_history.copy()
        
        # Fill brief gaps (20 samples or less) to connect musical phrases
        # This covers about 600ms at 30 FPS, which should cover most note transitions
        gap_threshold = 20
        non_zero_indices = np.where(self.velocity_history > 0)[0]
        
        if len(non_zero_indices) > 1:
            for i in range(len(non_zero_indices) - 1):
                start_idx = non_zero_indices[i]
                end_idx = non_zero_indices[i + 1]
                gap_size = end_idx - start_idx - 1
                
                # If gap is small enough, interpolate across it
                if gap_size <= gap_threshold and gap_size > 0:
                    start_vel = self.velocity_history[start_idx]
                    end_vel = self.velocity_history[end_idx]
                    start_note = self.note_history[start_idx]
                    end_note = self.note_history[end_idx]
                    
                    # Use a minimum velocity during transitions to avoid drops to 0
                    min_transition_velocity = min(start_vel, end_vel) * 0.7
                    
                    # Interpolate velocity values
                    for j in range(1, gap_size + 1):
                        interp_idx = start_idx + j
                        # Linear interpolation with minimum floor
                        alpha = j / (gap_size + 1)
                        interp_vel = start_vel * (1 - alpha) + end_vel * alpha
                        velocity_smoothed[interp_idx] = max(interp_vel, min_transition_velocity)
                        
                        # Use the end note for the interpolated section if it's valid
                        if end_note >= 0:
                            note_history_smoothed[interp_idx] = end_note
                        elif start_note >= 0:
                            note_history_smoothed[interp_idx] = start_note
        
        # Apply additional smoothing to reduce noise
        # Use a simple moving average over 3 points
        velocity_final = velocity_smoothed.copy()
        for i in range(1, len(velocity_final) - 1):
            if velocity_smoothed[i] > 0:
                velocity_final[i] = (velocity_smoothed[i-1] + velocity_smoothed[i] + velocity_smoothed[i+1]) / 3
        
        # Now plot the smoothed data
        smoothed_non_zero_indices = np.where(velocity_final > 0)[0]
        
        if len(smoothed_non_zero_indices) > 1:
            # Plot line segments between consecutive points with appropriate colors
            for i in range(len(smoothed_non_zero_indices) - 1):
                start_idx = smoothed_non_zero_indices[i]
                end_idx = smoothed_non_zero_indices[i + 1]
                
                start_note = note_history_smoothed[start_idx]
                end_note = note_history_smoothed[end_idx]
                
                # Use the color of the starting note for this segment
                if start_note >= 0:
                    color = self.note_colors.get(start_note, NOTE_COLORS[0])
                    normalized_color = tuple(c/255 for c in color)
                    
                    # Plot line segment
                    x_vals = [start_idx, end_idx]
                    y_vals = [velocity_final[start_idx], velocity_final[end_idx]]
                    self.ax.plot(x_vals, y_vals, color=normalized_color, linewidth=2, alpha=0.8)
        
        # Plot the mean line for current note only
        if self.is_note_active and self.stats["mean"] > 0:
            self.ax.axhline(y=self.stats["mean"], color='r', linestyle='--', alpha=0.7)
        
        # Render the plot to a pygame surface
        canvas = FigureCanvasAgg(self.fig)
        canvas.draw()
        
        # Convert to pygame surface using the correct modern API
        buf = canvas.buffer_rgba()
        size = canvas.get_width_height()
        surf = pygame.image.frombuffer(buf, size, "RGBA")
        
        return surf
    
    def render_debug_panel(self):
        """Render the debug panel showing MIDI messages and CC values"""
        debug_x = WINDOW_WIDTH - 400
        debug_y = 50
        
        # Debug mode indicator
        debug_title = self.font.render("DEBUG MODE (Press 'D' to toggle)", True, DEBUG_COLOR)
        self.screen.blit(debug_title, (debug_x, debug_y))
        
        # Current CC selection
        cc_text = self.font.render(f"Velocity Source: CC{self.selected_cc} (Use 1-9 keys)", True, TEXT_COLOR)
        self.screen.blit(cc_text, (debug_x, debug_y + 30))
        
        # Current CC values
        y_offset = debug_y + 70
        cc_title = self.font.render("Current CC Values:", True, TEXT_COLOR)
        self.screen.blit(cc_title, (debug_x, y_offset))
        y_offset += 25
        
        for cc_num in sorted(self.cc_values.keys()):
            if y_offset > WINDOW_HEIGHT - 200:  # Don't overflow the screen
                break
            cc_value = self.cc_values[cc_num]
            color = DEBUG_COLOR if cc_num == self.selected_cc else TEXT_COLOR
            cc_text = self.small_font.render(f"CC{cc_num}: {cc_value}", True, color)
            self.screen.blit(cc_text, (debug_x, y_offset))
            y_offset += 20
        
        # Recent MIDI messages
        y_offset += 20
        msg_title = self.font.render("Recent MIDI Messages:", True, TEXT_COLOR)
        self.screen.blit(msg_title, (debug_x, y_offset))
        y_offset += 25
        
        for message in self.debug_messages[-10:]:  # Show last 10 messages
            if y_offset > WINDOW_HEIGHT - 30:
                break
            msg_text = self.small_font.render(message, True, TEXT_COLOR)
            self.screen.blit(msg_text, (debug_x, y_offset))
            y_offset += 18
    
    def render_notes_legend(self):
        """Render the notes/color legend outside the graph"""
        # Get all unique notes that have been played
        unique_notes = np.unique(self.note_history[self.note_history >= 0])
        
        if len(unique_notes) == 0:
            return
        
        # Position the legend in the top right area
        legend_x = WINDOW_WIDTH - 200
        legend_y = 50
        
        # Title
        legend_title = self.font.render("Notes:", True, TEXT_COLOR)
        self.screen.blit(legend_title, (legend_x, legend_y))
        legend_y += 30
        
        # Show each note with its color
        for i, note in enumerate(unique_notes):
            if legend_y > WINDOW_HEIGHT - 30:  # Don't overflow
                break
                
            note_name = self.get_note_name(note)
            color = self.note_colors.get(note, NOTE_COLORS[0])
            
            # Draw a colored square
            square_size = 14
            pygame.draw.rect(self.screen, color, 
                           (legend_x, legend_y, square_size, square_size))
            
            # Draw the note name next to the square
            note_text = self.small_font.render(f" {note_name}", True, TEXT_COLOR)
            self.screen.blit(note_text, (legend_x + square_size + 5, legend_y))
            
            # Move to next line, arrange in two columns if we have many notes
            if i % 8 == 7:  # New column every 8 notes
                legend_x += 80
                legend_y = 80
            else:
                legend_y += 18
    
    def render_cc_button(self):
        """Render the CC controller selection dropdown"""
        # Button background
        button_color = (80, 80, 120) if not self.cc_dropdown_open else (100, 100, 140)
        
        # Check if mouse is hovering
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = self.cc_button_rect.collidepoint(mouse_pos)
        
        # Draw main button
        color = (120, 120, 160) if is_hovering else button_color
        pygame.draw.rect(self.screen, color, self.cc_button_rect)
        pygame.draw.rect(self.screen, TEXT_COLOR, self.cc_button_rect, 2)
        
        # Get CC name for display
        cc_names = {
            1: "Modulation (CC1)",
            2: "Breath (CC2)", 
            7: "Volume (CC7)",
            11: "Expression (CC11)",
            74: "Filter (CC74)"
        }
        
        cc_display = cc_names.get(self.selected_cc, f"CC{self.selected_cc}")
        current_value = self.cc_values.get(self.selected_cc, 0)
        
        # Button text
        button_text = f"Breath Control: {cc_display}"
        text_surface = self.small_font.render(button_text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(self.cc_button_rect.centerx, self.cc_button_rect.centery - 5))
        self.screen.blit(text_surface, text_rect)
        
        # Show current value
        value_text = f"Value: {current_value}"
        value_surface = self.small_font.render(value_text, True, TEXT_COLOR)
        value_rect = value_surface.get_rect(center=(self.cc_button_rect.centerx, self.cc_button_rect.centery + 8))
        self.screen.blit(value_surface, value_rect)
        
        # Draw dropdown arrow
        arrow_x = self.cc_button_rect.right - 20
        arrow_y = self.cc_button_rect.centery
        if self.cc_dropdown_open:
            # Up arrow
            pygame.draw.polygon(self.screen, TEXT_COLOR, [
                (arrow_x, arrow_y + 5),
                (arrow_x + 8, arrow_y - 5),
                (arrow_x - 8, arrow_y - 5)
            ])
        else:
            # Down arrow
            pygame.draw.polygon(self.screen, TEXT_COLOR, [
                (arrow_x, arrow_y - 5),
                (arrow_x + 8, arrow_y + 5),
                (arrow_x - 8, arrow_y + 5)
            ])
        
        # Draw dropdown options if open
        if self.cc_dropdown_open:
            common_ccs = [1, 2, 7, 11, 74]
            y_offset = self.cc_button_rect.top - (len(common_ccs) * 30) - 5  # Show above button
            
            for cc_num in common_ccs:
                option_rect = pygame.Rect(self.cc_button_rect.x, y_offset, 
                                        self.cc_button_rect.width, 28)
                
                # Highlight if hovering or if this is the current selection
                is_current = (cc_num == self.selected_cc)
                is_option_hovering = option_rect.collidepoint(mouse_pos)
                
                if is_current:
                    pygame.draw.rect(self.screen, (120, 160, 120), option_rect)  # Green for current
                elif is_option_hovering:
                    pygame.draw.rect(self.screen, (120, 120, 160), option_rect)  # Blue for hover
                else:
                    pygame.draw.rect(self.screen, (60, 60, 80), option_rect)     # Dark for normal
                
                pygame.draw.rect(self.screen, TEXT_COLOR, option_rect, 1)
                
                # Option text
                option_display = cc_names.get(cc_num, f"CC{cc_num}")
                option_value = self.cc_values.get(cc_num, 0)
                option_text = f"{option_display} - Value: {option_value}"
                
                text_surface = self.small_font.render(option_text, True, TEXT_COLOR)
                text_rect = text_surface.get_rect(center=option_rect.center)
                self.screen.blit(text_surface, text_rect)
                
                y_offset += 30
    
    def render(self):
        self.screen.fill(BG_COLOR)
        
        if self.debug_mode:
            # In debug mode, show smaller main display and debug panel
            main_width = WINDOW_WIDTH - 420
            
            # Render the current note
            note_text = self.large_font.render(f"Note: {self.note_name}", True, TEXT_COLOR)
            self.screen.blit(note_text, (50, 50))
            
            # Render the current velocity
            velocity_text = self.large_font.render(f"Velocity: {self.current_velocity} (CC{self.selected_cc})", True, TEXT_COLOR)
            self.screen.blit(velocity_text, (50, 120))
            
            # Render notes legend
            self.render_notes_legend()
            
            # Render debug panel
            self.render_debug_panel()
            
            # Render CC button
            self.render_cc_button()
            
        else:
            # Normal mode - full width display
            # Render the current note
            note_text = self.large_font.render(f"Note: {self.note_name}", True, TEXT_COLOR)
            self.screen.blit(note_text, (50, 50))
            
            # Render the current velocity
            velocity_text = self.large_font.render(f"Velocity: {self.current_velocity}", True, TEXT_COLOR)
            self.screen.blit(velocity_text, (50, 120))
            
            # Render time held
            time_text = self.font.render(f"Time: {self.time_held:.2f} seconds", True, TEXT_COLOR)
            self.screen.blit(time_text, (50, 190))
            
            # Render statistics
            stats_y = 230
            stats_text = self.font.render("Statistics:", True, TEXT_COLOR)
            self.screen.blit(stats_text, (50, stats_y))
            
            mean_text = self.font.render(f"Mean: {self.stats['mean']:.2f}", True, TEXT_COLOR)
            self.screen.blit(mean_text, (50, stats_y + 30))
            
            std_text = self.font.render(f"Std Dev: {self.stats['std_dev']:.2f}", True, TEXT_COLOR)
            self.screen.blit(std_text, (50, stats_y + 60))
            
            consistency_score = 100 - min(100, self.stats['std_dev'] * 5) if self.stats['mean'] > 0 else 0
            score_text = self.font.render(f"Consistency Score: {consistency_score:.1f}%", True, TEXT_COLOR)
            self.screen.blit(score_text, (50, stats_y + 90))
            
            # Draw the graph
            graph_surf = self.update_graph()
            self.screen.blit(graph_surf, (WINDOW_WIDTH // 2 - graph_surf.get_width() // 2, 
                                        WINDOW_HEIGHT // 2))
            
            # Render notes legend
            self.render_notes_legend()
            
            # Render CC button
            self.render_cc_button()
        
        # Add instructions
        if self.debug_mode:
            instructions = self.small_font.render("ESC: quit | D: toggle debug | C: clear history | 1-9: select CC", True, TEXT_COLOR)
        else:
            instructions = self.font.render("Press ESC to quit, D for debug, C to clear history", True, TEXT_COLOR)
        self.screen.blit(instructions, (50, WINDOW_HEIGHT - 40))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        last_midi_check = 0
        
        while running:
            current_time = pygame.time.get_ticks()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_d:
                        self.debug_mode = not self.debug_mode
                        if self.debug_mode:
                            self.add_debug_message("Debug mode enabled")
                        else:
                            self.debug_messages.clear()
                    elif event.key == pygame.K_c:
                        # Clear history
                        self.velocity_history = np.zeros(HISTORY_LENGTH)
                        self.note_history = np.full(HISTORY_LENGTH, -1)
                        self.note_colors.clear()
                        self.color_index = 0
                        if self.debug_mode:
                            self.add_debug_message("History cleared")
                    # Number keys 1-9 to select CC controller
                    elif pygame.K_1 <= event.key <= pygame.K_9:
                        self.selected_cc = event.key - pygame.K_0
                        if self.debug_mode:
                            self.add_debug_message(f"Selected CC{self.selected_cc} for velocity")
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mouse_pos = pygame.mouse.get_pos()
                        
                        # Check if clicking on CC controller button
                        if self.cc_button_rect.collidepoint(mouse_pos):
                            self.cc_dropdown_open = not self.cc_dropdown_open
                        elif self.cc_dropdown_open:
                            # Check if clicking on dropdown options
                            common_ccs = [1, 2, 7, 11, 74]
                            y_offset = self.cc_button_rect.top - (len(common_ccs) * 30) - 5
                            
                            clicked_option = False
                            for cc_num in common_ccs:
                                option_rect = pygame.Rect(self.cc_button_rect.x, y_offset, 
                                                        self.cc_button_rect.width, 28)
                                if option_rect.collidepoint(mouse_pos):
                                    self.selected_cc = cc_num
                                    self.cc_dropdown_open = False
                                    clicked_option = True
                                    if self.debug_mode:
                                        self.add_debug_message(f"Selected CC{self.selected_cc}")
                                    break
                                y_offset += 30
                            
                            # If clicked outside the dropdown, close it
                            if not clicked_option:
                                self.cc_dropdown_open = False
            
            # Check MIDI input at regular intervals
            if current_time - last_midi_check > MIDI_POLL_RATE:
                self.process_midi()
                last_midi_check = current_time
            
            # Render the visualization
            self.render()
            
            # Cap the frame rate
            self.clock.tick(UPDATE_RATE)
        
        # Clean up
        self.midi_input.close()
        pygame.midi.quit()
        pygame.quit()

if __name__ == "__main__":
    visualizer = LongToneVisualizer()
    visualizer.run()
