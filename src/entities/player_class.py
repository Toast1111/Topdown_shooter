"""
Player classes with different abilities and AI behaviors
"""

import pygame
import math
from enum import Enum
from typing import Tuple, Dict, Any
from dataclasses import dataclass

class ClassType(Enum):
    ASSAULT = "assault"
    SNIPER = "sniper"
    SUPPORT = "support"
    HEAVY = "heavy"
    SCOUT = "scout"
    MEDIC = "medic"

@dataclass
class ClassStats:
    """Statistics for a player class"""
    max_health: float
    speed: float
    damage: float
    fire_rate: float  # bullets per second
    range: float
    accuracy: float  # 0.0 to 1.0
    special_ability_cooldown: float
    size: int  # radius for collision detection

class PlayerClass:
    """Represents a player with specific class abilities"""
    
    # Class definitions
    CLASS_STATS = {
        ClassType.ASSAULT: ClassStats(
            max_health=100, speed=120, damage=25, fire_rate=3.0, 
            range=200, accuracy=0.8, special_ability_cooldown=8.0, size=8
        ),
        ClassType.SNIPER: ClassStats(
            max_health=75, speed=90, damage=80, fire_rate=0.8,
            range=400, accuracy=0.95, special_ability_cooldown=12.0, size=7
        ),
        ClassType.SUPPORT: ClassStats(
            max_health=90, speed=100, damage=30, fire_rate=4.0,
            range=250, accuracy=0.75, special_ability_cooldown=6.0, size=8
        ),
        ClassType.HEAVY: ClassStats(
            max_health=150, speed=60, damage=40, fire_rate=1.5,
            range=180, accuracy=0.7, special_ability_cooldown=15.0, size=10
        ),
        ClassType.SCOUT: ClassStats(
            max_health=70, speed=180, damage=20, fire_rate=5.0,
            range=150, accuracy=0.7, special_ability_cooldown=5.0, size=6
        ),
        ClassType.MEDIC: ClassStats(
            max_health=85, speed=110, damage=15, fire_rate=2.0,
            range=120, accuracy=0.8, special_ability_cooldown=10.0, size=7
        ),
    }
    
    # Class colors for visualization
    CLASS_COLORS = {
        ClassType.ASSAULT: (255, 100, 100),    # Red
        ClassType.SNIPER: (100, 255, 100),     # Green
        ClassType.SUPPORT: (100, 100, 255),    # Blue
        ClassType.HEAVY: (255, 165, 0),        # Orange
        ClassType.SCOUT: (255, 255, 100),      # Yellow
        ClassType.MEDIC: (255, 20, 147),       # Pink
    }
    
    def __init__(self, class_type: ClassType, team_id: int, position: Tuple[float, float], player_id: int):
        """Initialize a player with specific class"""
        self.class_type = class_type
        self.team_id = team_id
        self.player_id = player_id
        self.stats = self.CLASS_STATS[class_type]
        
        # Position and movement
        self.x, self.y = position
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.rotation = 0.0  # facing direction in degrees
        
        # Health and status
        self.health = self.stats.max_health
        self.is_alive = True
        
        # Combat
        self.last_shot_time = 0.0
        self.last_special_time = 0.0
        self.target = None
        
        # AI state
        self.ai_state = "idle"
        self.ai_state_time = 0.0
        self.path = []
        
        # Statistics for learning
        self.damage_dealt = 0.0
        self.damage_taken = 0.0
        self.shots_fired = 0
        self.shots_hit = 0
        self.kills = 0
        self.time_alive = 0.0
    
    def update(self, dt: float, game_map, enemies, allies):
        """Update player state"""
        if not self.is_alive:
            return
            
        self.time_alive += dt
        
        # Update AI behavior based on class
        self.update_ai(dt, game_map, enemies, allies)
        
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Keep within bounds
        self.x = max(self.stats.size, min(game_map.width - self.stats.size, self.x))
        self.y = max(self.stats.size, min(game_map.height - self.stats.size, self.y))
    
    def update_ai(self, dt: float, game_map, enemies, allies):
        """Update AI behavior - base implementation"""
        # Find nearest enemy
        nearest_enemy = self.find_nearest_enemy(enemies)
        
        if nearest_enemy:
            # Basic AI: move towards enemy and shoot
            dx = nearest_enemy.x - self.x
            dy = nearest_enemy.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Rotate towards enemy
            self.rotation = math.degrees(math.atan2(dy, dx))
            
            if distance > self.stats.range * 0.8:
                # Move closer
                move_x = dx / distance * self.stats.speed
                move_y = dy / distance * self.stats.speed
                self.velocity_x = move_x
                self.velocity_y = move_y
            else:
                # Stop and shoot
                self.velocity_x = 0
                self.velocity_y = 0
                self.try_shoot(nearest_enemy, dt)
        else:
            # No enemies, stop moving
            self.velocity_x = 0
            self.velocity_y = 0
    
    def find_nearest_enemy(self, enemies):
        """Find the nearest alive enemy"""
        nearest = None
        min_distance = float('inf')
        
        for enemy in enemies:
            if not enemy.is_alive:
                continue
                
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < min_distance:
                min_distance = distance
                nearest = enemy
        
        return nearest
    
    def try_shoot(self, target, dt: float):
        """Attempt to shoot at target"""
        current_time = pygame.time.get_ticks() / 1000.0
        
        if current_time - self.last_shot_time < (1.0 / self.stats.fire_rate):
            return False
        
        # Check if target is in range
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > self.stats.range:
            return False
        
        # Apply accuracy
        import random
        if random.random() > self.stats.accuracy:
            return False  # Miss
        
        # Hit!
        self.shots_fired += 1
        self.shots_hit += 1
        damage = self.stats.damage
        
        # Apply damage
        target.take_damage(damage, self)
        self.damage_dealt += damage
        
        self.last_shot_time = current_time
        return True
    
    def take_damage(self, damage: float, attacker):
        """Take damage from an attacker"""
        if not self.is_alive:
            return
            
        self.health -= damage
        self.damage_taken += damage
        
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            if attacker:
                attacker.kills += 1
    
    def use_special_ability(self, dt: float, allies, enemies):
        """Use class-specific special ability"""
        current_time = pygame.time.get_ticks() / 1000.0
        
        if current_time - self.last_special_time < self.stats.special_ability_cooldown:
            return False
        
        self.last_special_time = current_time
        
        # Class-specific abilities
        if self.class_type == ClassType.MEDIC:
            # Heal nearby allies
            for ally in allies:
                if ally != self and ally.is_alive:
                    dx = ally.x - self.x
                    dy = ally.y - self.y
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance < 100:  # Heal range
                        heal_amount = 30
                        ally.health = min(ally.stats.max_health, ally.health + heal_amount)
        
        elif self.class_type == ClassType.HEAVY:
            # Explosive shot - damage all nearby enemies
            for enemy in enemies:
                if enemy.is_alive:
                    dx = enemy.x - self.x
                    dy = enemy.y - self.y
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance < self.stats.range:
                        enemy.take_damage(self.stats.damage * 1.5, self)
                        self.damage_dealt += self.stats.damage * 1.5
        
        elif self.class_type == ClassType.SCOUT:
            # Speed boost
            self.stats.speed *= 1.5
            # Reset speed after 3 seconds (simplified)
        
        return True
    
    def render(self, screen):
        """Render the player"""
        if not self.is_alive:
            return
            
        # Get team color
        base_color = self.CLASS_COLORS[self.class_type]
        
        # Adjust color for team (team 2 gets darker colors)
        if self.team_id == 2:
            color = tuple(c // 2 for c in base_color)
        else:
            color = base_color
        
        # Draw player circle
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.stats.size)
        
        # Draw health bar
        if self.health < self.stats.max_health:
            bar_width = self.stats.size * 2
            bar_height = 4
            bar_x = self.x - bar_width // 2
            bar_y = self.y - self.stats.size - 8
            
            # Background
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            
            # Health
            health_width = int(bar_width * (self.health / self.stats.max_health))
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))
        
        # Draw facing direction
        facing_length = self.stats.size + 5
        end_x = self.x + math.cos(math.radians(self.rotation)) * facing_length
        end_y = self.y + math.sin(math.radians(self.rotation)) * facing_length
        pygame.draw.line(screen, (255, 255, 255), (self.x, self.y), (end_x, end_y), 2)
    
    def get_position(self) -> Tuple[float, float]:
        """Get current position"""
        return (self.x, self.y)
    
    def get_learning_data(self) -> Dict[str, Any]:
        """Get data for AI learning"""
        return {
            'class_type': self.class_type.value,
            'team_id': self.team_id,
            'damage_dealt': self.damage_dealt,
            'damage_taken': self.damage_taken,
            'shots_fired': self.shots_fired,
            'shots_hit': self.shots_hit,
            'accuracy': self.shots_hit / max(1, self.shots_fired),
            'kills': self.kills,
            'time_alive': self.time_alive,
            'survived': self.is_alive,
            'efficiency': self.damage_dealt / max(1, self.damage_taken),
        }