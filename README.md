# DGS (Don't Get Shot)

DGS is a top-down 2D shooter game built with Pygame. Fight enemies, collect weapons, and survive as long as you can! The game supports both singleplayer and multiplayer modes.

## Features

- Fast-paced top-down shooting action
- Multiple unique weapons with different behaviors
- Inventory management and weapon swapping
- Enemy AI with basic pathfinding and shooting
- Blood, explosions, and particle effects
- Multiplayer support (host or join a game)

## Requirements

- Python 3.8+
- [Pygame](https://www.pygame.org/) (`pip install pygame`)
- Tkinter (usually included with Python)
- All assets in the `assets/` directory (images, sounds, data)

## How to Play

1. **Run the game:**
   ```
   python main.py
   ```

2. **Select mode:**
   - `single` for singleplayer
   - `server` to host a multiplayer game
   - `client` to join a multiplayer game

3. **Controls:**
   - `WASD`: Move
   - `Mouse`: Aim
   - `Left Click`: Shoot
   - `Q` / `E`: Cycle weapons
   - `I`: Open/close inventory (swap weapon order)
   - `Esc`: Quit or close inventory

4. **Multiplayer:**
   - Start one instance as `server` (host).
   - Other players join as `client` (currently uses localhost; edit code for LAN).
   - Enter a username when prompted.

## Inventory

- Press `I` to open inventory.
- Click to select and swap weapons.
- Right-click or `Esc`/`I` to close inventory.

## Assets

- Place all images in `assets/images/`
- Place all sounds in `assets/sounds/`
- Place `guns.json` in `assets/data/`

## Notes

- Gun images are from [Enter the Gungeon Wiki](https://enterthegungeon.fandom.com/wiki/Guns).
- Multiplayer is local network only by default.
- For best experience, run in a window with a supported resolution.

---

Enjoy the game!