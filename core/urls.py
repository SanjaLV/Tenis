from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('game/<int:game_id>', views.game_data, name="game")
]