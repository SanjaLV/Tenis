"""
Module with AchievementBase - base class for achievements plugins
"""

from enum import Enum, auto, unique
from typing import Tuple, List


@unique
class Status(Enum):
    NOTHING = auto()
    FINISHED = auto()
    SAVE = auto()


"""
Helper structure contained plugin registration info.
"""


class AchievementsInfo:
    def __init__(self, save_progress: bool = False,  # Save progress after process
                 winner: bool = False,  # Need to call for winer
                 loser: bool = False,  # Need to call for loser
                 prev_games: int = 0,  # Count of previos games to pass
                 statistic: bool = False):  # Need to pass statistic
        self.save_progress = save_progress
        self.winner = winner
        self.loser = loser
        self.prev_games = prev_games
        self.statistic = statistic

    def __str__(self) -> str:
        res = ""
        for name, value in self.__dict__.items():
            if value is not None:
                if not value:
                    if res != "":
                        res += " "
                    res += name + ": " + str(value) + ""

        return res


class AchievementsData:
    def __init__(self, progress: int = None,  # Achievements progress
                 is_winner: bool = None,  # Current usere is winner?
                 prev_games: List[any] = None,  # List with previous games
                 statistic: any = None):  # Player statistic
        if progress is not None:
            self.progress = progress
        if is_winner is not None:
            self.is_winner = is_winner
        if prev_games is not None:
            self.prev_games = prev_games
        if statistic is not None:
            self.statistic = statistic


class Achievement:
    def __init__(self, pk):
        self.pk = pk

    def register(self) -> AchievementsInfo:
        pass

    def progress(self, data: AchievementsData) -> Tuple[Status, int]:
        pass
