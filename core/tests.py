from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, Client

# Create your tests here.
from django.utils import timezone

from core.management.commands.import_games import normalize_name
from .models import Game, Player, Statistic


class TestGame(TestCase):
    def setUp(self):
        pl = Player.objects.create(name="test", elo=0)

        Game.objects.create(player1=pl, player2=pl, score1=3, score2=4, elo1=0, elo2=0, date=timezone.now())
        Game.objects.create(player1=pl, player2=pl, elo1=1000, elo2=500, change=+10, date=timezone.now())
        Game.objects.create(player1=pl, player2=pl, elo1=1000, elo2=500, change=-7, date=timezone.now())

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
        self.John_password = "Dhuhg437fus"
        self.Max_password = "adjd8j82hDao"
        self.John = User.objects.create_user(username="John", password=self.John_password)
        self.Max = User.objects.create_user(username="Max", password=self.Max_password)

    def test_create_player(self):
        self.longMessage = True
        c = Client()

        # Guest should not be able to acces new_player page
        response = c.post('/core/new_player')
        self.assertEqual(response.status_code, 403)

        c.login(username="John", password=self.John_password)

        # User should be able to acces it
        response = c.get('/core/new_player')
        self.assertEqual(response.status_code, 200)

        # User should be able to create player
        response = c.post('/core/new_player', {'name': 'player_one'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/core/player/1')

        # User should be able to create one more
        response = c.post('/core/new_player', {'name': 'player_two'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/core/player/2')

        # Cannot create player with empty name
        response = c.post('/core/new_player', {'name': ''})
        self.assertEqual(response.status_code, 200)
        response = c.get('/core/player/3')
        self.assertEqual(response.status_code, 403)

        # Cannot create player with already taken name
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

        # Guest should not be able to acces my players
        response = c.get('/core/players')
        self.assertEqual(response.status_code, 403)

        c.login(username="John", password=self.John_password)

        # Loged user can acces it
        response = c.get('/core/players')
        self.assertEqual(response.status_code, 200)

        should_be_p = [p1]
        should_be_s = [s1]
        iteration = 0
        for p, s in response.context["players_stats"]:
            self.assertEqual(p, should_be_p[iteration])
            self.assertEqual(s, should_be_s[iteration])
            iteration += 1
        self.assertEqual(1, iteration)
        # Respone context should contain only p1 and s1

        c.login(username="Max", password=self.Max_password)

        # Other logged user should acces it too
        response = c.get('/core/players')
        self.assertEqual(response.status_code, 200)

        should_be_p = [p2, p3]
        should_be_s = [s2, s3]
        iteration = 0
        for p, s in response.context["players_stats"]:
            self.assertEqual(p, should_be_p[iteration])
            self.assertEqual(s, should_be_s[iteration])
            iteration += 1
        self.assertEqual(2, iteration)
        # Respone context should be p2, p3 s2 s3

    def test_activate_player(self):
        c = Client()

        p1 = Player.objects.create(name="John", user=self.John)
        s1 = Statistic.objects.create(player=p1)

        # Guest user shoud not be able to access it
        response = c.post('/core/player/1/enable')
        self.assertEqual(response.status_code, 403)

        c.login(username="Max", password=self.Max_password)

        # Other user should not be able to change
        response = c.post('/core/player/1/enable')
        self.assertEqual(response.status_code, 403)

        c.login(username="John", password=self.John_password)

        # Player's user should be fine
        response = c.post('/core/player/1/enable')
        self.assertEqual(response.status_code, 302)
        p1 = Player.objects.get(pk=1)
        self.assertFalse(p1.active)


class TestGames(TestCase):
    def setUp(self):
        self.John_password = "dadawkofkoefkeofef"
        self.John = User.objects.create_user(username="John", password=self.John_password)
        self.Max_password = "daifjvmf2389jsdde"
        self.Max = User.objects.create_user(username="Max", password=self.Max_password)

        self.player_John = Player.objects.create(user=self.John)
        self.player_stat_John = Statistic.objects.create(player=self.player_John)

        self.player_John2 = Player.objects.create(user=self.John, active=False)
        self.player_stat_John2 = Statistic.objects.create(player=self.player_John2)

        self.player_Max = Player.objects.create(user=self.Max)
        self.player_stat_Max = Statistic.objects.create(player=self.player_Max)

        self.player_Max2 = Player.objects.create(user=self.Max, active=False)
        self.player_stat_Max2 = Statistic.objects.create(player=self.player_Max2)

    def test_create_game(self):
        c = Client()

        # Goest user should not access it
        response = c.get('/core/create')
        self.assertEqual(response.status_code, 403)

        c.login(username="John", password=self.John_password)

        # John should be fine
        response = c.get('/core/create')
        self.assertEqual(response.status_code, 200)

        self.assertIn(self.player_John, response.context["my_players"])
        self.assertIn(self.player_Max, response.context["other"])
        self.assertNotIn(self.player_John2, response.context["my_players"])
        self.assertNotIn(self.player_Max2, response.context["other"])

        data = {
            'player1': self.player_John.pk,
            'player2': self.player_John2.pk
        }
        response = c.post('/core/create', data)
        self.assertContains(response, "ERROR!")
        # Cannot play with yourself

        # Create game
        data["player2"] = self.player_Max.pk
        response = c.post('/core/create', data)
        self.assertRedirects(response, '/core/game/1')

        try:
            game = Game.objects.get(pk=1)
        except ObjectDoesNotExist:
            self.assertFalse(True, "except ObjectDoesNotExist")

        # Player 1 should be your player
        data["player1"] = self.player_Max2.pk
        response = c.post('/core/create', data)
        self.assertContains(response, "ERROR!")

        self.assertEqual(Game.objects.count(), 1)

    def test_delete_game(self):
        c = Client()

        game = Game.objects.create(player1=self.player_John, player2=self.player_Max, elo1=1, elo2=2, score1=3,
                                   score2=4, date=timezone.now())

        c.login(username="Max", password=self.Max_password)

        # Away player should not be able to delete
        response = c.post("/core/game/1/delete")
        self.assertEqual(response.status_code, 403)

        c.login(username="John", password=self.John_password)

        # Home player should be able, but not when scores are set
        response = c.post("/core/game/1/delete")
        self.assertRedirects(response, "/core/game/1")
        self.assertEqual(Game.objects.count(), 1)

        game.score1 = 0
        game.score2 = 0
        game.save()

        # Now finaly Home player will delete it
        response = c.post("/core/game/1/delete")
        self.assertRedirects(response, "/core/")
        self.assertEqual(Game.objects.count(), 0)

    def test_verify(self):
        c = Client()

        game = Game.objects.create(player1=self.player_John, player2=self.player_Max, elo1=1, elo2=2, score1=3,
                                   score2=4, date=timezone.now())

        c.login(username="John", password=self.John_password)

        # Home player cannot verify
        response = c.post("/core/game/1/verify")
        self.assertEqual(response.status_code, 403)

        game = Game.objects.get(pk=1)
        self.assertFalse(game.verified)
        game.score1 = 0
        game.score2 = 0
        game.save()

        c.login(username="Max", password=self.Max_password)

        # Away player
        # But scores are not set
        response = c.post("/core/game/1/verify")
        self.assertEqual(response.status_code, 403)

        game = Game.objects.get(pk=1)
        self.assertFalse(game.verified)
        game.score1 = 3
        game.score2 = 4
        game.save()

        # We are away player and scores are done
        response = c.post("/core/game/1/verify")
        self.assertRedirects(response, "/core/game/1")
        import time
        time.sleep(0.3)  # wait for Achievements thread to complete

        game = Game.objects.get(pk=1)
        self.assertTrue(game.verified)

    def test_set_score(self):
        c = Client()

        game = Game.objects.create(player1=self.player_John, player2=self.player_Max, elo1=1, elo2=2, score1=0,
                                   score2=0, date=timezone.now())

        # Guest user should not have access
        response = c.post('/core/game/1/set_score', {'score1': 1, 'score2': 0})
        self.assertEqual(response.status_code, 403)

        game = Game.objects.get(pk=1)
        self.assertFalse(game.ended())

        c.login(username="John", password=self.John_password)

        # Home player should set
        response = c.post('/core/game/1/set_score', {'score1': 1, 'score2': 0})
        self.assertRedirects(response, '/core/game/1')

        game = Game.objects.get(pk=1)
        self.assertTrue(game.ended())

        # You need to reset score first!
        response = c.post('/core/game/1/set_score', {'score1': 2, 'score2': 1})
        self.assertRedirects(response, '/core/game/1')

        game = Game.objects.get(pk=1)
        self.assertEqual(game.score1, 1)
        self.assertEqual(game.score2, 0)

    def test_reset_score(self):
        c = Client()

        game1 = Game.objects.create(player1=self.player_John, player2=self.player_Max, elo1=1, elo2=2, score1=3,
                                    score2=4, date=timezone.now())
        game2 = Game.objects.create(player1=self.player_John, player2=self.player_Max, elo1=1, elo2=2, score1=2,
                                    score2=3, verified=True, date=timezone.now())

        # Guest user cannot do this
        response = c.post('/core/game/1/reset')
        self.assertEqual(response.status_code, 403)

        c.login(username="John", password=self.John_password)

        # Home player should reset
        response = c.post('/core/game/1/reset')
        self.assertRedirects(response, "/core/game/1")

        game = Game.objects.get(pk=1)
        self.assertFalse(game.ended())

        game.score1 = 3
        game.score2 = 4
        game.save()

        # Away player should reset
        c.login(username="Max", password=self.Max_password)
        response = c.post('/core/game/1/reset')
        self.assertRedirects(response, "/core/game/1")

        game = Game.objects.get(pk=1)
        self.assertFalse(game.ended())

        # Game is already verified
        response = c.post('/core/game/2/reset')
        self.assertEqual(response.status_code, 403)

        game = Game.objects.get(pk=2)
        self.assertTrue(game.ended())

        game.verified = False
        game.save()

        # Now game is not verified so we should reset it
        response = c.post('/core/game/2/reset')
        self.assertRedirects(response, "/core/game/2")

        game = Game.objects.get(pk=2)
        self.assertFalse(game.ended())

    def test_not_verified_list(self):
        c = Client()

        game1 = Game.objects.create(player1=self.player_John, player2=self.player_Max, elo1=1, elo2=2, score1=3,
                                    score2=4, date=timezone.now())

        game2 = Game.objects.create(player1=self.player_Max, player2=self.player_John, elo1=1, elo2=2, score1=3,
                                    score2=4, date=timezone.now())

        game3 = Game.objects.create(player1=self.player_John, player2=self.player_Max, elo1=1, elo2=2, score1=0,
                                    score2=0, date=timezone.now())

        game4 = Game.objects.create(player1=self.player_Max, player2=self.player_John, elo1=1, elo2=2, score1=0,
                                    score2=0, date=timezone.now())

        game5 = Game.objects.create(player1=self.player_John, player2=self.player_Max, elo1=1, elo2=2, score1=3,
                                    score2=4, verified=True, date=timezone.now())

        game6 = Game.objects.create(player1=self.player_Max, player2=self.player_John, elo1=1, elo2=2, score1=3,
                                    score2=4, verified=True, date=timezone.now())

        # Guest user have no access here
        response = c.get("/core/to_verify")
        self.assertEqual(response.status_code, 403)

        c.login(username="John", password=self.John_password)

        # John should have 2 games to_verify
        response = c.get("/core/to_verify")
        self.assertEqual(response.status_code, 200)
        self.assertIn(game2, response.context["games"])
        self.assertIn(game4, response.context["games"])
        self.assertEqual(len(response.context["games"]), 2)

        game2.verified = True
        game2.save()

        # Now should have 1 game
        response = c.get("/core/to_verify")
        self.assertEqual(response.status_code, 200)
        self.assertIn(game4, response.context["games"])
        self.assertEqual(len(response.context["games"]), 1)

        response = c.get('/core/json/get_to_verify')
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'count': 1}
        )

        # Max should have 2 games to_verify too
        c.login(username="Max", password=self.Max_password)
        response = c.get("/core/to_verify")
        self.assertEqual(response.status_code, 200)
        self.assertIn(game1, response.context["games"])
        self.assertIn(game3, response.context["games"])
        self.assertEqual(len(response.context["games"]), 2)

        response = c.get('/core/json/get_to_verify')
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'count': 2}
        )
