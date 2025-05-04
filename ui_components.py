import pygame
import math
from config import *

class UIRenderer:
    """Handles rendering of all UI components"""
    
    def __init__(self, simulation_state):
        """Initialize the UI renderer with simulation state"""
        self.state = simulation_state
        self.images = {}
        
    def load_images(self):
        """Load and scale all required images"""
        self.images['tree'] = pygame.transform.smoothscale(
            pygame.image.load(ASSET_PATHS['tree']).convert_alpha(),
            (int(TREE_RADIUS*2), int(TREE_RADIUS*2)))
            
        self.images['truck'] = pygame.transform.smoothscale(
            pygame.image.load(ASSET_PATHS['truck']).convert_alpha(),
            (CRATE_RECT.width, CRATE_RECT.height))
            
        self.images['loader'] = pygame.transform.smoothscale(
            pygame.image.load(ASSET_PATHS['loader']).convert_alpha(),
            (LOADER_SIZE, LOADER_SIZE))
        
    def draw_background(self, screen):
        """Draw background panels"""
        screen.fill(LIGHT_GREEN)
        
        # Main simulation area panel
        pygame.draw.rect(screen, PANEL_COLOR, (10, 10, TEXT_AREA_X-20, SCREEN_HEIGHT-20))
        pygame.draw.rect(screen, PANEL_BORDER, (10, 10, TEXT_AREA_X-20, SCREEN_HEIGHT-20), 2)
        
        # Event log panel
        pygame.draw.rect(screen, PANEL_COLOR, (TEXT_AREA_X+10, 10, SCREEN_WIDTH-TEXT_AREA_X-20, SCREEN_HEIGHT-20))
        pygame.draw.rect(screen, PANEL_BORDER, (TEXT_AREA_X+10, 10, SCREEN_WIDTH-TEXT_AREA_X-20, SCREEN_HEIGHT-20), 2)

    def draw_header(self, screen, speed_index):
        """Draw header with simulation info and speed controls"""
        font = pygame.font.SysFont(None, FONT_SIZE)
        hdr = pygame.font.SysFont(None, HEADER_FONT_SIZE, bold=True)
        
        # Header with title
        title_bg = pygame.Rect(25, PADDING, 300, HEADER_FONT_SIZE + 10)
        pygame.draw.rect(screen, MEDIUM_GREEN, title_bg)
        pygame.draw.rect(screen, DARK_BLUE, title_bg, 1)
        screen.blit(hdr.render(f"Orchard: {self.state.total_fruits} Fruits", True, WHITE), 
                  (30, PADDING + 5))
        
        # Speed control indicator
        speed_bg = pygame.Rect(25, PADDING + HEADER_FONT_SIZE + 20, 250, FONT_SIZE + 10)
        pygame.draw.rect(screen, MEDIUM_GREEN, speed_bg)
        pygame.draw.rect(screen, DARK_BLUE, speed_bg, 1)
        speed_text = f"Speed: {5-speed_index}/5 (↑/↓ to change)"
        screen.blit(font.render(speed_text, True, WHITE), 
                  (30, PADDING + HEADER_FONT_SIZE + 25))

    def draw_tree(self, screen):
        """Draw the tree and fruits"""
        font = pygame.font.SysFont(None, FONT_SIZE)
        
        # Draw tree image
        if 'tree' in self.images:
            screen.blit(self.images['tree'], 
                      self.images['tree'].get_rect(center=(int(TREE_POS.x), int(TREE_POS.y))))
        
        # Draw fruits on tree with shadows
        for pos in self.state.fruit_positions[:self.state.tree_fruits]:
            # Shadow
            pygame.draw.circle(screen, (100, 100, 100, 128), (int(pos.x+2), int(pos.y+2)), 7)
            # Fruit
            pygame.draw.circle(screen, YELLOW, (int(pos.x), int(pos.y)), 7)
            pygame.draw.circle(screen, ORANGE, (int(pos.x), int(pos.y)), 7, 1)
        
        # Tree info box
        tree_info_bg = pygame.Rect(TREE_POS.x - 50, TREE_POS.y - TREE_RADIUS - 40, 100, 25)
        pygame.draw.rect(screen, MEDIUM_GREEN, tree_info_bg)
        pygame.draw.rect(screen, DARK_BLUE, tree_info_bg, 1)
        screen.blit(font.render(f"Tree: {self.state.tree_fruits}", True, WHITE),
                  (TREE_POS.x - 45, TREE_POS.y - TREE_RADIUS - 35))

    def draw_crate(self, screen):
        """Draw the crate and its contents"""
        font = pygame.font.SysFont(None, FONT_SIZE)
        
        # Determine crate color based on fullness
        filled_slot_count = sum(1 for slot in self.state.crate_slots if slot > 0)
        crate_color = GREEN if filled_slot_count >= self.state.capacity else BROWN
        
        # Draw crate shadow
        shadow_rect = pygame.Rect(CRATE_RECT.x+4, CRATE_RECT.y+4, CRATE_RECT.width, CRATE_RECT.height)
        pygame.draw.rect(screen, (100, 100, 100, 128), shadow_rect)
        
        # Draw crate outline
        pygame.draw.rect(screen, LIGHT_BROWN, CRATE_RECT)
        pygame.draw.rect(screen, crate_color, CRATE_RECT, 3)
        
        # Draw fruit background slots
        self._draw_crate_slots(screen)
        
        # Draw fruits in crate
        self._draw_crate_contents(screen)
        
        # Crate info box - show actual count of filled slots
        filled_slot_count = sum(1 for slot in self.state.crate_slots if slot > 0)
        crate_status = "FULL" if filled_slot_count >= self.state.capacity else f"{filled_slot_count}/{self.state.capacity}"
        crate_info_bg = pygame.Rect(CRATE_RECT.x, CRATE_RECT.y - 30, 120, 25)
        pygame.draw.rect(screen, MEDIUM_GREEN, crate_info_bg)
        pygame.draw.rect(screen, DARK_BLUE, crate_info_bg, 1)
        screen.blit(font.render(f"Crate: {crate_status}", True, WHITE),
                  (CRATE_RECT.x + 5, CRATE_RECT.y - 25))
                  
    def _draw_crate_slots(self, screen):
        """Draw the empty slot markers in the crate"""
        small_font = pygame.font.SysFont(None, int(FONT_SIZE * 0.7))
        
        for i in range(self.state.capacity):
            pos = self.state.crate_positions[i]
            slot_number = i + 1
            
            # Draw subtle grid markers
            pygame.draw.circle(screen, (220, 220, 200), (int(pos.x), int(pos.y)), 8, 1)
            
            # Small slot number markers
            slot_text = small_font.render(f"{slot_number}", True, GRAY)
            screen.blit(slot_text, (int(pos.x - slot_text.get_width()/2), 
                                  int(pos.y - slot_text.get_height()/2)))
                                  
    def _draw_crate_contents(self, screen):
        """Draw fruits in the crate based on crate_slots data"""
        for slot_idx, fruit_num in enumerate(self.state.crate_slots):
            if fruit_num > 0:  # If there's a fruit in this slot
                pos = self.state.crate_positions[slot_idx]
                # Shadow
                pygame.draw.circle(screen, (100, 100, 100, 128), (int(pos.x+1), int(pos.y+1)), 9)
                # Fruit
                pygame.draw.circle(screen, YELLOW, (int(pos.x), int(pos.y)), 9)
                pygame.draw.circle(screen, ORANGE, (int(pos.x), int(pos.y)), 9, 1)

    def draw_truck(self, screen):
        """Draw the truck and delivery info"""
        font = pygame.font.SysFont(None, FONT_SIZE)
        
        # Draw truck image
        if 'truck' in self.images:
            screen.blit(self.images['truck'], TRUCK_RECT)
            
        # Truck info panel
        truck_info_bg = pygame.Rect(TRUCK_RECT.x, TRUCK_RECT.y + TRUCK_RECT.height + 5, 160, 50)
        pygame.draw.rect(screen, MEDIUM_GREEN, truck_info_bg)
        pygame.draw.rect(screen, DARK_BLUE, truck_info_bg, 1)
        
        # Delivery counts
        screen.blit(font.render(f"Crates delivered: {self.state.loaded_crates}", True, WHITE),
                  (TRUCK_RECT.x + 10, TRUCK_RECT.y + TRUCK_RECT.height + 10))
        screen.blit(font.render(f"Fruits delivered: {self.state.loaded_fruits}", True, WHITE),
                  (TRUCK_RECT.x + 10, TRUCK_RECT.y + TRUCK_RECT.height + 30))

    def draw_pickers(self, screen):
        """Draw all pickers with their states"""
        font = pygame.font.SysFont(None, FONT_SIZE)
        
        for idx, (name, state) in enumerate(self.state.states.items()):
            # Skip the loader, it's drawn separately
            if name == 'Loader':
                continue
                
            picker_id = int(name.split('-')[1])
            
            # Get position based on state
            base = self.state.get_picker_position(name, state)
            
            # Different colors for different pickers
            picker_colors = [BLUE, DARK_BLUE, (70, 150, 210)]
            color_idx = (picker_id - 1) % len(picker_colors)
            
            # Draw picker shadow for depth
            pygame.draw.circle(screen, (100, 100, 100, 128), (int(base.x+2), int(base.y+2)), 14)
            
            # Draw picker with outer ring
            pygame.draw.circle(screen, picker_colors[color_idx], (int(base.x), int(base.y)), 14)
            pygame.draw.circle(screen, WHITE, (int(base.x), int(base.y)), 14, 2)
            
            # Draw picker label and state box
            text_bg = pygame.Rect(base.x + 15 - 2, base.y - 14, 150, 45)
            pygame.draw.rect(screen, (240, 240, 240, 230), text_bg)
            pygame.draw.rect(screen, picker_colors[color_idx], text_bg, 2)
            
            # Label and state text
            screen.blit(font.render(name, True, BLACK), (base.x + 18, base.y - 10))
            screen.blit(font.render(state, True, RED), (base.x + 18, base.y + 8))

    def draw_loader(self, screen):
        """Draw the loader with its state"""
        font = pygame.font.SysFont(None, FONT_SIZE)
        
        # Get loader position based on state
        lstate = self.state.states['Loader']
        base = self.state.get_loader_position(lstate)

        if 'loader' in self.images:
            # Shadow
            shadow_rect = self.images['loader'].get_rect(center=(int(base.x+5), int(base.y+5)))
            shadow = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 100))
            screen.blit(shadow, shadow_rect)
            
            # Loader image
            rect = self.images['loader'].get_rect(center=(int(base.x), int(base.y)))
            screen.blit(self.images['loader'], rect)
        else:
            # Fallback if image not available
            pygame.draw.rect(screen, RED,
                         (base.x - LOADER_SIZE/2, base.y - LOADER_SIZE/2, LOADER_SIZE, LOADER_SIZE))
        
        # Position the loader text below the loader instead of to the right
        # to prevent overlap with the truck when the loader is near it
        loader_text_bg = pygame.Rect(base.x - 60, base.y + LOADER_SIZE/2 + 5, 120, 25)
        pygame.draw.rect(screen, (240, 240, 240, 230), loader_text_bg)
        pygame.draw.rect(screen, RED, loader_text_bg, 2)
        screen.blit(font.render(lstate, True, RED),
                  (base.x - 55, base.y + LOADER_SIZE/2 + 7))

    def draw_event_log(self, screen, log):
        """Draw the event log panel"""
        font = pygame.font.SysFont(None, FONT_SIZE)
        hdr = pygame.font.SysFont(None, HEADER_FONT_SIZE, bold=True)
        
        # Log title
        log_title_bg = pygame.Rect(TEXT_AREA_X+20, PADDING, 120, HEADER_FONT_SIZE + 10)
        pygame.draw.rect(screen, MEDIUM_GREEN, log_title_bg)
        pygame.draw.rect(screen, DARK_BLUE, log_title_bg, 1)
        screen.blit(hdr.render('Event Log', True, WHITE), (TEXT_AREA_X+25, PADDING + 5))
        
        # Log entries with alternate row coloring
        for i, line in enumerate(log):
            y_pos = PADDING + HEADER_FONT_SIZE + 20 + i * (FONT_SIZE + 5)
            # Alternate row background for readability
            if i % 2 == 0:
                row_bg = pygame.Rect(TEXT_AREA_X+20, y_pos, SCREEN_WIDTH-TEXT_AREA_X-40, FONT_SIZE + 4)
                pygame.draw.rect(screen, (230, 240, 255), row_bg)
            screen.blit(font.render(line, True, BLACK),
                      (TEXT_AREA_X + 25, y_pos + 2))
    
    def draw_all(self, screen, speed_index, log):
        """Draw the complete UI"""
        # 1. Draw background
        self.draw_background(screen)
        
        # 2. Draw header and controls
        self.draw_header(screen, speed_index)
        
        # 3. Draw simulation elements
        self.draw_tree(screen)
        self.draw_crate(screen)
        self.draw_truck(screen)
        
        # 4. Draw actors
        self.draw_pickers(screen)
        self.draw_loader(screen)
        
        # 5. Draw event log
        self.draw_event_log(screen, log)
        
    def take_screenshot(self, screen, filename):
        """Take a screenshot of the current screen and save it to a file"""
        pygame.image.save(screen, filename)
        print(f"Screenshot saved as {filename}")
        
    def draw_final_summary(self, screen):
        """Draw a special summary screen highlighting the final state of the simulation"""
        # Add a semi-transparent overlay to the main screen
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))  # Dark overlay with 120/255 alpha
        screen.blit(overlay, (0, 0))
        
        # Add a panel for the final summary
        panel_width, panel_height = 600, 200
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        # Draw panel background
        pygame.draw.rect(screen, PANEL_COLOR, 
                       (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, PANEL_BORDER, 
                       (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Create a large header font
        summary_font = pygame.font.SysFont(None, 36, bold=True)
        info_font = pygame.font.SysFont(None, 24)
        
        # Draw summary title
        title_text = "Simulation Complete - Final Results"
        title = summary_font.render(title_text, True, DARK_BLUE)
        screen.blit(title, (panel_x + (panel_width - title.get_width()) // 2, 
                          panel_y + 20))
        
        # Draw summary information with nice formatting
        info_y = panel_y + 80
        line_spacing = 30
        
        # Total fruits
        total_text = f"Total Fruits: {self.state.total_fruits}"
        total_rendered = info_font.render(total_text, True, BLACK)
        screen.blit(total_rendered, (panel_x + 50, info_y))
        
        # Fruits on tree
        tree_text = f"Remaining on Tree: {self.state.tree_fruits}"
        tree_rendered = info_font.render(tree_text, True, BLACK)
        screen.blit(tree_rendered, (panel_x + 50, info_y + line_spacing))
        
        # Fruits delivered
        delivered_text = f"Fruits Delivered: {self.state.loaded_fruits}"
        delivered_rendered = info_font.render(delivered_text, True, BLACK)
        screen.blit(delivered_rendered, (panel_x + 300, info_y))
        
        # Crates delivered
        crates_text = f"Crates Delivered: {self.state.loaded_crates}"
        crates_rendered = info_font.render(crates_text, True, BLACK)
        screen.blit(crates_rendered, (panel_x + 300, info_y + line_spacing))
        
        # Current crate status
        filled_slot_count = sum(1 for slot in self.state.crate_slots if slot > 0)
        if filled_slot_count > 0:
            crate_text = f"Current Crate: {filled_slot_count}/{self.state.capacity} fruits"
            crate_rendered = info_font.render(crate_text, True, BLACK)
            screen.blit(crate_rendered, (panel_x + 175, info_y + line_spacing * 2))
            
        # Press any key message
        key_text = "Screenshot saved - Press any key to continue"
        key_rendered = info_font.render(key_text, True, RED)
        screen.blit(key_rendered, (panel_x + (panel_width - key_rendered.get_width()) // 2, 
                                 panel_y + panel_height - 40))