from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader
from django.db.models import Q

from .models import Game, Player


def index(request):

    latest_game_list = Game.objects.order_by("-date")[:5]
    template = loader.get_template("core/index.html")

    context = {
        'games': latest_game_list,
    }

    return HttpResponse(template.render(context, request))


def game_data(request, game_id):
    try:
        this_game = Game.objects.get(pk=game_id)
    except ObjectDoesNotExist:
        return HttpResponseForbidden(request)
    return HttpResponse("ID is " + str(game_id))


def player_data(request, player_id):
    try:
        this_player = Player.objects.get(pk=player_id)
    except ObjectDoesNotExist:
        return HttpResponseForbidden(request)

    query = Q(player1=this_player.pk)
    query.add(Q(player2=this_player.pk), Q.OR)

    last_games = Game.objects.filter(query)[:5]

    template = loader.get_template("core/player.html")
    context = {
        'name'       : this_player.name,
        'elo'        : this_player.elo ,
        'last_games' : last_games
    }
    return HttpResponse(template.render(context, request))
