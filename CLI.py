import Display as dp
from Classes import TeamData
import main
from time import sleep
import os
import numpy as np

hidden_teams: list[int] = []
match_data: dict[int, TeamData] = {}


def clear_screen():
    print("\033[H\033[J", end="")


def print_menu():
    print("Menu:")
    print("1. Compare Team Scores")
    print("2. Deep info on a team")
    print("9. Exit")
    print("0. Hide/Unhide Team")


def select_menu(selection: int):
    global hidden_teams, match_data
    try:
        if selection == 1:  # Compare team scores
            clear_screen()
            print("Close the graph to return to the menu.")
            dp.compare_team_scores(list(match_data.values()), hidden_teams)

        if selection == 2:  # Deep info on a team
            team_info()

        elif selection == 0:  # Hide/Unhide Team
            toggle_teams()

        elif selection == 9:  # Exit
            print("Exiting...")
            exit(0)

        else:
            print("Invalid option. Please try again.")
    except Exception as e:
        print(f"An error occurred: {e}")


def run_cli(data: dict[int, TeamData]):
    global match_data
    match_data = data
    while True:
        clear_screen()
        print_menu()
        try:
            selection = int(input("Select an option: "))
            select_menu(selection)
        except ValueError:
            print("Please enter a valid number.")


def team_info():
    team_num = int(input("Enter team number: "))
    if team_num in match_data:
        clear_screen()
        print(
            f"Showing data for team {team_num}. Close the graph to return to the menu."
        )
        team_data = match_data[team_num]
        if team_data.pit_data is not None:
            # team_data.pit_data.
            print(f"Max Fuel Storage: {team_data.pit_data.maxFuelStorage}")
            print(f"Drivetrain: {team_data.pit_data.drivetrainType.value}")
            print(f"Turreting Shooter: {team_data.pit_data.rotatableShooter}")
            print(f"Trench Drive Ability: {team_data.pit_data.trenchDriveAbility}")
            print()

            print(f"Climbing Ability: Level {team_data.pit_data.climbingAbility}")
            print(f"Intake from Depot: {team_data.pit_data.intakeFromDepot}")
            print(f"Intake from Outpost: {team_data.pit_data.intakeFromOutpost}")
            print(f"Weight: {int(team_data.pit_data.weight)} lbs")
            if team_data.matches:
                climbs = [
                    match.climb.timeSeconds
                    for match in team_data.matches
                    if match.climb
                ]
                print(f"Avg climb: {np.mean(climbs) if climbs else 0:.1f} seconds")

        dp.show_team_data(team_data)
    else:
        print(f"Team number {team_num} not found. Please try again.")
        sleep(1)


def toggle_teams():
    global match_data, hidden_teams
    teamstr = lambda num: f"[{'X' if num not in hidden_teams else ' '}]" + f" {num:<5}"
    screen_width = os.get_terminal_size().columns
    width = int(
        max(1, (screen_width * 0.75) // (len(teamstr(0)) + 4))
    )  # Adjust width based on terminal size

    clear_screen()
    print()
    while True:
        num_teams = len(match_data.keys())
        i = 0
        for j in range(0, num_teams, width):
            for k in range(width):
                if i < num_teams:
                    print(teamstr(list(match_data.keys())[i]), end="    ")
                i += 1
            print()
        print("Enter team number to toggle visibility (or enter to finish): ", end="")
        inp = input()
        clear_screen()
        if inp == "":
            break
        try:
            team_num = int(inp)
            if team_num in match_data:
                if team_num in hidden_teams:
                    hidden_teams.remove(team_num)
                    print(f"Team {team_num} is now visible.")
                else:
                    hidden_teams.append(team_num)
                    print(f"Team {team_num} is now hidden.")
            else:
                print(f"Team number {team_num} not found. Please try again.")
        except ValueError:
            print("Please enter a valid team number.")


if __name__ == "__main__":
    main.main()
