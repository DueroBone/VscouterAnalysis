import Display as dp
from Classes import TeamData
import main
from time import sleep
import os

hidden_teams: list[int] = []
match_data: dict[int, TeamData] = {}


def clear_screen():
    print("\033[H\033[J", end="")


def print_menu():
    print("Menu:")
    print("1. Compare Team Scores")
    print("9. Exit")
    print("0. Hide/Unhide Team")


def select_menu(selection: int):
    global hidden_teams, match_data
    try:
        if selection == 1:
            clear_screen()
            print("Close the graph to return to the menu.")
            dp.compare_team_scores(list(match_data.values()), hidden_teams)

        elif selection == 0:
            toggle_teams()

        elif selection == 9:
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


def toggle_teams():
    global match_data, hidden_teams
    teamstr = lambda num: f"[{'X' if num not in hidden_teams else ' '}]" + f" {num:<5}"
    screen_width = os.get_terminal_size().columns
    width = int(max(1, (screen_width * 0.75) // (len(teamstr(0)) + 4)))  # Adjust width based on terminal size

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