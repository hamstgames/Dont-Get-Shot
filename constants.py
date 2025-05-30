from pygame_utils import * #type:ignore[wildcard-import]
from pathlib import Path
from typing import Literal
from pygame.transform import scale

def scale1_2(image: pg.Surface) -> pg.Surface:
    return scale(image, (image.get_width() * 1.2, image.get_height() * 1.2))

WINW = 800; WINH = 600
WINSIZE = (WINW, WINH)
WINSW = WINW // 2; WINSH = WINH // 2
WINSURFACE = (WINSW, WINSH)
WINTIMES = WINW / WINSW

FPS = 60

PLAYERSIZE = (50, 50)
PLAYERPOS = (WINSW // 2, WINSH // 2)

IMAGES: dict[str, pg.Surface] = {}
BASEPATH = Path(__file__).parent
ASSETSPATH = BASEPATH / "assets"
IMAGESPATH = ASSETSPATH / "images"
SOUNDPATH = ASSETSPATH / "sounds"

for image in IMAGESPATH.glob("*.*"):
    IMAGES[image.stem] = pg.image.load(image)

# Gun pictures from https://enterthegungeon.fandom.com/wiki/Guns
GUNTYPE:Literal['revolver', 'handgun', 'rifle', 'shotgun'] = "revolver"
GUNDATA = {
    "revolver": {
        "cooldown": 0.2,
        "bulletspeed": 10,
        "deviation": 6,
        "image": scale1_2(IMAGES["revolver"]),
        "quantity": 1
    }, "handgun": {
        "cooldown": 0.2,
        "bulletspeed": 10,
        "deviation": 0,
        "image": scale1_2(IMAGES["handgun"]),
        "quantity": 1
    }, "rifle": {
        "cooldown": 0.1,
        "bulletspeed": 15,
        "deviation": 5,
        "image": scale1_2(IMAGES["rifle"]),
        "quantity": 1
    }, "shotgun": {
        "cooldown": 0.6,
        "bulletspeed": 10,
        "deviation": 10,
        "image": scale1_2(IMAGES["shotgun"]),
        "quantity": 6
    }
}