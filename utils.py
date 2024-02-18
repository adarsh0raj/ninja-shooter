import pygame, numpy
from constants import *

scrolls = [0, 0] # [Screen Scroll, Background Scroll]

def transform_image(img_path, scale):
    img = pygame.image.load(img_path).convert_alpha()
    return pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))

def draw_background(screen, sky_img, mountain_img, pine1_img, pine2_img):
    screen.fill(BACKGROUND)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - scrolls[1] * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - scrolls[1] * 0.6, HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - scrolls[1] * 0.7, HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - scrolls[1] * 0.8, HEIGHT - pine2_img.get_height()))

def draw_text(screen, text, x, y, size, color):
    font = pygame.font.SysFont("Futura", size)
    text_surface = font.render(text, False, color)
    screen.blit(text_surface, (x, y))