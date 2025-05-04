import math
import random
import pygame
from config import TREE_POS, TREE_RADIUS, FRUIT_Y_OFFSET, CRATE_RECT, PADDING

class SimulationState:
    """Manages the simulation state including positions and counters"""
    
    def __init__(self, fruits, pickers, capacity):
        self.total_fruits = fruits
        self.capacity = capacity
        self.picker_count = pickers

        # Simulation state
        self.tree_fruits = fruits
        self.crate_count = 0
        self.loaded_crates = 0
        self.loaded_fruits = 0           
        self.states = {f"Picker-{i}": 'idle' for i in range(1, pickers+1)}
        self.states['Loader'] = 'idle'
        
        # Initialize crate slots for tracking
        self.crate_slots = [0] * capacity
        
        # Calculate positions
        self._initialize_positions()
    
    def _initialize_positions(self):
        """Initialize all positions for simulation elements"""
        # Fruit positions
        random.seed(0)  # Fixed seed for reproducibility
        self.fruit_positions = self._generate_fruit_positions()
        
        # Crate slot positions
        self.crate_positions = self._generate_crate_positions()
        
        # Initial human positions
        self.initial_positions = self._generate_initial_positions()
    
    def _generate_fruit_positions(self):
        """Generate positions for fruits on the tree"""
        positions = []
        for _ in range(self.total_fruits):
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(20, TREE_RADIUS * 0.5)
            x = TREE_POS.x + math.cos(angle) * r
            y = TREE_POS.y + math.sin(angle) * r - FRUIT_Y_OFFSET
            positions.append(pygame.math.Vector2(x, y))
        return positions
    
    def _generate_crate_positions(self):
        """Generate positions for crate slots"""
        positions = []
        cols, rows = 4, math.ceil(self.capacity / 4)
        for i in range(self.capacity):
            col = i % cols
            row = i // cols
            x = CRATE_RECT.x + 10 + col * (CRATE_RECT.width - 20) / (cols - 1)
            y = CRATE_RECT.y + 10 + row * (CRATE_RECT.height - 20) / (rows - 1)
            positions.append(pygame.math.Vector2(x, y))
        return positions
    
    def _generate_initial_positions(self):
        """Generate initial positions for pickers and loader"""
        positions = {}
        for idx, name in enumerate(list(self.states.keys())[:-1]):
            positions[name] = pygame.math.Vector2(PADDING + 20, 120 + idx * 50)
        positions['Loader'] = pygame.math.Vector2(CRATE_RECT.centerx, CRATE_RECT.centery - 220)
        return positions
    
    def get_picker_position(self, name, state):
        """Calculate the position of a picker based on their state"""
        if name == 'Loader':
            return None  # Loader has special handling
            
        picker_id = int(name.split('-')[1])
        idx = picker_id - 1
        
        # Position around tree, crate, or home based on state
        if 'tree' in state or state.startswith('picked '):
            ang = idx * (2 * math.pi / self.picker_count) - math.pi/2
            return TREE_POS + pygame.math.Vector2(math.cos(ang), math.sin(ang)) * (TREE_RADIUS * 0.5)
        elif 'crate' in state:
            # Position around the crate perimeter based on picker id
            angle_offset = idx * (2 * math.pi / self.picker_count)
            offset_x = 35 * math.cos(angle_offset)
            offset_y = 35 * math.sin(angle_offset)
            return pygame.math.Vector2(CRATE_RECT.centerx + offset_x, CRATE_RECT.y - 20)
        elif state.startswith('stored '):
            # Parse the "stored #X in Y" format to position pickers at correct slots
            try:
                parts = state.split()
                if len(parts) >= 4:
                    slot_number = int(parts[3]) - 1  # Convert to 0-based index
                    if 0 <= slot_number < len(self.crate_positions):
                        # Position the picker just above the slot where they placed the fruit
                        slot_pos = self.crate_positions[slot_number]
                        return pygame.math.Vector2(slot_pos.x, slot_pos.y - 20)
            except (ValueError, IndexError):
                pass
            # Fallback - position around the crate
            angle_offset = idx * (2 * math.pi / self.picker_count)
            offset_x = 30 * math.cos(angle_offset)
            offset_y = 30 * math.sin(angle_offset)
            return pygame.math.Vector2(CRATE_RECT.centerx + offset_x, CRATE_RECT.y - 20)
        else:
            return self.initial_positions[name]
            
    def get_loader_position(self, state):
        """Calculate the position of the loader based on state"""
        from config import TRUCK_RECT, CRATE_RECT
        
        if state == 'waiting full':
            return self.initial_positions['Loader']
        elif state == 'acquired crate':
            return pygame.math.Vector2(*TRUCK_RECT.center)
        elif state in ('got full', 'waiting crate', 'loading'):
            return pygame.math.Vector2(*CRATE_RECT.center)
        elif state in ('emptied crate', 'partial'):
            return pygame.math.Vector2(*TRUCK_RECT.center)
        else:
            return self.initial_positions['Loader']