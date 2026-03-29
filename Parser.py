import json
from Classes import *
import os
import main


def _parse_percent(value) -> float:
    if value is None or value == "":
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    if text.endswith("%"):
        text = text[:-1]

    try:
        return float(text) / 100.0
    except ValueError:
        return 0.0


def _parse_number(value, default: float = 0.0) -> float:
    if value is None or value == "":
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_int(value, default: int = 0) -> int:
    if value is None or value == "":
        return default

    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _parse_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False

    text = str(value).strip().lower()
    return text in {"true", "1", "yes", "y"}


def _parse_alliance(value) -> Alliance:
    text = str(value).strip()
    for alliance in Alliance:
        if alliance.value.lower() == text.lower():
            return alliance
    return Alliance.RED  # Default to RED if not recognized


def _parse_json_list(value) -> list[dict]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
            if isinstance(decoded, list):
                return [item for item in decoded if isinstance(item, dict)]
        except json.JSONDecodeError:
            return []
    return []


def _parse_auto_events(value) -> list[AutoEvent]:
    events: list[AutoEvent] = []
    for item in _parse_json_list(value):
        shot_info = item.get("shotInfo") or {}
        events.append(
            AutoEvent(
                x=_parse_number(item.get("x")),
                y=_parse_number(item.get("y")),
                hopperPercent=_parse_percent(shot_info.get("hopperPercent")),
                shotsPercent=_parse_percent(shot_info.get("shotsPercent")),
                timeSeconds=_parse_number(item.get("timeSeconds")),
            )
        )
    return events


def _parse_fuel_source(value) -> FuelSource:
    text = str(value).strip()
    for fuel_source in FuelSource:
        if fuel_source.value == text:
            return fuel_source
    return FuelSource.DEPOT


def _parse_drive_train_type(value) -> DriveTrainType:
    text = str(value).strip()
    for drivetrain in DriveTrainType:
        if drivetrain.value.lower() == text.lower():
            return drivetrain
    return DriveTrainType.OTHER


def _parse_climbing_ability(value) -> int:
    if value is None:
        return 0

    text = str(value).strip()
    if text == "":
        return 0

    lowered = text.lower()
    if lowered == "none":
        return 0
    if lowered.startswith("level"):
        return _parse_int(lowered.replace("level", "", 1).strip())

    parsed = _parse_int(text, default=-1)
    if parsed >= 0:
        return parsed

    digits = "".join(char for char in text if char.isdigit())
    if digits:
        return _parse_int(digits)
    return 0


def _parse_tele_events(value) -> list[TeleEvent]:
    events: list[TeleEvent] = []
    for item in _parse_json_list(value):
        events.append(
            TeleEvent(
                fuelSource=_parse_fuel_source(item.get("source")),
                hopperPercent=_parse_percent(item.get("hopperPercent")),
                shotsPercent=_parse_percent(item.get("shotsPercent")),
                timeSeconds=_parse_number(item.get("timeSeconds")),
            )
        )
    return events


def _parse_pit_row(row: list, col_index: dict[str, int]) -> PitData:
    def v(name: str, default=""):
        idx = col_index.get(name)
        if idx is None or idx >= len(row):
            return default
        return row[idx]

    image_data: str | None = None
    if _parse_bool(v("photoTaken")):
        raw_image = str(v("imageSrc", "")).strip()
        image_data = raw_image if raw_image else None

    return PitData(
        scouterInitials=str(v("scouterInitials", "")),
        teamNum=_parse_int(v("teamNumber")),
        drivetrainType=_parse_drive_train_type(v("drivetrainType")),
        weight=_parse_number(v("weight")),
        climbingAbility=_parse_climbing_ability(v("climbingAbility")),
        maxFuelStorage=_parse_int(v("maxFuelStorage")),
        trenchDriveAbility=_parse_bool(v("trenchDriveAbility")),
        rotatableShooter=_parse_bool(v("rotatableShooter")),
        intakeFromDepot=_parse_bool(v("intakeFromDepot")),
        intakeFromOutpost=_parse_bool(v("intakeFromOutpost")),
        image=image_data,
    )


def _parse_climb(value) -> Climb:
    if not isinstance(value, dict):
        return Climb(position="", timeSeconds=0.0, failed=False)

    position_value = value.get("position")
    time_seconds_value = value.get("timeSeconds")
    failed_value = value.get("failed")

    position = str(position_value) if position_value is not None else ""
    time_seconds = _parse_number(time_seconds_value)
    failed = _parse_bool(failed_value)

    return Climb(position=position, timeSeconds=time_seconds, failed=failed)


def _parse_defense(value) -> Defense | None:
    if not isinstance(value, dict):
        return None

    if value.get("playedDefense") is not True:
        return None

    time_value = value.get("time")
    skill_value = value.get("skill")

    time = _parse_percent(str(time_value)) if time_value is not None else 0.0
    skill = str(skill_value) if skill_value is not None else ""

    return Defense(time=time, skill=skill)


def _parse_match_row(row: list, col_index: dict[str, int]) -> MatchData:
    def v(name: str, default=""):
        idx = col_index.get(name)
        if idx is None or idx >= len(row):
            return default
        return row[idx]

    climb_position = str(v("climbPosition", "")).strip()
    climb_time = _parse_number(v("climbTimeSeconds"))
    climb_failed = _parse_bool(v("climbFailed"))

    climb_data: Climb | None = None
    if climb_position or climb_time > 0.0 or climb_failed:
        climb_data = _parse_climb(
            {
                "position": climb_position,
                "timeSeconds": climb_time,
                "failed": climb_failed,
            }
        )

    return MatchData(
        matchNumber=_parse_int(v("matchNumber")),
        alliance=_parse_alliance(v("alliance", "")),
        scouterInitials=str(v("scouterInitials", "")),
        teamNum=_parse_int(v("selectTeam")),
        autoEvents=_parse_auto_events(v("autoRobotPositions", "")),
        teleEvents=_parse_tele_events(v("fuelShotAndSourceInfo", "")),
        climb=climb_data,
        comments=str(v("comments", "")),
        broken=str(v("brokenDownTime", "")),
        defense=_parse_defense(
            {
                "playedDefense": _parse_bool(v("playedDefense")),
                "time": v("defenseTime", ""),
                "skill": v("defenseSkill", ""),
            }
        ),
    )


def parse_match_data_table(table: list[list]) -> list[MatchData]:
    if not table:
        return []

    headers = table[0]
    if not isinstance(headers, list):
        raise ValueError("Expected first row to contain header names.")

    col_index = {str(name): idx for idx, name in enumerate(headers)}

    parsed: list[MatchData] = []
    for row in table[1:]:
        if not isinstance(row, list):
            continue
        parsed.append(_parse_match_row(row, col_index))
    return parsed


def parse_match_data_file(file_path: str) -> list[MatchData]:
    with open(file_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, list):
        raise ValueError("Expected JSON file root to be a list of rows.")
    return parse_match_data_table(raw)


def parse_pit_data_table(table: list[list]) -> list[PitData]:
    if not table:
        return []

    headers = table[0]
    if not isinstance(headers, list):
        raise ValueError("Expected first row to contain header names.")

    col_index = {str(name): idx for idx, name in enumerate(headers)}

    parsed: list[PitData] = []
    for row in table[1:]:
        if not isinstance(row, list):
            continue
        parsed.append(_parse_pit_row(row, col_index))
    return parsed


def parse_pit_data_file(file_path: str) -> list[PitData]:
    with open(file_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, list):
        raise ValueError("Expected JSON file root to be a list of rows.")
    return parse_pit_data_table(raw)


def team_dict(matchData: list[MatchData]) -> dict[int, list[MatchData]]:
    teamMatches = {}
    for match in matchData:
        team = match.teamNum
        if team not in teamMatches:
            teamMatches[team] = []
        teamMatches[team].append(match)
    return teamMatches  # type: ignore


def pit_dict(pitData: list[PitData]) -> dict[int, PitData]:
    pits: dict[int, PitData] = {}
    for pit in pitData:
        pits[pit.teamNum] = pit
    return pits


def merge_team_data(
    matches_by_team: dict[int, list[MatchData]],
    pits_by_team: dict[int, PitData],
) -> dict[int, TeamData]:
    all_teams = set(matches_by_team.keys()) | set(pits_by_team.keys())
    merged: dict[int, TeamData] = {}

    for team_num in all_teams:
        merged[team_num] = TeamData(
            teamNum=team_num,
            pit_data=pits_by_team.get(team_num),
            matches=matches_by_team.get(team_num),
        )

    return merged


def remove_duplicate_matches(matchData: list[MatchData]) -> list[MatchData]:
    seen = set()
    unique = []
    for match in matchData:
        identifier = (
            match.matchNumber,
            match.teamNum,
            match.scouterInitials,
        )
        if identifier not in seen:
            seen.add(identifier)
            unique.append(match)
    return unique


def remove_duplicate_pits(pitData: list[PitData]) -> list[PitData]:
    seen_teams = set()
    unique = []
    for pit in pitData:
        if pit.teamNum in seen_teams:
            continue
        seen_teams.add(pit.teamNum)
        unique.append(pit)
    return unique


def sort_team_data(teamData: dict[int, TeamData]) -> dict[int, TeamData]:
    # Sort the team data by team number
    return dict(sorted(teamData.items(), key=lambda item: item[0]))


def parse_folder(folder_name: str) -> dict[int, TeamData] | None:
    # Open folder within same directory as this script and find all .json files.
    data_folder = os.path.join(os.path.dirname(__file__), folder_name)
    if not os.path.exists(data_folder):
        print(f"Data folder not found at {data_folder}")
        return None
    json_files = [f for f in os.listdir(data_folder) if f.endswith(".json")]
    if not json_files:
        print(f"No .json files found in {data_folder}")
        return None
    match_data: list[MatchData] = []
    pit_data: list[PitData] = []
    for json_file in json_files:
        file_path = os.path.join(data_folder, json_file)
        if "VScouter" not in json_file:
            continue  # Only parse real files
        try:
            if "MatchData" in json_file:
                match_data.extend(parse_match_data_file(file_path))
            elif "PitData" in json_file:
                pit_data.extend(parse_pit_data_file(file_path))
        except Exception as e:
            print(f"Error parsing {json_file}: {e}")
            return None

    matches = remove_duplicate_matches(match_data)
    pits = remove_duplicate_pits(pit_data)
    team_dict_result = team_dict(matches)
    pit_dict_result = pit_dict(pits)
    team_data = merge_team_data(team_dict_result, pit_dict_result)
    print(
        f"Successfully parsed {len(team_data)} teams from {len(matches)} matches and {len(pits)} pit entries across {len(json_files)} files."
    )
    return sort_team_data(team_data)


if __name__ == "__main__":
    main.main()
