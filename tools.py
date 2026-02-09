import pygame
import math
from settings import SCREEN_W, SCREEN_H, COLORS, FONTS, TILE_SIZE, FISHING_ROD

class Tool:
    def __init__(self, name, durability=100):
        self.name = name
        self.durability = durability

class FishingRod(Tool):
    def __init__(self, is_thrown=False):
        super().__init__("Fishing Rod", FISHING_ROD["durability"])
        self.is_thrown = is_thrown
        self.fishing_cooldown = 0
        self.fishing_cooldown_duration = FISHING_ROD["fishing_cooldown_duration"]
        
        # Casting mechanics
        self.is_casting = False
        self.cast_bar_fill = 0.0  # 0.0 to 1.0
        self.max_cast_time = FISHING_ROD["max_cast_time"]
        self.cast_start_time = 0
        
        # Hook mechanics
        self.hook_x = 0
        self.hook_y = 0
        self.hook_vx = 0
        self.hook_vy = 0
        self.line_length = 0
        self.max_line_length = FISHING_ROD["max_line_length"]
        self.desired_distance = 0
        self.distance_traveled = 0
        self.cast_direction = pygame.math.Vector2(0, 0)
        self.player_x_at_cast = 0
        self.player_y_at_cast = 0
        self.travel_time_frames = 0  # Variable based on distance
        
        # Retraction mechanics
        self.is_retracting = False
        self.retraction_progress = 0.0  # 0.0 to 1.0
        self.retraction_time_frames = FISHING_ROD["retraction_time_frames"]
        self.caught_item = None
        self.caught_item_x = 0
        self.caught_item_y = 0

    def start_casting(self, player_x, player_y):
        """Start the casting animation when SPACE is pressed down."""
        self.is_casting = True
        self.cast_bar_fill = 0.0
        self.cast_start_time = pygame.time.get_ticks()
        self.hook_x = player_x
        self.hook_y = player_y

    def update_casting(self):
        """Update casting power bar based on time held."""
        if self.is_casting:
            elapsed = (pygame.time.get_ticks() - self.cast_start_time) / 1000.0
            self.cast_bar_fill = min(1.0, elapsed / (self.max_cast_time / 60.0))

    def throw(self, direction, player_x, player_y):
        """Throw the hook in direction. Cast power affects distance and travel time is relative to distance."""
        self.is_thrown = True
        self.is_casting = False
        self.is_retracting = False
        
        self.player_x_at_cast = player_x
        self.player_y_at_cast = player_y
        
        self.desired_distance = self.cast_bar_fill * self.max_line_length
        self.distance_traveled = 0
        self.cast_direction = direction
        
        # Calculate travel time relative to distance
        base_travel_time = FISHING_ROD["travel_time_frames_base"]
        additional_time = FISHING_ROD["travel_time_frames_additional"]
        self.travel_time_frames = base_travel_time + (self.cast_bar_fill * additional_time)
        
        self.hook_x = player_x
        self.hook_y = player_y
        self.hook_vx = (direction.x * self.desired_distance) / self.travel_time_frames
        self.hook_vy = (direction.y * self.desired_distance) / self.travel_time_frames
        
        self.caught_item = None

    def update_hook(self, player_x, player_y, dropped_items):
        """Update hook position and check for collisions."""
        if not self.is_thrown and not self.is_retracting:
            return
        
        # DEPLOYMENT PHASE
        if self.is_thrown and not self.is_retracting:
            self.hook_x += self.hook_vx
            self.hook_y += self.hook_vy
            
            dx_moved = self.hook_vx
            dy_moved = self.hook_vy
            self.distance_traveled += math.sqrt(dx_moved**2 + dy_moved**2)
            
            # Check if hook has reached desired distance
            if self.distance_traveled >= self.desired_distance:
                self.is_thrown = False
                self.is_retracting = True
                self.retraction_progress = 0.0
                return
            
            # Check if hook went out of bounds
            if not (0 <= self.hook_x < SCREEN_W and 0 <= self.hook_y < SCREEN_H):
                self.is_thrown = False
                self.is_retracting = True
                self.retraction_progress = 0.0
                return
            
            # Check if hook hits any items
            hook_rect = pygame.Rect(self.hook_x - FISHING_ROD["hook_collision_radius"], 
                                    self.hook_y - FISHING_ROD["hook_collision_radius"], 
                                    FISHING_ROD["hook_collision_radius"] * 2, 
                                    FISHING_ROD["hook_collision_radius"] * 2)
            for item in dropped_items:
                item_rect = pygame.Rect(item.x, item.y, 16, 16)
                if hook_rect.colliderect(item_rect):
                    self.caught_item = item
                    self.caught_item_x = item.x
                    self.caught_item_y = item.y
                    dropped_items.remove(item)
                    self.is_thrown = False
                    self.is_retracting = True
                    self.retraction_progress = 0.0
                    return
        
        # RETRACTION PHASE
        elif self.is_retracting:
            self.retraction_progress += 1.0 / self.retraction_time_frames
            
            if self.retraction_progress >= 1.0:
                self.is_retracting = False
                self.retraction_progress = 0.0
                self.fishing_cooldown = self.fishing_cooldown_duration
                return
            
            # Ease-out quadratic: t = 1 - (1 - p)^2
            eased_progress = 1.0 - ((1.0 - self.retraction_progress) ** 2)
            
            # Pull hook to CURRENT player position, not cast position
            self.hook_x = self.hook_x + (player_x - self.hook_x) * eased_progress
            self.hook_y = self.hook_y + (player_y - self.hook_y) * eased_progress

    def draw_casting_ui(self, screen, player_x, player_y):
        """Draw the casting power bar at bottom of screen."""
        if not self.is_casting:
            return
        
        bar_width = FISHING_ROD["cast_bar_width"]
        bar_height = FISHING_ROD["cast_bar_height"]
        bar_x = (SCREEN_W - bar_width) // 2
        bar_y = SCREEN_H - FISHING_ROD["cast_bar_offset_y"]
        
        pygame.draw.rect(screen, COLORS["fishing_rod_cast_bar_background"], (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, COLORS["fishing_rod_cast_bar_outline"], (bar_x, bar_y, bar_width, bar_height), 2)
        
        fill_width = bar_width * self.cast_bar_fill
        pygame.draw.rect(screen, COLORS["fishing_rod_cast_bar_fill"], (bar_x, bar_y, fill_width, bar_height))

    def draw(self, screen, player_x, player_y):
        """Render the hook, line, and caught item when fishing."""
        if not self.is_thrown and not self.is_retracting:
            return
        
        pygame.draw.line(screen, COLORS["fishing_rod_line"], (player_x, player_y), 
                        (self.hook_x, self.hook_y), FISHING_ROD["line_width"])
        
        pygame.draw.circle(screen, COLORS["fishing_rod_hook"], (int(self.hook_x), int(self.hook_y)), 
                          FISHING_ROD["hook_radius"])
        pygame.draw.circle(screen, COLORS["fishing_rod_hook_outline"], (int(self.hook_x), int(self.hook_y)), 
                          FISHING_ROD["hook_radius"], 1)
        
        if self.is_retracting and self.caught_item:
            eased_progress = 1.0 - ((1.0 - self.retraction_progress) ** 2)
            item_x = self.caught_item_x + (player_x - self.caught_item_x) * eased_progress
            item_y = self.caught_item_y + (player_y - self.caught_item_y) * eased_progress
            
            item_rect = pygame.Rect(item_x, item_y, 16, 16)
            pygame.draw.rect(screen, self.caught_item.color, item_rect)
            pygame.draw.rect(screen, COLORS["dropped_item_outline"], item_rect, 1)

    def check_if_hook_hits_item(self, hook_x, hook_y, dropped_items):
        """Check if hook collides with any dropped items (now handled in update_hook)."""
        hook_rect = pygame.Rect(hook_x - FISHING_ROD["hook_collision_radius"], 
                                hook_y - FISHING_ROD["hook_collision_radius"], 
                                FISHING_ROD["hook_collision_radius"] * 2, 
                                FISHING_ROD["hook_collision_radius"] * 2)
        for item in dropped_items:
            item_rect = pygame.Rect(item.x, item.y, 16, 16)
            if hook_rect.colliderect(item_rect):
                return item
        return None

    def get_caught_item(self):
        """Return and clear the caught item."""
        item = self.caught_item
        self.caught_item = None
        return item
    
    def can_cast(self):
        """Check if enough time has passed since last fishing attempt."""
        return self.fishing_cooldown <= 0

    def update(self):
        """Call this every frame to update cooldowns."""
        if self.fishing_cooldown > 0:
            self.fishing_cooldown -= 1

