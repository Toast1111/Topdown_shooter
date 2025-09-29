"""
AI-enhanced player that uses machine learning for decision making
"""

import math
import pygame
from typing import List, Tuple, Optional
from src.entities.player_class import PlayerClass, ClassType
from src.ai.learning_agent import LearningAgent, Experience, State, Action

class AIPlayer(PlayerClass):
    """Player class enhanced with AI learning capabilities"""
    
    def __init__(self, class_type: ClassType, team_id: int, position: Tuple[float, float], player_id: int):
        super().__init__(class_type, team_id, position, player_id)
        
        # AI learning agent
        self.learning_agent = LearningAgent(class_type.value, f"team{team_id}_player{player_id}")
        
        # AI state tracking
        self.previous_state: Optional[State] = None
        self.previous_action: Optional[Action] = None
        self.previous_health = self.health
        self.previous_damage_dealt = 0.0
        self.step_count = 0
        
        # Enhanced AI behavior parameters based on class
        self.setup_class_specific_ai()
    
    def setup_class_specific_ai(self):
        """Setup AI parameters specific to this class"""
        if self.class_type == ClassType.SNIPER:
            self.preferred_range = self.stats.range * 0.9  # Stay at max range
            self.aggression = 0.3  # Low aggression
        elif self.class_type == ClassType.HEAVY:
            self.preferred_range = self.stats.range * 0.6  # Get closer
            self.aggression = 0.8  # High aggression
        elif self.class_type == ClassType.SCOUT:
            self.preferred_range = self.stats.range * 0.7  # Medium range
            self.aggression = 0.9  # Very high aggression, flanking
        elif self.class_type == ClassType.MEDIC:
            self.preferred_range = self.stats.range * 0.5  # Stay back
            self.aggression = 0.2  # Very low aggression
        elif self.class_type == ClassType.SUPPORT:
            self.preferred_range = self.stats.range * 0.8  # Good range
            self.aggression = 0.5  # Balanced
        else:  # ASSAULT
            self.preferred_range = self.stats.range * 0.7  # Balanced
            self.aggression = 0.6  # Balanced
    
    def update_ai(self, dt: float, game_map, enemies, allies):
        """Enhanced AI update using machine learning"""
        self.step_count += 1
        
        # Store allies and enemies for reward calculation
        self._current_allies = allies
        self._current_enemies = enemies
        
        # Get current state
        current_state = self.learning_agent.get_state(self, allies, enemies, game_map)
        
        # Get AI action
        action = self.learning_agent.choose_action(current_state)
        
        # Store previous experience if available
        if self.previous_state is not None and self.previous_action is not None:
            reward = self.calculate_reward(current_state)
            experience = Experience(
                state=self.previous_state,
                action=self.previous_action,
                reward=reward,
                next_state=current_state,
                done=not self.is_alive
            )
            self.learning_agent.remember(experience)
        
        # Execute action
        self.execute_action(action, dt, game_map, enemies, allies)
        
        # Update state tracking
        self.previous_state = current_state
        self.previous_action = action
        self.previous_health = self.health
        self.previous_damage_dealt = self.damage_dealt
    
    def calculate_reward(self, current_state: State) -> float:
        """Calculate reward based on state transition"""
        # Calculate changes since last step
        health_change = self.health - self.previous_health
        damage_dealt_change = self.damage_dealt - self.previous_damage_dealt
        
        # Get team counts
        alive_allies = len([a for a in self.get_allies() if a.is_alive])
        alive_enemies = len([e for e in self.get_enemies() if e.is_alive])
        
        # Use the learning agent's reward calculation
        reward = self.learning_agent.calculate_reward(
            prev_state=self.previous_state,
            action=self.previous_action,
            new_state=current_state,
            damage_dealt=damage_dealt_change,
            damage_taken=-health_change if health_change < 0 else 0,
            kills=0,  # Simplified for now
            team_alive=alive_allies,
            enemy_alive=alive_enemies
        )
        
        # Class-specific reward modifications
        if self.class_type == ClassType.MEDIC:
            # Reward staying alive and near allies
            if self.is_alive and current_state.nearest_ally_distance < 0.3:
                reward += 1.0
        elif self.class_type == ClassType.SNIPER:
            # Reward maintaining good range
            if 0.6 < current_state.nearest_enemy_distance < 0.9:
                reward += 0.5
        elif self.class_type == ClassType.SCOUT:
            # Reward flanking and mobility
            reward += 0.1  # Small bonus for being a scout (always moving)
        
        return reward
    
    def execute_action(self, action: Action, dt: float, game_map, enemies, allies):
        """Execute the AI-chosen action"""
        # Apply movement
        move_speed = self.stats.speed * self.aggression
        self.velocity_x = action.move_direction[0] * move_speed
        self.velocity_y = action.move_direction[1] * move_speed
        
        # Class-specific movement modifications
        if self.class_type == ClassType.SCOUT:
            # Scouts move faster
            self.velocity_x *= 1.2
            self.velocity_y *= 1.2
        elif self.class_type == ClassType.HEAVY:
            # Heavy moves slower but steadier
            self.velocity_x *= 0.8
            self.velocity_y *= 0.8
        
        # Apply shooting
        if action.should_shoot and enemies:
            target = self.find_best_target(enemies, action.target_priority)
            if target:
                self.try_shoot(target, dt)
        
        # Apply special ability
        if action.should_use_special:
            self.use_special_ability(dt, allies, enemies)
        
        # Class-specific behaviors
        self.apply_class_specific_behavior(action, dt, game_map, enemies, allies)
    
    def apply_class_specific_behavior(self, action: Action, dt: float, game_map, enemies, allies):
        """Apply class-specific AI behaviors"""
        if self.class_type == ClassType.MEDIC:
            # Medic tries to heal wounded allies
            for ally in allies:
                if ally != self and ally.is_alive and ally.health < ally.stats.max_health * 0.7:
                    # Move towards wounded ally
                    dx = ally.x - self.x
                    dy = ally.y - self.y
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance < 100:  # In heal range
                        self.use_special_ability(dt, allies, enemies)
                        break
                    elif distance < 200:  # Move closer
                        self.velocity_x += (dx / distance) * self.stats.speed * 0.3
                        self.velocity_y += (dy / distance) * self.stats.speed * 0.3
        
        elif self.class_type == ClassType.SNIPER:
            # Sniper tries to maintain range and find good positions
            nearest_enemy = self.find_nearest_enemy(enemies)
            if nearest_enemy:
                dx = nearest_enemy.x - self.x
                dy = nearest_enemy.y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                # Try to maintain optimal range
                if distance < self.preferred_range * 0.8:
                    # Too close, back away
                    self.velocity_x -= (dx / distance) * self.stats.speed * 0.5
                    self.velocity_y -= (dy / distance) * self.stats.speed * 0.5
                elif distance > self.preferred_range * 1.2:
                    # Too far, move closer slowly
                    self.velocity_x += (dx / distance) * self.stats.speed * 0.2
                    self.velocity_y += (dy / distance) * self.stats.speed * 0.2
        
        elif self.class_type == ClassType.SCOUT:
            # Scout tries to flank enemies
            if enemies:
                # Find enemy center
                enemy_center_x = sum(e.x for e in enemies if e.is_alive) / max(1, len([e for e in enemies if e.is_alive]))
                enemy_center_y = sum(e.y for e in enemies if e.is_alive) / max(1, len([e for e in enemies if e.is_alive]))
                
                # Calculate flanking position
                angle = math.atan2(enemy_center_y - self.y, enemy_center_x - self.x)
                flank_angle = angle + math.pi/3  # Flank at 60 degrees
                
                flank_x = enemy_center_x + math.cos(flank_angle) * self.preferred_range
                flank_y = enemy_center_y + math.sin(flank_angle) * self.preferred_range
                
                # Move towards flanking position
                dx = flank_x - self.x
                dy = flank_y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                if distance > 20:  # If not at flanking position
                    self.velocity_x += (dx / distance) * self.stats.speed * 0.3
                    self.velocity_y += (dy / distance) * self.stats.speed * 0.3
        
        elif self.class_type == ClassType.HEAVY:
            # Heavy tries to tank and get in close
            nearest_enemy = self.find_nearest_enemy(enemies)
            if nearest_enemy:
                dx = nearest_enemy.x - self.x
                dy = nearest_enemy.y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                # Always try to get closer (heavy is tank)
                if distance > self.preferred_range:
                    self.velocity_x += (dx / distance) * self.stats.speed * 0.6
                    self.velocity_y += (dy / distance) * self.stats.speed * 0.6
    
    def find_best_target(self, enemies, priority: int) -> Optional:
        """Find the best target based on AI priority"""
        alive_enemies = [e for e in enemies if e.is_alive]
        if not alive_enemies:
            return None
        
        # Different targeting strategies
        if priority == 0 or self.class_type == ClassType.ASSAULT:
            # Target nearest enemy
            return min(alive_enemies, key=lambda e: math.sqrt((e.x - self.x)**2 + (e.y - self.y)**2))
        elif priority == 1 or self.class_type == ClassType.SNIPER:
            # Target weakest enemy
            return min(alive_enemies, key=lambda e: e.health)
        elif priority == 2 or self.class_type == ClassType.SUPPORT:
            # Target enemy with highest damage output (simplified as assault/sniper)
            priority_classes = [ClassType.SNIPER, ClassType.ASSAULT, ClassType.HEAVY]
            for class_type in priority_classes:
                targets = [e for e in alive_enemies if e.class_type == class_type]
                if targets:
                    return min(targets, key=lambda e: math.sqrt((e.x - self.x)**2 + (e.y - self.y)**2))
            return alive_enemies[0]
        else:
            # Random target
            import random
            return random.choice(alive_enemies)
    
    def get_allies(self) -> List:
        """Get list of allied players"""
        return getattr(self, '_current_allies', [])
    
    def get_enemies(self) -> List:
        """Get list of enemy players"""
        return getattr(self, '_current_enemies', [])
    
    def end_episode(self, won: bool):
        """Called when the game/episode ends"""
        if self.previous_state and self.previous_action:
            # Create final experience
            final_reward = 10.0 if won else -10.0
            if self.is_alive:
                final_reward += 5.0  # Bonus for surviving
            
            # Add class-specific end rewards
            if self.class_type == ClassType.MEDIC and won:
                final_reward += 2.0  # Medic gets bonus for team win
            
            final_experience = Experience(
                state=self.previous_state,
                action=self.previous_action,
                reward=final_reward,
                next_state=self.previous_state,  # Terminal state
                done=True
            )
            self.learning_agent.remember(final_experience)
        
        # Update learning agent
        self.learning_agent.end_episode(won, final_reward if 'final_reward' in locals() else 0.0)
    
    def get_learning_data(self) -> dict:
        """Get enhanced learning data including AI metrics"""
        base_data = super().get_learning_data()
        ai_metrics = self.learning_agent.get_performance_metrics()
        
        base_data.update({
            'ai_episode_count': ai_metrics['episode_count'],
            'ai_win_rate': ai_metrics['win_rate'],
            'ai_epsilon': ai_metrics['epsilon'],
            'ai_avg_reward': ai_metrics['avg_reward'],
            'ai_memory_size': ai_metrics['memory_size'],
        })
        
        return base_data