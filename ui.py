from settings import *
import pygame

from pgfwb.utils import (
    quit_handler,
    up_pressed, 
    down_pressed,
    return_pressed,
)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen_rect = screen.get_rect()

font = pygame.font.Font('pgfwb/fonts/prstart.ttf', FONTSIZE)

def render_text(text):
    return font.render(text, False, 'white')

def get_y_pos(idx):
    '''Used for calculating the y position of a text line'''
    return FONTSIZE + idx * FONTSIZE

class TextLines:
    def __init__(self, lines):
        self.max_width = max(map(len, lines))
        self.length = len(lines)
        self.surf_pos = [(render_text(text), (FONTSIZE, get_y_pos(idx)))
                            for idx, text in enumerate(lines)]

class Window:
    def __init__(self, lines, width=None, height=None, size_by_lines=False, text_class=TextLines):
        self.text_lines = text_class(lines)

        if size_by_lines:
            width = FONTSIZE * 2 + self.text_lines.max_width * FONTSIZE
            height = FONTSIZE * 2 + self.text_lines.length * FONTSIZE

        if width is None: width = WIDTH

        if height is None: height = HEIGHT // 3

        self.surf = pygame.Surface((width, height))
        self.rect = self.surf.get_rect()
        self.border = self.surf.get_rect()

    def update(self):
        self.surf.fill('blue')
        pygame.draw.rect(self.surf, 'white', self.border, BORDER)
        for surf, pos in self.text_lines.surf_pos:
            self.surf.blit(surf, pos)

class Cursor:
    _surf = render_text('>')

    def __init__(self, window):
        self.window = window
        self.max_idx = window.text_lines.length - 1
        self.idx = 0

    @property
    def surf(self):
        return Cursor._surf

    @property
    def pos(self):
        return (BORDER, get_y_pos(self.idx))

    def move_up(self):
        self.idx = max(0, self.idx - 1)

    def move_down(self):
        self.idx = min(self.max_idx, self.idx + 1)

class Menu(Window):
    def __init__(self, options):
        super().__init__(options, size_by_lines=True)
        self.rect.center = screen_rect.center
        self.cursor = Cursor(self)

    def update(self):
        super().update()
        self.surf.blit(self.cursor.surf, self.cursor.pos)

def window(lines, autoreturn=False):
    window = Window(lines)

    while True:
        for event in pygame.event.get():
            quit_handler(event)

            if return_pressed(event):
                return

        window.update()

        screen.blit(window.surf, window.rect)

        pygame.display.flip()

        if autoreturn:
            return

def menu(options):
    menu = Menu(options)

    while True:
        for event in pygame.event.get():
            quit_handler(event)

            if return_pressed(event):
                return menu.cursor.idx

            if up_pressed(event):
                menu.cursor.move_up()

            if down_pressed(event):
                menu.cursor.move_down()

        menu.update()

        screen.blit(menu.surf, menu.rect)

        pygame.display.flip()

def confirm(text):
    window([text], autoreturn=True)
    return menu(['YES', 'NO']) == 0

