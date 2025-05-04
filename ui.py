import pygame
import sys
import argparse
import time
import test_case
import os
import datetime

# Import refactored components
from config import FPS, SPEED_LEVELS, DEFAULT_SPEED_INDEX, SCREEN_WIDTH, SCREEN_HEIGHT
from simulation_state import SimulationState
from event_processor import EventProcessor
from ui_components import UIRenderer

# Create screenshots directory if it doesn't exist
SCREENSHOTS_DIR = "screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

class UISimulation:
    """Main UI Simulation class that coordinates the simulation components"""
    
    def __init__(self, fruits, pickers, capacity):
        """Initialize the simulation with given parameters"""
        # Create simulation state manager
        self.state = SimulationState(fruits, pickers, capacity)
        
        # Create event processor
        self.event_processor = EventProcessor(fruits, pickers, capacity, self.state)
        
        # Speed control
        self.speed_index = DEFAULT_SPEED_INDEX
        self.event_delay = SPEED_LEVELS[self.speed_index]
        
        # Create UI renderer
        self.renderer = UIRenderer(self.state)
        
        # Simulation parameters for screenshot naming
        self.fruits = fruits
        self.pickers = pickers
        self.capacity = capacity

    def process_next(self):
        """Process the next event using the event processor"""
        return self.event_processor.process_next(self.event_delay)

    def draw(self, screen):
        """Draw all UI components using the renderer"""
        self.renderer.draw_all(screen, self.speed_index, self.event_processor.log)

    def run(self):
        """Run the main simulation loop"""
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Orchard UI')
        
        # Load images
        self.renderer.load_images()
        
        # Create the game clock
        clock = pygame.time.Clock()
        
        # Main game loop
        running = True
        is_finished = False
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # When simulation has ended and the summary screen is showing, 
                # wait for any key press to exit
                elif is_finished and event.type == pygame.KEYDOWN:
                    running = False
                # Handle keyboard input for speed control during simulation
                elif not is_finished and event.type == pygame.KEYDOWN:
                    self._handle_key_input(event)
                        
            # Process next event if simulation is still running
            if not is_finished:
                still_running = self.process_next()
                
                # If simulation has ended, take screenshot and show summary
                if not still_running:
                    is_finished = True
                    
                    # Draw final state before adding overlay
                    self.draw(screen)
                    
                    # Take screenshot of the final state
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    screenshot_filename = os.path.join(
                        SCREENSHOTS_DIR, 
                        f"sim_f{self.fruits}_p{self.pickers}_c{self.capacity}_{timestamp}.png"
                    )
                    self.renderer.take_screenshot(screen, screenshot_filename)
                    
                    # Draw summary screen with the final results
                    self.renderer.draw_final_summary(screen)
                    pygame.display.flip()
                    continue
            
            # Draw everything if not waiting for key press after finishing
            if not is_finished:
                self.draw(screen)
                
                # Update display and maintain frame rate
                pygame.display.flip()
                clock.tick(FPS)
            
        # Clean up pygame
        pygame.quit()
    
    def _handle_key_input(self, event):
        """Handle keyboard input for simulation control"""
        if event.key == pygame.K_UP:
            # Increase speed (decrease delay)
            self.speed_index = min(len(SPEED_LEVELS) - 1, self.speed_index + 1)
            self.event_delay = SPEED_LEVELS[self.speed_index]
        elif event.key == pygame.K_DOWN:
            # Decrease speed (increase delay)
            self.speed_index = max(0, self.speed_index - 1)
            self.event_delay = SPEED_LEVELS[self.speed_index]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pickers', type=int, default=3,
                       help='Number of pickers in the simulation (default: 3)')
    parser.add_argument('-c', '--capacity', type=int, default=12,
                       help='Capacity of the crate (default: 12)')
    parser.add_argument('-f', '--fruits', type=int, default=15, 
                       help='Number of fruits to simulate (default: 15)')
    parser.add_argument('--run-all-tests', action='store_true',
                       help='Run all test cases sequentially')
    args = parser.parse_args()
    
    if args.run_all_tests:
        # Run all test cases in sequence
        for fruits in test_case.TEST_FRUITS:
            sim = UISimulation(fruits, args.pickers, args.capacity)
            sim.run()
    else:
        # Run only a single simulation with the specified parameters
        sim = UISimulation(args.fruits, args.pickers, args.capacity)
        sim.run()
