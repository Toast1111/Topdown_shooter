"""
Team management for groups of AI players
"""

import pygame
from typing import List, Tuple, Dict, Any
from src.entities.ai_player import AIPlayer
from src.entities.player_class import ClassType

class Team:
    """Manages a team of AI players"""
    
    def __init__(self, team_id: int, class_types: List[ClassType], spawn_positions: List[Tuple[float, float]]):
        """Initialize team with specified classes and positions"""
        self.team_id = team_id
        self.players: List[AIPlayer] = []
        
        # Create players from class types and positions
        for i, (class_type, position) in enumerate(zip(class_types, spawn_positions)):
            player = AIPlayer(class_type, team_id, position, i)
            self.players.append(player)
        
        # Team statistics
        self.total_damage_dealt = 0.0
        self.total_damage_taken = 0.0
        self.total_kills = 0
        self.team_coordination_bonus = 0.0
        
        # AI coordination state
        self.team_strategy = "aggressive"  # aggressive, defensive, balanced
        self.focus_target = None
        self.formation_center = spawn_positions[0] if spawn_positions else (0, 0)
    
    def update(self, dt: float, game_map, enemy_team):
        """Update all players in the team"""
        # Update team coordination
        self.update_team_strategy(enemy_team)
        
        # Get enemy players for AI
        enemies = enemy_team.get_alive_players() if enemy_team else []
        allies = self.get_alive_players()
        
        # Update each player
        for player in self.players:
            if player.is_alive:
                # Pass team coordination info to player AI
                self.apply_team_coordination(player, allies, enemies)
                player.update(dt, game_map, enemies, allies)
    
    def update_team_strategy(self, enemy_team):
        """Update overall team strategy based on current situation"""
        alive_allies = self.get_alive_count()
        alive_enemies = enemy_team.get_alive_count() if enemy_team else 0
        
        if alive_allies > alive_enemies * 1.5:
            self.team_strategy = "aggressive"
        elif alive_allies < alive_enemies * 0.7:
            self.team_strategy = "defensive"
        else:
            self.team_strategy = "balanced"
        
        # Update formation center based on alive players
        alive_players = self.get_alive_players()
        if alive_players:
            center_x = sum(p.x for p in alive_players) / len(alive_players)
            center_y = sum(p.y for p in alive_players) / len(alive_players)
            self.formation_center = (center_x, center_y)
    
    def apply_team_coordination(self, player: AIPlayer, allies: List[AIPlayer], enemies: List[AIPlayer]):
        """Apply team coordination logic to individual player"""
        # Focus fire - all players target the same enemy when possible
        if enemies and self.team_strategy == "aggressive":
            # Find weakest enemy for focus fire
            weakest_enemy = min(enemies, key=lambda e: e.health)
            player.target = weakest_enemy
        
        # Formation keeping for defensive strategy
        if self.team_strategy == "defensive":
            # Players try to stay near formation center
            dx = self.formation_center[0] - player.x
            dy = self.formation_center[1] - player.y
            distance = (dx*dx + dy*dy) ** 0.5
            
            if distance > 100:  # Too far from formation
                # Adjust movement towards center
                player.velocity_x += dx * 0.1
                player.velocity_y += dy * 0.1
        
        # Class-specific coordination
        if player.class_type == ClassType.MEDIC:
            # Medics prioritize staying behind other units
            self.position_support_unit(player, allies)
        elif player.class_type == ClassType.HEAVY:
            # Heavy units take point
            self.position_front_unit(player, allies)
        elif player.class_type == ClassType.SCOUT:
            # Scouts flank enemies
            self.position_flanking_unit(player, enemies)
    
    def position_support_unit(self, player: AIPlayer, allies: List[AIPlayer]):
        """Position support units (medics) safely behind frontline"""
        if len(allies) <= 1:
            return
            
        # Find average position of other allies
        other_allies = [a for a in allies if a != player]
        avg_x = sum(a.x for a in other_allies) / len(other_allies)
        avg_y = sum(a.y for a in other_allies) / len(other_allies)
        
        # Try to stay behind allies relative to enemies
        # Simplified: just stay near ally center but slightly back
        target_x = avg_x + (player.x - avg_x) * 0.1
        target_y = avg_y + (player.y - avg_y) * 0.1
        
        dx = target_x - player.x
        dy = target_y - player.y
        if dx*dx + dy*dy > 50*50:  # If too far, move closer
            player.velocity_x += dx * 0.05
            player.velocity_y += dy * 0.05
    
    def position_front_unit(self, player: AIPlayer, allies: List[AIPlayer]):
        """Position front-line units (heavies) at the front"""
        # Heavy units should be more aggressive in positioning
        # Increase their forward momentum slightly
        player.velocity_x *= 1.1
        player.velocity_y *= 1.1
    
    def position_flanking_unit(self, player: AIPlayer, enemies: List[AIPlayer]):
        """Position flanking units (scouts) to attack from sides"""
        if not enemies:
            return
            
        # Find enemy center
        enemy_center_x = sum(e.x for e in enemies) / len(enemies)
        enemy_center_y = sum(e.y for e in enemies) / len(enemies)
        
        # Calculate flanking position (perpendicular to enemy center)
        import math
        angle = math.atan2(enemy_center_y - player.y, enemy_center_x - player.x)
        flank_angle = angle + math.pi/2  # 90 degrees off
        
        flank_distance = 150
        flank_x = enemy_center_x + math.cos(flank_angle) * flank_distance
        flank_y = enemy_center_y + math.sin(flank_angle) * flank_distance
        
        # Move towards flanking position
        dx = flank_x - player.x
        dy = flank_y - player.y
        player.velocity_x += dx * 0.02
        player.velocity_y += dy * 0.02
    
    def render(self, screen):
        """Render all players in the team"""
        for player in self.players:
            player.render(screen)
        
        # Optionally render team info
        self.render_team_info(screen)
    
    def render_team_info(self, screen):
        """Render team statistics and info"""
        # Team label
        font = pygame.font.Font(None, 24)
        
        # Position based on team ID
        if self.team_id == 1:
            x, y = 10, 50
            color = (0, 255, 0)
        else:
            x, y = screen.get_width() - 200, 50
            color = (255, 0, 0)
        
        # Strategy text
        strategy_text = f"Strategy: {self.team_strategy.title()}"
        text_surf = font.render(strategy_text, True, color)
        screen.blit(text_surf, (x, y))
        
        # Alive count by class
        class_counts = {}
        for player in self.players:
            if player.is_alive:
                class_type = player.class_type.value
                class_counts[class_type] = class_counts.get(class_type, 0) + 1
        
        y += 25
        for class_name, count in class_counts.items():
            class_text = f"{class_name}: {count}"
            text_surf = pygame.font.Font(None, 20).render(class_text, True, color)
            screen.blit(text_surf, (x, y))
            y += 20
    
    def get_alive_players(self) -> List[AIPlayer]:
        """Get list of alive players"""
        return [player for player in self.players if player.is_alive]
    
    def get_alive_count(self) -> int:
        """Get number of alive players"""
        return len(self.get_alive_players())
    
    def is_defeated(self) -> bool:
        """Check if team is completely defeated"""
        return self.get_alive_count() == 0
    
    def get_total_stats(self) -> Dict[str, float]:
        """Get aggregated team statistics"""
        stats = {
            'total_damage_dealt': sum(p.damage_dealt for p in self.players),
            'total_damage_taken': sum(p.damage_taken for p in self.players),
            'total_kills': sum(p.kills for p in self.players),
            'total_shots_fired': sum(p.shots_fired for p in self.players),
            'total_shots_hit': sum(p.shots_hit for p in self.players),
            'team_accuracy': 0.0,
            'survivors': self.get_alive_count(),
        }
        
        if stats['total_shots_fired'] > 0:
            stats['team_accuracy'] = stats['total_shots_hit'] / stats['total_shots_fired']
        
        return stats
    
    def save_learning_data(self):
        """Save team and individual learning data for AI improvement"""
        # This will be used by the AI learning system
        team_data = {
            'team_id': self.team_id,
            'strategy': self.team_strategy,
            'team_stats': self.get_total_stats(),
            'player_data': [player.get_learning_data() for player in self.players],
            'class_composition': [p.class_type.value for p in self.players],
        }
        
        # For now, just store in memory - later this would go to a database or file
        # This data will be used by the AI learning system to improve strategies
        self.last_match_data = team_data
        
        return team_data
    
    def end_episode(self, won: bool):
        """Notify all players that the episode has ended"""
        for player in self.players:
            player.end_episode(won)