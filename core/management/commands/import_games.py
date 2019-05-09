import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import datetime_safe

from core.models import Player, Game, Statistic

TODO_user = None


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

    print(args)

    args = list(map(int, args))
    return datetime_safe.date(args[0], args[1], args[2])


def process(params):
    global TODO_user
    id = int(params[0])
    date = get_date(params[1])
    player1_name = normalize_name(params[2])
    score1 = int(params[3])
    player2_name = normalize_name(params[4])
    score2 = int(params[5])

    player1, new_player1 = Player.objects.get_or_create(name=player1_name, user=TODO_user)
    player2, new_player2 = Player.objects.get_or_create(name=player2_name, user=TODO_user)

    # make sure there is statistics for players
    if new_player1:
        stat1 = Statistic.objects.create(player=player1)
    if new_player2:
        stat2 = Statistic.objects.create(player=player2)

    this_game = Game.objects.create(player1=player1, score1=score1, elo1=player1.elo,
                                    player2=player2, score2=score2, elo2=player2.elo,
                                    verified=True)
    this_game.date = date
    this_game.accept_game()  # <- will save this_game


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
        with open(self.filename, "r") as f:
            for line in f:
                splited_line = line.split(",")
                if splited_line[0] == "Nr":
                    continue
                if splited_line[1] == "":
                    continue
                if len(splited_line) >= 6:
                    process(splited_line[:6])
                    # NO DATA P1 S1 P2 S2
                    # 0  1    2  3  4  5


class Command(BaseCommand):
    help = 'Displays current time'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='Games csv file')

    def handle(self, *args, **kwargs):
        file = kwargs["file"]

        parser = CSVParser(file)
        if not parser.ok:
            self.stdout.write(self.style.ERROR('File "%s" does not exist.' % file))
        else:
            self.stdout.write(self.style.SUCCESS('Start'))
            parser.parse()
            self.stdout.write(self.style.SUCCESS('DONE'))
