import multiprocessing as mp
import random

class SharedResources:
    """
    Encapsulates shared state and synchronization primitives.
    """
    def __init__(self, num_fruits, crate_capacity, process_names, header_line, separator):
        manager = mp.Manager()
        self.process_names = process_names
        self.header_line = header_line
        self.separator = separator

        # Shared containers
        self.tree = manager.list(range(1, num_fruits + 1))
        self.crate = manager.list()

        # Synchronization primitives
        self.tree_lock = mp.Lock()
        self.crate_lock = mp.Lock()
        self.slots_sem = mp.Semaphore(crate_capacity)
        self.full_crate_sem = mp.Semaphore(0)

        # Printing lock
        self.print_lock = mp.Lock()

        # Termination flag
        self.done = mp.Value('b', False)

        # Crate counter
        self.crate_count = mp.Value('i', 0)
        self.crate_capacity = crate_capacity

        # Process states
        self.states = manager.dict({name: 'idle' for name in process_names})


def print_event(active, message, resources):
    """
    Update active state and print a snapshot of all process states.
    """
    with resources.print_lock:
        resources.states[active] = message
        cols = [f"{resources.states[name]:^15}" for name in resources.process_names]
        print(" | ".join(cols))
        print(resources.separator)


class Picker(mp.Process):
    """
    Picks fruits from the tree and stores them into the crate.
    """
    def __init__(self, picker_id, resources: SharedResources):
        super().__init__(name=f"Picker-{picker_id}")
        self.res = resources

    def run(self):
        while True:
            # Tree lock acquire (non-blocking to avoid false waiting)
            if not self.res.tree_lock.acquire(block=False):
                print_event(self.name, 'waiting tree', self.res)
                self.res.tree_lock.acquire()
            # Now acquired
            print_event(self.name, 'acquired tree', self.res)
            try:
                if not self.res.tree:
                    break
                fruit = self.res.tree.pop(random.randrange(len(self.res.tree)))
                print_event(self.name, f'picked {fruit}', self.res)
            finally:
                self.res.tree_lock.release()

            # Slot semaphore acquire
            if not self.res.slots_sem.acquire(block=False):
                print_event(self.name, 'waiting slot', self.res)
                self.res.slots_sem.acquire()
            print_event(self.name, 'got slot', self.res)

            # Crate lock acquire
            if not self.res.crate_lock.acquire(block=False):
                print_event(self.name, 'waiting crate', self.res)
                self.res.crate_lock.acquire()
            print_event(self.name, 'acquired crate', self.res)
            try:
                self.res.crate.append(fruit)
                slot = self.res.crate_count.value + 1
                self.res.crate_count.value = slot
                print_event(self.name, f'stored {slot}', self.res)
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
            self.res.full_crate_sem.acquire()
            print_event('Loader', 'got full', self.res)

            # Crate lock acquire
            if not self.res.crate_lock.acquire(block=False):
                print_event('Loader', 'waiting crate', self.res)
                self.res.crate_lock.acquire()
            print_event('Loader', 'acquired crate', self.res)
            try:
                if self.res.done.value:
                    if self.res.crate_count.value > 0:
                        print_event('Loader', f'partial {self.res.crate_count.value}', self.res)
                    print_event('Loader', 'exiting', self.res)
                    break
                cnt = self.res.crate_count.value
                print_event('Loader', f'loading {cnt}', self.res)
                self.res.crate[:] = []
                self.res.crate_count.value = 0
                print_event('Loader', 'emptied crate', self.res)
            finally:
                self.res.crate_lock.release()

            # Reset slots
            for _ in range(self.res.crate_capacity):
                self.res.slots_sem.release()
            print_event('Loader', 'reset slots', self.res)

