"""
Random map generation for battles
"""

import pygame
import random
import math
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class Obstacle:
    """Represents a map obstacle"""
    x: float
    y: float
    width: float
    height: float
    type: str  # 'wall', 'cover', 'pillar'

class GameMap:
    """Represents a game map with obstacles and spawn points"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.obstacles: List[Obstacle] = []
        self.team1_spawns: List[Tuple[float, float]] = []
        self.team2_spawns: List[Tuple[float, float]] = []
        
        # Visual elements
        self.background_color = (40, 40, 40)
        self.wall_color = (100, 100, 100)
        self.cover_color = (80, 60, 40)
        self.pillar_color = (120, 120, 120)
    
    def add_obstacle(self, obstacle: Obstacle):
        """Add an obstacle to the map"""
        self.obstacles.append(obstacle)
    
    def is_position_blocked(self, x: float, y: float, radius: float = 5) -> bool:
        """Check if a position is blocked by obstacles"""
        for obstacle in self.obstacles:
            # Simple rectangle collision detection
            if (obstacle.x - radius < x < obstacle.x + obstacle.width + radius and
                obstacle.y - radius < y < obstacle.y + obstacle.height + radius):
                return True
        return False
    
    def get_spawn_positions(self, team_id: int) -> List[Tuple[float, float]]:
        """Get spawn positions for a team"""
        if team_id == 1:
            return self.team1_spawns.copy()
        else:
            return self.team2_spawns.copy()
    
    def render(self, screen):
        """Render the map"""
        # Background
        screen.fill(self.background_color)
        
        # Render obstacles
        for obstacle in self.obstacles:
            color = self.wall_color
            if obstacle.type == 'cover':
                color = self.cover_color
            elif obstacle.type == 'pillar':
                color = self.pillar_color
            
            pygame.draw.rect(screen, color, 
                           (obstacle.x, obstacle.y, obstacle.width, obstacle.height))
        
        # Render spawn areas (debug)
        for x, y in self.team1_spawns:
            pygame.draw.circle(screen, (0, 100, 0), (int(x), int(y)), 15, 2)
        
        for x, y in self.team2_spawns:
            pygame.draw.circle(screen, (100, 0, 0), (int(x), int(y)), 15, 2)

class MapGenerator:
    """Generates random maps for battles"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.border_margin = 50
        
    def generate_map(self) -> GameMap:
        """Generate a random map"""
        game_map = GameMap(self.width, self.height)
        
        # Choose map type
        map_types = ['arena', 'maze', 'open_field', 'urban', 'bunker']
        map_type = random.choice(map_types)
        
        if map_type == 'arena':
            self.generate_arena_map(game_map)
        elif map_type == 'maze':
            self.generate_maze_map(game_map)
        elif map_type == 'open_field':
            self.generate_open_field_map(game_map)
        elif map_type == 'urban':
            self.generate_urban_map(game_map)
        else:  # bunker
            self.generate_bunker_map(game_map)
        
        # Always add border walls
        self.add_border_walls(game_map)
        
        # Generate spawn points
        self.generate_spawn_points(game_map)
        
        return game_map
    
    def add_border_walls(self, game_map: GameMap):
        """Add walls around the map border"""
        wall_thickness = 20
        
        # Top wall
        game_map.add_obstacle(Obstacle(0, 0, self.width, wall_thickness, 'wall'))
        
        # Bottom wall
        game_map.add_obstacle(Obstacle(0, self.height - wall_thickness, self.width, wall_thickness, 'wall'))
        
        # Left wall
        game_map.add_obstacle(Obstacle(0, 0, wall_thickness, self.height, 'wall'))
        
        # Right wall
        game_map.add_obstacle(Obstacle(self.width - wall_thickness, 0, wall_thickness, self.height, 'wall'))
    
    def generate_arena_map(self, game_map: GameMap):
        """Generate an arena-style map with scattered cover"""
        # Add some scattered cover obstacles
        num_obstacles = random.randint(8, 15)
        
        for _ in range(num_obstacles):
            # Random position not too close to edges
            x = random.randint(self.border_margin, self.width - self.border_margin - 60)
            y = random.randint(self.border_margin, self.height - self.border_margin - 60)
            
            # Random size
            width = random.randint(30, 80)
            height = random.randint(30, 80)
            
            obstacle_type = random.choice(['cover', 'pillar'])
            game_map.add_obstacle(Obstacle(x, y, width, height, obstacle_type))
    
    def generate_maze_map(self, game_map: GameMap):
        """Generate a maze-like map with corridors"""
        # Create a grid-based maze structure
        grid_size = 80
        grid_width = self.width // grid_size
        grid_height = self.height // grid_size
        
        # Create some wall segments
        for gx in range(1, grid_width - 1):
            for gy in range(1, grid_height - 1):
                if random.random() < 0.3:  # 30% chance of wall
                    x = gx * grid_size
                    y = gy * grid_size
                    
                    # Random wall orientation
                    if random.random() < 0.5:
                        # Horizontal wall
                        width = grid_size
                        height = 20
                    else:
                        # Vertical wall
                        width = 20
                        height = grid_size
                    
                    game_map.add_obstacle(Obstacle(x, y, width, height, 'wall'))
    
    def generate_open_field_map(self, game_map: GameMap):
        """Generate an open field with minimal cover"""
        # Just a few scattered pieces of cover
        num_obstacles = random.randint(3, 6)
        
        for _ in range(num_obstacles):
            x = random.randint(self.width // 4, 3 * self.width // 4 - 40)
            y = random.randint(self.height // 4, 3 * self.height // 4 - 40)
            
            width = random.randint(40, 60)
            height = random.randint(40, 60)
            
            game_map.add_obstacle(Obstacle(x, y, width, height, 'cover'))
    
    def generate_urban_map(self, game_map: GameMap):
        """Generate an urban environment with building-like structures"""
        # Create building blocks
        num_buildings = random.randint(4, 8)
        
        for _ in range(num_buildings):
            # Random building position
            x = random.randint(self.border_margin, self.width - self.border_margin - 120)
            y = random.randint(self.border_margin, self.height - self.border_margin - 120)
            
            # Building size
            width = random.randint(80, 150)
            height = random.randint(80, 150)
            
            # Make sure buildings don't overlap too much
            overlaps = False
            for obstacle in game_map.obstacles:
                # Calculate centers
                center_x1 = obstacle.x + obstacle.width / 2
                center_y1 = obstacle.y + obstacle.height / 2
                center_x2 = x + width / 2
                center_y2 = y + height / 2
                # Check overlap using center distances and sum of half-widths/heights
                if (abs(center_x1 - center_x2) < (obstacle.width / 2 + width / 2) and
                    abs(center_y1 - center_y2) < (obstacle.height / 2 + height / 2)):
                    overlaps = True
                    break
            
            if not overlaps:
                game_map.add_obstacle(Obstacle(x, y, width, height, 'wall'))
    
    def generate_bunker_map(self, game_map: GameMap):
        """Generate a bunker-style map with defensive positions"""
        # Central bunker
        center_x = self.width // 2 - 60
        center_y = self.height // 2 - 60
        game_map.add_obstacle(Obstacle(center_x, center_y, 120, 120, 'wall'))
        
        # Surrounding defensive positions
        positions = [
            (self.width * 0.25, self.height * 0.25),
            (self.width * 0.75, self.height * 0.25),
            (self.width * 0.25, self.height * 0.75),
            (self.width * 0.75, self.height * 0.75),
        ]
        
        for px, py in positions:
            # Small bunker
            x = px - 30
            y = py - 30
            game_map.add_obstacle(Obstacle(x, y, 60, 60, 'cover'))
    
    def generate_spawn_points(self, game_map: GameMap):
        """Generate spawn points for both teams"""
        # Team 1 spawns on the left side
        self.generate_team_spawns(game_map, 1, 
                                 x_range=(self.border_margin + 30, self.width * 0.3),
                                 y_range=(self.border_margin + 30, self.height - self.border_margin - 30))
        
        # Team 2 spawns on the right side
        self.generate_team_spawns(game_map, 2,
                                 x_range=(self.width * 0.7, self.width - self.border_margin - 30),
                                 y_range=(self.border_margin + 30, self.height - self.border_margin - 30))
    
    def generate_team_spawns(self, game_map: GameMap, team_id: int, 
                           x_range: Tuple[float, float], y_range: Tuple[float, float]):
        """Generate spawn points for a specific team"""
        spawns = []
        attempts = 0
        max_attempts = 100
        
        while len(spawns) < 6 and attempts < max_attempts:
            x = random.uniform(x_range[0], x_range[1])
            y = random.uniform(y_range[0], y_range[1])
            
            # Check if position is not blocked
            if not game_map.is_position_blocked(x, y, 15):
                # Check minimum distance from other spawns
                too_close = False
                for sx, sy in spawns:
                    if math.sqrt((x - sx)**2 + (y - sy)**2) < 40:
                        too_close = True
                        break
                
                if not too_close:
                    spawns.append((x, y))
            
            attempts += 1
        
        # If we couldn't find enough good positions, fill with basic positions
        while len(spawns) < 6:
            x = random.uniform(x_range[0], x_range[1])
            y = random.uniform(y_range[0], y_range[1])
            spawns.append((x, y))
        
        if team_id == 1:
            game_map.team1_spawns = spawns
        else:
            game_map.team2_spawns = spawns