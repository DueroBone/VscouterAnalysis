import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from Classes import TeamData, FuelSource
import Classes
import main
import numpy as np
import base64
from io import BytesIO
from PIL import Image


autoPrimary = "red"
autoSecondary = "pink"
telePrimary = "green"
teleSecondary = "lime"
climbPrimary = "blue"
climbSecondary = "lightblue"


def sum_inner_lists(data) -> list[float]:
    return [np.sum(sublist) for sublist in data]


def extend_boxplot_medians(boxplot: dict, scale: float = 1.5):
    # Make median line of boxplots wider to see easier
    for median in boxplot["medians"]:
        x0, x1 = median.get_xdata()
        center = (x0 + x1) / 2
        half_width = (x1 - x0) / 2
        new_half_width = half_width * scale
        median.set_xdata([center - new_half_width, center + new_half_width])


# TODO: TBA api score predictions, use for scaling?
def compare_team_scores(teams: list[TeamData], hidden_teams: list[int] = []):
    # Box plots per team and category, sorted by mean total score (auto + teleop + climb)
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

    # Calculate average shots and climbs per team
    avg_teleShots = []
    avg_autoShots = []
    avg_climbs = []  # 10 points per level
    for i in range(len(team_nums)):
        # sum each inner list then average
        avg_teleShots.append(
            np.sum([np.sum(match) for match in teleShots_data[i]])
            / len(teleShots_data[i])
            if len(teleShots_data[i]) > 0
            else 0
        )
        avg_autoShots.append(
            np.sum([np.sum(match) for match in autoShots_data[i]])
            / len(autoShots_data[i])
            if len(autoShots_data[i]) > 0
            else 0
        )
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
        zip(total_scores, team_nums, teleShots_data, autoShots_data, climb_data),
        key=lambda x: x[0],
        reverse=True,
    )
    total_scores, team_nums, teleShots_data, autoShots_data, climb_data = zip(
        *sorted_data
    )

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
    plt.title("Team Scores by Category")
    plt.ylabel("Scores")
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


def show_team_data(team: TeamData):
    plt.figure(figsize=(12, 10))

    autoShots = sum_inner_lists(team.getAutoShots())
    teleShots = sum_inner_lists(team.getTeleShots())
    climbs = team.getClimbData()
    if team.matches is not None:
        matches = [str(num.matchNumber) for num in team.matches if num.matchNumber]
    else:
        matches = []

    # Top graph, scores per match
    plt.subplot(2, 1, 1)
    max_score = max(
        max(autoShots) if autoShots else 0,
        max(teleShots) if teleShots else 0,
        max(climbs) if climbs.size > 0 else 0,
    )
    breakdown_time = [match.broken for match in team.matches or []]
    # Shortly = 0.2, A Lot = 0.5, Whole Match = 1, None = 0
    breakdown_time = [
        (
            0.2
            if x == "Shortly"
            else 0.5 if x == "A Lot" else 1 if x == "Whole Match" else 0
        )
        for x in breakdown_time
    ]
    breakdown_time = [x * max_score for x in breakdown_time]
    plt.plot(matches, autoShots, label="Auto", color=autoPrimary, marker="o")
    plt.plot(matches, teleShots, label="Teleop", color=telePrimary, marker="o")
    plt.plot(matches, climbs, label="Climb", color=climbPrimary, marker="o")
    plt.bar(
        matches,
        breakdown_time,
        label="Breakdown Time",
        color="#ff6600",
        alpha=0.3,
        width=1,
    )
    plt.axhline(
        np.mean(autoShots),  # type: ignore
        color=autoPrimary,
        linestyle="--",
        label="Auto Avg",
    )
    plt.axhline(
        np.mean(teleShots),  # type: ignore
        color=telePrimary,
        linestyle="--",
        label="Teleop Avg",
    )
    plt.axhline(
        np.mean(climbs),  # type: ignore
        color=climbPrimary,
        linestyle="--",
        label="Climb Avg",
    )
    plt.xlabel("Match number")
    plt.ylabel("Scores")
    plt.title(f"Detailed data for team {team.teamNum}")
    plt.grid(True)
    plt.legend()

    # Bottom left-top graph, fuel source breakdown
    plt.subplot(4, 3, 7)
    colors = ["orange", "purple", "cyan"]
    fuel_sources = ["Center", "Shuttle", "Received Shuttle"]
    fuel_counts: list[list[float]] = [[], [], []]
    try:
        exp = Classes.sqrt_data and 0.5 or 1  # Accounts better for high scoring
        for match in team.matches or []:
            fuel_counts[0].append(0)
            fuel_counts[1].append(0)
            fuel_counts[2].append(0)
            for teleEvent in match.teleEvents:
                if teleEvent.fuelSource == FuelSource.CENTER:
                    fuel_counts[0][-1] += teleEvent.hopperPercent**exp * team.getCapacity()  # type: ignore
                elif teleEvent.fuelSource == FuelSource.CENTER_SHUTTLE:
                    fuel_counts[1][-1] += teleEvent.hopperPercent**exp * team.getCapacity()  # type: ignore
                elif teleEvent.fuelSource == FuelSource.RECIEVE_SHUTTLE:
                    fuel_counts[2][-1] += teleEvent.hopperPercent**exp * team.getCapacity()  # type: ignore
        plt.title("Weighted Fuel Sources")
        plt.pie(
            sum_inner_lists(fuel_counts),
            colors=colors,
            explode=[0.05] * 3,
            labels=fuel_sources,
            autopct="%1.1f%%",
        )
        # plt.legend(labels=fuel_sources)
        plt.grid(axis="y")
    except Exception as e:
        plt.text(0.5, 0.5, "An error has occurred", ha="center", va="center")
        plt.axis("off")

    # Bottom left-bottom graph, fuel source per match
    plt.subplot(4, 3, 10)
    bottom = np.zeros(len(matches))
    for i in range(len(fuel_sources)):
        plt.bar(
            matches,
            fuel_counts[i],
            bottom=bottom,
            label=fuel_sources[i],
            color=colors[i],
        )
        bottom += np.array(fuel_counts[i])
    plt.xlabel("Match number")
    plt.legend()
    plt.grid(axis="y")

    # Bottom middle graph, pit data
    plt.subplot(2, 3, 5)
    if team.pit_data:
        plt.text(
            0.5,
            0.9,
            f"Max Fuel Storage: {team.pit_data.maxFuelStorage}",
            ha="center",
            va="center",
        )
        plt.text(
            0.5,
            0.8,
            f"Drivetrain: {team.pit_data.drivetrainType.value}",
            ha="center",
            va="center",
        )
        plt.text(
            0.5,
            0.7,
            f"Turreting Shooter: {team.pit_data.rotatableShooter}",
            ha="center",
            va="center",
        )
        plt.text(
            0.5,
            0.6,
            f"Trench Drive Ability: {team.pit_data.trenchDriveAbility}",
            ha="center",
            va="center",
        )
        plt.text(
            0.5,
            0.45,
            f"Climbing Ability: Level {team.pit_data.climbingAbility}",
            ha="center",
            va="center",
        )
        plt.text(
            0.5,
            0.35,
            f"Intake from Depot: {team.pit_data.intakeFromDepot}",
            ha="center",
            va="center",
        )
        plt.text(
            0.5,
            0.25,
            f"Intake from Outpost: {team.pit_data.intakeFromOutpost}",
            ha="center",
            va="center",
        )
        plt.text(
            0.5,
            0.15,
            f"Weight: {int(team.pit_data.weight)} lbs",
            ha="center",
            va="center",
        )
        if team.matches:
            climbs = [match.climb.timeSeconds for match in team.matches if match.climb]
            plt.text(
                0.5,
                0.05,
                f"Avg climb: {np.mean(climbs) if climbs else 'N/A'} seconds",
                ha="center",
                va="center",
            )
    else:
        plt.text(0.5, 0.5, "No pit data available", ha="center", va="center")
    plt.axis("off")
    plt.title("Pit Data")

    # Bottom right-top graph, img of robot
    plt.subplot(4, 3, 9)
    if team.pit_data and team.pit_data.image:
        try:
            img_data = base64.b64decode(team.pit_data.image.split(",")[1])
            img = Image.open(BytesIO(img_data))
            plt.imshow(img)
            plt.axis("off")
            plt.title("Robot Image")
        except Exception as e:
            print(f"Error loading image for team {team.teamNum}: {e}")
            plt.text(0.5, 0.5, "An error has occurred", ha="center", va="center")
            plt.axis("off")
    else:
        plt.text(0.5, 0.5, "No image available", ha="center", va="center")
        plt.axis("off")

    # Bottom right-bottom graph, clumb positions and success
    plt.subplot(4, 3, 12)
    climb_positions = ["depot", "outpost", "middle"]
    position_counts = {
        pos: [0, 0, 0] for pos in climb_positions
    }  # success, total, time
    for match in team.matches or []:
        if match.climb:
            pos = match.climb.position
            if pos in climb_positions:
                position_counts[pos][1] += 1
                position_counts[pos][2] += match.climb.timeSeconds or 0
                if not match.climb.failed:
                    position_counts[pos][0] += 1
    if sum(position_counts[pos][1] for pos in climb_positions) == 0:
        plt.text(0.5, 0.5, "No climb data available", ha="center", va="center")
    else:
        colors = []
        for pos in climb_positions:
            success_rate = (
                position_counts[pos][0] / position_counts[pos][1]
                if position_counts[pos][1] > 0
                else 0
            )
            colors.append((1 - success_rate, success_rate, 0))  # red to green
        plt.pie(
            [position_counts[pos][1] for pos in climb_positions],
            labels=climb_positions,
            autopct=lambda p: f"{p:.1f}%\n({int(p * sum(position_counts[pos][1] for pos in climb_positions) / 100)})",
            colors=colors,
            explode=[0.05] * len(climb_positions),
        )
    plt.axis("off")
    plt.title("Climb Positions and Success Rates")

    plt.tight_layout()
    plt.subplots_adjust(
        left=0.05, right=0.99, top=0.99, bottom=0.05, wspace=0, hspace=0.2
    )
    plt.show()


if __name__ == "__main__":
    main.main()
