from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.utils.html import format_html


class Player(models.Model):
    name   = models.CharField(max_length=30)
    elo    = models.IntegerField()
    userID = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

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

    def newElo1(self):
        return self.elo1 + self.change

    def newElo2(self):
        return self.elo2 - self.change

    def getEloChange1(self):
        tp = "success" if self.change > 0.0 else "danger"
        return format_html('<span class="badge badge-%s">%s</span>' % (tp, str(self.change)))

    def getEloChange2(self):
        tp = "success" if self.change < 0.0 else "danger"
        return format_html('<span class="badge badge-%s">%s</span>' % (tp, str(-self.change)))
