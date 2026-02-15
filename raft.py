import pygame
import random  # <-- Add this import
from settings import ITEM_DATA, TILE_DATA, TILE_SIZE, SCREEN_W, SCREEN_H, COLORS, GRID_W, GRID_H


class RaftTile:
    def __init__(self, grid_x, grid_y, type=None, durability=None, color=None):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.type = type
        self.durability = durability
        self.max_durability = durability  # Store the initial HP
        self.color = color

    def draw(self, screen):
        x = self.grid_x * TILE_SIZE
        y = self.grid_y * TILE_SIZE
        
        # 1. Draw the base tile
        pygame.draw.rect(screen, self.color, (x, y, TILE_SIZE, TILE_SIZE))

        # 2. Calculate Damage State
        if self.durability < self.max_durability:
            health_pct = self.durability / self.max_durability
            
            # State 1: Slightly Damaged (between 33% and 66% health)
            if 0.33 < health_pct <= 0.66:
                self._draw_cracks(screen, x, y, intensity=1)
            
            # State 2: Hardly Damaged (under 33% health)
            elif health_pct <= 0.33:
                self._draw_cracks(screen, x, y, intensity=2)

    def _draw_cracks(self, screen, x, y, intensity):
        crack_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        crack_color = (0, 0, 0, 180) # Dark, semi-transparent black
        p = TILE_SIZE // 8 
        
        # State 1: A few jagged points
        points = [
            (2*p, 2*p), (3*p, 3*p), (5*p, 2*p), 
            (6*p, 5*p), (3*p, 6*p), (4*p, 4*p)
        ]
        
        # State 2: Connect the points and add more for 'Hardly Damaged'
        if intensity == 2:
            points += [
                (p, 4*p), (4*p, p), (7*p, 7*p), 
                (p, 7*p), (7*p, p), (4*p, 7*p)
            ]

        for px, py in points:
            thick = max(2, TILE_SIZE // 16)
            pygame.draw.rect(crack_surf, crack_color, (px, py, thick, thick))
            
            # Optional: Add a tiny 'branch' to each point to make it look jagged
            pygame.draw.rect(crack_surf, crack_color, (px + thick, py + thick, thick, thick))

        screen.blit(crack_surf, (x, y))

class Raft:
    def __init__(self,size,grid_x,grid_y):
        self.size = size
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.tiles = {}

    def add_tile(self, world_x, world_y, tile):
        # bounds check in world grid
        if not (0 <= world_x < GRID_W and 0 <= world_y < GRID_H):
            return False

        # Build RaftTile instance
        if isinstance(tile, RaftTile):
            t = tile
        else:
            tile_name = tile if tile is not None else "Wet Wood"
            if tile_name not in TILE_DATA:
                raise KeyError(f"Unknown tile_name: {tile_name}")
            t = RaftTile(world_x, world_y, **TILE_DATA[tile_name])

        key = (world_x, world_y)

        # If tile already exists at key, overwrite
        if key in self.tiles:
            self.tiles[key] = t
            return True

        # If no tiles exist, allow placement anywhere
        if not self.tiles:
            self.tiles[key] = t
            return True

        # Otherwise require adjacency to existing tiles
        neighbors = [(world_x + 1, world_y), (world_x - 1, world_y), (world_x, world_y + 1), (world_x, world_y - 1)]
        for n in neighbors:
            if n in self.tiles:
                self.tiles[key] = t
                return True

        # Not adjacent, reject placement
        return False

    def create_initial_raft(self):
        # Create a square block of tiles starting at (grid_x, grid_y)
        for y in range(self.size):
            for x in range(self.size):
                wx = self.grid_x + x
                wy = self.grid_y + y
                self.add_tile(wx, wy, "Dry Wood")

    def draw(self,screen):
        for t in self.tiles.values():
            t.draw(screen)

    def grid_render(self, screen, highlight_pos=None):
        positions = set(self.tiles.keys())
        neighbours = set()
        for (x, y) in positions:
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < GRID_W and 0 <= ny < GRID_H and (nx, ny) not in positions:
                    neighbours.add((nx, ny))

        # Combine positions to render (existing tiles + possible expansion cells)
        render_positions = positions.union(neighbours)

        for (x, y) in render_positions:
            world_x = x * TILE_SIZE
            world_y = y * TILE_SIZE
            rect = pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (255, 255, 255), rect, 1)

        # Highlight hovered cell if provided and in render_positions
        if highlight_pos is not None:
            hx, hy = highlight_pos
            if (hx, hy) in render_positions:
                world_x = hx * TILE_SIZE
                world_y = hy * TILE_SIZE
                highlight_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                highlight_surf.fill((255, 255, 255, 64))
                screen.blit(highlight_surf, (world_x, world_y))
                pygame.draw.rect(screen, (255, 255, 255), (world_x, world_y, TILE_SIZE, TILE_SIZE), 3)

    def can_place(self, world_x, world_y):
        if len(self.tiles) >= 30:
            return False
        
        if not (0 <= world_x < GRID_W and 0 <= world_y < GRID_H):
            return False

        key = (world_x, world_y)
        # existing tile can be overwritten
        if key in self.tiles:
            return True

        # if no tiles exist, allow placement anywhere
        if not self.tiles:
            return True

        # require adjacency to at least one existing tile
        neighbors = [(world_x + 1, world_y), (world_x - 1, world_y), (world_x, world_y + 1), (world_x, world_y - 1)]
        for n in neighbors:
            if n in self.tiles:
                return True
        return False

    def get_center_tile(self):
        if not self.tiles:
            return None

        xs = [p[0] for p in self.tiles.keys()]
        ys = [p[1] for p in self.tiles.keys()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2

        candidate = (center_x, center_y)
        if candidate in self.tiles:
            return candidate

        # Find nearest existing tile (Manhattan distance, tie-breaker: Euclidean)
        def dist_key(p):
            manh = abs(p[0] - center_x) + abs(p[1] - center_y)
            eucl = (p[0] - center_x) ** 2 + (p[1] - center_y) ** 2
            return (manh, eucl)

        nearest = min(self.tiles.keys(), key=dist_key)
        return nearest

    def damage_tile(self, world_x, world_y, damage_amount):
        """Reduce a tile's durability by damage_amount. Remove if durability <= 0."""
        key = (world_x, world_y)
        if key not in self.tiles:
            return False
        
        tile = self.tiles[key]
        tile.durability -= damage_amount
        
        if tile.durability <= 0:
            del self.tiles[key]
            return True  # Tile destroyed
        
        return False  # Tile damaged but survived
