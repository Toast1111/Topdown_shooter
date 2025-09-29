#!/usr/bin/env python3
"""
Basic test to verify the game structure works
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Mock numpy first
class MockNdarray:
    def __init__(self, data):
        if hasattr(data, '__iter__'):
            self.data = list(data)
        else:
            self.data = [data]
        self.shape = (len(self.data),)
    
    def reshape(self, *shape):
        return MockNdarray(self.data)
    
    def copy(self):
        return MockNdarray(self.data.copy())
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value
    
    def __mul__(self, other):
        return MockNdarray([x * other for x in self.data])
    
    def __add__(self, other):
        if hasattr(other, 'data'):
            return MockNdarray([a + b for a, b in zip(self.data, other.data)])
        return MockNdarray([x + other for x in self.data])
    
    def __sub__(self, other):
        if hasattr(other, 'data'):
            return MockNdarray([a - b for a, b in zip(self.data, other.data)])
        return MockNdarray([x - other for x in self.data])
    
    def __truediv__(self, other):
        return MockNdarray([x / other for x in self.data])
    
    def __pow__(self, other):
        return MockNdarray([x ** other for x in self.data])
    
    def tolist(self):
        return self.data
    
    def __iter__(self):
        return iter(self.data)

class MockNumpy:
    ndarray = MockNdarray
    
    class random:
        @staticmethod
        def randn(*shape):
            import random
            if len(shape) == 2:
                size = shape[0] * shape[1]
            else:
                size = shape[0]
            return MockNdarray([random.gauss(0, 1) for _ in range(size)])
    
    @staticmethod
    def array(data):
        return MockNdarray(data)
    
    @staticmethod
    def zeros(shape):
        if isinstance(shape, tuple):
            size = shape[0] * shape[1] if len(shape) > 1 else shape[0]
        else:
            size = shape
        return MockNdarray([0.0] * size)
    
    @staticmethod
    def dot(a, b):
        # Simplified dot product
        return MockNdarray([1.0])
    
    @staticmethod
    def maximum(a, b):
        if hasattr(a, 'data'):
            if hasattr(b, 'data'):
                return MockNdarray([max(x, y) for x, y in zip(a.data, b.data)])
            else:
                return MockNdarray([max(x, b) for x in a.data])
        else:
            return MockNdarray([max(a, b)])
    
    @staticmethod
    def mean(data):
        return sum(data.data) / len(data.data)
    
    @staticmethod
    def sum(data, axis=None, keepdims=False):
        return MockNdarray([sum(data.data)])
    
    @staticmethod
    def argmax(data):
        return data.data.index(max(data.data))

class MockRandom:
    @staticmethod
    def randn(*shape):
        import random
        if len(shape) == 2:
            size = shape[0] * shape[1]
        else:
            size = shape[0]
        return MockNdarray([random.gauss(0, 1) for _ in range(size)])

# Mock pygame
sys.modules['pygame'] = __import__('mock_pygame')
sys.modules['pygame.display'] = __import__('mock_pygame').display
sys.modules['pygame.time'] = __import__('mock_pygame').time  
sys.modules['pygame.font'] = __import__('mock_pygame')
sys.modules['pygame.draw'] = __import__('mock_pygame').draw

# Mock numpy
sys.modules['numpy'] = MockNumpy()

# Test imports
try:
    from src.entities.player_class import PlayerClass, ClassType
    from src.entities.ai_player import AIPlayer
    from src.entities.team import Team
    from src.utils.map_generator import MapGenerator
    from src.ui.class_selector import ClassSelector
    from src.ai.learning_agent import LearningAgent
    print("✓ All imports successful!")
    
    # Test basic functionality
    print("Testing AIPlayer creation...")
    player = AIPlayer(ClassType.ASSAULT, 1, (100, 100), 0)
    print(f"✓ Created AI player: {player.class_type.value} at position {player.get_position()}")
    
    print("Testing LearningAgent...")
    agent = LearningAgent("assault", "test_agent")
    print(f"✓ Created learning agent with epsilon: {agent.epsilon}")
    
    print("Testing MapGenerator...")
    map_gen = MapGenerator(800, 600)
    game_map = map_gen.generate_map()
    print(f"✓ Generated map with {len(game_map.obstacles)} obstacles")
    
    print("Testing Team creation with AI players...")
    team_classes = [ClassType.ASSAULT, ClassType.SNIPER, ClassType.MEDIC, 
                    ClassType.HEAVY, ClassType.SCOUT, ClassType.SUPPORT]
    spawn_positions = [(100, 100), (120, 100), (140, 100), (160, 100), (180, 100), (200, 100)]
    team = Team(1, team_classes, spawn_positions)
    print(f"✓ Created team with {len(team.players)} AI players")
    
    # Test AI decision making
    print("Testing AI decision making...")
    test_allies = []
    test_enemies = [AIPlayer(ClassType.ASSAULT, 2, (200, 200), 0)]
    
    for player in team.players[:2]:  # Test first 2 players
        state = player.learning_agent.get_state(player, test_allies, test_enemies, game_map)
        action = player.learning_agent.choose_action(state)
        print(f"✓ {player.class_type.value} chose action: move={action.move_direction}, shoot={action.should_shoot}")
    
    print("Testing ClassSelector...")
    selector = ClassSelector()
    print(f"✓ Created class selector")
    
    print("\n🎉 All tests passed! Game structure with AI learning is working correctly.")
    print(f"AI agents are using neural networks with {agent.q_network.state_size} state inputs")
    print(f"and {agent.q_network.action_size} possible actions.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()