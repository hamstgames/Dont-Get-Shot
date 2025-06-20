from pygame_utils import * # pyright:ignore[reportWildcardImportFromLibrary]
from pathlib import Path
from pygame.transform import scale
pg.mixer.init()
pg.init()

def scale1_2(image: pg.Surface) -> pg.Surface:
    return scale(image, (image.get_width() * 1.2, image.get_height() * 1.2))

info = pg.display.Info()
WINW = info.current_w
WINH = info.current_h
# print(f"Window size: {WINW}x{WINH}")
WINSIZE = (WINW, WINH)
WINSW = WINW // 2; WINSH = WINH // 2
WINSURFACE = (WINSW, WINSH)
WINTIMES = WINW / WINSW

FPS = 60
TPS = 40

PLAYERSIZE = (50, 50)
PLAYERPOS = (WINSW // 2, WINSH // 2)
PLAYERSPEED = 3
PLAYERHEALTH = 100

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
    SOUNDS[sound.stem].set_volume(0.5)

# Gun pictures from https://enterthegungeon.fandom.com/wiki/Guns
GUNDATA = {
    "revolver": {
        "cooldown": 0.016,
        "bulletspeed": 15,
        "deviation": 6,
        "image": scale1_2(IMAGES["revolver"]),
        "quantity": 1,
        "sound": SOUNDS["revolver"],
        "damage": 3,
        "kickback": 0,
        "once_a_time": True,
        "penetrative": False
    }, "handgun": {
        "cooldown": 0.2,
        "bulletspeed": 15,
        "deviation": 10,
        "image": scale1_2(IMAGES["handgun"]),
        "quantity": 1,
        "sound": SOUNDS["handgun"],
        "damage": 4,
        "kickback": 1,
        "once_a_time": False,
        "penetrative": True
    }, "rifle": {
        "cooldown": 0.1,
        "bulletspeed": 20,
        "deviation": 5,
        "image": scale1_2(IMAGES["rifle"]),
        "quantity": 1,
        "sound": SOUNDS["rifle"],
        "damage": 4,
        "kickback": 0,
        "once_a_time": False,
        "penetrative": False
    }, "shotgun": {
        "cooldown": 0.6,
        "bulletspeed": 15,
        "deviation": 10,
        "image": scale1_2(IMAGES["shotgun"]),
        "quantity": 6,
        "sound": SOUNDS["shotgun"],
        "damage": 3,
        "kickback": 10,
        "once_a_time": True,
        "penetrative": False
    }, "rifle2": {
        "modes": [
            { # auto
                "cooldown": 0.08,
                "bulletspeed": 20,
                "deviation": 3,
                "image": scale1_2(IMAGES["rifle2"]),
                "quantity": 1,
                "sound": SOUNDS["rifle2"],
                "damage": 4,
                "kickback": 0,
                "once_a_time": False,
                "penetrative": False
            }, { # burst
                "cooldown": 0.25,
                "bulletspeed": 20,
                "deviation": 3,
                "image": scale1_2(IMAGES["rifle2"]),
                "quantity": 3,
                "sound": SOUNDS["handgun"],
                "damage": 4,
                "kickback": 3,
                "once_a_time": False,
                "penetrative": False
            }
        ]
    }, "submachinegun1": {
        "cooldown": 0.05,
        "bulletspeed": 20,
        "deviation": 5,
        "image": scale1_2(IMAGES["submachinegun"]),
        "quantity": 1,
        "sound": SOUNDS["submachinegun"],
        "damage": 2.5,
        "kickback": 0,
        "once_a_time": False,
        "penetrative": False
    }, "submachinegun2": {
        "cooldown": 0.067,
        "bulletspeed": 20,
        "deviation": 4,
        "image": scale1_2(IMAGES["submachinegun2"]),
        "quantity": 1,
        "sound": SOUNDS["submachinegun"],
        "damage": 2.5,
        "kickback": 0,
        "once_a_time": False,
        "penetrative": False
    }, "grenade_launcher": {
        "bomb": True,
        "cooldown": 1,
        "bulletspeed": 5,
        "image": scale1_2(IMAGES["grenade_launcher"]),
        "quantity": 1,
        "sound": SOUNDS["grenade_launcher"],
        "kickback": 10,
        "once_a_time": True,
        "penetrative": False
    }
}