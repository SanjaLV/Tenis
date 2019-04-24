from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('game/<int:game_id>', views.game_data, name="game"),
    path('player/<int:player_id>', views.player_data, name="player"),
    path('register', views.register, name="registration"),
    path('game/<int:game_id>/set_score', views.set_game_score, name="set_game_score")
]