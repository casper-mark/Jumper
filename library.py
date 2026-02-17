import sys, pygame
from pygame.locals import *
from pygame.rect import Rect
from pygame.draw import rect as draw_rect
vec = pygame.math.Vector2

#colors
BLACK = (0, 0, 0)
RED = (200, 0, 0)
DARK_RED = (150, 0, 0)
BLUE = (75, 150, 255)
LIGHT_BLUE = (100, 200, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)
WHITE  = (255, 255, 255)
PURPLE = (100, 0, 160)
TURQUOISE = (0, 200, 200)
YELLOW = (200, 200, 0)
DARK_YELLOW = (100, 100, 0)
BROWN = (200, 100, 0)
DARK_BROWN = (150, 75, 0)
GREY = (100, 100, 100)
DARK_GREY = (75,  75, 75)


def drawText(x, y, text, size, surface, color=BLACK):
    font = pygame.font.Font(None, size)
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

#['arial', 'arialblack', 'bahnschrift', 'calibri', 'cambria', 'cambriamath', 'candara', 'comicsansms', 'consolas', 'constantia', 'corbel', 'couriernew', 'ebrima', 'franklingothicmedium', 'gabriola', 'gadugi', 'georgia', 'impact', 'inkfree', 'javanesetext', 'leelawadeeui', 'leelawadeeuisemilight', 'lucidaconsole', 'lucidasans', 'malgungothic', 'malgungothicsemilight', 'microsofthimalaya', 'microsoftjhenghei', 'microsoftjhengheiui', 'microsoftnewtailue', 'microsoftphagspa', 'microsoftsansserif', 'microsofttaile', 'microsoftyahei', 'microsoftyaheiui', 'microsoftyibaiti', 'mingliuextb', 'pmingliuextb', 'mingliuhkscsextb', 'mongolianbaiti', 'msgothic', 'msuigothic', 'mspgothic', 'mvboli', 'myanmartext', 'nirmalaui', 'nirmalauisemilight', 'palatinolinotype', 'segoemdl2assets', 'segoeprint', 'segoescript', 'segoeui', 'segoeuiblack', 'segoeuiemoji', 'segoeuihistoric', 'segoeuisemibold', 'segoeuisemilight', 'segoeuisymbol', 'simsun', 'nsimsun', 'simsunextb', 'sitkasmall', 'sitkatext', 'sitkasubheading', 'sitkaheading', 'sitkadisplay', 'sitkabanner', 'sylfaen', 'symbol', 'tahoma', 'timesnewroman', 'trebuchetms', 'verdana', 'webdings', 'wingdings', 'yugothic', 'yugothicuisemibold', 'yugothicui', 'yugothicmedium', 'yugothicuiregular', 'yugothicregular', 'yugothicuisemilight', 'holomdl2assets', 'neosans']


def terminate():
    pygame.quit()
    sys.exit()


def wait():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                if event.key == K_SPACE:
                    return
            if event.type == MOUSEBUTTONDOWN:
                return
        
