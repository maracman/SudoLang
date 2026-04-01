# SudoLang - Language Acquisition Research Tool (LART)

A tool for developing goal-oriented experimental paradigms for cognitive and neurocognitive research into language learning, attention, memory, and semantic processes.

SudoLang presents participants with a pygame-based game where falling objects must be matched to pseudoword labels. Researchers can configure experimental parameters (word complexity, energy dynamics, vocabulary progression, etc.) via a PyQt5 settings interface, then export those settings for participants to use in a standardised survey mode.

## Features

- **Configurable word complexity**: 6 categories of pseudoword labels (two-letter through four+ syllable)
- **Adaptive difficulty**: Vocabulary size grows as participants meet score thresholds
- **Energy system**: Non-linear or linear energy dynamics with configurable stick-points
- **Mouse tracking**: Optional per-trial mouse coordinate recording for motor behaviour analysis
- **Flexible output**: 24+ configurable output variables exported per click event
- **Dual mode**: Researcher mode (full settings UI) and Survey mode (locked settings for participants)

## Requirements

- Python 3.7+
- Dependencies listed in `requirements.txt`

```bash
pip install -r requirements.txt
```

### Dependencies

| Package    | Version |
|------------|---------|
| matplotlib | 3.4.3   |
| numpy      | 1.21.2  |
| pandas     | 1.3.3   |
| pygame     | 2.0.2   |
| PyQt5      | 5.15.4  |

## Usage

### Researcher Mode (default)

Opens the settings configuration window, then launches the game:

```bash
python -m sudolang
```

The settings window has four tabs:

1. **Object Labels** - Word and object category distribution weights
2. **Gameplay** - Energy, lives, vocabulary size, thresholds, FPS
3. **Display/Audio** - Feedback sounds, scroll speed
4. **Outputs** - Select which variables to include in the output CSV

Use **File > Save Settings** to export a `.pkl` file, and check "Export these settings for survey application" to make them available in survey mode.

### Survey/Participant Mode

Loads pre-exported settings and prompts only for a participant ID:

```bash
python -m sudolang --survey
```

The legacy single-file entry point (`sudolang.py`) is also retained for backward compatibility.

## Project Structure

```
.
├── sudolang/                    # Main package
│   ├── __init__.py
│   ├── __main__.py              # Entry point (python -m sudolang)
│   ├── config.py                # Settings class, paths, pickle I/O
│   ├── gui.py                   # PyQt5 settings UI (App, Enter_Name, Canvas)
│   └── game.py                  # Pygame game loop and helper functions
├── sudolang.py                  # Legacy single-file entry point
├── epoch_csv_converter.py       # Post-processing: mouse tracking CSV to PNG heatmaps
├── requirements.txt
├── SL_data/
│   ├── game_input_data.csv      # Object definitions with pseudoword labels
│   ├── current_settings.pkl     # Cached researcher settings
│   ├── survey_settings.pkl      # Exported settings for survey mode
│   ├── freesansbold.ttf         # Game font
│   ├── Grass.png                # Background tile
│   ├── audio/                   # Label audio files + feedback sounds
│   ├── obj_images/              # Object sprite images
│   └── saved_game_states/       # Per-user session persistence
├── outputs/                     # CSV output directory
│   └── mouse_tracking/          # Per-session mouse coordinate data (if enabled)
└── icons/                       # Application icons (.icns, .ico)
```

## Output Data

### Click Times CSV

Saved to `outputs/{user_ID}_clicktimes_{timestamp}.csv`. Each row is a click event with configurable columns including:

- `click_time`, `since_last_click`, `since_stimulus` - timing metrics
- `isMatch` - whether the click was correct
- `clicked_label`, `target_label` - pseudoword labels
- `clicked_word_category`, `target_word_category` - word complexity levels
- `player_energy`, `vocab_size` - game state at time of click
- `score_for_clicked`, `score_for_target` - per-object match counts

### Mouse Tracking (optional)

Per-trial CSV files with `(x, y, timestamp)` coordinates saved to `outputs/mouse_tracking/`. Use `epoch_csv_converter.py` to convert these into PNG heatmaps where colour encodes temporal information relative to the final click.

## Data Files

> **Important**: Do not edit `SL_data/game_input_data.csv` without understanding its format. The game will include extra information from this file but will produce errors if the column structure is changed.

## Building Executables

When creating standalone executables with PyInstaller, include:

```bash
pyinstaller sudolang.py --hidden-import pandas.plotting._matplotlib --collect-submodules sudolang
```

This prevents the exception: `"Failed to execute script due to unhandled exception: matplotlib is required for plotting when the default backend 'matplotlib' is selected"`.

## License

Please contact the developer for licensing information.
