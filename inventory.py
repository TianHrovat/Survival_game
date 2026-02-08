import pygame
import random
from settings import COLORS, ITEM_DATA, SCREEN_W, SCREEN_H, FONTS

class Item:
    def __init__(self, name, color, health_restore=0, hunger_restore=0, thirst_restore=0, speed_boost=0):
        self.name = name
        self.count = 0
        self.color = color
        self.health_restore = health_restore
        self.hunger_restore = hunger_restore
        self.thirst_restore = thirst_restore
        self.speed_boost = speed_boost    

    def render(self, screen, x, y):
        pygame.draw.rect(screen, self.color, (x,y,16,16))
        
        
class DroppedItem(Item):
    def __init__(self, name, count, color, x, y):
        super().__init__(name, color)
        self.count = count
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, 16, 16)

        # Timer logic
        self.spawn_time = None  # We don't set this yet!
        self.pickup_cooldown = 2000

    def draw_in_world(self, surface, inventory_is_open):
        # 1. Logic: Start the timer ONLY when inventory is closed for the first time
        if self.spawn_time is None and not inventory_is_open:
            self.spawn_time = pygame.time.get_ticks()

        pygame.draw.rect(surface, self.color, self.rect)
        
        # 2. Only show outline if timer has started AND cooldown has passed
        if self.spawn_time is not None:
            if pygame.time.get_ticks() - self.spawn_time > self.pickup_cooldown:
                pygame.draw.rect(surface, COLORS["dropped_item_outline"], self.rect, 1)

    def check_pickup(self, player):
        # If inventory is open, we can't pick up items anyway
        if player.inv.is_open:
            return False

        # If the timer hasn't started yet (inventory was never closed), return
        if self.spawn_time is None:
            return False

        now = pygame.time.get_ticks()
        if now - self.spawn_time > self.pickup_cooldown:
            collide_rect = self.rect.inflate(10, 10)
            if player.rect.colliderect(collide_rect):
                stats = ITEM_DATA.get(self.name, {})
                
                new_item = Item(
                    name=self.name, 
                    color=self.color, 
                    hunger_restore=stats.get("hunger_restore", 0),
                    health_restore=stats.get("health_restore", 0),
                    thirst_restore=stats.get("thirst_restore", 0), # Added thirst back in
                    speed_boost=stats.get("speed_boost", 0)
                )
                
                player.inv.add_item(new_item, self.count)
                return True
        return False
dropped_items = []

class Inventory:
    def __init__(self):
        self.capacity = 32 # 8 columns * 4 rows
        self.items = [None] * self.capacity 
        self.is_open = False
        
        # Drag and drop properties
        self.dragging_item = None
        self.dragging_from_index = None
        self.drag_offset = (0, 0)

    def add_item(self, item_obj, count):
        # First, try to stack with existing item
        for i in range(self.capacity):
            if self.items[i] and self.items[i].name == item_obj.name:
                self.items[i].count += count
                return True
        
        # If no stack, find first empty slot
        for i in range(self.capacity):
            if self.items[i] is None:
                item_obj.count = count
                self.items[i] = item_obj
                return True
        return False # Inventory full

    def handle_input(self, input_handler, player, grid_x, grid_y):
        mouse_pos = pygame.mouse.get_pos()
        hovered_idx = self._get_hovered_slot_index(grid_x, grid_y)

        # START DRAGGING (Left Click Down)
        if input_handler.is_mouse_just_clicked(1): # Left click
            if hovered_idx is not None and self.items[hovered_idx]:
                self.dragging_item = self.items[hovered_idx]
                self.dragging_from_index = hovered_idx
                # Calculate offset so item doesn't "snap" to top-left of mouse
                slot_rect = self._get_slot_rect(grid_x, grid_y, hovered_idx // 8, hovered_idx % 8)
                self.drag_offset = (mouse_pos[0] - slot_rect.x, mouse_pos[1] - slot_rect.y)
                self.items[hovered_idx] = None # Temporarily remove from slot

        # STOP DRAGGING (Left Click Up)
        if not pygame.mouse.get_pressed()[0] and self.dragging_item:
            if hovered_idx is not None:
                # Swap items if something is already there
                temp = self.items[hovered_idx]
                self.items[hovered_idx] = self.dragging_item
                if temp: # If we swapped, put the old item back where we started
                    self.items[self.dragging_from_index] = temp
            else:
                # Return to original slot if dropped outside
                self.items[self.dragging_from_index] = self.dragging_item
            
            self.dragging_item = None
            self.dragging_from_index = None

        # CONSUME (Right Click)
        if input_handler.is_mouse_just_clicked(3): # Right Click
            if hovered_idx is not None and self.items[hovered_idx]:
                self._consume_item(hovered_idx, player)

        # DROP (Q Key)
        if input_handler.is_key_just_pressed(pygame.K_q):
            if hovered_idx is not None and self.items[hovered_idx]:
                item = self.items[hovered_idx]
                new_drop = self._drop_item(hovered_idx, 1, player.x, player.y)
                return new_drop
        return None

    def _render(self, screen):
        COLS, ROWS = 8, 4
        SLOT_SIZE, PADDING = 80, 12
        bg_width = COLS * (SLOT_SIZE + PADDING) + PADDING
        bg_height = ROWS * (SLOT_SIZE + PADDING) + PADDING
        grid_x = (SCREEN_W - bg_width) // 2
        grid_y = (SCREEN_H - bg_height) // 2

        # Draw Backgrounds
        pygame.draw.rect(screen, COLORS["inventory_background_background"], (grid_x, grid_y, bg_width, bg_height))
        pygame.draw.rect(screen, COLORS["inventory_background_forground"], (grid_x, grid_y, bg_width, bg_height), 4)

        # Dynamic Header
        hovered_idx = self._get_hovered_slot_index(grid_x, grid_y)
        hovered_item = self.items[hovered_idx] if hovered_idx is not None else None
        display_text = hovered_item.name.upper() if hovered_item else "INVENTORY"
        self._draw_dynamic_header(screen, display_text, grid_x, grid_y, bg_width)

        # Draw Slots
        for i in range(self.capacity):
            row, col = i // 8, i % 8
            slot_rect = self._get_slot_rect(grid_x, grid_y, row, col)
            pygame.draw.rect(screen, COLORS["slot_background"], slot_rect)
            pygame.draw.rect(screen, COLORS["slot_forground"], slot_rect, 2)

            item = self.items[i]
            if item:
                self._draw_item_icon(screen, item, slot_rect)

        # Draw Dragging Item
        if self.dragging_item:
            m_x, m_y = pygame.mouse.get_pos()
            drag_rect = pygame.Rect(m_x - self.drag_offset[0], m_y - self.drag_offset[1], 80, 80)
            self._draw_item_icon(screen, self.dragging_item, drag_rect)

    def _draw_item_icon(self, screen, item, rect):
        item_surface = pygame.Surface((16, 16))
        item_surface.fill(item.color)
        scaled = pygame.transform.scale(item_surface, (48, 48))
        screen.blit(scaled, (rect.x + 16, rect.y + 12))
        self._draw_item_count(screen, item, rect)

    def _get_hovered_slot_index(self, grid_x, grid_y):
        mouse_pos = pygame.mouse.get_pos()
        for i in range(self.capacity):
            if self._get_slot_rect(grid_x, grid_y, i // 8, i % 8).collidepoint(mouse_pos):
                return i
        return None

    def _drop_item(self, index, count, x, y):
        item = self.items[index]
        dropped_obj = DroppedItem(item.name, count, item.color, x + random.randint(-20, 20), y + random.randint(-20, 20))
        item.count -= count
        if item.count <= 0:
            self.items[index] = None
        return dropped_obj

    def _consume_item(self, index, player):
        item = self.items[index]
        # ... (same logic as before, just using item from list)
        can_use = (item.health_restore > 0 and player.health < player.max_health) or \
                  (item.hunger_restore > 0 and player.hunger < player.max_hunger) or \
                  (item.thirst_restore > 0 and player.thirst < player.max_thirst)
        
        if can_use:
            player.health = min(player.max_health, player.health + item.health_restore)
            player.hunger = min(player.max_hunger, player.hunger + item.hunger_restore)
            player.thirst = min(player.max_thirst, player.thirst + item.thirst_restore)
            item.count -= 1
            if item.count <= 0:
                self.items[index] = None
            return True
        return False
    
    def _draw_dynamic_header(self, screen, text_str, grid_x, grid_y, bg_width):
        # Determine color: Gold if it's an item name, White/Gray if it's just "INVENTORY"
        text_color = (255, 220, 100) if text_str != "INVENTORY" else COLORS.get("inventory_head_text", (200, 200, 200))
        
        # Use your defined font
        text_surf = FONTS["large"].render(text_str, True, text_color)
        
        # Header Box Dimensions
        h_padding = 40 
        header_w = text_surf.get_width() + h_padding
        header_h = 44
        
        # Position: Centered above the inventory main box
        header_x = grid_x + (bg_width - header_w) // 2
        header_y = grid_y - header_h + 4 # Slight overlap for aesthetic
        
        header_rect = pygame.Rect(header_x, header_y, header_w, header_h)
        
        # Draw the Plaque (Background and Border)
        pygame.draw.rect(screen, COLORS["inventory_background_background"], header_rect)
        pygame.draw.rect(screen, COLORS["inventory_background_forground"], header_rect, 4)
        
        # Center the text inside the plaque
        text_x = header_rect.centerx - (text_surf.get_width() // 2)
        text_y = header_rect.centery - (text_surf.get_height() // 2)
        screen.blit(text_surf, (text_x, text_y))

    def _draw_item_count(self, screen, item, slot_rect):
        count_str = str(item.count)
        # Scale font size based on digit count
        size = 42 if len(count_str) == 1 else 32 if len(count_str) == 2 else 24
        
        font = pygame.font.Font(None, size)
        count_text = font.render(count_str, True, COLORS.get("draw_item_count", (255, 255, 255)))
        
        # Bottom-right corner alignment
        text_x = slot_rect.right - count_text.get_width() - 5
        text_y = slot_rect.bottom - count_text.get_height() - 5
        screen.blit(count_text, (text_x, text_y))

    def _get_slot_rect(self, grid_x, grid_y, row, col):
        SLOT_SIZE, PADDING = 80, 12
        slot_x = grid_x + PADDING + col * (SLOT_SIZE + PADDING)
        slot_y = grid_y + PADDING + row * (SLOT_SIZE + PADDING)
        return pygame.Rect(slot_x, slot_y, SLOT_SIZE, SLOT_SIZE)