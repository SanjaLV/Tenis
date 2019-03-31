from django.shortcuts import render
from django.http import HttpResponse


from .models import Game


def index(request):

    latest_game_list = Game.objects.order_by("-date")[:5]
    output = "<h1>Latest games:</h1> <br>\n"
    for game in latest_game_list:
        output += str(game) + "<br>\n"
    return HttpResponse(output)
