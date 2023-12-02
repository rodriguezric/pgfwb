from collections import deque

from settings import *
import string
import pygame 
from pgfwb.utils import (
    quit_handler,
    keydown,
)


screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen_rect = screen.get_rect()

font = pygame.font.Font('pgfwb/fonts/prstart.ttf', FONTSIZE)

SCROLLING_FPS = 5
clock = pygame.time.Clock()

def render_text(text):
    """Creates a surf for the text"""
    return font.render(text, False, 'white')

def get_y_pos(idx):
    """Used for calculating the y position of a text line"""
    return FONTSIZE + idx * FONTSIZE

class TextLines:
    """This class is for conveniently creating surfs and pos for
       a list of strings. There max_width and length are used to
       calculate relative window sizes.
    """
    def __init__(self, lines):
        self.max_width = max(map(len, lines))
        self.length = len(lines)
        self.surf_pos = [(render_text(text), (FONTSIZE, get_y_pos(idx)))
                            for idx, text in enumerate(lines)]

class ScrollngTextLines(TextLines):
    """Renders each character one at a time per line based on  
       a clock ticking. Pressing enter will fill all the lines
    """
    def __init__(self, lines):
        super().__init__(lines)

        self.surf_pos = []
        self.lines = lines
        self.idx = 0
        self.row = 0

    def update(self):
        if self.row < len(self.lines):
            self.surf_pos = [(render_text(text), (FONTSIZE, get_y_pos(idx)))
                                for idx, text in enumerate(self.lines[:self.row])]

            self.surf_pos.append((render_text(self.lines[self.row][:self.idx+1]), 
                                 (FONTSIZE, get_y_pos(self.row))))

            self.idx += 1
            if self.idx >= len(self.lines[self.row]):
                self.row += 1
                self.idx = 0

    def fill(self):
        self.row = len(self.lines)
        self.surf_pos = [(render_text(text), (FONTSIZE, get_y_pos(idx)))
                            for idx, text in enumerate(self.lines)]

    @property
    def filled(self):
        return self.row == len(self.lines)


class Window:
    """A class for showing a rectangle with lines of text inside it"""
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

class ScrollingWindow(Window):
    def __init__(self, lines):
        super().__init__(lines, text_class=ScrollngTextLines)

    def update(self):
        super().update()
        self.text_lines.update()

class LogWindow(Window):
    """A window for appending messages to the top"""
    def __init__(self, lines=None, maxlen=9, *args, **kwargs):
        if lines is None:
            lines = ['']

        super().__init__(lines, *args, **kwargs)
        self.deque = deque(lines, maxlen=maxlen)

    def add(self, text):
        self.deque.appendleft(text)
        self.text_lines = TextLines(list(self.deque))

    def add_bottom(self, text):
        self.deque.append(text)
        self.text_lines = TextLines(list(self.deque))

    def clear(self):
        self.deque = deque([''])
        self.text_lines = TextLines(list(self.deque))

class Cursor:
    """A cursor for selecting options from a menu"""
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
    """A window with a cursor"""
    def __init__(self, options):
        super().__init__(options, size_by_lines=True)
        self.rect.center = screen_rect.center
        self.cursor = Cursor(self)

    def update(self):
        super().update()
        self.surf.blit(self.cursor.surf, self.cursor.pos)

def window(lines, autoreturn=False):
    """Function for instantiating a Window object with a game loop

    The autoreturn parm is used when we want to display something
    else while the window is visible without having to press return
    to exit its game loop
    """
    window = Window(lines)

    while True:
        for event in pygame.event.get():
            quit_handler(event)
            pressed = keydown(event)

            if pressed(pygame.K_RETURN):
                return

        window.update()

        screen.blit(window.surf, window.rect)

        pygame.display.flip()

        if autoreturn:
            return

def scrolling_window(lines, autoreturn=False):
    """Note autoreturn in this function returns when the 
       text lines for the window are filled.
    """
    window = ScrollingWindow(lines)

    while True:
        for event in pygame.event.get():
            quit_handler(event)
            pressed = keydown(event)

            if pressed(pygame.K_RETURN):
                if window.text_lines.filled:
                    return
                else:
                    window.text_lines.fill()

        window.update()

        screen.blit(window.surf, window.rect)

        pygame.display.flip()

        clock.tick(SCROLLING_FPS)
        
        if autoreturn and window.text_lines.filled:
            return

def menu(options):
    """Function for instantiating a Menu object with a game loop

    Returns the menu's cursor's index when pressing return
    """
    menu = Menu(options)

    while True:
        for event in pygame.event.get():
            quit_handler(event)
            pressed = keydown(event)

            if pressed(pygame.K_RETURN):
                return menu.cursor.idx

            if pressed(pygame.K_UP):
                menu.cursor.move_up()

            if pressed(pygame.K_DOWN):
                menu.cursor.move_down()

        menu.update()

        screen.blit(menu.surf, menu.rect)

        pygame.display.flip()

def confirm(text=None):
    """Convenient function for displaying a window with text and a yes/no menu"""
    if text:
        window([text], autoreturn=True)

    return menu(['YES', 'NO']) == 0

def prompt(text=None, pos=None, width=None, height=None):
    if text:
        window([text], autoreturn=True)

    if not width:
        width = FONTSIZE * 2 + 10 * FONTSIZE
       
    if not height:
        height = FONTSIZE * 3

    prompt_window = Window([''], width=width, height=height)
    prompt_window.rect.center = screen_rect.center
    input_text = []
    ordmap = list(map(ord, string.ascii_lowercase + string.digits + '.'))

    while True:
        for event in pygame.event.get():
            quit_handler(event)
            pressed = keydown(event)

            if pressed(pygame.K_RETURN):
                screen.fill('black')
                return ''.join(input_text)

            if pressed(pygame.K_BACKSPACE):
                if input_text:
                    input_text.pop()

                prompt_window.text_lines = TextLines([''.join(input_text)])

            if event.type != pygame.KEYDOWN:
                continue

            if event.key in ordmap:
                key = chr(event.key)
                pressed_keys = pygame.key.get_pressed()

                if pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]:
                    key = key.upper()
                input_text.append(key)
                prompt_window.text_lines = TextLines([''.join(input_text)])

        prompt_window.update()

        screen.blit(prompt_window.surf, prompt_window.rect)

        pygame.display.flip()
