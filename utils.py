import pygame
import sys

from pygame.event import Event, post

def quit_game():
    pygame.quit()
    sys.exit()

def quit_handler(event):
    if event.type == pygame.QUIT:
        quit_game()

def preserve_keys(keys):
    pressed_keys = pygame.key.get_pressed()

    for key in keys:
        if pressed_keys[key]:
            post(Event(pygame.KEYUP, {'key': key}))
        else:
            post(Event(pygame.KEYDOWN, {'key': key}))

def keydown(key):
    def inner(event):
        return event.type == pygame.KEYDOWN and event.key == key
    return inner

def keyup(key):
    def inner(event):
        return event.type == pygame.KEYUP and event.key == key
    return inner

escape_pressed = keydown(pygame.K_ESCAPE)
return_pressed = keydown(pygame.K_RETURN)

up_pressed = keydown(pygame.K_UP)
down_pressed = keydown(pygame.K_DOWN)
right_pressed = keydown(pygame.K_RIGHT)
left_pressed = keydown(pygame.K_LEFT)

up_released = keyup(pygame.K_UP)
down_released = keyup(pygame.K_DOWN)
right_released = keyup(pygame.K_RIGHT)
left_released = keyup(pygame.K_LEFT)

