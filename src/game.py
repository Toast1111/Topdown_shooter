"""
Core Game class for the Top-Down Shooter
Manages game state, teams, and main game loop
"""

import pygame
import random
from enum import Enum
from typing import List, Dict, Any
from src.entities.team import Team
from src.entities.player_class import PlayerClass, ClassType
from src.utils.map_generator import MapGenerator
from src.ui.class_selector import ClassSelector

class GameState(Enum):
    MENU = "menu"
    CLASS_SELECTION = "class_selection"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"

class Game:
    """Main game controller"""
    
    # Game constants
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    FPS = 60
    TEAM_SIZE = 6
    
    def __init__(self):
        """Initialize the game"""
        # Pygame setup
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Top-Down AI Shooter")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = GameState.CLASS_SELECTION
        self.running = True
        
        # Game components
        self.map_generator = MapGenerator(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.class_selector = ClassSelector()
        
        # Teams
        self.team1: Team = None
        self.team2: Team = None
        
        # Current map
        self.current_map = None
        
        # Game statistics
        self.match_count = 0
        self.team1_wins = 0
        self.team2_wins = 0
        
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.update(dt)
            self.render()
            
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                    else:
                        self.running = False
            
            # Delegate event handling to current state
            if self.state == GameState.CLASS_SELECTION:
                self.class_selector.handle_event(event, self)
            
    def update(self, dt: float):
        """Update game state"""
        if self.state == GameState.PLAYING and self.team1 and self.team2:
            self.team1.update(dt, self.current_map, self.team2)
            self.team2.update(dt, self.current_map, self.team1)
            
            # Check win conditions
            if self.team1.is_defeated():
                self.end_match(winner=2)
            elif self.team2.is_defeated():
                self.end_match(winner=1)
    
    def render(self):
        """Render the current game state"""
        self.screen.fill((50, 50, 50))  # Dark gray background
        
        if self.state == GameState.CLASS_SELECTION:
            self.class_selector.render(self.screen)
        elif self.state in [GameState.PLAYING, GameState.PAUSED]:
            self.render_game()
        elif self.state == GameState.GAME_OVER:
            self.render_game_over()
            
        pygame.display.flip()
    
    def render_game(self):
        """Render the main game view"""
        # Render map
        if self.current_map:
            self.current_map.render(self.screen)
        
        # Render teams
        if self.team1:
            self.team1.render(self.screen)
        if self.team2:
            self.team2.render(self.screen)
            
        # Render UI elements
        self.render_hud()
        
        # Render pause overlay if paused
        if self.state == GameState.PAUSED:
            self.render_pause_overlay()
    
    def render_hud(self):
        """Render heads-up display"""
        font = pygame.font.Font(None, 36)
        
        # Team 1 info (top-left)
        if self.team1:
            team1_text = f"Team 1: {self.team1.get_alive_count()}/{self.TEAM_SIZE}"
            text_surf = font.render(team1_text, True, (0, 255, 0))
            self.screen.blit(text_surf, (10, 10))
        
        # Team 2 info (top-right)  
        if self.team2:
            team2_text = f"Team 2: {self.team2.get_alive_count()}/{self.TEAM_SIZE}"
            text_surf = font.render(team2_text, True, (255, 0, 0))
            text_rect = text_surf.get_rect()
            text_rect.topright = (self.WINDOW_WIDTH - 10, 10)
            self.screen.blit(text_surf, text_rect)
        
        # Match statistics (top-center)
        stats_text = f"Match {self.match_count + 1} | Team 1 Wins: {self.team1_wins} | Team 2 Wins: {self.team2_wins}"
        stats_surf = pygame.font.Font(None, 24).render(stats_text, True, (255, 255, 255))
        stats_rect = stats_surf.get_rect()
        stats_rect.midtop = (self.WINDOW_WIDTH // 2, 10)
        self.screen.blit(stats_surf, stats_rect)
    
    def render_pause_overlay(self):
        """Render pause screen overlay"""
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 72)
        pause_text = font.render("PAUSED", True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2))
        self.screen.blit(pause_text, pause_rect)
        
        help_font = pygame.font.Font(None, 36)
        help_text = help_font.render("Press ESC to resume", True, (255, 255, 255))
        help_rect = help_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 60))
        self.screen.blit(help_text, help_rect)
    
    def render_game_over(self):
        """Render game over screen"""
        # Still show the game state
        self.render_game()
        
        # Overlay
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Winner announcement
        font = pygame.font.Font(None, 72)
        if self.team1.get_alive_count() > self.team2.get_alive_count():
            winner_text = "TEAM 1 WINS!"
            color = (0, 255, 0)
        else:
            winner_text = "TEAM 2 WINS!"
            color = (255, 0, 0)
            
        text_surf = font.render(winner_text, True, color)
        text_rect = text_surf.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2))
        self.screen.blit(text_surf, text_rect)
    
    def start_match(self, team1_classes: List[ClassType], team2_classes: List[ClassType]):
        """Start a new match with the selected class compositions"""
        # Generate new random map
        self.current_map = self.map_generator.generate_map()
        
        # Create teams with selected classes
        self.team1 = Team(1, team1_classes, self.current_map.get_spawn_positions(1))
        self.team2 = Team(2, team2_classes, self.current_map.get_spawn_positions(2))
        
        # Change to playing state
        self.state = GameState.PLAYING
        self.match_count += 1
    
    def end_match(self, winner: int):
        """End the current match"""
        if winner == 1:
            self.team1_wins += 1
        else:
            self.team2_wins += 1
            
        # Notify teams about match end for AI learning
        if self.team1:
            self.team1.end_episode(winner == 1)
            self.team1.save_learning_data()
        if self.team2:
            self.team2.end_episode(winner == 2)
            self.team2.save_learning_data()
            
        self.state = GameState.GAME_OVER
        
        # Auto-restart after a delay
        pygame.time.set_timer(pygame.USEREVENT + 1, 3000)  # 3 seconds
    
    def restart_match(self):
        """Restart with same team compositions"""
        if self.team1 and self.team2:
            team1_classes = [player.class_type for player in self.team1.players]
            team2_classes = [player.class_type for player in self.team2.players]
            self.start_match(team1_classes, team2_classes)