import pygame

from dataclasses import dataclass

import pgfwb
from settings import *

@dataclass
class Moving:
    left: int = 0
    right: int = 0

class PhysicsEntity:
    def __init__(
        self, 
        pos=pygame.Vector2(), 
        width=TILESIZE,
        height=TILESIZE,
        gravity=1,
        movespeed=6,
        jumpforce=10,
        maxfallspeed=8,
    ):
        self.pos = pos
        self.gravity = gravity
        self.movespeed = movespeed
        self.jumpforce = jumpforce
        self.maxfallspeed = maxfallspeed

        self.surf = pygame.Surface((width, height))
        self.rect = pygame.Rect(*pos, width, height)
        self.air_frames = 0
        self.moving = Moving()
        self.movey = 0

    def update(self, rects):
        self.update_horizontal(rects)
        self.update_vertical(rects)

    def update_horizontal(self, rects):
        movex = self.moving.right - self.moving.left
        self.pos.x += movex * self.movespeed
        self.rect.x = int(self.pos.x)
        
        if movex and (idx := self.rect.collidelist(rects)) != -1:
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

    def render(self, target=pgfwb.ui.display, camera=None):
        if camera:
            target.blit(self.surf, camera.offset_rect(self.rect))
        else:
            target.blit(self.surf, self.rect)

def player_controls(event, player):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            player.moving.left = 1
        if event.key == pygame.K_RIGHT:
            player.moving.right = 1
        if event.key == pygame.K_SPACE:
            if player.air_frames <= 6:
                player.jump()
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_LEFT:
            player.moving.left = 0
        if event.key == pygame.K_RIGHT:
            player.moving.right = 0

