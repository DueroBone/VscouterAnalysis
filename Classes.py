from enum import Enum


class AutoEvent:
    def __init__(
        self,
        x: float,
        y: float,
        hopperPercent: float,
        shotsPercent: float,
        timeSeconds: float,
    ):
        self.x = x
        self.y = y
        self.hopperPercent = hopperPercent
        self.shotsPercent = shotsPercent
        self.timeSeconds = timeSeconds


class FuelSource(Enum):
    CENTER = "Center Pick Up"
    CENTER_SHUTTLE = "Center Shuttle"
    RECIEVE_SHUTTLE = "Received Shuttle"
    DEPOT = "Depot or Outpost"


class TeleEvent:
    def __init__(
        self,
        fuelSource: FuelSource,
        hopperPercent: float,
        shotsPercent: float,
        timeSeconds: float,
    ):
        self.fuelSource = fuelSource
        self.hopperPercent = hopperPercent
        self.shotsPercent = shotsPercent
        self.timeSeconds = timeSeconds


class Climb:
    def __init__(self, position: str, timeSeconds: float, failed: bool):
        self.position = position
        self.timeSeconds = timeSeconds
        self.failed = failed


class Defense:
    def __init__(self, time: float, skill: str):
        self.time = time
        self.skill = skill


class Alliance(Enum):
    RED = "redAlliance"
    BLUE = "blueAlliance"


class MatchData:
    def __init__(
        self,
        matchNumber: int,
        alliance: Alliance,
        scouterInitials: str,
        teamNum: int,
        autoEvents: list[AutoEvent],
        teleEvents: list[TeleEvent],
        climb: Climb | None,
        comments: str,
        broken: str,
        defense: Defense | None,
    ):
        self.matchNumber = matchNumber
        self.alliance = alliance
        self.scouterInitials = scouterInitials
        self.teamNum = teamNum
        self.autoEvents = autoEvents
        self.teleEvents = teleEvents
        self.climb = climb
        self.comments = comments
        self.broken = broken
        self.defense = defense


class DriveTrainType(Enum):
    SWERVE = "Swerve"
    TANK = "Tank"
    MECANUM = "Mecanum"
    OTHER = "Other"


class PitData:
    def __init__(
        self,
        scouterInitials: str,
        teamNum: int,
        drivetrainType: DriveTrainType,
        weight: float,
        climbingAbility: int,
        maxFuelStorage: int,
        trenchDriveAbility: bool,
        rotatableShooter: bool,
        intakeFromDepot: bool,
        intakeFromOutpost: bool,
        image: str | None,
    ):
        self.teamNum = teamNum
        self.scouterInitials = scouterInitials
        self.drivetrainType = drivetrainType
        self.weight = weight
        self.climbingAbility = climbingAbility
        self.maxFuelStorage = maxFuelStorage
        self.trenchDriveAbility = trenchDriveAbility
        self.rotatableShooter = rotatableShooter
        self.intakeFromDepot = intakeFromDepot
        self.intakeFromOutpost = intakeFromOutpost
        self.image = image


class TeamData:
    def __init__(
        self, teamNum: int, pit_data: PitData | None, matches: list[MatchData] | None
    ):
        self.teamNum = teamNum
        self.pit_data: PitData | None = pit_data
        self.matches: list[MatchData] | None = matches

    def getCapacity(self) -> int | None:
        if self.pit_data is None:
            raise Exception(f"No pit data for team {self.teamNum}")
        return self.pit_data.maxFuelStorage

    def getTeleShots(self) -> list[list[int]]:
        if self.matches is None:
            return []
        shots = []
        for match in self.matches:
            matchShots = []
            for teleEvent in match.teleEvents:
                if teleEvent.fuelSource in (
                    FuelSource.CENTER,
                    FuelSource.DEPOT,
                    FuelSource.RECIEVE_SHUTTLE,
                ):  # if scoring shots
                    matchShots.append(
                        teleEvent.hopperPercent
                        * teleEvent.shotsPercent
                        * self.getCapacity()  # type: ignore
                    )
            shots.append(matchShots)
        return shots

    def getAutoShots(self) -> list[list[int]]:
        if self.matches is None:
            return []
        shots = []
        for match in self.matches:
            matchShots = []
            for autoEvent in match.autoEvents:
                matchShots.append(
                    autoEvent.hopperPercent
                    * autoEvent.shotsPercent
                    * self.getCapacity()  # type: ignore
                )
            shots.append(matchShots)
        return shots

    def getAvgShots(self) -> tuple[float, float]:
        autoShots = self.getAutoShots()
        totalAutoShots = sum(sum(match) for match in autoShots)
        numAutoMatches = len(autoShots)
        avgAutoShots = totalAutoShots / numAutoMatches if numAutoMatches > 0 else 0
        teleShots = self.getTeleShots()
        totalTeleShots = sum(sum(match) for match in teleShots)
        numTeleMatches = len(teleShots)
        avgTeleShots = totalTeleShots / numTeleMatches if numTeleMatches > 0 else 0
        return avgAutoShots, avgTeleShots
