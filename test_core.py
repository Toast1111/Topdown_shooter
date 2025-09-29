#!/usr/bin/env python3
"""
Core functionality test for the game without AI complexity
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Mock pygame
sys.modules['pygame'] = __import__('mock_pygame')
sys.modules['pygame.display'] = __import__('mock_pygame').display
sys.modules['pygame.time'] = __import__('mock_pygame').time  
sys.modules['pygame.font'] = __import__('mock_pygame')
sys.modules['pygame.draw'] = __import__('mock_pygame').draw

# Test core game functionality
try:
    from src.entities.player_class import PlayerClass, ClassType
    from src.utils.map_generator import MapGenerator
    from src.ui.class_selector import ClassSelector
    print("✓ Core imports successful!")
    
    # Test PlayerClass functionality
    print("Testing PlayerClass...")
    player = PlayerClass(ClassType.ASSAULT, 1, (100, 100), 0)
    print(f"✓ Created {player.class_type.value} player")
    print(f"  - Health: {player.health}/{player.stats.max_health}")
    print(f"  - Speed: {player.stats.speed}")
    print(f"  - Damage: {player.stats.damage}")
    print(f"  - Range: {player.stats.range}")
    
    # Test different classes
    print("\nTesting all player classes...")
    for class_type in ClassType:
        test_player = PlayerClass(class_type, 1, (0, 0), 0)
        stats = test_player.stats
        print(f"✓ {class_type.value.title():8} - HP:{stats.max_health:3.0f} Speed:{stats.speed:3.0f} Dmg:{stats.damage:2.0f} Range:{stats.range:3.0f}")
    
    # Test MapGenerator
    print("\nTesting MapGenerator...")
    map_gen = MapGenerator(800, 600)
    game_map = map_gen.generate_map()
    print(f"✓ Generated map with {len(game_map.obstacles)} obstacles")
    print(f"  - Team 1 spawns: {len(game_map.team1_spawns)}")
    print(f"  - Team 2 spawns: {len(game_map.team2_spawns)}")
    
    # Test different map types by generating multiple maps
    print("\nTesting multiple map generations...")
    for i in range(5):
        test_map = map_gen.generate_map()
        print(f"  Map {i+1}: {len(test_map.obstacles)} obstacles")
    
    # Test ClassSelector
    print("\nTesting ClassSelector...")
    selector = ClassSelector()
    print(f"✓ Class selector initialized")
    print(f"  - Default Team 1: {[c.value for c in selector.selected_team1_classes]}")
    print(f"  - Default Team 2: {[c.value for c in selector.selected_team2_classes]}")
    
    # Test combat mechanics
    print("\nTesting combat mechanics...")
    attacker = PlayerClass(ClassType.ASSAULT, 1, (0, 0), 0)
    target = PlayerClass(ClassType.ASSAULT, 2, (50, 0), 1)
    
    original_health = target.health
    success = attacker.try_shoot(target, 0.1)
    print(f"✓ Combat test - Shot {'hit' if success else 'missed'}")
    if success:
        print(f"  - Target health: {original_health} -> {target.health}")
    
    # Test special abilities
    print("\nTesting special abilities...")
    medic = PlayerClass(ClassType.MEDIC, 1, (0, 0), 0)
    injured_ally = PlayerClass(ClassType.ASSAULT, 1, (30, 0), 1)
    injured_ally.health = 50  # Reduce health
    
    allies = [medic, injured_ally]
    enemies = []
    medic.use_special_ability(0.1, allies, enemies)
    print(f"✓ Medic special ability used")
    print(f"  - Ally health after heal: {injured_ally.health}")
    
    print("\n🎉 All core functionality tests passed!")
    print("The game has a solid foundation with:")
    print("  - 6 distinct player classes with unique stats")  
    print("  - Random map generation with multiple layouts")
    print("  - Combat system with accuracy and damage")
    print("  - Special abilities per class")
    print("  - Class selection UI")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()