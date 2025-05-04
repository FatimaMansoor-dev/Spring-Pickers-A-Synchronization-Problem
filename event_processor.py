import subprocess
import sys
import time
from config import MAX_LOG_LINES


class EventProcessor:
    """Handles processing of simulation events from external process output"""
    
    def __init__(self, fruits, pickers, capacity, simulation_state):
        """Initialize the event processor with simulation parameters"""
        self.simulation_state = simulation_state
        self.log = []
        
        # Fetch CLI output from main.py
        self._fetch_simulation_events(fruits, pickers, capacity)
        
        # Tracking
        self.current_index = 0
        self.last_time = time.time()
        self.pending_tree_updates = []  # Track pending fruit removal
        
        # Track previous states per picker to avoid duplicate updates
        self.previous_picker_states = {name: '' for name in simulation_state.states.keys()}
        
    def _fetch_simulation_events(self, fruits, pickers, capacity):
        """Run main.py as subprocess and capture output"""
        cmd = [sys.executable, 'main.py',
               '--fruits', str(fruits),
               '--pickers', str(pickers),
               '--capacity', str(capacity)]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        out, _ = proc.communicate()
        self.raw_events = out.splitlines()[2:]  # Skip header lines
    
    def process_next(self, event_delay):
        """Process the next event from raw output if enough time has passed"""
        current_time = time.time()
        
        # Check if enough time has passed since last event
        if current_time - self.last_time < event_delay:
            return True  # Continue running, but don't process a new event yet
            
        # Process one pending tree update if available
        # This creates a visual delay between when fruits are picked and when they disappear
        if self.pending_tree_updates and self.simulation_state.tree_fruits > 0:
            self.simulation_state.tree_fruits -= 1
            self.pending_tree_updates.pop(0)  # Remove the processed update
            return True
            
        # Check if we've reached the end of events
        if self.current_index >= len(self.raw_events):
            # Continue processing any remaining pending updates
            if self.pending_tree_updates:
                return True
            return False
            
        # Get and process the next event line
        line = self.raw_events[self.current_index].strip()
        self.current_index += 1
        
        if not line:
            return True  # Skip empty lines
            
        # Print the line for debugging
        print(line)
        
        # Process the line and update simulation state
        self._process_event_line(line)
        
        # Update the last event time
        self.last_time = current_time
        
        # Stop when everyone's done and no pending updates
        if all(s == 'exiting' for s in self.simulation_state.states.values()) and not self.pending_tree_updates:
            return False
            
        return True
        
    def _process_event_line(self, line):
        """Process a single event line and update the simulation state"""
        # Add to log with max size limit
        self.log.append(line)
        if len(self.log) > MAX_LOG_LINES:
            self.log.pop(0)
            
        # Parse the event line
        cols = [c.strip() for c in line.split('|')]
        if len(cols) == len(self.simulation_state.states):
            # Update each actor's state
            for name, state in zip(self.simulation_state.states.keys(), cols):
                prev = self.simulation_state.states[name]
                
                # Only handle state transitions if state has actually changed
                if state != prev:
                    self.simulation_state.states[name] = state
                    # Handle the state transition only if it's actually new
                    self._handle_state_transition(name, prev, state)
    
    def _handle_state_transition(self, name, prev_state, new_state):
        """Handle special state transitions that affect simulation state"""
        # Check for a real state transition to avoid duplicates
        if name.startswith('Picker') and new_state.startswith('picked '):
            # Only add to pending updates if this picker wasn't already in a picked state
            if not prev_state.startswith('picked '):
                # Extract the fruit information to avoid duplicating
                fruit_info = new_state.split(' ', 1)[1]  # Get everything after "picked "
                
                # Add a unique identifier for this pick action to avoid duplicates
                pick_id = f"{name}:{fruit_info}"
                
                # Check if this exact pick isn't already pending
                if not any(update == pick_id for update in self.pending_tree_updates):
                    # Add the pick identifier to the pending updates
                    self.pending_tree_updates.append(pick_id)
        
        # Storing logic - parse "stored #X in Y" format
        if name.startswith('Picker') and new_state.startswith('stored '):
            self._handle_fruit_stored(new_state)
            
        # Loader empties crate → increment totals & reset crate count
        if name == 'Loader' and new_state == 'emptied crate' and prev_state != new_state:
            self._handle_crate_emptied()
    
    def _handle_fruit_stored(self, state):
        """Handle a fruit being stored in a crate"""
        try:
            # Parse the stored message: "stored #8 in 3" format
            parts = state.split()
            if len(parts) >= 4:
                fruit_number = int(parts[1].replace('#', ''))  # Extract fruit number
                slot_number = int(parts[3])  # Extract slot number
                
                # Update crate count based on number of filled slots
                # Instead of tracking max fruit ID, count the number of filled slots
                self.simulation_state.crate_slots[slot_number-1] = fruit_number
                
                # Count non-zero slots to determine actual crate count
                self.simulation_state.crate_count = sum(1 for slot in self.simulation_state.crate_slots if slot > 0)
                
        except (ValueError, IndexError) as e:
            print(f"Error parsing store message: {state} - {str(e)}")
    
    def _handle_crate_emptied(self):
        """Handle the loader emptying a crate"""
        # Add current crate count to loaded fruits
        self.simulation_state.loaded_crates += 1
        self.simulation_state.loaded_fruits += self.simulation_state.crate_count
        self.simulation_state.crate_count = 0
        # Reset all crate slots
        for i in range(len(self.simulation_state.crate_slots)):
            self.simulation_state.crate_slots[i] = 0