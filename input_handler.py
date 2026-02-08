"""Tega class-a nisem sam napisal, ampak sem ga našel na internetu. Nisem prepričan,
 kdo je avtor, ampak mislim, da je nekdo delil ta InputHandler razred kot del tutoriala
"""
import pygame

class InputHandler:
    def __init__(self):
        self.keys_pressed = None
        self.keys_just_pressed = set()
        self.mouse_just_clicked = set()
    
    def update(self):
        """Call this once per frame to update input states."""
        self.keys_pressed = pygame.key.get_pressed()
        self.keys_just_pressed = set()
        self.mouse_just_clicked = set()
    
    def handle_event(self, event):
        """Call this for each pygame event."""
        if event.type == pygame.KEYDOWN:
            self.keys_just_pressed.add(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_just_clicked.add(event.button)
    
    # --- KEYBOARD CHECKS ---
    def is_key_pressed(self, key):
        """Check if key is currently held down."""
        if self.keys_pressed is None:
            return False
        return self.keys_pressed[key]
    
    def is_key_just_pressed(self, key):
        """Check if key was just pressed this frame."""
        return key in self.keys_just_pressed
    
    def get_movement_input(self):
        """Returns a normalized movement vector."""
        move = pygame.math.Vector2(0, 0)
        if self.is_key_pressed(pygame.K_a):
            move.x = -1
        if self.is_key_pressed(pygame.K_d):
            move.x = 1
        if self.is_key_pressed(pygame.K_w):
            move.y = -1
        if self.is_key_pressed(pygame.K_s):
            move.y = 1
        
        if move.length_squared() > 0:
            move = move.normalize()
        
        return move
    
    # --- MOUSE CHECKS ---
    def is_mouse_just_clicked(self, button):
        """Check if mouse button was just clicked this frame."""
        return button in self.mouse_just_clicked
    
    def get_mouse_pos(self):
        """Get current mouse position."""
        return pygame.mouse.get_pos()
    
    def get_modifiers(self):
        """Get currently held modifier keys."""
        return pygame.key.get_mods()
    
    def is_shift_held(self):
        """Check if Shift is currently held."""
        return self.get_modifiers() & pygame.KMOD_SHIFT
    
    def is_ctrl_held(self):
        """Check if Ctrl is currently held."""
        return self.get_modifiers() & pygame.KMOD_CTRL
    
    def is_alt_held(self):
        """Check if Alt is currently held."""
        return self.get_modifiers() & pygame.KMOD_ALT