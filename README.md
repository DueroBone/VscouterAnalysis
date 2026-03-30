# VscouterAnalysis

VscouterAnalysis is a Python tool for parsing VScouter JSON exports, merging match and pit scouting data by team, and visualizing team performance with Matplotlib.

## What It Does

- Parses multiple JSON files from the Data folder.
- Merges match data and pit data into a per-team model.
- Provides a terminal menu for quick scouting analysis.
- Generates charts for:
  - Team-to-team score comparisons (auto, teleop, climb)
  - Detailed per-team trend views across matches

## Project Layout

- main.py: Entry point.
- Parser.py: JSON parsing, deduplication, and team data merging.
- Classes.py: Data models and scoring helpers.
- CLI.py: Interactive terminal menu.
- Display.py: Plot generation and chart styling.
- Data/: Input JSON exports.

## Requirements

- Python 3.10+
- Dependencies listed in requirements.txt

Install dependencies:

    pip install -r requirements.txt

## Run

From the repository root:

    python main.py

## CLI Menu

When launched, the app shows a menu:

- 1: Compare Team Scores
- 2: Deep info on a team
- 0: Hide or unhide team(s)
- 9: Exit

The plot window must be closed before returning to the menu.

## Data Input Rules

Output the data from VScouter into the Data folder.
Don't worry about duplicates, it is automatically handled.

## Scoring and Visualization Notes

- Auto and teleop values are derived from event percentages and team fuel capacity from pit data.
- Climb contribution is derived from climb ability and successful climb entries.
- Team comparison uses box plots by category and includes color-coded legends.