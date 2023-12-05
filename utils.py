"""
Common functions used between framework modules and main script
"""
import pygame
import sys

from pygame.event import Event, post

def quit_game():
    """Convenience function for fully quiting the game"""
    pygame.quit()
    sys.exit()

def quit_handler(event):
    """Calls quit_game for the pygame.QUIT event
    
    This is meant to consume the event in the event loop.

    Usage:
        while True:
            for event in pygame.event.get():
                quit_handler(event)
    """
    if event.type == pygame.QUIT:
        quit_game()

def preserve_keys(*keys):
    """Posts events for KEYUP or KEYDOWN based on key state.

    This is used when we are running a game loop that calls
    another function with a game loop. Without preserving
    the keys, we can lose the state of the keys when 
    returning to the original function.

    Example:
    You are running a platformer scene and press a key to 
    show a menu. The menu will consume the keys that are 
    pressed and released. When returning to the platformer
    scene, we want to account for the keys that were 
    pressed or released while the menu scene was shown. 

    If we don't do this, we risk having a character continue
    moving in a direction from a KEYDOWN event because the
    cleanup in the KEYUP event was not captured in its scene.
    """
    pressed_keys = pygame.key.get_pressed()

    for key in keys:
        if pressed_keys[key]:
            post(Event(pygame.KEYDOWN, {'key': key}))
        else:
            post(Event(pygame.KEYUP, {'key': key}))

def keydown(event):
    """Used for creating functions for capturing KEYDOWN events with a key"""
    def inner(key):
        return event.type == pygame.KEYDOWN and event.key == key
    return inner

def keyup(event):
    """Used for creating functions for capturing KEYUP events with a key"""
    def inner(key):
        return event.type == pygame.KEYUP and event.key == key
    return inner
