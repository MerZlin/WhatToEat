# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

"下一顿吃什么" (What to Eat Next Meal?) — a meal randomizer app to help decide your next meal. Two versions share the same design language and feature set:

- **Desktop**: Python + tkinter (`meal_picker.py`), built into a Windows `.exe` via PyInstaller
- **Web/PWA**: Standalone HTML/CSS/JS app (`android_pwa/index.html`) with Service Worker for offline/mobile use. The root-level `下一顿吃什么.html` is an older single-file web version.

## Build & Run

```bash
# Run desktop app directly (no deps needed — tkinter is stdlib)
python meal_picker.py

# Build Windows exe
pyinstaller 下一顿吃什么.spec
# Output: dist/下一顿吃什么.exe

# PWA: just serve android_pwa/ as static files, e.g.:
python -m http.server 8080 -d android_pwa
```

The desktop app only needs Python 3 with tkinter (included in standard Python on Windows). There is no `requirements.txt`, no npm, no virtual environment.

## Architecture

### Desktop app (`meal_picker.py`)

Single-file tkinter app. The `MealPicker` class owns everything: data loading, UI construction, spin animation logic, and CRUD for dishes.

- **Data persistence**: reads/writes `meal_picker_data.json` — a JSON file with `dishes` (list of `{name, cat}`) and `history` (list of `{name, cat, time}`, capped at 200 entries). Falls back to `DEFAULT_DISHES` hardcoded list if the JSON is missing or corrupt.
- **UI**: Two tabs via `ttk.Notebook` — "挑选" (pick) and "管理菜品" (manage). The pick tab has category filter buttons, a spinning wheel label, result display, and history log. The manage tab has add/remove dish functionality with a Treeview.
- **Spin animation**: Uses `root.after(40ms, callback)` for 40ms-per-frame scrolling. The "instant pick" mode skips animation with a 200ms flash and direct result.
- **Keyboard shortcuts**: Space (start/stop spin), R (instant pick), Escape (cancel spin).
- **Styling**: ttk `clam` theme with custom dark color scheme (#1e1e2e background, #e94560 accent).

### PWA (`android_pwa/`)

- `index.html` — complete standalone app (all CSS/JS inline). Same dark theme and two-tab layout as the desktop version.
- `sw.js` — Service Worker using **network-first** strategy (fetches network, falls back to cache). Cache name versioned (`meal-picker-v3`).
- `manifest.json` — PWA manifest for "add to home screen" on Android. App name "吃啥", standalone display mode.
- **Data**: Uses `localStorage` (key: `meal_picker_data`), not the JSON file. The SW does not cache data — only the static app shell.

### Data flow

Desktop and PWA are independent — they do not share data. Desktop uses the JSON file; PWA uses localStorage. The `meal_picker_data.json` checked into the repo is a snapshot of the desktop app's data.

## Key behaviors

- Filtering by category affects both the spin pool and the dish list in the manage tab.
- History displays relative timestamps (今天/昨天 for today/yesterday, month/day otherwise).
- The status bar shows total dishes, category count, and today's pick count.
- Removing the currently displayed last result clears `last_result` so Escape/cancel doesn't restore a deleted dish.
- If no dishes match the current filter, spin/instant-pick shows an info dialog instead of crashing.
