import pygame
import PIL
from pygame.locals import *

#Charge une image avec des paramètres de largeur et longueur
def load_image(path, w=0, h=0, colorkey = False):
    image = pygame.image.load(path)
    if w and h:
        image = pygame.transform.scale(image, (w, h))
    if colorkey:
        image.set_colorkey((0, 0, 0))
    else:
        image = image.convert_alpha()
    return image

#Sépare une longue image en plein de plus petites images
def split_image(path, rows, cols, w=0, h=0):
    images = []
    image_to_split = load_image(path) if type(path) is str else path
    width, height = image_to_split.get_width()/cols, image_to_split.get_height()/rows
    for i in range(rows):
        for j in range(cols):
            new_image = image_to_split.subsurface(pygame.Rect((width*j, height*i), (width, height)))
            if w and h:
                new_image = pygame.transform.scale(new_image, (w, h))
            images.append(new_image)
    return images
