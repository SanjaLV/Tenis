from django.contrib import admin

# Register your models here.

from .models import Player, Game, Statistic

admin.site.register(Player)
admin.site.register(Game)
admin.site.register(Statistic)
