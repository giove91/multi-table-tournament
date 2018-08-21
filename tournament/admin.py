from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect

from django_object_actions import DjangoObjectActions # https://github.com/crccheck/django-object-actions

from .models import *



@admin.register(Tournament)
class TournamentAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ('name', 'creation_time', 'bye_score', 'num_rounds', 'team_scores', 'player_scores')
    search_fields = ('name',)
    
    def create_round(self, request, obj):
        round, success = obj.create_round()
        if not success:
            self.message_user(
                request,
                format_html('<a href="%s">Round %d</a> created, but not all teams could be paired.' % (reverse('admin:tournament_round_change', args=(round.id,)), round.number)),
                level=messages.WARNING
            )
        else:
            self.message_user(
                request,
                format_html('<a href="%s">Round %d</a> created.' % (reverse('admin:tournament_round_change', args=(round.id,)), round.number)),
                level=messages.SUCCESS
            )
    
    create_round.label = "Create round"
    create_round.short_description = "Generate a new round with matches"

    change_actions = ('create_round',)
    
    def team_scores(self, obj):
        return score_counter_to_str(obj.team_scoreboard())
    
    def player_scores(self, obj):
        return score_counter_to_str(obj.player_scoreboard(), hide_secondary=True)




class PlayerInline(admin.TabularInline):
    model = Player

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    inlines = (PlayerInline,)
    list_display = ('name', 'players')
    search_fields = ('name',)
    
    def players(self, obj):
        return ", ".join(player.name for player in obj.player_set.all())


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'phone_number', 'is_captain')
    # list_editable = ('team', 'phone_number', 'is_captain')
    
    search_fields = ('name', 'team__name')
    autocomplete_fields = ('team',)


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'num_matches')
    list_editable = ('priority',)

    search_fields = ('name',)


@admin.register(Round)
class RoundAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ('__str__', 'tournament', 'num_matches', 'completed_matches', 'scheduled_time', 'team_scores')
    
    def view_matches(self, request, obj):
        return HttpResponseRedirect(reverse('admin:tournament_match_changelist') + '?round__id__exact=%d' % obj.id)
    
    view_matches.label = "View matches"
    view_matches.short_description = "View list of matches of this round"

    change_actions = ('view_matches',)
    
    def team_scores(self, obj):
        return score_counter_to_str(obj.team_scoreboard())
    


class TeamResultInline(admin.TabularInline):
    model = TeamResult
    verbose_name_plural = 'teams'
    autocomplete_fields = ('team',)
    # TODO: limit teams to those that are not already in a match
    # (Django 2.1 does not support this together with autocomplete_fields)
    
    max_num = 2
    extra = 2

class PlayerResultInline(admin.TabularInline):
    model = PlayerResult
    verbose_name_plural = 'players'
    autocomplete_fields = ('player',)
    extra = 0
    can_delete = False

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    inlines = (TeamResultInline, PlayerResultInline)
    list_display = ('__str__', 'show_round', 'type', 'valid', 'table', 'result', 'team_scores', 'player_scores')
    list_filter = ('round', 'table', 'type')
    
    def show_round(self, obj):
        return format_html("<a href='{url}'>{round}</a>", url=reverse('admin:tournament_round_change', args=(obj.round.id,)), round=obj.round)
    show_round.short_description = "round"
    
    def team_scores(self, obj):
        return score_counter_to_str(obj.team_scoreboard())

    def player_scores(self, obj):
        return score_counter_to_str(obj.player_scoreboard(), hide_secondary=True)


