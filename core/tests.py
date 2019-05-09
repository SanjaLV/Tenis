from django.test import TestCase

# Create your tests here.
from core.management.commands.import_games import normalize_name
from .models import Game, Player


class TestGame(TestCase):
    def setUp(self):
        pl = Player.objects.create(name="test", elo=0)

        Game.objects.create(player1=pl, player2=pl, score1=3, score2=4, elo1=0, elo2=0)
        Game.objects.create(player1=pl, player2=pl, elo1=1000, elo2=500, change=+10)
        Game.objects.create(player1=pl, player2=pl, elo1=1000, elo2=500, change=-7)

    def test_win(self):
        self.assertEqual(Game.objects.get(pk=1).player1_badge(), "danger")
        self.assertEqual(Game.objects.get(pk=1).player2_badge(), "success")
        self.assertFalse(Game.objects.get(pk=1).player1_win())
        self.assertTrue(Game.objects.get(pk=1).player2_win())

    def test_elo(self):
        self.assertEqual(Game.objects.get(pk=2).newElo1(), Game.objects.get(pk=2).elo1 + Game.objects.get(pk=2).change)
        self.assertEqual(Game.objects.get(pk=2).newElo2(), Game.objects.get(pk=2).elo2 - Game.objects.get(pk=2).change)

        self.assertEqual(Game.objects.get(pk=3).newElo1(), Game.objects.get(pk=3).elo1 + Game.objects.get(pk=3).change)
        self.assertEqual(Game.objects.get(pk=3).newElo2(), Game.objects.get(pk=3).elo2 - Game.objects.get(pk=3).change)

    def test_ended(self):
        self.assertTrue(Game.objects.get(pk=1).ended())
        self.assertFalse(Game.objects.get(pk=2).ended())
        self.assertFalse(Game.objects.get(pk=3).ended())


class TestNormalizeName(TestCase):
    def test_normalize_name(self):
        self.assertEqual(normalize_name(" AaA bB"), "Aaa Bb")
        self.assertEqual(normalize_name("   A A a A"), "A A A A")
        self.assertEqual(normalize_name("sanja"), "Sanja")
        self.assertEqual(normalize_name(" Edgars K"), "Edgars K")
