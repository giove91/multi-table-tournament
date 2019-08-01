import django
from django.shortcuts import render
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView, CreateView


from django.utils.decorators import method_decorator

from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required

from .models import *
from .forms import *

def sorted_scoreboard(scoreboard):
    """
    Take as input a scoreboard given as a counter, and return a sorted list with ranks.
    """
    by_score = {}
    for (entity, score) in scoreboard.items():
        # skip inactive entity
        if not entity.active:
            continue

        if score.raw() not in by_score:
            by_score[score.raw()] = []
        by_score[score.raw()].append(entity)

    res = []
    rank = 1

    for score in reversed(sorted(by_score)):
        for entity in sorted(by_score[score], key=lambda x: x.name):
            res.append((entity, scoreboard[entity], rank))

        rank += len(by_score[score])

    return res


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tournament = self.request.current_tournament
        context['tournament'] = tournament

        if tournament is not None:
            context['team_scoreboard'] = sorted_scoreboard(tournament.team_scoreboard(public=True))
            context['player_scoreboard'] = sorted_scoreboard(tournament.player_scoreboard(public=True))
            context['rounds'] = tournament.round_set.exclude(visibility=HIDE).order_by('-number').prefetch_related('match_set__teams', 'match_set__teamresult_set', 'match_set__table')
            context['teams'] = Team.objects.filter(active=True).prefetch_related('player_set')

            if tournament.shown_players is not None:
                context['player_scoreboard'] = context['player_scoreboard'][:min(tournament.shown_players, len(context['player_scoreboard']))]

        return context


class RegistrationView(FormView):
    template_name = 'registration.html'
    form_class = RegistrationForm
    success_url = '/thanks/'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tournament = self.request.current_tournament
        context['tournament'] = tournament

        return context

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        if self.request.current_tournament.can_register():
            data = form.cleaned_data

            # create team
            try:
                team = Team.objects.create(name=data['team_name'])
            except django.db.utils.IntegrityError:
                # a team with this name already exists...
                return redirect('registration')

            # create players
            for i in range(100):
                key = 'player_{}'.format(i)
                if key in data:
                    if data[key] is not None:
                        Player.objects.create(name=data[key], team=team, is_captain=(i == 0))

                else:
                    break

        else:
            return redirect('registration')

        return super().form_valid(form)


class PlayerRegistrationView(FormView):
    template_name = 'player_registration.html'
    form_class = PlayerRegistrationForm
    success_url = '/thanks/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tournament = self.request.current_tournament
        context['tournament'] = tournament

        # TODO: avoid duplicate code (see forms.PlayerRegistrationForm)
        context['available_teams'] = Team.objects.annotate(num_players=Count('player')).filter(num_players__lt=tournament.max_players_per_team)

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tournament'] = self.request.current_tournament
        return kwargs


    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        if self.request.current_tournament.can_register_player():
            data = form.cleaned_data

            # create team
            try:
                player = Player.objects.create(name=data['name'], team=data['team'])
            except django.db.utils.IntegrityError:
                # a team with this name already exists...
                return redirect('player-registration')

        else:
            return redirect('player-registration')

        return super().form_valid(form)


class ThanksView(TemplateView):
    template_name = 'thanks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tournament = self.request.current_tournament
        context['tournament'] = tournament

        return context


class TablesView(ListView):
    template_name = 'tables.html'
    model = Table

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tournament = self.request.current_tournament
        context['tournament'] = tournament
        return context



@method_decorator(staff_member_required, name='dispatch')
class CreateRoundView(View):
    def dispatch(self, request, pk):
        tournament = Tournament.objects.get(pk=pk)
        round, success = tournament.create_round()
        return redirect('admin:index')
