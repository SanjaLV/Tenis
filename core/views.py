from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


from .models import Game


def index(request):

    latest_game_list = Game.objects.order_by("-date")[:5]
    template = loader.get_template("core/index.html")

    context = {
        'games': latest_game_list,
    }

    return HttpResponse(template.render(context, request))
