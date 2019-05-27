from random import randint, random

from django.core.management.base import BaseCommand

from django.contrib.auth.models import User
from django.db import transaction

from core.models import Player, Statistic, Game


class Command(BaseCommand):
    help = 'Create random data'


    def add_arguments(self, parser):
        parser.add_argument('games', type=int, help='Games to simulate', default=100)

    def handle(self, *args, **kwargs):
        names = "Sol Fred Patricia Hettie Luana Shonda Gabriele Antionette Joaquin Elroy Cyrstal Lamonica Esperanza Blanch Yong Mazie Charla Gwen Torrie Katherin".split()
        pks = []
        strengths = []

        name_count = len(names)

        for name in names:
            user = User.objects.create_user(username=name, password="123")
            player = Player.objects.create(user=user, name=name)
            Statistic.objects.create(player=player)
            pks.append(player.pk)
            strengths.append(randint(1, 100))

        for x in range(kwargs["games"]):
            pk_1 = randint(0, name_count-1)
            p1 = Player.objects.get(pk=pks[pk_1])
            pk_2 = pk_1
            while pk_1 == pk_2:
                pk_2 = randint(0, name_count - 1)

            p2 = Player.objects.get(pk=pks[pk_2])

            score1 = 0
            score2 = 0

            for _ in range(7):
                if random() <= strengths[pk_1] / (strengths[pk_1] + strengths[pk_2]):
                    score1 += 1
                else:
                    score2 += 1

            game = Game.objects.create(player1=p1, elo1=p1.elo, player2=p2, elo2=p2.elo, score1=score1, score2=score2, verified=True)
            game.accept_game()

            print("Done", x)







