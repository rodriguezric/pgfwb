import functools
import settings
import os

import pygame

def spritesheet_animation_gen(file, cells, frames, tile_size, loop=True):
    """
    Spritesheet Animation Generator

    Spritesheets are horizontal sheets with the height of tile_size and
    width tile_size * cells. A spritesheet generator will offset the 
    spritesheet by the tile_size to the left (-cell_idx * tile_size)
    for each cell in the spritesheet.

    The frames parm determines how many times it will yield the surf
    for the cell. This is meant to be called every clock tick, so it
    will animate at the speed of the framerate of the caller.
    """
    _loop = True

    while _loop:
        spritesheet = pygame.image.load(file).convert_alpha()
        surf = pygame.Surface((tile_size, tile_size)).convert_alpha()

        for cell_idx in range(cells):
            surf.fill(pygame.Color(0, 0, 0, 0))
            surf.blit(spritesheet, (-cell_idx *tile_size, 0))
            for _ in range(frames):
                yield surf

        _loop = loop

class AnimationManager:
    def __init__(self, folder, frames=8):
        self.folder = f"animations/{folder}"
        self.animations = {}
        self.frames = frames
        self._animation = None
        self.animation_name = None

        for filename in os.listdir(self.folder):
            spritesheet_file = f"{self.folder}/{filename}"

            width, tile_size = pygame.image \
                                     .load(spritesheet_file) \
                                     .get_size()

            cells = width // tile_size

            animation_name = filename.split("-")[-1] \
                                     .split(".")[0]

            self.animation_name = animation_name

            self.animations[animation_name] = functools.partial(
                spritesheet_animation_gen,
                file=spritesheet_file,
                cells=cells,
                frames=self.frames,
                tile_size=tile_size
            )

            if not self._animation:
                self.animation = animation_name
            

    def next(self):
        return next(self.animation)

    @property
    def animation(self):
        return self._animation

    @animation.setter
    def animation(self, animation_name):
        self.animation_name = animation_name
        self._animation = self.animations[animation_name]()

