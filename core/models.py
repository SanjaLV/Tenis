from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Player(models.Model):
    name   = models.CharField(max_length=30)
    elo    = models.IntegerField()
    userID = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name + "[" + str(self.elo) + "]"

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

    def __str__(self):
        output = "%s(%d) %d - %d %s(%d)" % (self.player1.name, self.elo1,
                                            self.score1, self.score2,
                                            self.player2.name, self.elo2)
        return output

    def p1win(self):
        if (self.score1 > self.score2):
            return "success"
        else:
            return "danger"

    def p2win(self):
        if (self.score2 > self.score1):
            return "success"
        else:
            return "danger"