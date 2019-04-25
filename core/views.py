from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader
from django.db.models import Q

import core.errors
from .models import Game, Player


def index(request):
    latest_game_list = Game.objects.order_by("-date")[:5]
    template = loader.get_template("core/index.html")

    context = {
        'games': latest_game_list,
    }

    return HttpResponse(template.render(context, request))


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.clean_password2()
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {'form': form})


def game_data(request, game_id):
    try:
        this_game = Game.objects.get(pk=game_id)
    except ObjectDoesNotExist:
        return HttpResponseForbidden(core.errors.THERE_IS_NO_GAME)

    template = loader.get_template("core/game.html")

    context = {
        'game': this_game
    }
    return HttpResponse(template.render(context, request))


def player_data(request, player_id):
    try:
        this_player = Player.objects.get(pk=player_id)
    except ObjectDoesNotExist:
        return HttpResponseForbidden(core.errors.THERE_IS_NO_PLAYER)

    query = Q(player1=this_player.pk)
    query.add(Q(player2=this_player.pk), Q.OR)

    last_games = Game.objects.filter(query).order_by("-date")[:5]

    template = loader.get_template("core/player.html")
    context = {
        'name': this_player.name,
        'elo': this_player.elo,
        'last_games': last_games,
        'user_id': this_player.pk
    }
    return HttpResponse(template.render(context, request))


def validate_score(post_data):
    if "score1" not in post_data:
        return False, "There is no player one score!"
    if "score2" not in post_data:
        return False, "There is no player two score!"
    try:
        s = int(post_data["score1"])
        s = int(post_data["score2"])
    except TypeError:
        return False, "Data is not int"
    return True, ""


def validate_game(post_data, user):
    if "player1" not in post_data:
        return False, "There is no player one!"
    if "player2" not in post_data:
        return False, "There is no player two!"
    try:
        p1 = Player.objects.get(pk=int(post_data["player1"]))
        p2 = Player.objects.get(pk=int(post_data["player2"]))

        if p1.userID == p2.userID:
            return False, "You cannot play with yourself!"

        if p1.userID != user:
            return False, "Player one is not your player!"
    except ObjectDoesNotExist:
        return False, "Incorrect player ID!"

    return True, ""


def set_game_score(request, game_id):
    if request.method == "POST":
        post_data = request.POST

        if request.user.is_authenticated:
            current_user = request.user
        else:
            return HttpResponseForbidden(core.errors.YOU_ARE_NOT_ALLOWED)
        try:
            this_game = Game.objects.get(pk=game_id)
        except ObjectDoesNotExist:
            return HttpResponseForbidden(core.errors.THERE_IS_NO_GAME)
        if this_game.player1.pk != current_user.pk:
            return HttpResponseForbidden(core.errors.YOU_ARE_NOT_ALLOWED)

        flag, res = validate_score(post_data)

        if flag:
            this_game.score1 = int(post_data["score1"])
            this_game.score2 = int(post_data["score2"])
            this_game.calculate()
            this_game.save()
            messages.success(request, "Scores updated.")
        else:
            messages.warning(request, "ERROR!" + res)

    return game_data(request, game_id)


def rating(request):
    players = Player.objects.all().order_by("-elo")

    template = loader.get_template("core/rating.html")

    context = {
        'players': players
    }
    return HttpResponse(template.render(context, request))


def create_game(request):
    if request.user.is_authenticated:
        current_user = request.user
    else:
        return HttpResponseForbidden(core.errors.YOU_ARE_NOT_ALLOWED)

    if request.method == "POST":
        print("HELLO!")
        post_data = request.POST
        print(post_data)
        flag, res = validate_game(post_data, current_user)
        if flag:
            p1 = Player.objects.get(pk=int(post_data["player1"]))
            p2 = Player.objects.get(pk=int(post_data["player2"]))
            new_game = Game.objects.create(player1=p1, elo1=p1.elo, player2=p2, elo2= p2.elo)
            messages.success(request, "Game created.")
            return game_data(request, new_game.pk)
        else:
            messages.warning(request, "ERROR!" + res)
            #Fallthrough

    template = loader.get_template("core/create_game.html")
    my_players = Player.objects.filter(userID=current_user)
    other = Player.objects.filter(~Q(userID=current_user))
    context = {
        'my_players': my_players,
        'other': other
    }

    return HttpResponse(template.render(context, request))

#TODO Fix problems with multiple Player users
#TODO Add statistics
#TODO Add Graph
