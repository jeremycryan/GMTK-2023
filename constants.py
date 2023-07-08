WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT

FPS = 120

CAPTION = "Hello this is a game"

TILE_WIDTH = 64
TILE_HEIGHT = 64
TILE_SIZE = TILE_WIDTH, TILE_HEIGHT

# Physics parameters
GRAVITY = 800                   # pixels/s^2
DRAG = 0.1                      # 1/s
TERMINAL_VELOCITY = 500
VERTICAL_RESTITUTION = 0.0
HORIZONTAL_RESTITUTION = 0.2
TANGENTIAL_RESTITUTION = 0.7     # unitless
V_MIN_BOUNCE = 25               # pixels/s

FRICTION = 10                   # 1/s
V_MIN_SLIDE = 5                 # pixels/s

# Zombie parameters
ZOMBIE_SPEED = 10              # pixels/s

# Hero parameters
RECOIL = 50                     # pixels/s
COOLDOWN = 1                    # s
TARGET_PRIORITY = 0.7           # unitless
SWIVEL_SPEED = 2                # rad/s

# Direction constants
UP_LEFT = (-1, -1)
UP = (0, -1)
UP_RIGHT = (1, -1)
LEFT = (-1, 0)
SELF = (0, 0)
RIGHT = (1, 0)
DOWN_LEFT = (-1, 1)
DOWN = (0, 1)
DOWN_RIGHT = (1, 0)
