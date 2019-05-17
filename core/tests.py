from django.contrib.auth.models import User
from django.test import TestCase, Client

# Create your tests here.
import core.errors
from core.management.commands.import_games import normalize_name
from .models import Game, Player, Statistic


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


class TestPlayer(TestCase):
    def setUp(self):
        self.John = User.objects.create_user(username="John", password="Dhuhg437fus")
        self.Max = User.objects.create_user(username="Max", password="adjd8j82hDao")

    def test_create_player(self):
        self.longMessage = True
        c = Client()

        response = c.post('/core/new_player')
        self.assertEqual(response.status_code, 403)

        c.login(username="John", password="Dhuhg437fus")

        response = c.get('/core/new_player')
        self.assertEqual(response.status_code, 200)

        response = c.post('/core/new_player', {'name': 'player_one'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/core/player/1')

        response = c.post('/core/new_player', {'name': 'player_two'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/core/player/2')

        response = c.post('/core/new_player', {'name': ''})
        self.assertEqual(response.status_code, 200)

        response = c.get('/core/player/3')
        self.assertEqual(response.status_code, 403)

        response = c.post('/core/new_player', {'name': 'player_one'})
        self.assertEqual(response.status_code, 200)

        response = c.get('/core/player/3')
        self.assertEqual(response.status_code, 403)

    def test_my_players(self):
        c = Client()

        p1 = Player.objects.create(name="John", user=self.John)
        s1 = Statistic.objects.create(player=p1)
        p2 = Player.objects.create(name="Max", user=self.Max)
        s2 = Statistic.objects.create(player=p2)
        p3 = Player.objects.create(name="Max2", user=self.Max)
        s3 = Statistic.objects.create(player=p3)

        response = c.get('/core/players')
        self.assertEqual(response.status_code, 403)

        c.login(username="John", password="Dhuhg437fus")

        response = c.get('/core/players')
        self.assertEqual(response.status_code, 200)

        should_be_p = [p1]
        should_be_s = [s1]
        iteration = 0
        for p, s in response.context["players_stats"]:
            self.assertEqual(p, should_be_p[iteration])
            self.assertEqual(s, should_be_s[iteration])
            iteration += 1

        c.login(username="Max", password="adjd8j82hDao")

        response = c.get('/core/players')
        self.assertEqual(response.status_code, 200)

        should_be_p = [p2, p3]
        should_be_s = [s2, s3]

        for p, s in response.context["players_stats"]:
            self.assertEqual(p, should_be_p[iteration])
            self.assertEqual(s, should_be_s[iteration])
            iteration += 1

    def test_activate_player(self):
        c = Client()

        p1 = Player.objects.create(name="John", user=self.John)
        s1 = Statistic.objects.create(player=p1)

        respone = c.get('/core/player/1/enable')
        self.assertEqual(respone.status_code, 403)

        c.login(username="Max", password="adjd8j82hDao")

        respone = c.get('/core/player/1/enable')
        self.assertEqual(respone.status_code, 403)
