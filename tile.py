'''
The Tile module handles the organization and management of individual tiles and groups of tiles. 

This module is designed to be used by higher-level modules for various game types, such as platformers or top-down games.

Design choices:
    - Positions are 2-value tuples
'''
import pygame
import settings

class Tile:
    '''
    Models a Tile object. Children implement the graphics.
    '''
    def __init__(self, pos=(0, 0)):
        self.surf = pygame.Surface((settings.TILESIZE, settings.TILESIZE))
        self.rect = self.surf.get_rect()
        self.rect.x, self.rect.y = list(map(int, pos))
        self.pos = pos

    @property
    def blit_args(self):
        return (self.surf, self.rect)

    def render(self, target):
        target.blit(*self.blit_args)

    def recalc_rect(self):
        '''
        Rects are integer only. If we move a fraction of a pixel on our pos
        we want to preserve the amount we traveled rather than truncating
        it by directly working with the rect
        '''
        self.rect = pygame.Rect(
            int(*self.pos), 
            (settings.TILESIZE, settings.TILESIZE)
        )

class ColorTile(Tile):
    def __init__(self, color='white', **kwargs):
        super().__init__(**kwargs)
        self.color = color
        self.surf.fill(color)

class GraphicTile(Tile):
    def __init__(self, image):
        super().__init__(**kwargs)
        # load an image for the surf, it is expected to be settngs.TILESIZE dims
        ...
