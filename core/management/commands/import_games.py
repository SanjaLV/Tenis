import os
import time

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import datetime_safe

from core.models import Player, Game, Statistic

from caching.cache import Cacher

TODO_user = None

player_cache = Cacher()
statistic_cache = Cacher()


def normalize_name(name):
    """Capitalize all words in name."""
    words = name.split()
    res = ""
    for w in words:
        if res != "":
            res += " "
        res += w.capitalize()
    return res


def get_date(s):
    """Returns date object from string."""
    if s.find(".") != -1:
        # DD.MM.YYYY(.) format
        args = s.split(".")
        if args[len(args) - 1] == "":
            args.pop()
        args.reverse()
    else:
        # YYYY-MM-DD format
        args = s.split("-")

    args = list(map(int, args))
    return datetime_safe.date(args[0], args[1], args[2])


def process(games, params):
    id = int(params[0])
    date = get_date(params[1])
    player1_name = normalize_name(params[2])
    score1 = int(params[3])
    player2_name = normalize_name(params[4])
    score2 = int(params[5])

    # get cached players
    player1 = player_cache.get(unique=player1_name)
    player2 = player_cache.get(unique=player2_name)

    # get cached statistics
    stat1 = statistic_cache.get(unique=player1.pk)
    stat2 = statistic_cache.get(unique=player2.pk)

    this_game = Game(player1=player1, score1=score1, elo1=player1.elo,
                     player2=player2, score2=score2, elo2=player2.elo,
                     verified=True, date=date)
    this_game.calculate()

    games.append(this_game)

    # update ratings and stats
    player1.elo += this_game.change
    player2.elo -= this_game.change

    stat1.games += 1
    stat2.games += 1
    if this_game.player1_win():
        stat1.wins += 1
    else:
        stat2.wins += 1



class CSVParser(object):
    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(filename):
            self.ok = False
            return
        self.ok = True

    def parse(self):
        global TODO_user
        TODO_user, flag = User.objects.get_or_create(username="TODO")

        # Collect all player names

        names = []

        with open(self.filename, "r") as f:
            for line in f:
                splited_line = line.split(",")
                if splited_line[0] == "Nr":
                    continue
                if splited_line[1] == "":
                    continue
                if len(splited_line) >= 6:
                    normalized_name = normalize_name(splited_line[2])
                    if normalized_name not in names:
                        names.append(normalized_name)
                    normalized_name = normalize_name(splited_line[4])
                    if normalized_name not in names:
                        names.append(normalized_name)

        # Create all players
        players = []

        for name in names:
            players.append(Player(name=name, user=TODO_user))

        Player.objects.bulk_create(players)

        players = Player.objects.all()

        # Create players statistics
        statistics = []
        for player in players:
            statistics.append(Statistic(player=player))

        Statistic.objects.bulk_create(statistics)

        statistics = Statistic.objects.all()

        # Cache all data
        for player in players:
            player_cache.create(pk=player.pk, item=player, unique=player.name)

        for stat in statistics:
            statistic_cache.create(pk=stat.pk, item=stat, unique=stat.player.pk)

        # Process games
        games = []

        with open(self.filename, "r") as f:
            for line in f:
                splited_line = line.split(",")
                if splited_line[0] == "Nr":
                    continue
                if splited_line[1] == "":
                    continue
                if len(splited_line) >= 6:
                    process(games, splited_line[:6])
                    # NO DATA P1 S1 P2 S2
                    # 0  1    2  3  4  5

        # Create all games
        Game.objects.bulk_create(games)

        # Atomic update all data
        with transaction.atomic():
            for key, player in player_cache.data.items():
                player.save()
            for key, stat in statistic_cache.data.items():
                stat.save()


class Command(BaseCommand):
    help = 'Import games from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='Games csv file')

    def handle(self, *args, **kwargs):
        start_time = time.time()
        file = kwargs["file"]

        parser = CSVParser(file)
        if not parser.ok:
            self.stdout.write(self.style.ERROR('File "%s" does not exist.' % file))
        else:
            self.stdout.write(self.style.SUCCESS('Start'))
            parser.parse()
            self.stdout.write(self.style.SUCCESS('DONE'))

        end_time = time.time()
        self.stdout.write(self.style.SUCCESS('Done in {:.3f} ms'.format((end_time - start_time) * 1000.0)))
