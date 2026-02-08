import pygame

SCREEN_W, SCREEN_H = 1024, 640

COLORS = {
    # World & Entity
    "background": (135, 206, 235),
    "player": (220, 40, 40),

    # Health Bar (Bold Red)
    "health_bar": (220, 40, 40),
    "health_bar_background": (60, 20, 20),
    "health_bar_outline": (20, 20, 20),
    "health_bar_text_color": (255, 255, 255),

    # Hunger Bar (Amber/Gold)
    "hunger_bar": (240, 180, 40),
    "hunger_bar_background": (40, 40, 20),
    "hunger_bar_outline": (20, 20, 20),
    "hunger_bar_text_color": (255, 255, 255),

    # Thirst Bar (Deep Sky Blue)
    "thirst_bar": (40, 140, 240),
    "thirst_bar_background": (15, 30, 50),
    "thirst_bar_outline": (20, 20, 20),
    "thirst_bar_text_color": (255, 255, 255),

    # Inventory UI
    "draw_item_count": (240, 230, 200),
    "slot_background": (80, 50, 30),
    "slot_forground": (120, 80, 50),
    "inventory_background_background": (101, 67, 33),
    "inventory_background_forground": (160, 120, 80),
    "inventory_head_text": (100, 100, 100),
    "inventory_hover_text": (255, 220, 100),

    # Items
    "dropped_item_outline" : (255, 255, 255),

    # Item Colors
    "red": (220, 40, 40),
    "yellow": (240, 180, 40),
    "blue": (40, 140, 240), # Added for water items

    # General Colors
    "black": (0, 0, 0),
    "gray": (50, 50, 50),
    "white": (255, 255, 255),

}

FONTS = {
    "large": pygame.font.SysFont("monospace", 20, bold=True),
    "small": pygame.font.SysFont("monospace", 16, bold=True),
}


ITEM_DATA = {
    "Apple": {"name": "Apple", "type" : "consumable", "color": COLORS["red"], "health_restore": 10, "hunger_restore": 0, "thirst_restore": 0, "speed_boost": 0},
    "Banana": {"name": "Banana", "type" : "consumable", "color": COLORS["yellow"], "health_restore": 0, "hunger_restore": 15, "thirst_restore": 0, "speed_boost": 0},
    "Water Bottle": {"name": "Water Bottle", "type" : "consumable", "color": COLORS["blue"], "health_restore": 0, "hunger_restore": 0, "thirst_restore": 30, "speed_boost": 0},
}