"""
User interface for selecting team class compositions
"""

import pygame
from typing import List, Dict, Optional
from src.entities.player_class import ClassType, PlayerClass

class ClassSelector:
    """UI for selecting class composition for both teams"""
    
    def __init__(self):
        self.selected_team1_classes = [ClassType.ASSAULT] * 6  # Default composition
        self.selected_team2_classes = [ClassType.ASSAULT] * 6
        
        self.current_team = 1
        self.current_slot = 0
        
        # UI state
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Colors
        self.bg_color = (30, 30, 30)
        self.text_color = (255, 255, 255)
        self.highlight_color = (100, 150, 255)
        self.team1_color = (0, 255, 0)
        self.team2_color = (255, 0, 0)
        
        # Class descriptions
        self.class_descriptions = {
            ClassType.ASSAULT: "Balanced fighter with good damage and mobility",
            ClassType.SNIPER: "Long-range specialist with high damage but slow fire rate",
            ClassType.SUPPORT: "Provides suppressing fire and team buffs",
            ClassType.HEAVY: "High health tank with explosive abilities",
            ClassType.SCOUT: "Fast and agile with flanking capabilities", 
            ClassType.MEDIC: "Heals allies and provides battlefield support"
        }
    
    def handle_event(self, event, game):
        """Handle input events for class selection"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Start game with current selections
                game.start_match(self.selected_team1_classes, self.selected_team2_classes)
            
            elif event.key == pygame.K_TAB:
                # Switch between teams
                self.current_team = 2 if self.current_team == 1 else 1
                self.current_slot = 0
            
            elif event.key == pygame.K_LEFT:
                self.current_slot = max(0, self.current_slot - 1)
            
            elif event.key == pygame.K_RIGHT:
                self.current_slot = min(5, self.current_slot + 1)
            
            elif event.key == pygame.K_UP:
                # Cycle through class types
                current_classes = (self.selected_team1_classes if self.current_team == 1 
                                 else self.selected_team2_classes)
                
                class_types = list(ClassType)
                current_type = current_classes[self.current_slot]
                current_index = class_types.index(current_type)
                new_index = (current_index - 1) % len(class_types)
                current_classes[self.current_slot] = class_types[new_index]
            
            elif event.key == pygame.K_DOWN:
                # Cycle through class types (other direction)
                current_classes = (self.selected_team1_classes if self.current_team == 1 
                                 else self.selected_team2_classes)
                
                class_types = list(ClassType)
                current_type = current_classes[self.current_slot]
                current_index = class_types.index(current_type)
                new_index = (current_index + 1) % len(class_types)
                current_classes[self.current_slot] = class_types[new_index]
            
            elif event.key >= pygame.K_1 and event.key <= pygame.K_6:
                # Quick select class by number
                class_types = list(ClassType)
                class_index = event.key - pygame.K_1
                if class_index < len(class_types):
                    current_classes = (self.selected_team1_classes if self.current_team == 1 
                                     else self.selected_team2_classes)
                    current_classes[self.current_slot] = class_types[class_index]
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle mouse clicks for class selection
            self.handle_mouse_click(event.pos, game)
    
    def handle_mouse_click(self, pos, game):
        """Handle mouse clicks on UI elements"""
        x, y = pos
        
        # Check if clicking on team selection areas
        team1_rect = pygame.Rect(50, 150, 500, 300)
        team2_rect = pygame.Rect(650, 150, 500, 300)
        
        if team1_rect.collidepoint(pos):
            self.current_team = 1
            # Calculate which slot was clicked
            slot_width = 80
            slot_x = (x - team1_rect.x) // slot_width
            self.current_slot = min(5, max(0, slot_x))
        
        elif team2_rect.collidepoint(pos):
            self.current_team = 2
            slot_width = 80
            slot_x = (x - team2_rect.x) // slot_width
            self.current_slot = min(5, max(0, slot_x))
        
        # Check if clicking on start button
        start_button_rect = pygame.Rect(500, 700, 200, 50)
        if start_button_rect.collidepoint(pos):
            game.start_match(self.selected_team1_classes, self.selected_team2_classes)
    
    def render(self, screen):
        """Render the class selection interface"""
        screen.fill(self.bg_color)
        
        # Title
        title_text = self.font_large.render("CLASS SELECTION", True, self.text_color)
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 50))
        screen.blit(title_text, title_rect)
        
        # Instructions
        instruction_lines = [
            "Use ARROW KEYS to navigate, UP/DOWN to change classes",
            "TAB to switch teams, ENTER to start battle",
            "Number keys 1-6 for quick class selection"
        ]
        
        y = 90
        for line in instruction_lines:
            text = self.font_small.render(line, True, self.text_color)
            text_rect = text.get_rect(center=(screen.get_width() // 2, y))
            screen.blit(text, text_rect)
            y += 25
        
        # Team selection areas
        self.render_team_selection(screen, 1, 50, 150)
        self.render_team_selection(screen, 2, 650, 150)
        
        # Class descriptions
        self.render_class_description(screen)
        
        # Start button
        self.render_start_button(screen)
    
    def render_team_selection(self, screen, team_id: int, x: int, y: int):
        """Render class selection for a specific team"""
        team_color = self.team1_color if team_id == 1 else self.team2_color
        classes = self.selected_team1_classes if team_id == 1 else self.selected_team2_classes
        
        # Team header
        header_text = f"TEAM {team_id}"
        header_surf = self.font_medium.render(header_text, True, team_color)
        screen.blit(header_surf, (x, y))
        
        # Team selection border
        border_rect = pygame.Rect(x - 5, y - 5, 510, 310)
        border_color = self.highlight_color if self.current_team == team_id else (100, 100, 100)
        pygame.draw.rect(screen, border_color, border_rect, 3)
        
        # Class slots
        slot_y = y + 40
        slot_width = 80
        slot_height = 100
        
        for i, class_type in enumerate(classes):
            slot_x = x + i * slot_width
            
            # Slot background
            slot_rect = pygame.Rect(slot_x, slot_y, slot_width - 5, slot_height)
            
            # Highlight current slot
            if self.current_team == team_id and self.current_slot == i:
                pygame.draw.rect(screen, self.highlight_color, slot_rect)
            else:
                pygame.draw.rect(screen, (60, 60, 60), slot_rect)
            
            pygame.draw.rect(screen, (200, 200, 200), slot_rect, 2)
            
            # Class representation
            class_color = PlayerClass.CLASS_COLORS[class_type]
            if team_id == 2:
                class_color = tuple(c // 2 for c in class_color)  # Darker for team 2
            
            # Draw class icon (circle)
            circle_center = (slot_x + slot_width // 2, slot_y + 30)
            pygame.draw.circle(screen, class_color, circle_center, 15)
            
            # Class name
            class_name = class_type.value.title()
            name_surf = self.font_small.render(class_name, True, self.text_color)
            name_rect = name_surf.get_rect(center=(slot_x + slot_width // 2, slot_y + 65))
            screen.blit(name_surf, name_rect)
            
            # Slot number
            slot_num = str(i + 1)
            num_surf = pygame.font.Font(None, 20).render(slot_num, True, self.text_color)
            screen.blit(num_surf, (slot_x + 2, slot_y + 2))
        
        # Team composition stats
        self.render_team_stats(screen, classes, x, slot_y + slot_height + 20)
    
    def render_team_stats(self, screen, classes: List[ClassType], x: int, y: int):
        """Render team composition statistics"""
        # Count classes
        class_counts = {}
        for class_type in classes:
            class_counts[class_type] = class_counts.get(class_type, 0) + 1
        
        # Display counts
        stats_y = y
        for class_type, count in class_counts.items():
            if count > 0:
                stats_text = f"{class_type.value.title()}: {count}"
                stats_surf = self.font_small.render(stats_text, True, self.text_color)
                screen.blit(stats_surf, (x, stats_y))
                stats_y += 20
        
        # Team total stats
        total_health = sum(PlayerClass.CLASS_STATS[ct].max_health for ct in classes)
        avg_speed = sum(PlayerClass.CLASS_STATS[ct].speed for ct in classes) / len(classes)
        total_damage = sum(PlayerClass.CLASS_STATS[ct].damage for ct in classes)
        
        stats_y += 10
        team_stats = [
            f"Total Health: {int(total_health)}",
            f"Avg Speed: {int(avg_speed)}",
            f"Total Damage: {int(total_damage)}"
        ]
        
        for stat in team_stats:
            stat_surf = pygame.font.Font(None, 20).render(stat, True, (200, 200, 200))
            screen.blit(stat_surf, (x, stats_y))
            stats_y += 18
    
    def render_class_description(self, screen):
        """Render description of currently selected class"""
        current_classes = (self.selected_team1_classes if self.current_team == 1 
                         else self.selected_team2_classes)
        current_class = current_classes[self.current_slot]
        
        # Description box
        desc_rect = pygame.Rect(50, 500, 1100, 150)
        pygame.draw.rect(screen, (50, 50, 50), desc_rect)
        pygame.draw.rect(screen, (150, 150, 150), desc_rect, 2)
        
        # Class name and description
        class_name = current_class.value.title()
        name_surf = self.font_medium.render(class_name, True, PlayerClass.CLASS_COLORS[current_class])
        screen.blit(name_surf, (desc_rect.x + 10, desc_rect.y + 10))
        
        # Description text
        description = self.class_descriptions[current_class]
        desc_surf = self.font_small.render(description, True, self.text_color)
        screen.blit(desc_surf, (desc_rect.x + 10, desc_rect.y + 50))
        
        # Class stats
        stats = PlayerClass.CLASS_STATS[current_class]
        stat_lines = [
            f"Health: {int(stats.max_health)}  Speed: {int(stats.speed)}  Damage: {int(stats.damage)}",
            f"Fire Rate: {stats.fire_rate:.1f}/sec  Range: {int(stats.range)}  Accuracy: {stats.accuracy:.1%}"
        ]
        
        y_offset = 85
        for line in stat_lines:
            line_surf = self.font_small.render(line, True, (200, 200, 200))
            screen.blit(line_surf, (desc_rect.x + 10, desc_rect.y + y_offset))
            y_offset += 25
    
    def render_start_button(self, screen):
        """Render the start battle button"""
        button_rect = pygame.Rect(500, 700, 200, 50)
        pygame.draw.rect(screen, (0, 150, 0), button_rect)
        pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)
        
        button_text = "START BATTLE"
        text_surf = self.font_medium.render(button_text, True, self.text_color)
        text_rect = text_surf.get_rect(center=button_rect.center)
        screen.blit(text_surf, text_rect)