from pygame_utils import * #type:ignore[wildcard-import]
from pathlib import Path

WINW = 800; WINH = 600
WINSIZE = (WINW, WINH)
WINSW = WINW // 2; WINSH = WINH // 2
WINSURFACE = (WINSW, WINSH)
WINTIMES = WINW / WINSW

FPS = 60

PLAYERSIZE = (50, 50)
PLAYERPOS = (WINSW // 2, WINSH // 2)

BULLETSPEED = 5

IMAGES: dict[str, pg.Surface] = {}
BASEPATH = Path(__file__).parent
ASSETSPATH = BASEPATH / "assets"
IMAGESPATH = ASSETSPATH / "images"
SOUNDPATH = ASSETSPATH / "sounds"

for image in IMAGESPATH.glob("*.*"):
    IMAGES[image.stem] = pg.image.load(image)