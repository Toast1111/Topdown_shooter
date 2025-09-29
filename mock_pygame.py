"""
Mock pygame module for testing without pygame dependency
"""

class MockFont:
    def __init__(self, name, size):
        pass
    
    def render(self, text, antialias, color):
        return MockSurface()
    
    def get_rect(self):
        return MockRect()

class MockSurface:
    def __init__(self):
        pass
    
    def get_rect(self, **kwargs):
        return MockRect()
    
    def get_width(self):
        return 800
    
    def get_height(self):
        return 600
    
    def fill(self, color):
        pass
    
    def blit(self, surface, pos):
        pass
    
    def set_alpha(self, alpha):
        pass

class MockRect:
    def __init__(self, x=0, y=0, width=100, height=100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center = (x + width//2, y + height//2)
        self.topright = (x + width, y)
        self.midtop = (x + width//2, y)
    
    def collidepoint(self, pos):
        x, y = pos
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

class MockDisplay:
    @staticmethod
    def set_mode(size):
        return MockSurface()
    
    @staticmethod
    def set_caption(caption):
        pass
    
    @staticmethod
    def flip():
        pass

class MockTime:
    @staticmethod
    def Clock():
        return MockClock()
    
    @staticmethod
    def get_ticks():
        return 1000
    
    @staticmethod
    def set_timer(event, time):
        pass

class MockClock:
    def tick(self, fps):
        return 16  # ~60 FPS

# Mock pygame modules
display = MockDisplay()
time = MockTime()

class font:
    Font = MockFont

# Constants
QUIT = 256
KEYDOWN = 2
MOUSEBUTTONDOWN = 5
USEREVENT = 24

# Keys
K_ESCAPE = 27
K_RETURN = 13
K_TAB = 9
K_LEFT = 276
K_RIGHT = 275
K_UP = 273
K_DOWN = 274
K_1 = 49
K_2 = 50
K_3 = 51
K_4 = 52
K_5 = 53
K_6 = 54

def init():
    pass

def quit():
    pass

def draw():
    pass

draw.circle = lambda surface, color, pos, radius, width=0: None
draw.rect = lambda surface, color, rect, width=0: None  
draw.line = lambda surface, color, start, end, width=1: None

class MockEvent:
    def __init__(self, type, **kwargs):
        self.type = type
        for k, v in kwargs.items():
            setattr(self, k, v)

def get():
    return []

# Add Rect class to global namespace
Rect = MockRect