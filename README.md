<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-6c5ce7?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/license-GPLv3-6c5ce7?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/platform-Windows-6c5ce7?style=flat-square" alt="Platform">
</p>

<h1 align="center">Luaroad</h1>

<p align="center">
  <b>A modern, all-in-one Steam unlocker manager with Lua plugins,<br>game fixing, cloud saves, and manifest tools.</b>
</p>

<p align="center">
  <img src="website/preview.png" alt="Screenshot" width="700">
</p>

---

## Features

### Dual Engine Support
Swap between **OpenSteamTool** and **LumaCore** engines. Each has its own Lua config directory and DLL set — switch with one click in Settings.

### Lua Plugin System
Extend Luaroad with custom Lua scripts. A full plugin API with load/unload/reload lifecycle hooks. Create your own plugins from templates in the Plugins tab.

### Multi-Source Lua Downloads
Download Lua configs from:
- **revobd.club** — free, no auth required (primary source)
- **Ryuu** — with API key
- **Hubcap Manifest** — with API key
- **Steam depot query** — builds Lua from Steam store data + bundled key database (363K+ keys)

### Game Fix Pipeline
Apply Steam emulators with one click:
- **ColdClient Simple** (recommended)
- **ColdClient Advanced** (GSE Fork)
- **ColdLoader DLL**
- **Regular** (steam_api.dll replacement)

Auto-unpack SteamStub DRM, create launch scripts, auto-detect App ID from game folder.

### Cloud Save Manager
Scan your Steam library for games with cloud saves, back them up to any folder, and restore with automatic safety copies.

### Manifest & Depot Tools
- Fetch manifest request codes (steamrun, Ryuu)
- Browse depot history via GitHub mirror
- Generate GBE tokens (Goldberg Emulator)
- Extract VDF decryption keys from config.vdf
- Manage AppList profiles

### Download Tracking
Queue-based download manager with active download progress, completed history, failed items with retry.

### Game Search
Search games via Steam Community API, add to your configured list, scan installed library games.

### Dark Titlebar
Full dark theme including the Windows title bar — no bright white bar at the top.

---

## Installation

### Requirements
- Windows 10 or 11
- [Python 3.10+](https://python.org)
- [Steam](https://store.steampowered.com) installed

### Quick Start

```bash
# Clone or download
git clone https://github.com/len-dx/luaroad.git
cd luaroad

# Install dependencies
install_deps.bat

# Run
run.bat
```

Or manually:

```bash
pip install -r requirements.txt
python main.py
```

### First Run
1. Launch Luaroad — it auto-detects your Steam installation
2. Go to **Settings > General** to set your default Lua source
3. Add API keys under **Settings > API Keys** (optional — revobd works without any)
4. Head to the **Games** tab, search for a game, double-click to add it
5. Select the game and click **Download Lua + Write to Steam**

---

## Project Structure

```
luaroad/
├── luaroad_app/
│   ├── app.py                  # Main application
│   ├── config.py               # JSON config persistence
│   ├── constants.py            # Paths, URLs, settings keys
│   ├── engines/
│   │   ├── base.py             # Engine ABC
│   │   ├── opensteamtool.py    # OpenSteamTool engine
│   │   ├── lumacore.py         # LumaCore engine
│   │   └── manager.py          # Engine manager
│   ├── plugins/
│   │   ├── api.py              # Plugin API for Lua scripts
│   │   ├── engine.py           # Lua runtime (lupa)
│   │   └── registry.py         # Plugin registry
│   ├── services/
│   │   ├── lua_downloader.py   # Multi-source Lua downloader
│   │   ├── ryuu.py             # Ryuu API client
│   │   ├── manifest.py         # Steam manifest fetching
│   │   ├── steam.py            # Steam ACF/VDF, library scan
│   │   ├── fix_game_service.py # Emulator fix pipeline
│   │   ├── cloud_saves.py      # Save backup/restore
│   │   ├── download_manager.py # Queue-based download tracking
│   │   ├── hubcap_client.py    # Hubcap Manifest API client
│   │   ├── depot_history.py    # Depot version history
│   │   └── updater.py          # Local OST update system
│   ├── ui/
│   │   ├── titlebar.py         # Custom dark titlebar
│   │   ├── theme.py            # sv-ttk theme + DWM dark mode
│   │   ├── dialogs.py          # Input/Confirm/About dialogs
│   │   ├── home_tab.py         # Main hub with quick actions
│   │   ├── games_tab.py        # Game search + configured list
│   │   ├── downloads_tab.py    # Download tracking
│   │   ├── manifests_tab.py    # Manifest code fetching
│   │   ├── fix_game_tab.py     # Emulator fix pipeline UI
│   │   ├── cloud_saves_tab.py  # Save backup/restore UI
│   │   ├── plugins_tab.py      # Plugin manager
│   │   ├── tools_tab.py        # GBE/VDF/AppList tools
│   │   └── settings_tab.py     # All configuration
│   └── utils/
│       ├── steam_path.py       # Registry + common paths
│       ├── helpers.py          # Misc utilities
│       └── async_utils.py      # Async helpers
├── engines/                    # Engine DLLs
├── plugins/                    # Lua plugin directory
├── website/                    # Landing page HTML
├── main.py                     # Entry point
├── run.bat                     # Windows launcher
├── install_deps.bat            # Dependency installer
└── requirements.txt            # Python dependencies
```

---

## API Keys (Optional)

| Service | Used For | Where to Get |
|---------|----------|--------------|
| **revobd.club** | Lua downloads | Free, no key needed |
| **Ryuu** | Lua downloads, manifest hub | generator.ryuu.lol |
| **Hubcap Manifest** | Lua downloads, manifest library | hubcapmanifest.com |
| **Steam Web** | GBE Token Generator | steamcommunity.com/dev/apikey |

---

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE).

This project incorporates code from:
- [OpenSteamTool](https://github.com/OpenSteam001/OpenSteamTool)
- [SFF / LumaCore](https://github.com/Midrags/SFF)
- [Sun-Valley-ttk-theme](https://github.com/rdbende/Sun-Valley-ttk-theme)

<p align="center"><i>For educational purposes only.</i></p>
