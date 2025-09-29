#!/usr/bin/env python3
"""
Top-Down Shooter Game with AI Learning
Main entry point for the game
"""

import pygame
import sys
from src.game import Game

def main():
    """Main game entry point"""
    pygame.init()
    
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        return 1
    finally:
        pygame.quit()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())