import pygame
pygame.init()
import random
from settings import ITEM_DATA, SCREEN_W, SCREEN_H, COLORS
from sprites import Character
from inventory import Inventory, Item
from input_handler import InputHandler


# Setup Display
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Survival Game")
clock = pygame.time.Clock()

# Initialize Game Objects
input_handler = InputHandler()
# Character params: x, y, width, height, health, max_health, hunger, max_hunger, thirst, max_thirst, speed, inventory_obj
player = Character(SCREEN_W//2, SCREEN_H//2, 20, 20, 100, 100, 100, 100, 80, 100, 5, Inventory())
dropped_items = []

# Starting Items
player.inv.add_item(Item(**ITEM_DATA["Apple"]), 3)
player.inv.add_item(Item(**ITEM_DATA["Banana"]), 3)
player.inv.add_item(Item(**ITEM_DATA["Water Bottle"]), 3)

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
    if player.inv.is_open:
        # Calculate grid positions (Needed for mouse collision math)
        bg_width = 8 * (80 + 12) + 12
        bg_height = 4 * (80 + 12) + 12
        grid_x = (SCREEN_W - bg_width) // 2
        grid_y = (SCREEN_H - bg_height) // 2
        
        # This one line handles: 
        # - Left Click: Dragging/Moving
        # - Right Click: Consuming
        # - Q Key: Dropping
        new_drop = player.inv.handle_input(input_handler, player, grid_x, grid_y)
        
        if new_drop:
            dropped_items.append(new_drop)
    else:
        # Only move if inventory is closed
        move_vec = input_handler.get_movement_input()
        player.apply_movement(move_vec)
    

    # --- Rendering ---
    screen.fill(COLORS["background"])
    
    # 1. Render dropped items in the world
    for dropped_item in dropped_items[:]:
        dropped_item.draw_in_world(screen, player.inv.is_open)
        if dropped_item.check_pickup(player):
            dropped_items.remove(dropped_item)

    # 2. Render player and HUD
    player.draw(screen)
    player._draw_hud(screen)

    # 3. Render Inventory UI on top
    if player.inv.is_open:
        player.inv._render(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()