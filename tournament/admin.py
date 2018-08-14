from django.contrib import admin, messages
from .models import *

from django_object_actions import DjangoObjectActions # https://github.com/crccheck/django-object-actions


@admin.register(Tournament)
class TournamentAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ('name', 'creation_time', 'bye_score', 'num_rounds', 'team_scores', 'player_scores')
    search_fields = ('name',)
    
    def create_round(self, request, obj):
        round_number, success = obj.create_round()
        if not success:
            self.message_user(request, "Round %d created, but not all teams could be paired." % round_number, level=messages.WARNING)
        else:
            self.message_user(request, "Round %d created." % round_number, level=messages.SUCCESS)
    
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
class RoundAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'tournament', 'num_matches', 'completed_matches', 'scheduled_time', 'team_scores')
    
    def team_scores(self, obj):
        return score_counter_to_str(obj.team_scoreboard())


class TeamResultInline(admin.TabularInline):
    model = TeamResult
    verbose_name_plural = 'teams'
    autocomplete_fields = ('team',)
    max_num = 2
    extra = 2

class PlayerResultInline(admin.TabularInline):
    model = PlayerResult
    verbose_name_plural = 'players'
    autocomplete_fields = ('player',)
    extra = 0

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    inlines = (TeamResultInline, PlayerResultInline)
    list_display = ('__str__', 'round', 'type', 'table', 'result', 'team_scores', 'player_scores')
    list_filter = ('round', 'table', 'type')
    
    def team_scores(self, obj):
        return score_counter_to_str(obj.team_scoreboard())

    def player_scores(self, obj):
        return score_counter_to_str(obj.player_scoreboard(), hide_secondary=True)


