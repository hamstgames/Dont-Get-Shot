from pygame_utils import * #type:ignore[wildcard-import]
from pathlib import Path
from pygame.transform import scale
pg.mixer.init()

def scale1_2(image: pg.Surface) -> pg.Surface:
    return scale(image, (image.get_width() * 1.2, image.get_height() * 1.2))

WINW = 1500; WINH = 800
WINSIZE = (WINW, WINH)
WINSW = WINW // 2; WINSH = WINH // 2
WINSURFACE = (WINSW, WINSH)
WINTIMES = WINW / WINSW

FPS = 60
TPS = 10

PLAYERSIZE = (50, 50)
PLAYERPOS = (WINSW // 2, WINSH // 2)
PLAYERSPEED = 3
PLAYERHEALTH = 20

IMAGES: dict[str, pg.Surface] = {}
SOUNDS = {}
BASEPATH = Path(__file__).parent
ASSETSPATH = BASEPATH / "assets"
IMAGESPATH = ASSETSPATH / "images"
SOUNDPATH = ASSETSPATH / "sounds"

for image in IMAGESPATH.glob("*.*"):
    IMAGES[image.stem] = pg.image.load(image)
for sound in SOUNDPATH.glob("*.*"):
    SOUNDS[sound.stem] = pg.mixer.Sound(sound)

GUNDATA = {
    "revolver": {
        "cooldown": 0.2,
        "bulletspeed": 15,
        "deviation": 6,
        "image": scale1_2(IMAGES["revolver"]),
        "quantity": 1,
        "sound": SOUNDS["revolver"],
        "damage": 4,
        "kickback": 4
    }, "handgun": {
        "cooldown": 0.2,
        "bulletspeed": 15,
        "deviation": 0,
        "image": scale1_2(IMAGES["handgun"]),
        "quantity": 1,
        "sound": SOUNDS["handgun"],
        "damage": 3,
        "kickback": 2
    }, "rifle": {
        "cooldown": 0.1,
        "bulletspeed": 20,
        "deviation": 5,
        "image": scale1_2(IMAGES["rifle"]),
        "quantity": 1,
        "sound": SOUNDS["rifle"],
        "damage": 2,
        "kickback": 2
    }, "shotgun": {
        "cooldown": 0.6,
        "bulletspeed": 15,
        "deviation": 10,
        "image": scale1_2(IMAGES["shotgun"]),
        "quantity": 6,
        "sound": SOUNDS["shotgun"],
        "damage": 2,
        "kickback": 10
    }, "rifle2": {
        "modes": [
            { # auto
                "cooldown": 0.08,
                "bulletspeed": 20,
                "deviation": 3,
                "image": scale1_2(IMAGES["rifle2"]),
                "quantity": 1,
                "sound": SOUNDS["rifle2"],
                "damage": 1.5,
                "kickback": 2
            }, { # burst
                "cooldown": 0.25,
                "bulletspeed": 20,
                "deviation": 3,
                "image": scale1_2(IMAGES["rifle2"]),
                "quantity": 3,
                "sound": SOUNDS["handgun"],
                "damage": 2,
                "kickback": 2
            }
        ]
    }, "microgun": {
        "cooldown": 0.05,
        "bulletspeed": 20,
        "deviation": 5,
        "image": scale1_2(IMAGES["microgun"]),
        "quantity": 1,
        "sound": SOUNDS["microgun"],
        "damage": 1.5,
        "kickback": 2
    }
}