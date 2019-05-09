from django.contrib import admin

# Register your models here.

from .models import Player, Game, Statistic, Achievement, PlayerAchievement

admin.site.register(Player)
admin.site.register(Game)
admin.site.register(Statistic)
admin.site.register(Achievement)
admin.site.register(PlayerAchievement)
