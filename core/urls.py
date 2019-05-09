from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('player/<int:player_id>', views.player_data, name="player"),
    path('player/<int:player_id>/enable', views.activate_player, name="activate_player"),
    path('player/<int:player_id>/edit', views.edit_player, name="edit_player"),
    path('player/<int:player_id>/achievements', views.player_achievements, name="player_achievements"),
    path('register', views.register, name="registration"),
    path('game/<int:game_id>', views.game_data, name="game"),
    path('game/<int:game_id>/set_score', views.set_game_score, name="set_game_score"),
    path('game/<int:game_id>/reset', views.reset_game_score, name="reset_game_score"),
    path('game/<int:game_id>/verify', views.verify_game, name="verify_game"),
    path('game/<int:game_id>/delete', views.delete_game, name="delete_game"),
    path('rating', views.rating, name="rating"),
    path('create', views.create_game, name="create_game"),
    path('user/<int:user_id>', views.user_data, name="user"),
    path('players', views.user_players, name="user_players"),
    path('new_player', views.create_player, name="create_player"),
    path('graphs', views.graphs, name="graphs"),
    path('to_verify', views.not_verified_games, name="not_verified_games"),
    path('achievement/<int:a_id>', views.achievement_info, name="achievement_info")
]
