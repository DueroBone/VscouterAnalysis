import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from Classes import TeamData
import main
import numpy as np


autoPrimary = "red"
autoSecondary = "pink"
telePrimary = "green"
teleSecondary = "lime"
climbPrimary = "blue"
climbSecondary = "lightblue"


def sum_inner_lists(data) -> list[float]:
    return [np.sum(sublist) for sublist in data]


def extend_boxplot_medians(boxplot: dict, scale: float = 1.5):
    for median in boxplot["medians"]:
        x0, x1 = median.get_xdata()
        center = (x0 + x1) / 2
        half_width = (x1 - x0) / 2
        new_half_width = half_width * scale
        median.set_xdata([center - new_half_width, center + new_half_width])


def compare_team_scores_old(teams: list[TeamData], hidden_teams: list[int] = []):
    print(f"Hidden teams: {hidden_teams}")
    team_nums = [
        str(team.teamNum) for team in teams if team.teamNum not in hidden_teams
    ]
    shots_data = [
        team.getAvgShots() if team.pit_data else (0, 0)
        for team in teams
        if team.teamNum not in hidden_teams
    ]
    climb_data = [
        team.getClimbData() if team.pit_data else [0]
        for team in teams
        if team.teamNum not in hidden_teams
    ]

    shotsAuto = [shots[0] for shots in shots_data]
    shotsTeleop = [shots[1] for shots in shots_data]
    climbs = [
        (sum(climb) * 10) / len(climb) if climb else 0 for climb in climb_data
    ]  # 10 points per level

    # Sort teams by total shots (auto + teleop)
    total_shots = [s1 + s2 + c for s1, s2, c in zip(shotsAuto, shotsTeleop, climbs)]
    sorted_data = sorted(
        zip(team_nums, shotsAuto, shotsTeleop, climbs, total_shots),
        key=lambda x: x[4],
        reverse=True,
    )
    team_nums, shotsAuto, shotsTeleop, climbs, total_shots = zip(*sorted_data)

    plt.figure(figsize=(10, 5))
    plt.bar(team_nums, shotsAuto, label="Auto", color=autoPrimary)
    plt.bar(team_nums, shotsTeleop, bottom=shotsAuto, label="Teleop", color=telePrimary)
    plt.bar(
        team_nums,
        climbs,
        bottom=[s1 + s2 for s1, s2 in zip(shotsAuto, shotsTeleop)],
        label="Climb",
        color=climbPrimary,
    )
    plt.xlabel("Team Number")
    plt.ylabel("Average Score")
    plt.title("Average Score by Team")
    plt.legend()

    plt.tight_layout()
    plt.show()


def compare_team_scores(teams: list[TeamData], hidden_teams: list[int] = []):
    print(f"Hidden teams: {hidden_teams}")
    team_nums = []
    teleShots_data = []
    autoShots_data = []
    climb_data = []

    for team in teams:
        if team.teamNum not in hidden_teams:
            team_nums.append(str(team.teamNum))
            teleShots_data.append(sum_inner_lists(team.getTeleShots()))
            autoShots_data.append(sum_inner_lists(team.getAutoShots()))
            climb_data.append(team.getClimbData())

    """
    # Calculate average shots and climbs per team
    avg_teleShots = []
    avg_autoShots = []
    avg_climbs = []  # 10 points per level
    for i in range(len(team_nums)):
        # sum each inner list then average
        avg_teleShots.append(np.mean([np.sum(match) for match in teleShots_data[i]]))
        avg_autoShots.append(np.mean([np.sum(match) for match in autoShots_data[i]]))
        avg_climbs.append(
            (np.sum(climb_data[i]) * 10) / len(climb_data[i])
            if climb_data[i].size > 0
            else 0
        )
    total_scores = [
        s1 + s2 + c for s1, s2, c in zip(avg_autoShots, avg_teleShots, avg_climbs)
    ]

    # Sort teams by mean total score
    sorted_data = sorted(
        zip(team_nums, avg_autoShots, avg_teleShots, avg_climbs, total_scores),
        key=lambda x: x[4],
        reverse=True,
    )
    team_nums, avg_autoShots, avg_teleShots, avg_climbs, total_scores = zip(
        *sorted_data
    )
    """

    # Box plots per team
    plt.figure(figsize=(10, 5))
    auto_boxplot = plt.boxplot(
        autoShots_data,
        labels=team_nums,  # type: ignore
        patch_artist=True,
        boxprops=dict(facecolor=autoSecondary, edgecolor=autoPrimary),
        medianprops=dict(color=autoPrimary, linewidth=2.5),
        whiskerprops=dict(color=autoSecondary, linewidth=1.5),
        capprops=dict(color=autoSecondary, linewidth=1.5),
        flierprops=dict(
            markerfacecolor=autoSecondary, markeredgecolor=autoPrimary, markersize=5
        ),
    )
    tele_boxplot = plt.boxplot(
        teleShots_data,
        labels=team_nums,  # type: ignore
        patch_artist=True,
        boxprops=dict(facecolor=teleSecondary, edgecolor=telePrimary),
        medianprops=dict(color=telePrimary, linewidth=2.5),
        whiskerprops=dict(color=teleSecondary, linewidth=1.5),
        capprops=dict(color=teleSecondary, linewidth=1.5),
        flierprops=dict(
            markerfacecolor=teleSecondary, markeredgecolor=telePrimary, markersize=5
        ),
    )

    climb_boxplot = plt.boxplot(
        climb_data,
        labels=team_nums,  # type: ignore
        patch_artist=True,
        boxprops=dict(facecolor=climbSecondary, edgecolor=climbPrimary),
        medianprops=dict(color=climbPrimary, linewidth=2.5),
        whiskerprops=dict(color=climbSecondary, linewidth=1.5),
        capprops=dict(color=climbSecondary, linewidth=1.5),
        flierprops=dict(
            markerfacecolor=climbSecondary, markeredgecolor=climbPrimary, markersize=5
        ),
    )

    extend_boxplot_medians(auto_boxplot, scale=1.6)
    extend_boxplot_medians(tele_boxplot, scale=1.6)
    extend_boxplot_medians(climb_boxplot, scale=1.6)
    plt.xlabel("Team Number")
    plt.ylabel("Scores")
    plt.title("Average Scores by Category")
    plt.ylabel("Average Score")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.legend(
        handles=[
            Patch(facecolor=autoSecondary, edgecolor=autoPrimary, label="Auto"),
            Patch(facecolor=teleSecondary, edgecolor=telePrimary, label="Teleop"),
            Patch(facecolor=climbSecondary, edgecolor=climbPrimary, label="Climb"),
        ]
    )
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main.main()
