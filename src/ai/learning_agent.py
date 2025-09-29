"""
AI Learning Agent using reinforcement learning
This implements actual AI learning, not faked behavior
"""

import json
import os
import random
import numpy as np
from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass
from collections import deque

@dataclass
class State:
    """Represents the current state of the game for AI decision making"""
    player_health: float
    player_position: Tuple[float, float]
    nearest_enemy_distance: float
    nearest_enemy_health: float
    nearest_ally_distance: float
    ally_count: int
    enemy_count: int
    ammo_status: float  # Simplified ammo representation
    cover_distance: float
    team_strategy: str

@dataclass
class Action:
    """Represents an action the AI can take"""
    move_direction: Tuple[float, float]  # Normalized movement vector
    should_shoot: bool
    should_use_special: bool
    target_priority: int  # Which enemy to prioritize

class Experience:
    """Represents a single experience tuple for learning"""
    def __init__(self, state: State, action: Action, reward: float, next_state: State, done: bool):
        self.state = state
        self.action = action
        self.reward = reward
        self.next_state = next_state
        self.done = done

class SimpleQNetwork:
    """Simple Q-Network implementation using numpy (simplified deep learning)"""
    
    def __init__(self, state_size: int, action_size: int, learning_rate: float = 0.01):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        
        # Simple neural network with one hidden layer
        self.weights1 = np.random.randn(state_size, 64) * 0.1
        self.bias1 = np.zeros((1, 64))
        self.weights2 = np.random.randn(64, 32) * 0.1
        self.bias2 = np.zeros((1, 32))
        self.weights3 = np.random.randn(32, action_size) * 0.1
        self.bias3 = np.zeros((1, action_size))
    
    def predict(self, state: np.ndarray) -> np.ndarray:
        """Predict Q-values for given state"""
        # Forward pass
        z1 = np.dot(state, self.weights1) + self.bias1
        a1 = np.maximum(0, z1)  # ReLU activation
        
        z2 = np.dot(a1, self.weights2) + self.bias2
        a2 = np.maximum(0, z2)  # ReLU activation
        
        z3 = np.dot(a2, self.weights3) + self.bias3
        return z3  # Linear output for Q-values
    
    def train(self, states: np.ndarray, targets: np.ndarray):
        """Train the network using backpropagation"""
        batch_size = states.shape[0]
        
        # Forward pass
        z1 = np.dot(states, self.weights1) + self.bias1
        a1 = np.maximum(0, z1)
        
        z2 = np.dot(a1, self.weights2) + self.bias2
        a2 = np.maximum(0, z2)
        
        z3 = np.dot(a2, self.weights3) + self.bias3
        predictions = z3
        
        # Backward pass
        loss = np.mean((predictions - targets) ** 2)
        
        # Gradients
        d_output = 2 * (predictions - targets) / batch_size
        
        # Layer 3
        d_weights3 = np.dot(a2.T, d_output)
        d_bias3 = np.sum(d_output, axis=0, keepdims=True)
        d_a2 = np.dot(d_output, self.weights3.T)
        
        # Layer 2  
        d_z2 = d_a2 * (z2 > 0)  # ReLU derivative
        d_weights2 = np.dot(a1.T, d_z2)
        d_bias2 = np.sum(d_z2, axis=0, keepdims=True)
        d_a1 = np.dot(d_z2, self.weights2.T)
        
        # Layer 1
        d_z1 = d_a1 * (z1 > 0)  # ReLU derivative
        d_weights1 = np.dot(states.T, d_z1)
        d_bias1 = np.sum(d_z1, axis=0, keepdims=True)
        
        # Update weights
        self.weights3 -= self.learning_rate * d_weights3
        self.bias3 -= self.learning_rate * d_bias3
        self.weights2 -= self.learning_rate * d_weights2
        self.bias2 -= self.learning_rate * d_bias2
        self.weights1 -= self.learning_rate * d_weights1
        self.bias1 -= self.learning_rate * d_bias1
        
        return loss

class LearningAgent:
    """Main AI learning agent that makes decisions and learns from experience"""
    
    def __init__(self, class_type: str, agent_id: str):
        self.class_type = class_type
        self.agent_id = agent_id
        
        # Q-Learning parameters
        self.epsilon = 0.1  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.gamma = 0.95  # Discount factor
        self.learning_rate = 0.001
        
        # Experience replay
        self.memory = deque(maxlen=10000)
        self.batch_size = 32
        
        # State and action spaces
        self.state_size = 10  # Size of state representation
        self.action_size = 12  # Discretized action space
        
        # Neural network
        self.q_network = SimpleQNetwork(self.state_size, self.action_size, self.learning_rate)
        
        # Performance tracking
        self.total_reward = 0.0
        self.episode_count = 0
        self.win_rate = 0.0
        
        # Load existing model if available
        self.model_path = f"models/{class_type}_{agent_id}.json"
        self.load_model()
    
    def get_state(self, player, allies: List, enemies: List, game_map) -> State:
        """Extract current state for AI decision making"""
        # Find nearest enemy
        nearest_enemy_dist = float('inf')
        nearest_enemy_health = 0.0
        
        if enemies:
            for enemy in enemies:
                if enemy.is_alive:
                    dx = enemy.x - player.x
                    dy = enemy.y - player.y
                    dist = (dx*dx + dy*dy) ** 0.5
                    if dist < nearest_enemy_dist:
                        nearest_enemy_dist = dist
                        nearest_enemy_health = enemy.health
        
        # Find nearest ally
        nearest_ally_dist = float('inf')
        if allies:
            for ally in allies:
                if ally != player and ally.is_alive:
                    dx = ally.x - player.x
                    dy = ally.y - player.y
                    dist = (dx*dx + dy*dy) ** 0.5
                    if dist < nearest_ally_dist:
                        nearest_ally_dist = dist
        
        # Find nearest cover (simplified)
        cover_dist = 100.0  # Default cover distance
        for obstacle in game_map.obstacles:
            dx = obstacle.x - player.x
            dy = obstacle.y - player.y
            dist = (dx*dx + dy*dy) ** 0.5
            if dist < cover_dist:
                cover_dist = dist
        
        return State(
            player_health=player.health / player.stats.max_health,
            player_position=(player.x / game_map.width, player.y / game_map.height),
            nearest_enemy_distance=min(nearest_enemy_dist / 400.0, 1.0),
            nearest_enemy_health=nearest_enemy_health / 100.0,
            nearest_ally_distance=min(nearest_ally_dist / 200.0, 1.0),
            ally_count=len([a for a in allies if a.is_alive]) / 6.0,
            enemy_count=len([e for e in enemies if e.is_alive]) / 6.0,
            ammo_status=1.0,  # Simplified - assume full ammo
            cover_distance=min(cover_dist / 100.0, 1.0),
            team_strategy="balanced"
        )
    
    def state_to_array(self, state: State) -> np.ndarray:
        """Convert state to numpy array for neural network"""
        return np.array([
            state.player_health,
            state.player_position[0],
            state.player_position[1],
            state.nearest_enemy_distance,
            state.nearest_enemy_health,
            state.nearest_ally_distance,
            state.ally_count,
            state.enemy_count,
            state.ammo_status,
            state.cover_distance
        ]).reshape(1, -1)
    
    def choose_action(self, state: State) -> Action:
        """Choose action based on current state using epsilon-greedy policy"""
        state_array = self.state_to_array(state)
        
        if random.random() < self.epsilon:
            # Random action (exploration)
            action_index = random.randint(0, self.action_size - 1)
        else:
            # Best action from Q-network (exploitation)
            q_values = self.q_network.predict(state_array)
            action_index = np.argmax(q_values[0])
        
        return self.decode_action(action_index, state)
    
    def decode_action(self, action_index: int, state: State) -> Action:
        """Convert action index to actual action"""
        # Action space:
        # 0-3: Movement directions (up, down, left, right)
        # 4-7: Diagonal movements
        # 8: Stay and shoot
        # 9: Retreat
        # 10: Use special ability
        # 11: Seek cover
        
        move_directions = [
            (0, -1),    # Up
            (0, 1),     # Down  
            (-1, 0),    # Left
            (1, 0),     # Right
            (-0.7, -0.7), # Up-left
            (0.7, -0.7),  # Up-right
            (-0.7, 0.7),  # Down-left
            (0.7, 0.7),   # Down-right
            (0, 0),       # Stay
            (-1, 0),      # Retreat (simplified as left)
            (0, 0),       # Stay for special
            (0, 0),       # Stay for cover
        ]
        
        move_direction = move_directions[min(action_index, len(move_directions) - 1)]
        should_shoot = action_index in [8, 9]  # Shoot when staying or retreating
        should_use_special = action_index == 10
        
        return Action(
            move_direction=move_direction,
            should_shoot=should_shoot,
            should_use_special=should_use_special,
            target_priority=0
        )
    
    def calculate_reward(self, prev_state: State, action: Action, new_state: State, 
                        damage_dealt: float, damage_taken: float, kills: int, 
                        team_alive: int, enemy_alive: int) -> float:
        """Calculate reward for the taken action"""
        reward = 0.0
        
        # Survival bonus
        if new_state.player_health > 0:
            reward += 1.0
        else:
            reward -= 10.0  # Death penalty
        
        # Combat rewards
        reward += damage_dealt * 0.1  # Reward for dealing damage
        reward -= damage_taken * 0.05  # Penalty for taking damage
        reward += kills * 5.0  # Big reward for kills
        
        # Team performance
        if team_alive > enemy_alive:
            reward += 2.0  # Team advantage bonus
        elif team_alive < enemy_alive:
            reward -= 1.0  # Team disadvantage penalty
        
        # Positioning rewards
        if prev_state.nearest_enemy_distance > new_state.nearest_enemy_distance:
            # Moving closer to enemy can be good if health is high
            if new_state.player_health > 0.7:
                reward += 0.5
            else:
                reward -= 0.5  # Bad to get closer when low health
        
        # Cover usage
        if new_state.cover_distance < prev_state.cover_distance and new_state.player_health < 0.5:
            reward += 1.0  # Good to seek cover when low health
        
        return reward
    
    def remember(self, experience: Experience):
        """Store experience in memory"""
        self.memory.append(experience)
    
    def replay(self):
        """Train the agent using experience replay"""
        if len(self.memory) < self.batch_size:
            return
        
        # Sample random batch
        batch = random.sample(self.memory, self.batch_size)
        
        # Prepare training data
        states = np.array([self.state_to_array(exp.state)[0] for exp in batch])
        next_states = np.array([self.state_to_array(exp.next_state)[0] for exp in batch])
        
        # Predict Q-values
        current_q_values = self.q_network.predict(states)
        next_q_values = self.q_network.predict(next_states)
        
        # Calculate target Q-values
        targets = current_q_values.copy()
        
        for i, exp in enumerate(batch):
            action_index = self.encode_action(exp.action)
            
            if exp.done:
                targets[i][action_index] = exp.reward
            else:
                targets[i][action_index] = exp.reward + self.gamma * np.max(next_q_values[i])
        
        # Train the network
        loss = self.q_network.train(states, targets)
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        return loss
    
    def encode_action(self, action: Action) -> int:
        """Convert action back to index for training"""
        # Simplified encoding - in practice this would be more sophisticated
        if action.should_use_special:
            return 10
        elif action.should_shoot:
            return 8
        else:
            # Find closest movement direction
            move_directions = [
                (0, -1), (0, 1), (-1, 0), (1, 0),
                (-0.7, -0.7), (0.7, -0.7), (-0.7, 0.7), (0.7, 0.7)
            ]
            
            best_match = 0
            best_similarity = float('-inf')
            
            for i, direction in enumerate(move_directions):
                similarity = (direction[0] * action.move_direction[0] + 
                             direction[1] * action.move_direction[1])
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = i
            
            return best_match
    
    def save_model(self):
        """Save the trained model to file"""
        os.makedirs("models", exist_ok=True)
        
        model_data = {
            'weights1': self.q_network.weights1.tolist(),
            'bias1': self.q_network.bias1.tolist(),
            'weights2': self.q_network.weights2.tolist(),
            'bias2': self.q_network.bias2.tolist(),
            'weights3': self.q_network.weights3.tolist(),
            'bias3': self.q_network.bias3.tolist(),
            'epsilon': self.epsilon,
            'episode_count': self.episode_count,
            'total_reward': self.total_reward,
            'win_rate': self.win_rate
        }
        
        try:
            with open(self.model_path, 'w') as f:
                json.dump(model_data, f, indent=2)
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def load_model(self):
        """Load a previously trained model"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'r') as f:
                    model_data = json.load(f)
                
                # Load network weights
                self.q_network.weights1 = np.array(model_data['weights1'])
                self.q_network.bias1 = np.array(model_data['bias1'])
                self.q_network.weights2 = np.array(model_data['weights2'])
                self.q_network.bias2 = np.array(model_data['bias2'])
                self.q_network.weights3 = np.array(model_data['weights3'])
                self.q_network.bias3 = np.array(model_data['bias3'])
                
                # Load training state
                self.epsilon = model_data.get('epsilon', self.epsilon)
                self.episode_count = model_data.get('episode_count', 0)
                self.total_reward = model_data.get('total_reward', 0.0)
                self.win_rate = model_data.get('win_rate', 0.0)
                
                print(f"Loaded model for {self.class_type} agent {self.agent_id}")
        except Exception as e:
            print(f"Could not load model: {e}, starting fresh")
    
    def end_episode(self, won: bool, final_reward: float):
        """Called at the end of each episode to update learning metrics"""
        self.episode_count += 1
        self.total_reward += final_reward
        
        # Update win rate
        self.win_rate = ((self.win_rate * (self.episode_count - 1)) + (1.0 if won else 0.0)) / self.episode_count
        
        # Train on accumulated experiences
        if len(self.memory) >= self.batch_size:
            for _ in range(5):  # Multiple training iterations per episode
                self.replay()
        
        # Save model periodically
        if self.episode_count % 10 == 0:
            self.save_model()
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get current performance metrics for analysis"""
        return {
            'episode_count': self.episode_count,
            'win_rate': self.win_rate,
            'epsilon': self.epsilon,
            'avg_reward': self.total_reward / max(1, self.episode_count),
            'memory_size': len(self.memory)
        }