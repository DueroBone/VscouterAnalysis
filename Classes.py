from enum import Enum
import numpy as np

sqrt_data = True


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
    # DEPOT = "Depot or Outpost"

    # Depot is interpreted as recieved shuttle, as a
    # large number of balls are piled under driver stations
    # and it can be hard to differentiate between the two.


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
    def __init__(self, position: str, timeSeconds: int, failed: bool):
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
        # base64 encoded webp image string, or None if no image was provided
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
        """Returns the maximum fuel storage capacity of the robot, as reported in the pit data."""
        if self.pit_data is None:
            raise Exception(f"No pit data for team {self.teamNum}")
        return self.pit_data.maxFuelStorage

    def getTeleShots(self) -> list[np.ndarray]:
        """Returns a list of numpy arrays, where each array contains the number of shots scored in each teleop event (shot) for a match."""
        if self.matches is None:
            return list[np.ndarray]()
        shots: list[np.ndarray] = []
        for i, match in enumerate(self.matches):
            matchShots = np.zeros(len(match.teleEvents), dtype=float)
            for j, teleEvent in enumerate(match.teleEvents):
                if teleEvent.fuelSource in (
                    FuelSource.CENTER,
                    # FuelSource.DEPOT,
                    FuelSource.RECIEVE_SHUTTLE,
                ):  # if scoring shots
                    if sqrt_data:
                        matchShots[j] = (
                            teleEvent.hopperPercent * teleEvent.shotsPercent
                        ) ** 0.5 * self.getCapacity()  # type: ignore
                    else:
                        matchShots[j] = (
                            teleEvent.hopperPercent
                            * teleEvent.shotsPercent
                            * self.getCapacity()  # type: ignore
                        )
            shots.append(matchShots)
        return shots

    def getAutoShots(self) -> list[np.ndarray]:
        """Returns a list of numpy arrays, where each array contains the number of shots scored in each autonomous event (shot) for a match."""
        if self.matches is None:
            return list[np.ndarray]()
        shots: list[np.ndarray] = []
        for i, match in enumerate(self.matches):
            matchShots = np.zeros(len(match.autoEvents), dtype=float)
            for j, autoEvent in enumerate(match.autoEvents):
                try:
                    if sqrt_data:
                        matchShots[j] = float(
                            (autoEvent.hopperPercent * autoEvent.shotsPercent) ** 0.5
                            * self.getCapacity()
                        )  # type: ignore
                    else:
                        matchShots[j] = float(
                            autoEvent.hopperPercent
                            * autoEvent.shotsPercent
                            * self.getCapacity()  # type: ignore
                        )
                except Exception as e:
                    print(
                        f"Error calculating auto shots for team {self.teamNum} in match {match.matchNumber}: {e}"
                    )
                    matchShots[j] = 0
            shots.append(matchShots)
        return shots

    def getAvgShots(self) -> tuple[float, float]:
        """Returns a tuple containing the average number of shots scored in autonomous and teleop, respectively."""
        autoShots = self.getAutoShots()
        totalAutoShots = float(np.sum([np.sum(match) for match in autoShots]))
        numAutoMatches = len(autoShots)
        avgAutoShots = totalAutoShots / numAutoMatches if numAutoMatches > 0 else 0
        teleShots = self.getTeleShots()
        totalTeleShots = float(np.sum([np.sum(match) for match in teleShots]))
        numTeleMatches = len(teleShots)
        avgTeleShots = totalTeleShots / numTeleMatches if numTeleMatches > 0 else 0
        return avgAutoShots, avgTeleShots

    def getClimbData(self) -> np.ndarray:
        """Returns a numpy array containing the climbing height for each match.
        Vscouter does not differentiate between different levels of climb, so this is just the maximum climb height.
        """
        if self.matches is None:
            return np.array([])
        climbData = []
        for match in self.matches:
            if match.climb is not None:
                climbData.append(self.pit_data.climbingAbility if self.pit_data else 0)  # type: ignore
            else:
                climbData.append(0)
        return np.array(climbData, dtype=int)
