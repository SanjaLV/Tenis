from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader


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

    return HttpResponse("ID is " + str(player_id))
