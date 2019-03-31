from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Player(models.Model):
    name   = models.CharField(max_length=30)
    elo    = models.IntegerField()
    userID = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class Game(models.Model):
    player1 = models.ForeignKey(Player, on_delete=models.PROTECT, related_name="player_one")
    player2  = models.ForeignKey(Player, on_delete=models.PROTECT, related_name="player_two")
    score1   = models.IntegerField(default=0)
    score2   = models.IntegerField(default=0)
    elo1     = models.IntegerField()
    elo2     = models.IntegerField()
    change   = models.IntegerField()
    date     = models.DateTimeField()
    verified = models.BooleanField(default=False)

