import matplotlib.pyplot as plt
from Classes import MatchData, TeamData


def compare_team_scores(teams: list[TeamData]):
    team_nums = [str(team.teamNum) for team in teams]
    shots_data = [team.getAvgShots() if team.pit_data else (0, 0) for team in teams]

    shots1 = [shots[0] for shots in shots_data]
    shots2 = [shots[1] for shots in shots_data]

    plt.figure(figsize=(10, 5))
    plt.bar(team_nums, shots1, label="Auto", color="green")
    plt.bar(team_nums, shots2, bottom=shots1, label="Teleop", color="lime")
    plt.xlabel("Team Number")
    plt.ylabel("Average Score")
    plt.title("Average Score by Team")
    plt.legend()

    plt.tight_layout()
    plt.show()
