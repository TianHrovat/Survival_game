import pygame
from settings import SCREEN_W, SCREEN_H, COLORS, TILE_SIZE, FONTS

class Character:
    def __init__(self, x, y, w, h, health, max_health, hunger, max_hunger, thirst, max_thirst, speed, inv):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = pygame.Rect(x, y, w, h)

        self.velx = 0
        self.vely = 0
        self.speed = speed

        # Survival Stats
        self.hunger = hunger
        self.max_hunger = max_hunger
        self.thirst = thirst
        self.max_thirst = max_thirst
        self.health = health
        self.max_health = max_health

        self.inv = inv

    def apply_movement(self, move_vec):
        """Receives a normalized vector from InputHandler and moves the player."""
        if move_vec.length_squared() > 0:
            # Multiply normalized direction by speed
            self.velx = move_vec.x * self.speed
            self.vely = move_vec.y * self.speed
        else:
            self.velx = 0
            self.vely = 0

        self.x += self.velx
        self.y += self.vely
        self.rect.topleft = (self.x, self.y)

    def mark_off(self, cooldown_ms=1000):
        """Mark the player as 'off' for cooldown_ms milliseconds."""
        self.feel_off = True
        try:
            self.off_cooldown_end = pygame.time.get_ticks() + int(cooldown_ms)
        except Exception:
            self.off_cooldown_end = 0

    def update_off_status(self):
        """Update off status; clear if cooldown has passed."""
        if self.feel_off:
            try:
                if pygame.time.get_ticks() >= self.off_cooldown_end:
                    self.feel_off = False
            except Exception:
                self.feel_off = False

    def is_on_raft(self, raft):
        player_center_x = self.x + self.w / 2
        player_center_y = self.y + self.h / 2

        # Convert player center to world grid coordinates using TILE_SIZE
        grid_x = int(player_center_x // TILE_SIZE)
        grid_y = int(player_center_y // TILE_SIZE)

        return (grid_x, grid_y) in raft.tiles


    def _draw_hud(self, surface):
        X_OFFSET = 30
        Y_OFFSET = 40
        
        HEALTH_W, HEALTH_H = 350, 24 
        HUNGER_W, HUNGER_H = 200, 12  
        THIRST_W, THIRST_H = 200, 12 # Same size as hunger

        # --- 1. HEALTH BAR ---
        hp_ratio = max(0, min(1, self.health / self.max_health))
        pygame.draw.rect(surface, COLORS["health_bar_outline"], (X_OFFSET - 3, Y_OFFSET - 3, HEALTH_W + 6, HEALTH_H + 6))
        pygame.draw.rect(surface, COLORS["health_bar_background"], (X_OFFSET, Y_OFFSET, HEALTH_W, HEALTH_H))
        pygame.draw.rect(surface, COLORS["health_bar"], (X_OFFSET, Y_OFFSET, HEALTH_W * hp_ratio, HEALTH_H))
        
        for i in range(1, 10):
            line_x = X_OFFSET + (HEALTH_W * i // 10)
            pygame.draw.line(surface, (0, 0, 0, 150), (line_x, Y_OFFSET), (line_x, Y_OFFSET + HEALTH_H - 1), 2)
            
        hp_text = FONTS["large"].render(f" HEALTH {int(self.health)}/{int(self.max_health)} ", True, COLORS["health_bar_text_color"])
        text_rect = hp_text.get_rect(bottomleft=(X_OFFSET, Y_OFFSET - 3))
        pygame.draw.rect(surface, COLORS["black"], text_rect)
        surface.blit(hp_text, text_rect)

        # --- 2. HUNGER BAR ---
        HG_X = X_OFFSET
        HG_Y = Y_OFFSET + HEALTH_H + 10 
        hg_ratio = max(0, min(1, self.hunger / self.max_hunger))

        pygame.draw.rect(surface, COLORS["hunger_bar_outline"], (HG_X - 2, HG_Y - 2, HUNGER_W + 4, HUNGER_H + 4))
        pygame.draw.rect(surface, COLORS["hunger_bar_background"], (HG_X, HG_Y, HUNGER_W, HUNGER_H))
        if hg_ratio > 0:
            pygame.draw.rect(surface, COLORS["hunger_bar"], (HG_X, HG_Y, HUNGER_W * hg_ratio, HUNGER_H))

        hg_text = FONTS["small"].render(f" FOOD {int(self.hunger)}% ", True, COLORS["hunger_bar_text_color"])
        hg_text_rect = hg_text.get_rect(topleft=(HG_X, HG_Y + HUNGER_H + 2))
        pygame.draw.rect(surface, COLORS["black"], hg_text_rect)
        surface.blit(hg_text, hg_text_rect)

        # --- 3. THIRST BAR ---
        # Positioned to the right of the Hunger Bar
        TH_X = X_OFFSET
        TH_Y = HG_Y + HUNGER_H + 20
        th_ratio = max(0, min(1, self.thirst / self.max_thirst))

        # Outline & Background
        pygame.draw.rect(surface, COLORS["thirst_bar_outline"], (TH_X - 2, TH_Y - 2, THIRST_W + 4, THIRST_H + 4))
        pygame.draw.rect(surface, COLORS["thirst_bar_background"], (TH_X, TH_Y, THIRST_W, THIRST_H))
        
        # Fill
        if th_ratio > 0:
            pygame.draw.rect(surface, COLORS.get("thirst_bar", (0, 0, 255)), (TH_X, TH_Y, THIRST_W * th_ratio, THIRST_H))

        # Text
        th_text = FONTS["small"].render(f" WATER {int(self.thirst)}% ", True, COLORS.get("thirst_bar_text_color", (255, 255, 255)))
        th_text_rect = th_text.get_rect(topleft=(TH_X, TH_Y + THIRST_H + 2))
        pygame.draw.rect(surface, COLORS["black"], th_text_rect)
        surface.blit(th_text, th_text_rect)

    def draw(self, surface):
        pygame.draw.rect(surface, COLORS["player"], self.rect)
        self._draw_hud(surface)