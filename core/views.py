from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader
from django.db.models import Q

import core.errors
from core.forms import PlayerCreation
from core.utils import GraphData
from .models import Game, Player, Statistic


def index(request):
    page = 1
    if "page" in request.GET:
        try:
            page = int(request.GET["page"])
        except ValueError:
            page = 1

    ITEMS_ON_PAGE = 20

    game_count = Game.objects.count()

    max_page = (game_count + ITEMS_ON_PAGE - 1) // ITEMS_ON_PAGE

    page = max(page, 1)
    page = min(page, max_page)

    i_start = (page - 1) * ITEMS_ON_PAGE
    i_end   = (page) * ITEMS_ON_PAGE
    i_end = min(i_end, game_count+1)
    latest_game_list = Game.objects.order_by("-pk")[i_start:i_end]
    template = loader.get_template("core/index.html")

    context = {
        'games': latest_game_list,
        'page': page,
        'max_page': max_page
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

    all_games = Game.objects.filter(query).order_by("pk")

    if len(all_games) < 5:
        last_games = all_games
    else:
        last_games = all_games[len(all_games) - 5:]

    last_games.reverse()
    graph_data = []
    graph_data.append(GraphData(all_games[0].pk - 1, 800))

    for g in all_games:
        if g.player1 == this_player:
            graph_data.append(GraphData(g.pk, g.newElo1()))
        else:
            graph_data.append(GraphData(g.pk, g.newElo2()))

    stat = Statistic.objects.get(player=this_player)

    template = loader.get_template("core/player.html")
    context = {
        'name': this_player.name,
        'elo': this_player.elo,
        'last_games': last_games,
        'player_user': this_player.user.pk,
        'stat': stat,
        'graph_data': graph_data
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

        if p1.user == p2.user:
            return False, "You cannot play with yourself!"

        if p1.user != user:
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
            return HttpResponseForbidden(core.errors.YOU_MUST_LOGIN)
        try:
            this_game = Game.objects.get(pk=game_id)
        except ObjectDoesNotExist:
            return HttpResponseForbidden(core.errors.THERE_IS_NO_GAME)
        if this_game.player1.user != current_user:
            return HttpResponseForbidden(core.errors.YOU_ARE_NOT_ALLOWED)

        flag, res = validate_score(post_data)

        if flag:
            this_game.score1 = int(post_data["score1"])
            this_game.score2 = int(post_data["score2"])
            this_game.accept_game()
            messages.success(request, "Scores updated.")
        else:
            messages.warning(request, "ERROR!" + res)

    return game_data(request, game_id)


def rating(request):
    players = Player.objects.all().order_by("-elo")
    stats = []
    for p in players:
        stats.append(Statistic.objects.get(player=p))

    template = loader.get_template("core/rating.html")

    context = {
        'players_stats': zip(players, stats)
    }
    return HttpResponse(template.render(context, request))


def create_game(request):
    if request.user.is_authenticated:
        current_user = request.user
    else:
        return HttpResponseForbidden(core.errors.YOU_MUST_LOGIN)

    if request.method == "POST":
        post_data = request.POST
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
    my_players = Player.objects.filter(Q(user=current_user) & Q(active=True)).order_by("name")
    other = Player.objects.filter(~Q(user=current_user) & Q(active=True)).order_by("name")
    context = {
        'my_players': my_players,
        'other': other
    }

    return HttpResponse(template.render(context, request))


def user_data(request, user_id):
    try:
        this_user = User.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        return HttpResponseForbidden(core.errors.YOU_ARE_NOT_ALLOWED)

    user_players = Player.objects.filter(user=this_user)

    if len(user_players) == 0:
        messages.warning(request, "Please create new player!")
        return redirect('user_players')
    elif len(user_players) == 1:
        return redirect('player', player_id=user_players[0].pk)
    else:
        return redirect('user_players')


def user_players(request):
    if request.user.is_authenticated:
        user = request.user
        template = loader.get_template("core/my_players.html")
        my_players = Player.objects.filter(user=user)
        stats = []
        for p in my_players:
            stats.append(Statistic.objects.get(player=p))
        context = {
            'players_stats': zip(my_players, stats)
        }
        return HttpResponse(template.render(context, request))

    else:
        return HttpResponseForbidden(core.errors.YOU_MUST_LOGIN)


def create_player(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden(core.errors.YOU_MUST_LOGIN)
    user = request.user

    if request.method == "POST":
        form = PlayerCreation(request.POST)
        if form.is_valid():
            player = form.save(commit=False)
            player.user = user
            player.save()
            stat = Statistic.objects.create(player=player)

            return redirect("player", player_id=player.pk)
    else:
        form = PlayerCreation()

    template = loader.get_template("core/create_player.html")
    context = {
        'form': form
    }
    return HttpResponse(template.render(context, request))


def edit_player(request, player_id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden(core.errors.YOU_MUST_LOGIN)
    user = request.user
    try:
        player = Player.objects.get(pk=player_id)
    except ObjectDoesNotExist:
        return HttpResponseForbidden(core.errors.THERE_IS_NO_PLAYER)

    if player.user != user:
        return HttpResponseForbidden(core.errors.YOU_ARE_NOT_ALLOWED)

    if request.method == "POST":
        form = PlayerCreation(request.POST)
        if form.is_valid():
            player.name = form.cleaned_data["name"]
            player.save()
            messages.success(request, "Player name is changed to " + player.name)
            return redirect('user_players')
    else:
        form = PlayerCreation(initial={'name': player.name})

    template = loader.get_template("core/edit_player.html")
    context = {
        'form': form,
        'pk': player.pk
    }
    return HttpResponse(template.render(context, request))


def activate_player(request, player_id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden(core.errors.YOU_MUST_LOGIN)
    user = request.user
    try:
        player = Player.objects.get(pk=player_id)
    except ObjectDoesNotExist:
        return HttpResponseForbidden(core.errors.THERE_IS_NO_PLAYER)

    if player.user != user:
        return HttpResponseForbidden(core.errors.YOU_ARE_NOT_ALLOWED)

    player.active = not player.active

    if player.active:
        messages.success(request, player.name + " activated!")
    else:
        messages.success(request, player.name + " deactivated!")

    player.save()
    return redirect('user_players')


def reset_game_score(request, game_id):
    if request.user.is_authenticated:
        user = request.user
        try:
            this_game = Game.objects.get(pk=game_id)
        except ObjectDoesNotExist:
            return HttpResponseForbidden(core.errors.THERE_IS_NO_GAME)

        if user != this_game.player1.user and user != this_game.player2.user:
            return HttpResponseForbidden(core.errors.YOU_ARE_NOT_ALLOWED)

        this_game.cancel_game()
        return redirect('game', game_id=game_id)
    else:
        return HttpResponseForbidden(core.errors.YOU_MUST_LOGIN)


def verify_game(request, game_id):
    if request.user.is_authenticated:
        user = request.user
        try:
            this_game = Game.objects.get(pk=game_id)
        except ObjectDoesNotExist:
            return HttpResponseForbidden(core.errors.THERE_IS_NO_GAME)

        if user != this_game.player2.user:
            return HttpResponseForbidden(core.errors.YOU_ARE_NOT_ALLOWED)

        this_game.verified = True
        this_game.save()
        return redirect('game', game_id=game_id)
    else:
        return HttpResponseForbidden(core.errors.YOU_MUST_LOGIN)


def delete_game(request, game_id):
    if request.user.is_authenticated:
        user = request.user
        try:
            this_game = Game.objects.get(pk=game_id)
        except ObjectDoesNotExist:
            return HttpResponseForbidden(core.errors.THERE_IS_NO_GAME)

        if this_game.player1.user != user:
            return HttpResponseForbidden(core.errors.YOU_ARE_NOT_ALLOWED)

        if this_game.ended():
            messages.error(request, "You cannot delete game with score!")
            return redirect('game', game_id=game_id)
        this_game.delete()

        messages.error(request, "Game was deleted!")
        return index(request)

    return HttpResponseForbidden(core.errors.YOU_MUST_LOGIN)


def graphs(request):
    template = loader.get_template("core/graphs.html")

    players = []
    for x in Player.objects.all():
        players.append((x.name, x.pk))

    games = []

    for x in Game.objects.all():
        games.append((x.player1.pk, x.player2.pk, x.change))

    context = {
        'players': players,
        'graph_data': games
    }

    return HttpResponse(template.render(context, request))

#TODO Add achivments
