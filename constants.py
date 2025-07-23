from pygame_utils import * # pyright:ignore[reportWildcardImportFromLibrary]
from pathlib import Path
from pygame.transform import scale
pg.mixer.init()
pg.init()

def scale1_2(image: pg.Surface) -> pg.Surface:
    """Scale a pygame Surface by 1.2x in both width and height."""
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
PLAYERSPEED = 4
PLAYERHEALTH = 20

IMAGES: dict[str, pg.Surface] = {}
SOUNDS = {}
BASEPATH = Path(__file__).parent
ASSETSPATH = BASEPATH / "assets"
IMAGESPATH = ASSETSPATH / "images"
SOUNDPATH = ASSETSPATH / "sounds"
DATAPATH = ASSETSPATH / "data"

for image in IMAGESPATH.glob("*.*"):
    IMAGES[image.stem] = pg.image.load(image)
for sound in SOUNDPATH.glob("*.*"):
    SOUNDS[sound.stem] = pg.mixer.Sound(sound)
    SOUNDS[sound.stem].set_volume(0.5)

# Gun pictures from https://enterthegungeon.fandom.com/wiki/Guns
raw_gundata = json_load(open(DATAPATH / "guns.json", encoding='utf-8'))
GUNDATA: dict[str, dict] = raw_gundata
for gun, data in GUNDATA.items():
    if "modes" in data:
        for mode, mode_data in enumerate(data["modes"]):
            GUNDATA[gun]["modes"][mode]["image"] = scale1_2(IMAGES[mode_data["image"]])
            GUNDATA[gun]["modes"][mode]["sound"] = SOUNDS[mode_data["sound"]]
    else:
        GUNDATA[gun]["image"] = scale1_2(IMAGES[data["image"]])
        GUNDATA[gun]["sound"] = SOUNDS[data["sound"]]
# print(GUNDATA)

get_blood = lambda: IMAGES[choice(["blood1","blood1", "blood2"])]
def get_font(size: int) -> pg.font.Font:
    """Return a pygame system font of the given size."""
    return pg.font.SysFont(None, size)