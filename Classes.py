from enum import Enum


class AutoEvent:
    def __init__(
        self,
        x: float,
        y: float,
        driveType: str,
        hopperPercent: float,
        shotsPercent: float,
        timeSeconds: float,
    ):
        self.x = x
        self.y = y
        self.driveType = driveType
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
        self.selectTeam = teamNum
        self.autoEvents = autoEvents
        self.teleEvents = teleEvents
        self.climb = climb
        self.comments = comments
        self.broken = broken
        self.defense = defense
