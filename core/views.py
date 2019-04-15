from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
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


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.clean_password2()
            user = authenticate(username=username, password=raw_password)
            login(request,user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {'form': form})



def game_data(request, game_id):
    try:
        this_game = Game.objects.get(pk=game_id)
    except ObjectDoesNotExist:
        return HttpResponseForbidden(request)

    template = loader.get_template("core/game.html")

    context = {
        'game': this_game
    }
    return HttpResponse(template.render(context, request))


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
        'last_games' : last_games,
        'user_id'    : this_player.pk
    }
    return HttpResponse(template.render(context, request))
