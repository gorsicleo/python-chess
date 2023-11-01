import pygame
pygame.init()

"""
Create program window
"""

window = pygame.display.set_mode((500, 500))
background = (200, 255, 255)
window.fill(background)
clock = pygame.time.Clock()

"""
Create card class
"""


class Card:
    rect = pygame.Rect(0, 0, 10, 10)
    fill_color = "blue"

    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.fill_color = color

    def change_color(self, new_color):
        self.fill_color = new_color

    def fill(self):
        pygame.draw.rect(window, self.fill_color, self.rect)

    def outline(self, color, thickness):
        pygame.draw.rect(window, color, self.rect, thickness)


class Label(Card):

    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height, color)
        self.image = None

    def set_text(self, text, font_size, text_color):
        self.image = pygame.font.SysFont("verdana", font_size).render(text, True, text_color)

    def draw(self, shift_x, shift_y):
        self.fill()
        window.blit(self.image, (self.rect.x + shift_x, self.rect.y + shift_y))

