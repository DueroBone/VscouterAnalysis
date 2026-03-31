# VscouterAnalysis

This program provides analysis tools for the VScouter app made by Vihaan Chhabria of FRC team 7414. The repo of the app is [here](https://github.com/VihaanChhabria/VScouter).

Most of the data is derived from the pit scouting's fuel capacity, so most results are unusable and may crash if that data is missing.

## Requirements

Install dependencies:

    pip install -r requirements.txt

If there is an error about pip not being found, create a virtual environment and install the dependencies there:

    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt

## To Run

When the scouting app(s) is done scouting, dump the data and transfer all of the json files in the Data folder. Then, run the program.

From the repository root:

    python main.py

## CLI Menu

When launched, the app shows a menu:

- 1: Hide/Unhide Team: Toggle the visibility of teams in the comparison graph. You can also enter 0 to toggle all teams at once.
- 2: Compare Team Scores: Displays a box plot comparing the scores of all teams across various categories. Teams that are hidden will be excluded from the plot.
- 3: Deep info on a team: Displays detailed information about a specific team, including their performance in different matches and categories. You will be prompted to enter a team number to view their details.
- 0: Exit

The plot window must be closed before returning to the menu.

## Data Input Rules

Dump the data from VScouter into the Data folder.
With duplicates, the most recent file will be used.
(Having multiple people scouting the same bot on a match is untested)

## Scoring and Visualization Notes

- Team comparison uses box plots by category and includes color-coded legends.
- Auto and teleop values are derived from vague percentages and team fuel capacity from pit data. Take scores with a grain of salt.
- In Classes.py you can disable square rooting of the input percentages, which account for higher scoring teams better. Example: 50% full \* 80% accurate = 40% vs sqrt(50% \* 80%) = 63%.
- Climb contribution is derived from climb ability and successful climb entries.
Vscouter does not track individual climb attempts, just location and success.

## Issues

Feel free to open an issue if you find a bug or have a suggestion for improvement!
