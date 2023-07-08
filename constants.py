WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT

FPS = 120

CAPTION = "Hello this is a game"

TILE_WIDTH = 64
TILE_HEIGHT = 64
TILE_SIZE = TILE_WIDTH, TILE_HEIGHT

# Physics parameters
GRAVITY = 800                   # acceleration in pixels/s^2
DRAG = 0.1                      # ballistic drag time constant in 1/s
RESTITUTION = 0.1               # elasticity in normal direction
TANGENTIAL_RESTITUTION = 0.7    # elasticity in tangential direction
V_MIN_BOUNCE = 25               # minimum bounce velocity in pixels/s

FRICTION = 10                   # grounded friction time constant in 1/s
V_MIN_SLIDE = 5                 # minimum sliding velocity in pixels/s

# Zombie parameters
ZOMBIE_SPEED = 20               # zombie walking speed in pixels/s
ZOMBIE_KNOCKBACK = 50           # zombie attack impulse on hero in pixels/s
ZOMBIE_COOLDOWN = 0.5           # time between attacks in s

# Hero parameters
RECOIL = 10                     # gun knockback in pixels/s
HERO_COOLDOWN = 0.1             # time between shots in s
TARGET_PRIORITY = 0.7           # amount to prioritize switching to a closer target (0 to 1)
SWIVEL_SPEED = 2                # gun aiming speed in rad/s
SHOT_JITTER = 20                # maximum projectile initial offset in pixels

# Projectile parameters
BULLET_SPEED = 500              # bullet speed in pixels/s
BULLET_FORCE = 0.1              # bullet mass to zombie mass ratio
