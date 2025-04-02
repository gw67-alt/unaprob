import random
import math
import numpy as np
import time
import os
from enum import Enum, auto
from PIL import Image, ImageDraw, ImageFont

# Get the current directory to save the GIF
current_dir = os.getcwd()
output_gif_path = os.path.join(current_dir, "quantum_circuit_simulation.gif")

# Define component states
class ComponentState(Enum):
    OFF = auto()
    ON = auto()
    ACTIVE = auto()
    INACTIVE = auto()
    OPEN = auto()
    CLOSED = auto()

class CircuitComponent:
    def __init__(self, name):
        self.name = name
        self.state = ComponentState.OFF
        self.inputs = []
        self.outputs = []
        self.probability = 1.0
        self.time_coordinate = 0.0
        
    def add_input(self, component):
        self.inputs.append(component)
        component.outputs.append(self)
        
    def update(self, dt):
        pass
    
    def __str__(self):
        return f"{self.name}: {self.state.name}"

class PowerSource(CircuitComponent):
    def __init__(self, name="Power Source"):
        super().__init__(name)
        self.voltage = 5.0
        
    def update(self, dt):
        self.state = ComponentState.ON
        self.time_coordinate += dt
        
class LED(CircuitComponent):
    def __init__(self, name="LED"):
        super().__init__(name)
        self.brightness = 0.0
        self.color = "red"
        
    def update(self, dt):
        power_on = any(input_comp.state == ComponentState.ON for input_comp in self.inputs)
        button_pressed = any(isinstance(input_comp, PowerButton) and input_comp.state == ComponentState.CLOSED 
                            for input_comp in self.inputs)
        
        if power_on and button_pressed:
            self.state = ComponentState.ON
            self.brightness = 1.0
        else:
            self.state = ComponentState.OFF
            self.brightness = 0.0
            
        self.time_coordinate += dt

class Phototransistor(CircuitComponent):
    def __init__(self, name="Phototransistor"):
        super().__init__(name)
        self.sensitivity = 0.8
        
    def update(self, dt):
        led_on = any(isinstance(input_comp, LED) and input_comp.state == ComponentState.ON 
                    for input_comp in self.inputs)
        power_on = any(isinstance(input_comp, PowerSource) and input_comp.state == ComponentState.ON 
                     for input_comp in self.inputs)
        
        if led_on and power_on:
            self.state = ComponentState.ACTIVE
        else:
            self.state = ComponentState.INACTIVE
            
        self.time_coordinate += dt

class Resistor(CircuitComponent):
    def __init__(self, name="Resistor", resistance=1000):
        super().__init__(name)
        self.resistance = resistance
        
    def update(self, dt):
        quantum_box = any(input_comp.name == "Quantum Box" for input_comp in self.inputs)
        
        if quantum_box:
            self.state = ComponentState.ACTIVE
        else:
            self.state = ComponentState.INACTIVE
            
        self.time_coordinate += dt

class PowerButton(CircuitComponent):
    def __init__(self, name="Power Button"):
        super().__init__(name)
        self.state = ComponentState.OPEN
        self.pressed = False
        
    def press(self):
        self.pressed = not self.pressed
        self.state = ComponentState.CLOSED if self.pressed else ComponentState.OPEN
        
    def update(self, dt):
        power_on = any(isinstance(input_comp, PowerSource) and input_comp.state == ComponentState.ON 
                     for input_comp in self.inputs)
        
        if not power_on:
            self.state = ComponentState.OPEN
            self.pressed = False
            
        self.time_coordinate += dt

class TunnelDiode(CircuitComponent):
    def __init__(self, name="Tunnel Diode"):
        super().__init__(name)
        self.tunnel_probability = 0.3
        
    def update(self, dt):
        button_active = any(isinstance(input_comp, PowerButton) and input_comp.state == ComponentState.CLOSED 
                          for input_comp in self.inputs)
        
        if button_active and random.random() < self.tunnel_probability:
            self.state = ComponentState.ACTIVE
        else:
            self.state = ComponentState.INACTIVE
            
        self.time_coordinate += dt

class DetermineSelection(CircuitComponent):
    def __init__(self, name="Determine Selection"):
        super().__init__(name)
        
    def update(self, dt):
        phototransistor_active = any(isinstance(input_comp, Phototransistor) and 
                                    input_comp.state == ComponentState.ACTIVE 
                                    for input_comp in self.inputs)
        
        if phototransistor_active:
            self.state = ComponentState.ACTIVE
        else:
            self.state = ComponentState.INACTIVE
            
        self.time_coordinate += dt

class QuantumBox(CircuitComponent):
    def __init__(self, name="Quantum Box"):
        super().__init__(name)
        self.p = 0.5  # position coordinate
        self.t = -0.5  # time coordinate
        self.probability_field = np.zeros((10, 10))
        self.update_probability_field()
        self.simulation_stopped = False
        self.reset_count = 0
        self.p_reset_count = 0
        self.t_reset_count = 0
        
    def update_probability_field(self):
        x = np.linspace(-1, 1, 10)
        y = np.linspace(-1, 1, 10)
        X, Y = np.meshgrid(x, y)
        
        wave_function = np.sin(5 * X + self.t) * np.cos(5 * Y + self.p)
        self.probability_field = np.abs(wave_function)**2
        self.probability_field = self.probability_field / np.max(self.probability_field) if np.max(self.probability_field) > 0 else self.probability_field
        
    def update(self, dt):
        determine_active = any(isinstance(input_comp, DetermineSelection) and 
                             input_comp.state == ComponentState.ACTIVE 
                             for input_comp in self.inputs)
        
        tunnel_active = any(isinstance(input_comp, TunnelDiode) and 
                          input_comp.state == ComponentState.ACTIVE 
                          for input_comp in self.inputs)
                          
        if self.simulation_stopped:
            if self.p > 0:
                self.state = ComponentState.ACTIVE
            else:
                self.state = ComponentState.INACTIVE
            return
            
        old_t = self.t
        self.t += dt * 0.5
        
        old_p = self.p
        if determine_active:
            self.p += 0.05
        if tunnel_active:
            self.p -= 0.05
            
        if abs(self.p - 1.0) < 0.05 and abs(self.t - 1.0) < 0.05:
            self.simulation_stopped = True
            self.p = 1.0
            self.t = 1.0
            print(f"\n*** FINAL STATE REACHED: p = {self.p:.2f}, t = {self.t:.2f} ***")
            print(f"*** After {self.reset_count} total resets ({self.p_reset_count} p-resets, {self.t_reset_count} t-resets) ***")
            return
            
        p_reset = False
        t_reset = False
        
        if self.p >= 1.0:
            old_p = self.p
            self.p = 0.5
            p_reset = True
            self.p_reset_count += 1
            
        if self.t >= 1.0:
            old_t = self.t
            self.t = -0.5
            t_reset = True
            self.t_reset_count += 1
        
        if p_reset or t_reset:
            self.reset_count += 1
            reset_type = []
            if p_reset:
                reset_type.append(f"p={old_p:.2f}→0.5")
            if t_reset:
                reset_type.append(f"t={old_t:.2f}→-0.5")
                
            reset_str = " and ".join(reset_type)
            print(f"\n*** RESET #{self.reset_count}: {reset_str} ***")
            
        self.p = max(-1.0, self.p)
        self.t = max(-1.0, self.t)
        
        self.update_probability_field()
        
        if self.p > 0:
            self.state = ComponentState.ACTIVE
        else:
            self.state = ComponentState.INACTIVE
            
        self.time_coordinate += dt

class CircuitSimulation:
    def __init__(self):
        self.power_source = PowerSource()
        self.led = LED()
        self.phototransistor = Phototransistor()
        self.resistor = Resistor()
        self.power_button = PowerButton()
        self.tunnel_diode = TunnelDiode()
        self.determine_selection = DetermineSelection()
        self.quantum_box = QuantumBox()
        
        # Force initial button state
        self.power_button.pressed = True
        self.power_button.state = ComponentState.CLOSED
        
        # Connect components
        self.led.add_input(self.power_source)
        self.led.add_input(self.power_button)
        self.led.add_input(self.resistor)
        
        self.phototransistor.add_input(self.power_source)
        self.phototransistor.add_input(self.led)
        
        self.determine_selection.add_input(self.phototransistor)
        self.determine_selection.add_input(self.power_source)
        
        self.power_button.add_input(self.power_source)
        
        self.tunnel_diode.add_input(self.power_button)
        
        self.quantum_box.add_input(self.determine_selection)
        self.quantum_box.add_input(self.tunnel_diode)
        
        self.resistor.add_input(self.quantum_box)
        
        self.components = [
            self.power_source,
            self.led,
            self.phototransistor,
            self.resistor,
            self.power_button,
            self.tunnel_diode,
            self.determine_selection,
            self.quantum_box
        ]
        
        self.time = 0.0
        self.dt = 0.1
        self.frames = []
        self.max_frames = 300
        self.frames_after_final_state = 20
        
    def update_simulation(self, dt):
        if random.random() < 0.02:
            self.power_button.press()
            
        for component in self.components:
            component.update(dt)
            
        self.time += dt
        
    def run_simulation_for_gif(self):
        """Run the simulation and generate frames for a GIF"""
        try:
            # Try to load a font, with fallbacks
            try:
                # Try to load Arial, a common font
                font = ImageFont.truetype("arial.ttf", 12)
                title_font = ImageFont.truetype("arial.ttf", 16)
            except:
                try:
                    # Try a default TrueType font that might be on the system
                    font = ImageFont.truetype("DejaVuSans.ttf", 12)
                    title_font = ImageFont.truetype("DejaVuSans.ttf", 16)
                except:
                    # Fallback to default
                    font = ImageFont.load_default()
                    title_font = ImageFont.load_default()
                    
            frames = []
            frame_count = 0
            final_state_frames = 0
            
            # Viridis-like colormap for the probability field
            def viridis_like(value):
                r = int(255 * (0.4 + 0.6 * value))
                g = int(255 * (0.2 + 0.8 * math.sqrt(value)))
                b = int(255 * (0.5 + 0.5 * value))
                return (r, g, b)
                
            while frame_count < self.max_frames:
                # Update simulation
                self.update_simulation(self.dt)
                
                # Create a new image for this frame
                img = Image.new('RGB', (900, 400), color=(255, 255, 255))
                draw = ImageDraw.Draw(img)
                
                # Draw title
                draw.text((400, 20), "Quantum Circuit Simulation with Reset Until p=1 AND t=1", 
                          fill=(0, 0, 0), font=title_font, anchor="ms")
                
                # Draw component states (Left panel)
                draw.text((150, 50), "Circuit Components", fill=(0, 0, 0), font=title_font, anchor="ms")
                if self.quantum_box.simulation_stopped:
                    draw.text((150, 70), f"FINAL STATE", fill=(0, 100, 0), font=font, anchor="ms")
                else:
                    draw.text((150, 70), f"Resets: {self.quantum_box.reset_count}", fill=(0, 0, 0), font=font, anchor="ms")
                
                # Draw component bars
                bar_width = 60
                bar_height = 150
                bar_x_start = 30
                bar_y_base = 250
                
                for i, component in enumerate(self.components):
                    # Determine if component is active
                    is_active = component.state in [ComponentState.ON, ComponentState.ACTIVE, ComponentState.CLOSED]
                    color = (0, 150, 0) if is_active else (200, 0, 0)
                    
                    # Draw the bar
                    bar_x = bar_x_start + i * (bar_width + 10)
                    bar_height_actual = bar_height if is_active else bar_height // 3
                    draw.rectangle([bar_x, bar_y_base - bar_height_actual, bar_x + bar_width, bar_y_base], 
                                  fill=color, outline=(0, 0, 0))
                    
                    # Draw component name
                    name = component.name.replace(" ", "\n")
                    draw.text((bar_x + bar_width//2, bar_y_base + 10), name, 
                             fill=(0, 0, 0), font=font, anchor="ma")
                
                # Draw quantum field (Right panel)
                draw.text((725, 50), "Quantum Probability Field", fill=(0, 0, 0), font=title_font, anchor="ms")
                
                if self.quantum_box.simulation_stopped:
                    draw.text((725, 70), f"FINAL STATE REACHED", fill=(0, 100, 0), font=font, anchor="ms")
                else:
                    draw.text((725, 70), f"p={self.quantum_box.p:.2f}, t={self.quantum_box.t:.2f}", 
                             fill=(0, 0, 0), font=font, anchor="ms")
                
                # Draw probability field as a grid of colored cells
                cell_size = 25
                field_size = 10
                field_x_start = 600
                field_y_start = 100
                
                # Add labels for the coordinate system
                # Bottom-left corner now has (-1, -1)
                draw.text((field_x_start - 15, field_y_start + field_size * cell_size + 5), 
                         "(-1, -1)", fill=(0, 0, 0), font=font, anchor="lt")
                
                # Top-right corner has (1, 1)
                draw.text((field_x_start + field_size * cell_size + 5, field_y_start - 5), 
                         "(1, 1)", fill=(0, 0, 0), font=font, anchor="lb")
                
                for i in range(field_size):
                    for j in range(field_size):
                        # Modified to flip the y-axis so bottom-left is (-1, -1)
                        # j corresponds to x-axis, 0 -> -1, 9 -> 1
                        # i corresponds to y-axis, 0 -> 1, 9 -> -1 (flipped)
                        # So we need to use (9 - i) to flip vertical axis
                        value = self.quantum_box.probability_field[field_size - 1 - i, j]
                        color = viridis_like(value)
                        x = field_x_start + j * cell_size
                        y = field_y_start + i * cell_size
                        draw.rectangle([x, y, x + cell_size, y + cell_size], fill=color, outline=(200, 200, 200))
                
                # Draw p and t coordinate lines
                # Map from [-1, 1] to pixel coordinates
                # For p (x-axis): -1 -> 0, 1 -> field_size * cell_size
                p_pixel = field_x_start + int((self.quantum_box.p + 1) / 2 * field_size * cell_size)
                
                # For t (y-axis): -1 -> field_size * cell_size, 1 -> 0 (flipped)
                t_pixel = field_y_start + int((1 - (self.quantum_box.t + 1) / 2) * field_size * cell_size)
                
                # Draw coordinate lines
                draw.line([p_pixel, field_y_start, p_pixel, field_y_start + field_size * cell_size], 
                         fill=(255, 0, 0), width=2)
                draw.line([field_x_start, t_pixel, field_x_start + field_size * cell_size, t_pixel], 
                         fill=(255, 0, 0), width=2)
                
                # Draw boundary lines
                boundary_p = field_x_start + field_size * cell_size
                boundary_t = field_y_start + field_size * cell_size
                draw.line([boundary_p, field_y_start, boundary_p, boundary_t], fill=(0, 0, 255), width=2)
                draw.line([field_x_start, field_y_start, boundary_p, field_y_start], fill=(0, 0, 255), width=2)
                
                # Draw reset count
                reset_text = f"Resets: {self.quantum_box.reset_count}\n"
                reset_text += f"p-resets: {self.quantum_box.p_reset_count}\n"
                reset_text += f"t-resets: {self.quantum_box.t_reset_count}"
                draw.text((850, 350), reset_text, fill=(0, 0, 0), font=font, anchor="rs")
                
                # Draw final state message
                if self.quantum_box.simulation_stopped:
                    draw.rectangle([500, 150, 700, 200], fill=(0, 150, 0, 128), outline=(0, 0, 0))
                    draw.text((600, 175), "FINAL STATE REACHED!\np=1 AND t=1", 
                             fill=(255, 255, 255), font=title_font, anchor="ms")
                    final_state_frames += 1
                
                # Draw frame number
                draw.text((20, 380), f"Frame: {frame_count}", fill=(100, 100, 100), font=font)
                
                # Append the frame
                frames.append(img)
                frame_count += 1
                
                # Print progress
                if frame_count % 10 == 0:
                    print(f"Generated frame {frame_count}/{self.max_frames}")
                
                # Check if we've shown enough frames after final state
                if self.quantum_box.simulation_stopped and final_state_frames >= self.frames_after_final_state:
                    print(f"Final state reached, stopping after {final_state_frames} additional frames")
                    break
            
            # Save as GIF
            print(f"Saving GIF with {len(frames)} frames...")
            frames[0].save(
                output_gif_path,
                save_all=True,
                append_images=frames[1:],
                optimize=False,
                duration=150,
                loop=0
            )
            print(f"GIF saved to: {output_gif_path}")
            
        except Exception as e:
            print(f"Error creating GIF: {e}")
            import traceback
            traceback.print_exc()

# Run the simulation and create GIF
if __name__ == "__main__":
    print("Starting quantum circuit simulation for GIF creation:")
    print("- p will reset to 0.5 when it reaches 1.0")
    print("- t will reset to -0.5 when it reaches 1.0")
    print("- Simulation will stop only when p=1 AND t=1 occur simultaneously")
    print("- Creating GIF of the simulation...")
    
    # Set random seed for reproducibility but with an interesting path
    random.seed(42)
    
    simulation = CircuitSimulation()
    simulation.run_simulation_for_gif()