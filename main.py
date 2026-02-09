import pygame
pygame.init()
import random
from settings import ITEM_DATA, TILE_DATA, GRID_H, GRID_W, SCREEN_W, SCREEN_H, COLORS, TILE_SIZE, FONTS
from sprites import Character
from inventory import Inventory, Item
from input_handler import InputHandler
from raft import Raft, RaftTile


# Setup Display
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Survival Game")
clock = pygame.time.Clock()

# Initialize Game Objects
input_handler = InputHandler()
# Character params: x, y, width, height, health, max_health, hunger, max_hunger, thirst, max_thirst, speed, inventory_obj
player = Character(SCREEN_W//2, SCREEN_H//2, 20, 20, 100, 100, 100, 100, 80, 100, 5, Inventory())
dropped_items = []

# Initialize Raft
raft_initial_size = 3
raft = Raft(size=3, grid_x=GRID_W // 2 - raft_initial_size // 2, grid_y= GRID_H // 2 - raft_initial_size // 2)
raft.create_initial_raft()

# Starting Items
player.inv.add_item(Item(**ITEM_DATA["Apple"]), 3)
player.inv.add_item(Item(**ITEM_DATA["Banana"]), 3)
player.inv.add_item(Item(**ITEM_DATA["Water Bottle"]), 3)
player.inv.add_item(Item(**ITEM_DATA["Wet Wood"]), 5)
player.inv.add_item(Item(**ITEM_DATA["Dry Wood"]), 5)

# Main game loop
running = True
while running:
    # 1. Reset 'just pressed' states for this frame
    input_handler.update() 

    # 2. Feed events into the handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        input_handler.handle_event(event)

    # 3. Handle Inventory Toggle (TAB)
    if input_handler.is_key_just_pressed(pygame.K_TAB):
        player.inv.is_open = not player.inv.is_open
        # Safety: if closing inventory, stop dragging
        if not player.inv.is_open:
            player.inv.dragging_item = None

    # 4. Handle Logic
    # Calculate grid positions (Needed for mouse collision math)
    bg_width = 8 * (80 + 12) + 12
    bg_height = 4 * (80 + 12) + 12
    grid_x = (SCREEN_W - bg_width) // 2
    grid_y = (SCREEN_H - bg_height) // 2

    # Handle input: normally when inventory is open, but also when placement
    # is active so left/right click work while inventory is closed.
    if player.inv.is_open or player.inv.placement_active:
        new_drop = player.inv.handle_input(input_handler, player, grid_x, grid_y, raft)
        if new_drop:
            dropped_items.append(new_drop)
    else:
        # Only move if inventory is closed
        move_vec = input_handler.get_movement_input()
        player.apply_movement(move_vec)
        # Check raft occupancy after movement. If player is NOT on the raft,
        # teleport them to the raft's center (or nearest tile) and subtract 10 HP,
        # but only once per cooldown period.
        try:
            if raft and not player.is_on_raft(raft):
                center = raft.get_center_tile()
                if center is not None:
                    center_x, center_y = center
                    # center in pixels, position player so their center matches tile center
                    pixel_x = int(center_x * TILE_SIZE + TILE_SIZE / 2 - player.w / 2)
                    pixel_y = int(center_y * TILE_SIZE + TILE_SIZE / 2 - player.h / 2)
                    player.x = pixel_x
                    player.y = pixel_y
                    player.rect.topleft = (player.x, player.y)

                # apply damage only if cooldown expired
                now = pygame.time.get_ticks()
                if now >= getattr(player, "off_cooldown_end", 0):
                    player.health -= 10
                    # mark player 'off' briefly to avoid repeated damage
                    try:
                        player.mark_off(1000)
                    except Exception:
                        player.off_cooldown_end = now + 1000
        except Exception:
            pass
    


    # --- Rendering ---
    screen.fill(COLORS["background"])
    
    # 1. Render raft tiles in the world
    raft.draw(screen)

    # If player is placing a raft tile from inventory, render grid overlay
    if player.inv.placement_active:
        mx, my = pygame.mouse.get_pos()
        tile_x = mx // TILE_SIZE
        tile_y = my // TILE_SIZE
        raft.grid_render(screen, highlight_pos=(tile_x, tile_y))
        # Draw ghost preview of the tile at the hovered world tile
        item_name = player.inv.placement_item_name or ""
        # Resolve color from TILE_DATA or ITEM_DATA
        color = None
        if item_name in TILE_DATA:
            color = TILE_DATA[item_name].get("color")
        elif item_name in ITEM_DATA:
            color = ITEM_DATA[item_name].get("color")

        if color is not None:
            valid = raft.can_place(tile_x, tile_y)
            ghost_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            # greenish for valid, reddish for invalid; include some transparency
            if valid:
                ghost_surf.fill((color[0], color[1], color[2], 160))
                border_col = (0, 255, 0)
            else:
                ghost_surf.fill((color[0], color[1], color[2], 80))
                border_col = (255, 0, 0)
            screen.blit(ghost_surf, (tile_x * TILE_SIZE, tile_y * TILE_SIZE))
            pygame.draw.rect(screen, border_col, (tile_x * TILE_SIZE, tile_y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 3)

        # Draw a tooltip near the mouse indicating placement instructions
        try:
            text = f"Placing: {item_name} — Left click to place, Right click to cancel"
            txt_surf = FONTS["small"].render(text, True, (255, 255, 255))
            padding_x, padding_y = 8, 6
            bg = pygame.Surface((txt_surf.get_width() + padding_x * 2, txt_surf.get_height() + padding_y * 2), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 180))
            tx = mx + 16
            ty = my + 16
            screen.blit(bg, (tx, ty))
            screen.blit(txt_surf, (tx + padding_x, ty + padding_y))
        except Exception:
            pass

    # 2. Render dropped items in the world
    for dropped_item in dropped_items[:]:
        dropped_item.draw_in_world(screen, player.inv.is_open)
        if dropped_item.check_pickup(player):
            dropped_items.remove(dropped_item)

    # 3. Render player and HUD
    player.draw(screen)
    player._draw_hud(screen)

    # 4. Render Inventory UI on top
    if player.inv.is_open:
        player.inv._render(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()