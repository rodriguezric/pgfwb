import pygame
import json

from dataclasses import dataclass
import functools
import random

import pgfwb
from settings import *

@dataclass
class Moving:
    left: bool = False
    right: bool = False

    def __bool__(self):
        return self.left or self.right

class PhysicsEntity:
    def __init__(
        self, 
        pos=None, 
        coord=None,
        width=TILESIZE,
        height=TILESIZE,
        gravity=1,
        movespeed=6,
        jumpforce=10,
        maxfallspeed=8,
        color=None,
        folder=None,
    ):
        if coord:
            pos = pygame.Vector2(pgfwb.tile.coord_to_pos(coord))

        if pos is None:
            pos = pygame.Vector2()

        self.pos = pos
        self.gravity = gravity
        self.movespeed = movespeed
        self.jumpforce = jumpforce
        self.maxfallspeed = maxfallspeed

        self.surf = pygame.Surface((width, height))
        
        self.color = color
        if color: 
            self.surf.fill(color)

        self.folder = folder
        if folder:
            self.animation_manager = pgfwb.animation.AnimationManager(
                folder=folder
            )

            self.surf = self.animation_manager.next()
        
        self.rect = pygame.Rect(*pos, width, height)
        self.air_frames = 0
        self.moving = Moving()
        self.movey = 0
        self.flip = False

    def update(self, rects):
        self.update_vertical(rects)
        self.update_horizontal(rects)

        if self.animation_manager:
            self.update_animation()

    def update_animation(self):
        if self.air_frames > 0:
            self.animation_manager.animation = 'jumping'
        elif self.moving:
            if self.animation_manager.animation_name != 'walking':
                self.animation_manager.animation = 'walking'
        elif self.animation_manager.animation_name != 'standing':
            self.animation_manager.animation = 'standing'

        print(self.animation_manager.animation_name)
        self.surf = self.animation_manager.next()

    def update_horizontal(self, rects):
        movex = self.moving.right - self.moving.left
        self.pos.x += movex * self.movespeed
        self.rect.x = int(self.pos.x)
        
        if (idx := self.rect.collidelist(rects)) != -1:
            other_rect = rects[idx]
            if movex > 0:
                self.rect.right = other_rect.left
            else:
                self.rect.left = other_rect.right
            self.pos.x = self.rect.x

    def update_vertical(self, rects):
        self.air_frames += 1
        self.movey = min(self.maxfallspeed, self.movey + self.gravity)
        self.pos.y += self.movey
        self.rect.y = int(self.pos.y)

        if (idx := self.rect.collidelist(rects)) != -1:
            other_rect = rects[idx]
            if self.movey > 0:
                self.rect.bottom = other_rect.top
                self.movey = self.gravity
                self.air_frames = 0
            else:
                self.rect.top = other_rect.bottom
                self.movey = 0
            self.pos.y = self.rect.y

    def jump(self):
        self.movey = -self.jumpforce

    def move_left(self):
        self.moving.left = True
        self.moving.right = False
        self.flip = True

    def move_right(self):
        self.moving.right = True
        self.moving.left = False

    def stand(self):
        self.moving.right = False
        self.moving.left = False

    def render(self, target=pgfwb.ui.display, camera=None):
        _surf = self.surf.copy()
        if self.flip:
            _surf = pygame.transform.flip(_surf, True, False)

        if camera:
            target.blit(_surf, camera.offset_rect(self.rect))
        else:
            target.blit(_surf, self.rect)

class Player(PhysicsEntity):
    def event_controls(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.moving.left = True
                self.flip = True
            if event.key == pygame.K_RIGHT:
                self.moving.right = True
                self.flip = False
            if event.key == pygame.K_SPACE:
                if self.air_frames <= 6:
                    self.jump()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.moving.left = False
            if event.key == pygame.K_RIGHT:
                self.moving.right = False


# Rates are applied for behaviors. 
SLOW_RATE = 120
NORMAL_RATE = 60
FAST_RATE = 30

class FrameEntity(PhysicsEntity):
    """
    A physics entity that tracks its frames. Used for behavior
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frame = 0

    def update(self, rects):
        super().update(rects)
        self.frame += 1
    
class Enemy(FrameEntity):
    def __init__(self, behavior_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.behavior_name = behavior_name
        self.behavior = behavior_function_map[behavior_name]

    def update(self, rects):
        super().update(rects)
        self.behavior(self)

def standing_behavior(frame_entity):
    ...

def pacing_behavior(frame_entity, frame_rate, variance=5):
    behaviors = [
        frame_entity.stand,
        frame_entity.move_left,
        frame_entity.stand,
        frame_entity.move_right
    ]

    variance_frames = random.randint(-variance, variance)

    behavior = behaviors[frame_entity.frame // frame_rate % len(behaviors)]
    behavior()

def pacing_behavior_slow(frame_entity):
    pacing_behavior(frame_entity=frame_entity, frame_rate=SLOW_RATE)

def pacing_behavior_normal(frame_entity): 
    pacing_behavior(frame_entity=frame_entity, frame_rate=NORMAL_RATE)

def pacing_behavior_fast(frame_entity):
    pacing_behavior(frame_entity=frame_entity, frame_rate=FAST_RATE)

behavior_functions = [
    standing_behavior,
    pacing_behavior_slow,
    pacing_behavior_normal,
    pacing_behavior_fast
]

behavior_function_map = {fn.__name__: fn for fn in behavior_functions}

class Door:
    def __init__(
        self, 
        pos=None, 
        coord=None,
        width=TILESIZE,
        height=TILESIZE,
        color=None,
        filepath=None,
    ):
        if coord:
            pos = pygame.Vector2(pgfwb.tile.coord_to_pos(coord))

        if pos is None:
            pos = pygame.Vector2()

        self.surf = pygame.Surface((width, height))

        self.color = color
        if color: 
            self.surf.fill(color)

        self.filepath = filepath
        if filepath:
            self.surf = pygame.image.load(filepath).convert_alpha()
        
        self.rect = pygame.Rect(*pos, width, height)

    def render(self, target=pgfwb.ui.display, camera=None):
        if camera:
            target.blit(self.surf, camera.offset_rect(self.rect))
        else:
            target.blit(self.surf, self.rect)

entity_classes = [
    Player,
    Enemy,
    Door,
]

entity_class_map = {cls.__name__: cls for cls in entity_classes}

class PlatformerTileMap(pgfwb.tile.TileMap):
    def __init__(self, file=None):
        self.tiles = {}

        if file:
            self.load(file, [entity_class_map])

    @property
    def player(self):
        return [x for x in self.tiles.values()
                if isinstance(x, Player)][0]

    @property
    def enemies(self):
        return [x for x in self.tiles.values()
                if isinstance(x, Enemy)]

    @property
    def door(self):
        return [x for x in self.tiles.values()
                if isinstance(x, Door)][0]
