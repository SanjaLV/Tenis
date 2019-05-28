import time
from datetime import datetime
from random import randint, random

from django.core.management.base import BaseCommand

from django.contrib.auth.models import User
from django.utils import timezone

from caching.cache import Cacher

from core.models import Player, Statistic, Game


class Command(BaseCommand):
    help = 'Create random data'


    def add_arguments(self, parser):
        parser.add_argument('games', type=int, help='Games to simulate', default=100)

    def handle(self, *args, **kwargs):
        start_time = time.time()

        player_cache = Cacher()
        statistic_cache = Cacher()

        names = "Sol Fred Patricia Hettie Luana Shonda Gabriele Antionette Joaquin Elroy Cyrstal Lamonica Esperanza Blanch Yong Mazie Charla Gwen Torrie Katherin".split()
        pks = []
        strengths = []

        name_count = len(names)

        for name in names:
            user = User.objects.create_user(username=name, password="123")
            player = Player.objects.create(user=user, name=name)
            stat = Statistic.objects.create(player=player)
            pks.append(player.pk)
            strengths.append(randint(1, 100))

            player_cache.create(pk=player.pk, item=player, unique=player.name)
            statistic_cache.create(pk=stat.pk, item=stat, unique=player.pk)

        game_bulk = []

        for x in range(kwargs["games"]):
            pk_1 = randint(0, name_count-1)
            pk_2 = pk_1
            while pk_1 == pk_2:
                pk_2 = randint(0, name_count - 1)

            p1 = player_cache.get(pk=pks[pk_1])
            p2 = player_cache.get(pk=pks[pk_2])

            score1 = 0
            score2 = 0

            for _ in range(7):
                if random() <= strengths[pk_1] / (strengths[pk_1] + strengths[pk_2]):
                    score1 += 1
                else:
                    score2 += 1

            game = Game(player1=p1, elo1=p1.elo, player2=p2, elo2=p2.elo, score1=score1, score2=score2, verified=True, date=timezone.now())
            game.calculate()

            # update cache
            p1.elo += game.change
            p2.elo -= game.change

            s1 = statistic_cache.get(unique=p1.pk)
            s2 = statistic_cache.get(unique=p2.pk)

            s1.games += 1
            s2.games += 2

            if game.player1_win():
                s1.wins += 1
            else:
                s2.wins += 1

            # cache done

            game_bulk.append(game)
            print("Done", x)

        # save all players
        for pk, item in player_cache.data.items():
            item.save()

        # save all stats
        for pk, item in statistic_cache.data.items():
            item.save()

        # create all games
        Game.objects.bulk_create(game_bulk)

        end_time = time.time()
        print('Done in {:.3f} ms'.format((end_time - start_time) * 1000.0))








