"""
The Tile module handles the organization and management of individual tiles and groups of tiles. 

This module is designed to be used by higher-level modules for various game types, such as platformers or top-down games.

Design choices:
    - pos are 2-value tuples representing x and y pixels on a screen
    - coord are 2-value tuple representing x and y positions on a map
        based on the TILESIZE value in settings
"""
import pgfwb
import pygame
import settings
import json
import itertools

def pos_to_coord(pos):
    return tuple(map(lambda x: int(x // settings.TILESIZE), pos))

def coord_to_pos(coord):
    return tuple(map(lambda x: int(x * settings.TILESIZE), coord))

adjacent_coords = tuple(itertools.product([-1, 0, 1], [-1, 0, 1]))
adjacent_poses = tuple(map(coord_to_pos, adjacent_coords))

class Tile:
    """
    Models a Tile object. Children implement the graphics.
    """
    def __init__(self, coord=(0, 0), detect_collision=True):
        self.surf = pygame.Surface((settings.TILESIZE, settings.TILESIZE))
        self.rect = self.surf.get_rect()
        self.coord = coord
        self.pos = coord_to_pos(coord)
        self.rect.x, self.rect.y = list(map(int, self.pos))
        self.detect_collision = detect_collision

    @property
    def blit_args(self):
        return (self.surf, self.rect)

    def render(self, target=pgfwb.ui.display, camera=None):
        if camera:
            target.blit(self.surf, camera.offset_rect(self.rect))
        else:
            target.blit(*self.blit_args)

    def recalc_rect(self):
        """
        Rects are integer only. If we move a fraction of a pixel on our pos
        we want to preserve the amount we traveled rather than truncating
        it by directly working with the rect
        """
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
    def __init__(self, filepath):
        super().__init__(**kwargs)
        self.surf = pygame.image.load(filepath).convert()

tile_classes = (
    ColorTile,
    GraphicTile,
)

tile_class_map = {cls.__name__: cls for cls in tile_classes}


class TileMap:
    """
    Object for holding tiles. Build from a JSON file.

    Data is:
        pos_str: {kwargs + tile_class}
    """
    def __init__(self, file=None):
        self.tiles = {}

        if file:
            self.load(file)

    def key_to_coord(self, key):
        """
        TileMap JSON keys are comma delimited pos strings
        """
        return tuple(map(int, key.split(",")))

    def render(self, target=pgfwb.ui.display, camera=None):
        for tile in self.tiles.values():
            tile.render(target, camera=camera)

    def add(self, coord, tile_partial):
        """
        tile_partial expects all the args for the tile class to 
        be filled except the coordition.

        e.g.
        green_tile = functools.partial(ColorTile, color=Green)
        """
        self.tiles[coord] = tile_partial(coord=coord)

    def remove(self, coord):
        if coord in self.tiles:
            del self.tiles[coord]

    def load(self, file):
        self.tiles = {}
        with open(file) as fp:
            for key, kwargs in json.load(fp).items():
                coord = self.key_to_coord(key)
                tile_class = tile_class_map[kwargs.pop('tile_class')]
                self.tiles[coord] = tile_class(coord=coord, **kwargs)

    def save(self, file):
        data = {}
        for coord, tile in self.tiles.items():
            key = ",".join(map(str, coord))
            tile_class = tile.__class__.__name__

            exclude_fields = ('surf', 'rect', 'coord', 'pos')
            kwargs = {k: v for k, v in tile.__dict__.items()
                      if k not in exclude_fields}
            
            kwargs['tile_class'] = tile_class

            data[key] = kwargs

        with open(file, 'w') as fp:
            json.dump(data, fp)

    def rects_around(self, pos):
        coord = pos_to_coord(pos)
        coords = [(coord[0] + adjacent_coord[0], coord[1] + adjacent_coord[1])
                 for adjacent_coord in adjacent_coords]

        return [tile.rect 
                for coord in coords 
                if (tile := self.tiles.get(coord))]

class Camera:
    def __init__(self, target, followx=True, followy=True, follow_rate=30):
        self.target = target
        self.followx = followx
        self.followy = followy
        self.follow_rate = max(min(follow_rate, 30), 1)

        self.pos = pygame.Vector2(
            x=target.rect.centerx - pgfwb.ui.display.get_width() / 2,
            y=target.rect.centery - pgfwb.ui.display.get_height() / 2
        )
        self.render_scroll = pygame.Vector2()

    def update(self):
        if self.followx:
            self.pos.x += (self.target.rect.centerx - pgfwb.ui.display.get_width() / 2 - self.pos.x) / self.follow_rate

        if self.followy:
            self.pos.y += (self.target.rect.centery - pgfwb.ui.display.get_height() / 2 - self.pos.y) / self.follow_rate

        self.render_scroll.x = int(self.pos.x)
        self.render_scroll.y = int(self.pos.y)

    def offset_pos(self, pos):
        return (pos[0] - self.render_scroll.x, pos[1] - self.render_scroll.y)

    def offset_rect(self, rect):
        rect_copy = rect.copy()
        rect_copy.x -= self.render_scroll.x
        rect_copy.y -= self.render_scroll.y

        return rect_copy

