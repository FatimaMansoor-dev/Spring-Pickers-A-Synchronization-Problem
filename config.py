import pygame

# General Configuration
FPS = 30
FONT_SIZE = 18
HEADER_FONT_SIZE = 20
MAX_LOG_LINES = 15
DEFAULT_EVENT_DELAY = 0.5
PADDING = 10
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 620

# Speed settings
SPEED_LEVELS = [1.5, 1.0, 0.5, 0.25, 0.1]  # Slower to faster (delay in seconds)
DEFAULT_SPEED_INDEX = 2  # Index 2 corresponds to 0.5 seconds (default speed)

# Colors
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
BROWN = (139, 69, 19)
GREEN = (34, 139, 34)
LIGHT_BROWN = (205, 133, 63)
YELLOW = (255, 215, 0)
ORANGE = (255, 165, 0)
GRAY = (200, 200, 200)
BLUE = (70, 130, 180)
DARK_BLUE = (25, 25, 112)
RED = (220, 20, 60)
LIGHT_GREEN = (144, 238, 144)
MEDIUM_GREEN = (60, 179, 113)

# Layout
TREE_POS = pygame.math.Vector2(180, 450)
TREE_RADIUS = 220
FRUIT_Y_OFFSET = 20
CRATE_RECT = pygame.Rect(570, 360, 160, 120)
TRUCK_RECT = pygame.Rect(700, 30, 140, 140)
TEXT_AREA_X = 850
LOADER_SIZE = 150  # loader image size

# UI Enhancement
PANEL_COLOR = (240, 248, 255)  # Light blue background
PANEL_BORDER = (100, 149, 237)  # Cornflower blue border

# Asset paths
ASSET_PATHS = {
    'tree': 'assets/tree.png',
    'truck': 'assets/truck.png',
    'loader': 'assets/loader.png'
}