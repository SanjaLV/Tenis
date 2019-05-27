import time

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.template import loader
from django.db.models import Q
from django.utils.datetime_safe import datetime

import core.errors
from core.forms import PlayerCreation, SignUpForm

from core.utils import GraphData
from .models import Game, Player, Statistic, Achievement, PlayerAchievement

from core.apps import plugins


def apply_plugin(plugin, achievement, player, stat, last_games, is_winner):
    from core.plugins.plugin_interface import AchievementsData, Status

    # Already have Achievement
    try:
        ach = PlayerAchievement.objects.get(player=player, achievement=achievement)
        if ach.finished:
            return
        progress = ach.progress
    except ObjectDoesNotExist:
        progress = 0

    games = last_games[:plugin.info.prev_games]

    save = plugin.info.save_progress

    if not save:
        progress = None

    data = AchievementsData(progress=progress,
                            is_winner=is_winner,
                            prev_games=games,
                            statistic=stat)

    flag, progress = plugin.progress(data)

    if flag == Status.FINISHED:
        new_ach, ignore = PlayerAchievement.objects.get_or_create(player=player, achievement=achievement)
        new_ach.finished = True
        new_ach.date = datetime.now()
        new_ach.save()
        stat.achievements_count += 1
        stat.save()
        return
    elif flag == Status.NOTHING:
        pass
    elif flag == Status.SAVE:
        new_ach, ignore = PlayerAchievement.objects.get_or_create(player=player, achievement=achievement)
        new_ach.progress = progress
        new_ach.save()
    else:
        assert False


def progress_achievement(game):
    if not game.ended():
        return

    all_achievements = Achievement.objects.all()
    if all_achievements.count() == 0:
        return

    # need to sleep here, otherwise there will be no response until we finish this task
    time.sleep(0.5)

    p1stat = Statistic.objects.get(player=game.player1.pk)
    p2stat = Statistic.objects.get(player=game.player2.pk)

    p1games = Game.objects.filter(Q(player1=game.player1) | Q(player2=game.player2)).order_by("-pk")
    p2games = Game.objects.filter(Q(player1=game.player1) | Q(player2=game.player2)).order_by("-pk")

    for achivm in all_achievements:
        if plugins[achivm.pk].info.winner:
            if game.player1_win:
                apply_plugin(plugins[achivm.pk], achivm, game.player1, p1stat, p1games, True)
            else:
                apply_plugin(plugins[achivm.pk], achivm, game.player2, p2stat, p2games, True)
        if plugins[achivm.pk].info.loser:
            if game.player1_win:
                apply_plugin(plugins[achivm.pk], achivm, game.player2, p2stat, p2games, False)
            else:
                apply_plugin(plugins[achivm.pk], achivm, game.player1, p1stat, p1games, False)


def async_progress_achievement(game):
    import threading
    t = threading.Thread(target=progress_achievement, args=(game,))
    t.setDaemon(True)
    t.start()
    return


def index(request):
    start_time = time.time()

    page = 1
    if "page" in request.GET:
        try:
            page = int(request.GET["page"])
        except ValueError:
            page = 1

    ITEMS_ON_PAGE = 20

    game_count = Game.objects.count()

    if game_count > ITEMS_ON_PAGE:
        max_page = (game_count + ITEMS_ON_PAGE - 1) // ITEMS_ON_PAGE

        page = max(page, 1)
        page = min(page, max_page)

        i_start = (page - 1) * ITEMS_ON_PAGE
        i_end   = (page) * ITEMS_ON_PAGE
        i_end = min(i_end, game_count+1)
        latest_game_list = Game.objects.order_by("-pk")[i_start:i_end]
    else:
        latest_game_list = Game.objects.all().order_by("-pk")
        max_page = 1
        page = 1

    template = loader.get_template("core/index.html")

    end_time = time.time()
    server_time = ('Done in {:.3f} ms'.format((end_time - start_time) * 1000.0))

    context = {
        'games': latest_game_list,
        'page': page,
        'max_page': max_page,
        'render_time': server_time
    }

    return HttpResponse(template.render(context, request))


def register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.clean_password2()
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
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
    # make sure this_player is always displayed as player1
    for i in range(len(last_games)):
        if last_games[i].player1 != this_player:
            last_games[i].player1, last_games[i].player2 = last_games[i].player2, last_games[i].player1
            last_games[i].change *= -1
            last_games[i].score1, last_games[i].score2 = last_games[i].score2, last_games[i].score1
            last_games[i].elo1, last_games[i].elo2 = last_games[i].elo2, last_games[i].elo1

    graph_data = []
    if len(all_games) > 0:
        graph_data.append(GraphData(all_games[0].pk - 1, 800))

    for g in all_games:
        if g.player1 == this_player:
            graph_data.append(GraphData(g.pk, g.newElo1()))
        else:
            graph_data.append(GraphData(g.pk, g.newElo2()))

    stat = Statistic.objects.get(player=this_player)

    template = loader.get_template("core/player.html")
    context = {
        'player': this_player,
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
    except ValueError:
        return False, "Data is not int"
    return True, ""


def validate_game(post_data, user):
    if "player1" not in post_data:
        return False, "There is no player one!"
    if "player2" not in post_data:
        return False, "There is no player two!"
    try:
        player_1 = int(post_data["player1"])
        player_2 = int(post_data["player2"])
    except ValueError:
        return False, "Data is not int"

    try:
        p1 = Player.objects.get(pk=player_1)
        p2 = Player.objects.get(pk=player_2)

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

        if this_game.ended():
            flag = False
            res += "Cannot change already saved scores, please remove it first."

        if flag:
            this_game.score1 = int(post_data["score1"])
            this_game.score2 = int(post_data["score2"])
            this_game.accept_game()
            messages.success(request, "Scores updated.")
        else:
            messages.warning(request, "ERROR!" + res)

    return redirect('game', game_id=game_id)


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
            new_game = Game.objects.create(player1=p1, elo1=p1.elo, player2=p2, elo2=p2.elo)
            messages.success(request, "Game created.")
            return redirect('game', game_id=new_game.pk)
        else:
            messages.warning(request, "ERROR!" + res)
            # Fallthrough

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
    if request.method != "POST":
        return HttpResponseForbidden(core.errors.YOU_ARE_NOT_ALLOWED)

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


def player_achievements(request, player_id):
    start_time = time.time()

    try:
        player = Player.objects.get(pk=player_id)
    except ObjectDoesNotExist:
        return HttpResponseForbidden(core.errors.THERE_IS_NO_PLAYER)

    all_list = PlayerAchievement.objects.filter(player_id=player)

    complete_list = all_list.filter(finished=True)
    unfinished_list = all_list.filter(finished=False).order_by("-progress")

    end_time = time.time()
    server_time = ('Done in {:.3f} ms'.format((end_time - start_time) * 1000.0))

    context = {
        'player': player,
        'finished': complete_list,
        'in_progress': unfinished_list,
        'render_time': server_time
    }
    template = loader.get_template("core/players_achievements.html")
    return HttpResponse(template.render(context, request))


def reset_game_score(request, game_id):
    if request.method != "POST":
        return HttpResponseForbidden(core.errors.YOU_ARE_NOT_ALLOWED)

    if request.user.is_authenticated:
        user = request.user
        try:
            this_game = Game.objects.get(pk=game_id)
        except ObjectDoesNotExist:
            return HttpResponseForbidden(core.errors.THERE_IS_NO_GAME)

        if user != this_game.player1.user and user != this_game.player2.user:
            return HttpResponseForbidden(core.errors.YOU_ARE_NOT_ALLOWED)

        if this_game.verified:
            return HttpResponseForbidden(core.errors.YOU_ARE_NOT_ALLOWED)

        this_game.cancel_game()
        return redirect('game', game_id=game_id)
    else:
        return HttpResponseForbidden(core.errors.YOU_MUST_LOGIN)


def verify_game(request, game_id):
    if request.method != "POST":
        return HttpResponseForbidden(core.errors.YOU_ARE_NOT_ALLOWED)

    if request.user.is_authenticated:
        user = request.user
        try:
            this_game = Game.objects.get(pk=game_id)
        except ObjectDoesNotExist:
            return HttpResponseForbidden(core.errors.THERE_IS_NO_GAME)

        if user != this_game.player2.user:
            return HttpResponseForbidden(core.errors.YOU_ARE_NOT_ALLOWED)

        if not this_game.ended():
            return HttpResponseForbidden(core.errors.GAME_NOT_ENDED)

        messages.success(request, "Game is verified!")
        this_game.verified = True
        this_game.save()
        async_progress_achievement(this_game)
        return redirect('game', game_id=game_id)
    else:
        return HttpResponseForbidden(core.errors.YOU_MUST_LOGIN)


def delete_game(request, game_id):
    if request.method != "POST":
        return HttpResponseForbidden(core.errors.YOU_ARE_NOT_ALLOWED)

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
        return redirect('index')

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


def not_verified_games(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden(core.errors.YOU_MUST_LOGIN)
    else:
        user = request.user

    user_players = Player.objects.filter(user=user)

    if user_players is not None and len(user_players) != 0:
        my_player_q = Q(player2__user__pk=user.pk)
        games_to_validate = Game.objects.filter(verified=False).filter(my_player_q)
    else:
        games_to_validate = None

    # make sure player1 is this user's player
    for i in range(len(games_to_validate)):
        if games_to_validate[i].player1.user != user:
            games_to_validate[i].player1, games_to_validate[i].player2 = games_to_validate[i].player2, games_to_validate[i].player1
            games_to_validate[i].change *= -1
            games_to_validate[i].score1, games_to_validate[i].score2 = games_to_validate[i].score2, games_to_validate[i].score1
            games_to_validate[i].elo1, games_to_validate[i].elo2 = games_to_validate[i].elo2, games_to_validate[i].elo1

    context = {
        'games': games_to_validate
    }
    template = loader.get_template("core/to_verify.html")

    return HttpResponse(template.render(context, request))


def achievement_info(request, a_id):
    try:
        ach = Achievement.objects.get(pk=a_id)
    except ObjectDoesNotExist:
        return HttpResponseForbidden(core.errors.THERE_IS_NO_ACHIEVEMENT)

    players_that_have_it = PlayerAchievement.objects.filter(finished=True, achievement=ach).order_by("date")

    template = loader.get_template("core/achievement.html")

    context = {
        'ach': ach,
        'players_achievements': players_that_have_it,
        'count': len(players_that_have_it),
        'players_count': Player.objects.all().count()
    }

    return HttpResponse(template.render(context, request))


def json_to_verify(request):
    if not request.user.is_authenticated:
        return JsonResponse({})
    cnt = Game.objects.filter(verified=False, player2__user__pk=request.user.pk).count()

    return JsonResponse({'count': cnt})


def json_pvp_stat(request, player_one, player_two):
    try:
        p1 = Player.objects.get(pk=player_one)
        p2 = Player.objects.get(pk=player_two)
    except ObjectDoesNotExist:
        return JsonResponse({})

    query_12 = Q(player1=player_one) & Q(player2=player_two)
    query_21 = Q(player1=player_two) & Q(player2=player_one)

    games = Game.objects.filter(query_12 | query_21)

    p1_win = 0
    p2_win = 0
    total_set_1 = 0
    total_set_2 = 0
    games_count = 0

    for game in games:
        if game.ended():
            games_count += 1
            if game.player1.pk == player_one:
                total_set_1 += game.score1
                total_set_2 += game.score2

                # One vs Two
                if game.player1_win():
                    p1_win += 1
                else:
                    p2_win += 1
            else:
                total_set_2 += game.score1
                total_set_1 += game.score2

                # Two vs One
                if game.player1_win():
                    p2_win += 1
                else:
                    p1_win += 1

    import decimal
    p1_should = decimal.Decimal(1) / (decimal.Decimal(1) +
                                      decimal.Decimal(10) ** (
                                                  decimal.Decimal(p2.elo - p1.elo) / decimal.Decimal(400)))
    p2_should = 1 - p1_should
    p1_should *= 100
    p2_should *= 100
    res = {
        'games': games_count,
        'w1' : p1_win,
        'w2' : p2_win,
        'st1': total_set_1,
        'st2': total_set_2,
        'elo1': "%.2f" % p1_should,
        'elo2': "%.2f" % p2_should
    }

    return JsonResponse(res)
