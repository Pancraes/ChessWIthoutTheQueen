import pygame as p
import os

# creating screen dimensions
WIDTH = 560
HEIGHT = 560
#Board Dimensions
ROWS = 7
COLUMNS = 7
SQUARESIZE = HEIGHT//ROWS
MAXFPS = 15
IMAGES = {}

def createImages():
    pieces = ["wP", "wR", "wB", "wN", "wK", "bP", "bR", "bB", "bN", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f'assets/images/imgs-128px/{piece}.png'),(SQUARESIZE, SQUARESIZE))