from django.core.management import BaseCommand
from django.db import transaction

from core.models import Player, Statistic, Game


def update(value, win):
    if win:
        if value > 0:
            return value + 1
        else:
            return 1
    else:
        if value < 0:
            return value - 1
        else:
            return -1


class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **options):

        # set all streak to zero
        streaks = {}
        for player in Player.objects.all():
            streaks[player.pk] = 0

        # recalculate streaks
        games = Game.objects.all()

        for game in games:
            if game.ended():
                streaks[game.player1.pk] = update(streaks[game.player1.pk], game.player1_win())
                streaks[game.player2.pk] = update(streaks[game.player2.pk], game.player2_win())

        with transaction.atomic():
            all_stats = Statistic.objects.all()
            for stat in all_stats:
                stat.streak = streaks[stat.player.pk]
                stat.save()
