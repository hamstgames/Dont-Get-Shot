from pygame_utils import *
from pathlib import Path

WINW = 800; WINH = 600
WINSIZE = (WINW, WINH)
WINQW = WINW // 4; WINQH = WINH // 4
WINQUARTER = (WINQW, WINQH)

FPS = 60

PLAYERSIZE = (50, 50)
PLAYERPOS = (WINQW // 2, WINQH // 2)

BULLETSPEED = 5

IMAGES = {}
BASEPATH = Path(__file__).parent
ASSETSPATH = BASEPATH / "assets"
IMAGESPATH = ASSETSPATH / "images"
SOUNDPATH = ASSETSPATH / "sounds"

for image in IMAGESPATH.glob("*.*"):
    IMAGES[image.stem] = pg.image.load(image)