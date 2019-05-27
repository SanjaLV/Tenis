from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.utils.html import format_html


class Player(models.Model):
    name = models.CharField(max_length=30)
    elo = models.DecimalField(max_digits=6, decimal_places=2, default=800)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    active   = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Game(models.Model):
    player1  = models.ForeignKey(Player, on_delete=models.PROTECT, related_name="player_one")
    player2  = models.ForeignKey(Player, on_delete=models.PROTECT, related_name="player_two")
    score1   = models.IntegerField(default=0)
    score2   = models.IntegerField(default=0)
    elo1     = models.DecimalField(max_digits=6, decimal_places=2)
    elo2     = models.DecimalField(max_digits=6, decimal_places=2)
    change   = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    date     = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        output = "%s(%f) %d - %d %s(%f)" % (self.player1.name, self.elo1,
                                            self.score1, self.score2,
                                            self.player2.name, self.elo2)
        return output

    def player1_badge(self):
        if self.score1 > self.score2:
            return "success"
        else:
            return "danger"

    def player2_badge(self):
        if self.score2 > self.score1:
            return "success"
        else:
            return "danger"

    def player1_win(self):
        return self.score1 > self.score2

    def player2_win(self):
        return self.score2 > self.score1

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

    def ended(self):
        return self.score1 + self.score2 > 0

    def calculate(self):
        import decimal

        p1_should = decimal.Decimal(1) / (decimal.Decimal(1) +
                                          decimal.Decimal(10)**(decimal.Decimal(self.elo2-self.elo1) / decimal.Decimal(400)))
        p1_got = decimal.Decimal(self.score1) / decimal.Decimal(self.score1 + self.score2)

        change = decimal.Decimal(40) * (p1_got - p1_should)

        decimal_ctx = decimal.Context(prec=6, rounding=decimal.ROUND_HALF_UP)
        change = decimal_ctx.create_decimal(change).quantize(decimal.Decimal(10) ** -2)
        self.change = change


    def apply_change(self, subtract=False):
        p1 = Player.objects.get(pk=self.player1.pk)
        p2 = Player.objects.get(pk=self.player2.pk)

        if not subtract:
            p1.elo += self.change
            p2.elo -= self.change
        else:
            p1.elo -= self.change
            p2.elo += self.change
        p1.save()
        p2.save()

    def accept_game(self):
        self.calculate()
        self.save()
        self.apply_change()

        p1_stat = Statistic.objects.get(player=self.player1)
        p2_stat = Statistic.objects.get(player=self.player2)

        p1_stat.games += 1
        p2_stat.games += 1

        if self.score1 > self.score2:
            p1_stat.wins += 1
        else:
            p2_stat.wins += 1

        p1_stat.save()
        p2_stat.save()

    def cancel_game(self):
        self.apply_change(subtract=True)
        p1_stat = Statistic.objects.get(player=self.player1)
        p2_stat = Statistic.objects.get(player=self.player2)

        p1_stat.games -= 1
        p2_stat.games -= 1

        if self.score1 > self.score2:
            p1_stat.wins -= 1
        else:
            p2_stat.wins -= 1

        p1_stat.save()
        p2_stat.save()

        self.score1 = 0
        self.score2 = 0
        self.change = 0
        self.save()


class Statistic(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    games = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    achievements_count = models.IntegerField(default=0)

    def __str__(self):
        return "%s (%d/%d)" % (self.player.name,
                               self.wins,
                               self.games)

    def loses(self):
        return self.games - self.wins

    def winrate(self):
        if self.games == 0:
            return "NA"
        else:
            return "%.2f" % (self.wins / self.games * 100)


class Achievement(models.Model):
    name = models.CharField(max_length=30)
    desc = models.CharField(max_length=200)
    # plugin_name = do i need it?

    def __str__(self):
        return self.name


class PlayerAchievement(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    finished = models.BooleanField(default=False)
    progress = models.IntegerField(default=0)
    date = models.DateTimeField(null=True)

    def __str__(self):
        if self.finished:
            return self.player.name + ">" + self.achievement.name
        else:
            return self.player.name + ">" + self.achievement.name + "[" + str(self.progress) + "]"

    def max_progress(self):
        from core.apps import plugins
        return plugins[self.achievement.pk].info.max_progress

    def progress_percentage(self):
        return "%.2f" % (self.progress / self.max_progress() * 100)
