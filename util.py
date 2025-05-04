import multiprocessing as mp
import random
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

class SharedResources:
    """
    Encapsulates shared state and synchronization primitives.
    """
    def __init__(self, num_fruits, crate_capacity, process_names, header_line, separator):
        manager = mp.Manager()

        # printing wali cheez hai nothing important
        self.process_names = process_names
        self.header_line = header_line
        self.separator = separator

        # Shared containers - store (index, value) pairs for fruits
        self.tree = manager.list([(i, i) for i in range(1, num_fruits + 1)])
        self.crate = manager.list()

        # Previous states for color highlighting
        self.prev_states = manager.dict({name: 'idle' for name in process_names})

        # Synchronization primitives
        self.tree_lock = mp.Lock()  # locks take care of mutual exclusion
        self.crate_lock = mp.Lock()
        self.slots_sem = mp.Semaphore(crate_capacity) # semaphore to limit the number of fruits in the crate
        self.full_crate_sem = mp.Semaphore(0) # semaphore to signal that the crate is full

        # Printing lock (When multiple processes all do print() at the same time, their output can get interleaved on the console, producing jumbled lines )
        self.print_lock = mp.Lock()

        # Termination flag
        self.done = mp.Value('b', False)

        # Crate counter  - takes care of empty slots
        self.crate_count = mp.Value('i', 0)
        self.crate_capacity = crate_capacity # (12)

        # Process states - for printing
        self.states = manager.dict({name: 'idle' for name in process_names})


def get_state_color(state):
    """
    Return color code based on the state.
    """
    if 'waiting' in state:
        return Fore.YELLOW
    elif 'acquired' in state or 'got' in state:
        return Fore.GREEN
    elif 'picked' in state or 'stored' in state:
        return Fore.CYAN
    elif 'full' in state:
        return Fore.MAGENTA + Style.BRIGHT
    elif 'loading' in state or 'emptied' in state:
        return Fore.BLUE + Style.BRIGHT
    elif 'exiting' in state:
        return Fore.RED
    else:
        return Fore.WHITE


def print_event(active, message, resources):
    """
    Update active state and print a snapshot of all process states with color.
    """
    with resources.print_lock:
        # Store previous state and update current state
        resources.prev_states[active] = resources.states.get(active, 'idle')
        resources.states[active] = message
        
        # Format columns with appropriate colors
        cols = []
        for name in resources.process_names:
            state = resources.states[name]
            # Highlight the active process with a different background
            if name == active:
                col_text = Back.BLUE + Fore.WHITE + Style.BRIGHT + f"{state:^15}" + Style.RESET_ALL
            else:
                # Color based on state
                color = get_state_color(state)
                col_text = color + f"{state:^15}"
            cols.append(col_text)
        
        print(" | ".join(cols))
        print(Fore.WHITE + Style.DIM + resources.separator)


class Picker(mp.Process):
    """
    Picks fruits from the tree and stores them into the crate.
    """
    def __init__(self, picker_id, resources: SharedResources):
        super().__init__(name=f"Picker-{picker_id}")
        self.res = resources

    def run(self):
        while True:
            # Tree lock acquire - always block for fairness
            print_event(self.name, 'waiting tree', self.res)
            self.res.tree_lock.acquire()
            # Now acquired
            print_event(self.name, 'acquired tree', self.res)
            try:
                # if tree empty, exit
                if not self.res.tree:
                    break
                # Pop random fruit (index, value pair)
                random_idx = random.randrange(len(self.res.tree))
                fruit_idx, fruit_val = self.res.tree.pop(random_idx)
                print_event(self.name, f'picked #{fruit_idx}:{fruit_val}', self.res)
            finally:
                # release teh lock
                self.res.tree_lock.release()

            # Slot semaphore acquire - always block for fairness
            print_event(self.name, 'waiting slot', self.res)
            self.res.slots_sem.acquire()
            print_event(self.name, 'got slot', self.res)

            # Crate lock acquire - always block for fairness
            print_event(self.name, 'waiting crate', self.res)
            self.res.crate_lock.acquire()
            print_event(self.name, 'acquired crate', self.res)
            try:
                # add fruit (index, value) to crate
                self.res.crate.append((fruit_idx, fruit_val))
                slot = self.res.crate_count.value + 1
                self.res.crate_count.value = slot
                print_event(self.name, f'stored #{fruit_idx} in {slot}', self.res)
                # check if crate is full
                if slot == self.res.crate_capacity:
                    print_event(self.name, 'crate full', self.res)
                    self.res.full_crate_sem.release()
            finally:
                self.res.crate_lock.release()

        print_event(self.name, 'exiting', self.res)


class Loader(mp.Process):
    """
    Waits for full or final crates and loads them.
    """
    def __init__(self, resources: SharedResources):
        super().__init__(name='Loader')
        self.res = resources

    def run(self):
        while True:
            print_event('Loader', 'waiting full', self.res)
            # Wait for a full crate 
            self.res.full_crate_sem.acquire()
            print_event('Loader', 'got full', self.res)

            # Crate lock acquire - always block for fairness
            print_event('Loader', 'waiting crate', self.res)
            self.res.crate_lock.acquire()
            print_event('Loader', 'acquired crate', self.res)
            try:
                # if done, see if partial hain ya nh
                if self.res.done.value:
                    if self.res.crate_count.value > 0:
                        fruit_indices = [f"#{idx}" for idx, _ in self.res.crate]
                        print_event('Loader', f'partial {self.res.crate_count.value} {",".join(fruit_indices)}', self.res)
                    print_event('Loader', 'exiting', self.res)
                    break
                
                cnt = self.res.crate_count.value
                fruit_indices = [f"#{idx}" for idx, _ in self.res.crate]
                print_event('Loader', f'loading {cnt} {",".join(fruit_indices)}', self.res)

                # empty the crate
                self.res.crate[:] = []
                self.res.crate_count.value = 0
                print_event('Loader', 'emptied crate', self.res)
            finally:
                self.res.crate_lock.release()

            # Reset slots
            for _ in range(self.res.crate_capacity):
                self.res.slots_sem.release()
            print_event('Loader', 'reset slots', self.res)

