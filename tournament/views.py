from django.shortcuts import render
from django.views.generic.base import TemplateView

from .models import *

def sorted_scoreboard(scoreboard):
    """
    Take as input a scoreboard given as a counter, and return a sorted list with ranks.
    """
    by_score = {}
    for (entity, score) in scoreboard.items():
        if score not in by_score:
            by_score[score] = []
        by_score[score].append(entity)
    
    res = []
    rank = 1
    
    for score in reversed(sorted(by_score)):
        for entity in sorted(by_score[score], key=lambda x: x.name):
            res.append((entity, scoreboard[entity], rank))
        
        rank += len(by_score[score])
    
    return res


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        tournament = Tournament.objects.latest()
        
        context = super().get_context_data(**kwargs)
        context['tournament'] = tournament
        context['team_scoreboard'] = sorted_scoreboard(tournament.team_scoreboard())
        context['player_scoreboard'] = sorted_scoreboard(tournament.player_scoreboard())
        context['rounds'] = tournament.round_set.all().order_by('-number')
        return context

