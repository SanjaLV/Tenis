"""
Play first match example Achievement
"""

from core.plugins.plugin_interface import Achievement, AchievementsInfo, Status


class FirstGame(Achievement):
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
    def register(self):
        info = AchievementsInfo(winner=True)
        return info

    def progress(self, data):
        return Status.FINISHED, None


class FirstLose(Achievement):
    def register(self):
        info = AchievementsInfo(loser=True)
        return info

    def progress(self, data):
        return Status.FINISHED, None


# This is intentionally writen without usage of statistics.wins, to test progress save/load
# Win games_to_win to get achievement
class WinGames(Achievement):

    def __init__(self, pk, games_to_win):
        Achievement.__init__(self, pk)
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
    plugin_list.append(FirstGame(1))   # Achievement model PK = 1
    plugin_list.append(FirstWin(2))    # Achievement model PK = 2
    plugin_list.append(FirstLose(3))   # Achievement model PK = 3
    plugin_list.append(WinGames(4, 5)) # Cnt of wins = 5,  PK = 4
    plugin_list.append(WinGames(5, 50))
    plugin_list.append(WinGames(6, 200))
    plugin_list.append(WinGames(7, 500))


# How to add new Achievement
#
# 1 Create Achievement model in admin page
# 2 Create plugin
# 3 register plugin
# 3.1 define setPlugins(plist)
# 3.2 call setPlugins from apps.py
# 4 Done
