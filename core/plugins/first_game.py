"""
Play first match example Achievement
"""

from core.plugins.plugin_interface import Achievement, AchievementsInfo, Status


class FirstGame(Achievement):

    def __init__(self):
        Achievement.__init__(self, name="I wanna be the very best", desc="Play your first game.")

    def register(self):
        info = AchievementsInfo(save_progress=False,
                                winner=True,
                                loser=True,
                                prev_games=0,
                                statistic=False)
        return info

    def progress(self, data):
        return Status.FINISHED, None


class FirstWin(Achievement):

    def __init__(self):
        Achievement.__init__(self, name="Easy game, easy win", desc="Win your first game.")

    def register(self):
        info = AchievementsInfo(winner=True)
        return info

    def progress(self, data):
        return Status.FINISHED, None


class FirstLose(Achievement):

    def __init__(self):
        Achievement.__init__(self, name="Start of losers journey", desc="Lose your first game.")

    def register(self):
        info = AchievementsInfo(loser=True)
        return info

    def progress(self, data):
        return Status.FINISHED, None


# This is intentionally writen without usage of statistics.wins, to test progress save/load
# Win games_to_win to get achievement
class WinGames(Achievement):

    def __init__(self, games_to_win, name):
        desc = "Win %d games." % games_to_win
        Achievement.__init__(self, name=name, desc=desc)
        self.games_to_win = games_to_win

    def register(self):
        info = AchievementsInfo(winner=True,
                                save_progress=True,
                                max_progress=self.games_to_win)
        return info

    def progress(self, data):
        progress = data.progress + 1
        if progress == self.games_to_win:
            return Status.FINISHED, None
        else:
            return Status.SAVE, progress


def setPlugins(plugin_list):
    plugin_list.append(FirstGame())
    plugin_list.append(FirstWin())
    plugin_list.append(FirstLose())
    plugin_list.append(WinGames(games_to_win=5, name="Win 5 games."))
    plugin_list.append(WinGames(games_to_win=50, name="Win 50 games."))
    plugin_list.append(WinGames(games_to_win=200, name="I have won so many times."))
    plugin_list.append(WinGames(games_to_win=500, name="Tennis champion"))


# How to add new Achievement
#
# 1 Create Achievement model in admin page
# 2 Create plugin
# 3 register plugin
# 3.1 define setPlugins(plist)
# 3.2 call setPlugins from apps.py
# 4 Done
