import pygame
import sys
import argparse
import subprocess
import time
import math
import random
import test_case

# Configuration
FPS = 30
FONT_SIZE = 18
HEADER_FONT_SIZE = 20
MAX_LOG_LINES = 15
EVENT_DELAY = 0.5
PADDING = 10
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 620

# Colors
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
BROWN = (139, 69, 19)
GREEN = (34, 139, 34)
YELLOW = (255, 215, 0)
GRAY = (200, 200, 200)
BLUE = (70, 130, 180)
RED = (220, 20, 60)
LIGHT_GREEN = (144, 238, 144)

# Layout
TREE_POS = pygame.math.Vector2(180, 450)
TREE_RADIUS = 220
FRUIT_Y_OFFSET = 20
CRATE_RECT = pygame.Rect(570, 360, 160, 120)
TRUCK_RECT = pygame.Rect(700, 30, 140, 140)
TEXT_AREA_X = 850
LOADER_SIZE = 150  # loader image size

class UISimulation:
    def __init__(self, fruits, pickers, capacity):
        self.total_fruits = fruits
        self.capacity = capacity
        self.picker_count = pickers

        # Simulation state
        self.tree_fruits = fruits
        self.crate_count = 0
        self.loaded_crates = 0
        self.loaded_fruits = 0           # <— new: cumulative fruits delivered
        self.states = {f"Picker-{i}": 'idle' for i in range(1, pickers+1)}
        self.states['Loader'] = 'idle'
        self.log = []

        # Fetch CLI output
        cmd = [sys.executable, 'main.py',
               '--fruits', str(fruits),
               '--pickers', str(pickers),
               '--capacity', str(capacity)]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        out, _ = proc.communicate()
        self.raw_events = out.splitlines()[2:]
        self.current_index = 0
        self.last_time = time.time()

        # Fruit positions...
        random.seed(0)
        self.fruit_positions = []
        for _ in range(fruits):
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(20, TREE_RADIUS * 0.5)
            x = TREE_POS.x + math.cos(angle) * r
            y = TREE_POS.y + math.sin(angle) * r - FRUIT_Y_OFFSET
            self.fruit_positions.append(pygame.math.Vector2(x, y))

        # Crate slot positions...
        cols, rows = 4, math.ceil(capacity / 4)
        self.crate_positions = []
        for i in range(capacity):
            col = i % cols; row = i // cols
            x = CRATE_RECT.x + 10 + col * (CRATE_RECT.width - 20) / (cols - 1)
            y = CRATE_RECT.y + 10 + row * (CRATE_RECT.height - 20) / (rows - 1)
            self.crate_positions.append(pygame.math.Vector2(x, y))

        # Initial human positions
        self.initial_positions = {}
        for idx, name in enumerate(list(self.states.keys())[:-1]):
            self.initial_positions[name] = pygame.math.Vector2(PADDING + 20, 120 + idx * 50)
        self.initial_positions['Loader'] = pygame.math.Vector2(CRATE_RECT.centerx, CRATE_RECT.centery - 220)

        # Images
        self.tree_img = None
        self.truck_img = None
        self.loader_img = None

    def process_next(self):
        if self.current_index >= len(self.raw_events):
            return False
        line = self.raw_events[self.current_index].strip()
        self.current_index += 1
        if line:
            print(line)
            cols = [c.strip() for c in line.split('|')]
            if len(cols) == len(self.states):
                for name, state in zip(self.states.keys(), cols):
                    prev = self.states[name]
                    self.states[name] = state

                    # Picking logic
                    if name.startswith('Picker') and state.startswith('picked '):
                        self.tree_fruits = max(0, self.tree_fruits - 1)
                    if name.startswith('Picker') and state.startswith('stored '):
                        try:
                            self.crate_count = int(state.split()[1])
                        except ValueError:
                            pass

                    # Loader empties crate → increment totals & reset crate_count
                    if name == 'Loader' and state == 'emptied crate' and prev != state:
                        self.loaded_crates += 1
                        self.loaded_fruits += self.crate_count      # <— add this crate’s fruits
                        self.crate_count = 0                        # <— new empty crate returns

            self.log.append(line)
            if len(self.log) > MAX_LOG_LINES:
                self.log.pop(0)

        # Stop when everyone’s done
        if all(s == 'exiting' for s in self.states.values()):
            return False
        return True

    def draw(self, screen):
        font = pygame.font.SysFont(None, FONT_SIZE)
        hdr = pygame.font.SysFont(None, HEADER_FONT_SIZE, bold=True)

        # Background panels
        screen.fill(LIGHT_GREEN)
        pygame.draw.rect(screen, GRAY, (0, 0, TEXT_AREA_X, SCREEN_HEIGHT), 2)
        pygame.draw.rect(screen, GRAY, (TEXT_AREA_X, 0, SCREEN_WIDTH - TEXT_AREA_X, SCREEN_HEIGHT), 2)

        # Header
        screen.blit(hdr.render(f"Orchard: {self.total_fruits} Fruits", True, BLACK), (PADDING, PADDING))

        # Tree + fruits
        if self.tree_img:
            screen.blit(self.tree_img, self.tree_img.get_rect(center=(int(TREE_POS.x), int(TREE_POS.y))))
        for pos in self.fruit_positions[:self.tree_fruits]:
            pygame.draw.circle(screen, YELLOW, (int(pos.x), int(pos.y)), 6)
        screen.blit(font.render(f"Tree: {self.tree_fruits}", True, BLACK),
                    (TREE_POS.x - 30, TREE_POS.y - TREE_RADIUS - 30))

        # Crate + its contents
        pygame.draw.rect(screen, BROWN, CRATE_RECT, 3)
        for pos in self.crate_positions[:self.crate_count]:
            pygame.draw.circle(screen, YELLOW, (int(pos.x), int(pos.y)), 6)
        screen.blit(font.render(f"Crate: {self.crate_count}/{self.capacity}", True, BLACK),
                    (CRATE_RECT.x, CRATE_RECT.y - 25))

        # Truck + loaded info
        if self.truck_img:
            screen.blit(self.truck_img, TRUCK_RECT)
        screen.blit(font.render(f"Crates delivered: {self.loaded_crates}", True, BLACK),
                    (TRUCK_RECT.x + 10, TRUCK_RECT.y + 10))
        screen.blit(font.render(f"Fruits delivered: {self.loaded_fruits}", True, BLACK),
                    (TRUCK_RECT.x + 10, TRUCK_RECT.y + 30))  # <— new line

        # Draw pickers
        for idx, (name, state) in enumerate(self.states.items()):
            if name == 'Loader': continue
            # position around tree, crate, or home
            if 'tree' in state or state.startswith('picked '):
                ang = idx * (2 * math.pi / self.picker_count) - math.pi/2
                base = TREE_POS + pygame.math.Vector2(math.cos(ang), math.sin(ang)) * (TREE_RADIUS * 0.5)
            elif 'crate' in state or 'stored' in state:
                slot = min(self.crate_count, len(self.crate_positions)-1)
                base = self.crate_positions[slot]
            else:
                base = self.initial_positions[name]
            pygame.draw.circle(screen, BLUE, (int(base.x), int(base.y)), 12)
            screen.blit(font.render(name, True, BLACK), (base.x + 15, base.y - 10))
            screen.blit(font.render(state, True, RED), (base.x + 15, base.y + 5))

        # Draw loader, but move it to the truck as soon as it “acquires” the crate
        lstate = self.states['Loader']
        if lstate == 'waiting full':
            base = self.initial_positions['Loader']
        elif lstate == 'acquired crate':
            base = pygame.math.Vector2(*TRUCK_RECT.center)       # <— jump straight to truck
        elif lstate in ('got full', 'waiting crate', 'loading'):
            base = pygame.math.Vector2(*CRATE_RECT.center)       # crate area
        elif lstate in ('emptied crate', 'partial'):
            base = pygame.math.Vector2(*TRUCK_RECT.center)       # stay at truck
        else:
            base = self.initial_positions['Loader']

        if self.loader_img:
            rect = self.loader_img.get_rect(center=(int(base.x), int(base.y)))
            screen.blit(self.loader_img, rect)
        else:
            pygame.draw.rect(screen, RED,
                             (base.x - LOADER_SIZE/2, base.y - LOADER_SIZE/2, LOADER_SIZE, LOADER_SIZE))
        screen.blit(font.render(lstate, True, RED),
                    (base.x + LOADER_SIZE/2 + 5, base.y - FONT_SIZE/2))

        # Event log
        screen.blit(font.render('Event Log', True, BLACK), (TEXT_AREA_X + PADDING, PADDING))
        for i, line in enumerate(self.log):
            screen.blit(font.render(line, True, BLACK),
                        (TEXT_AREA_X + PADDING, PADDING + HEADER_FONT_SIZE + i * (FONT_SIZE + 2)))

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Orchard UI')
        self.tree_img = pygame.transform.smoothscale(
            pygame.image.load('assets/tree.png').convert_alpha(),
            (int(TREE_RADIUS*2), int(TREE_RADIUS*2)))
        self.truck_img = pygame.transform.smoothscale(
            pygame.image.load('assets/truck.png').convert_alpha(),
            (CRATE_RECT.width, CRATE_RECT.height))
        self.loader_img = pygame.transform.smoothscale(
            pygame.image.load('assets/loader.png').convert_alpha(),
            (LOADER_SIZE, LOADER_SIZE))
        clock = pygame.time.Clock()
        running = True
        while running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
            if time.time() - self.last_time > EVENT_DELAY:
                if not self.process_next():
                    break
                self.last_time = time.time()
            self.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pickers', type=int, default=3)
    parser.add_argument('-c', '--capacity', type=int, default=12)
    args = parser.parse_args()
    for fruits in test_case.TEST_FRUITS:
        sim = UISimulation(fruits, args.pickers, args.capacity)
        sim.run()
