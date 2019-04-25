from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('game/<int:game_id>', views.game_data, name="game"),
    path('player/<int:player_id>', views.player_data, name="player"),
    path('register', views.register, name="registration"),
    path('game/<int:game_id>/set_score', views.set_game_score, name="set_game_score"),
    path('rating', views.rating, name="rating"),
    path('create', views.create_game, name="create_game"),
    path('user/<int:user_id>', views.user_data, name="user"),
    path('players', views.user_players, name="users_players")
]