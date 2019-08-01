import networkx as nx
import itertools
import random
from collections import Counter
from decimal import Decimal

from django.db import models

from django.core.validators import RegexValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _


# match types
NORMAL = 'N'
BYE = 'B'

# round visibility
HIDE = 'H'
HIDE_RESULTS = 'R'
SHOW = 'S'
VISIBILITY_CHOICES = (
    (HIDE, 'Hide'),
    (HIDE_RESULTS, 'Hide results'),
    (SHOW, 'Show'),
)


class Score:
    """
    A score of a team or a player.
    This class comprises a primary (more important) and a secondary (less important) score.
    It also keeps track of the number of matches and (in the case of one match)
    of the type of match (normal/bye).
    """
    def __init__(self, primary=Decimal('0.0'), secondary=Decimal('0.0'), num_matches=0, match_type=None):
        self.primary = primary
        self.secondary = secondary
        self.num_matches = num_matches
        self.match_type = match_type


    def raw(self):
        return (self.primary, self.secondary)


    def __repr__(self):
        return self.raw().__repr__()


    def __eq__(self, other):
        return self.primary == other.primary and self.secondary == other.secondary and self.num_matches == other.num_matches

    def __le__(self, other):
        return self.primary < other.primary or self.primary == other.primary and (self.secondary < other.secondary or self.secondary == other.secondary and self.num_matches >= other.num_matches)

    def __gt__(self, other):
        if other is 0:
            return self != Score()
        else:
            return not self <= other

    def __hash__(self):
        return hash((self.primary, self.secondary))

    def __add__(self, other):
        if other is 0:
            return self
        else:
            return Score(self.primary + other.primary, self.secondary + other.secondary, self.num_matches + other.num_matches)

    def __radd__(self, other):
        if other is 0:
            return self
        else:
            return self + other

    def to_int(self):
        """
        Integer representation of the score, used in round creation.
        The primary score weights much more than the secondary score.
        """
        return int(10*(100 * self.primary + self.secondary))



def score_counter_to_str(counter, hide_secondary=False):
    """
    Transform a counter of scores into a string, for display purposes.
    """
    if hide_secondary:
        return ', '.join('%s (%s)' % (entity.name, str(score.primary)) for (entity, score) in reversed(sorted(counter.items(), key=lambda x: x[1])))

    else:
        return ', '.join('%s (%s, %s)' % (entity.name, str(score.primary), str(score.secondary)) for (entity, score) in reversed(sorted(counter.items(), key=lambda x: x[1])))



class Tournament(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255, null=True, blank=True, default=None, help_text='Name to show on mobile devices.')

    creation_time = models.DateTimeField(auto_now_add=True)
    bye_score = models.DecimalField(max_digits=4, decimal_places=1, default=3, help_text='Score to assign for a bye.')

    description = models.TextField(null=True, blank=True, default=None, help_text='This appears at the beginning of the public page. You can use HTML tags.')
    default_round_visibility = models.CharField(max_length=2, choices=VISIBILITY_CHOICES, default=SHOW, help_text='Default visibility of newly generated rounds.')
    shown_players = models.PositiveIntegerField(null=True, blank=True, default=0, help_text='Number of players to show in the scoreboard. If no value is given, all players are shown. If 0, the player scoreboard is not shown.')

    # registration parameters
    is_registration_open = models.BooleanField(default=False)
    max_teams = models.PositiveIntegerField(null=True, blank=True, default=None, help_text='Maximum number of allowed teams during registration. If no value is given, the number is unlimited.')
    max_players_per_team = models.PositiveIntegerField(null=True, blank=True, default=0, help_text='Maximum number of allowed players per team during registration. If no value is given, the number is unlimited (probably unsupported!). If 0 is given, player registration is disabled.')    # TODO


    def __str__(self):
        return self.name

    def num_rounds(self):
        return Round.objects.filter(tournament=self).count()

    def can_register(self):
        return self.is_registration_open and (self.max_teams is None or Team.objects.count() < self.max_teams)

    def can_register_player(self):
        return self.is_registration_open and self.max_players_per_team > 0


    def team_scoreboard(self, public=False, fill_results=False):
        res = sum((match.team_scoreboard(public=public, fill_results=fill_results) for match in Match.objects.filter(round__tournament=self).prefetch_related('round', 'teamresult_set__team__player_set', 'teams')), Counter())
        for team in Team.objects.filter(active=True):
            if team not in res:
                res[team] = Score()
        return res

    def player_scoreboard(self, public=False):
        res = sum((match.player_scoreboard(public=public) for match in Match.objects.filter(round__tournament=self).prefetch_related('round', 'playerresult_set__player__team')), Counter())
        for player in Player.objects.filter(team__active=True):
            if player not in res:
                res[player] = Score()
        return res


    def create_round(self):
        """
        Create a new round for this tournament.
        """
        teams = Team.objects.filter(active=True).order_by('pk')
        tables = Table.objects.all()
        matches = Match.objects.filter(round__tournament=self)

        previous_pairs = set(match.team_pair() for match in matches)
        previous_byes = set(match.team_bye() for match in matches)

        previous_tables = {table: set() for table in tables}
        for match in matches:
            if match.table is not None:
                for team in match.teams.all():
                    previous_tables[match.table].add(team)

        ### pair teams ###
        if self.num_rounds() == 0:
            # random pairings
            team_queue = list(teams)
            random.shuffle(team_queue)
            pairs = []
            while len(team_queue) > 1:
                pairs.append((team_queue.pop(), team_queue.pop()))
            if len(team_queue) == 1:
                pairs.append((team_queue.pop(),))

        else:
            G = nx.Graph()
            G.add_nodes_from(teams)

            # analyze scoreboard
            scoreboard = self.team_scoreboard(public=False, fill_results=True) # pending results are considered as full victories for all teams
            # print("Scoreboard")
            # print(scoreboard)

            clusters = {} # clusters of teams with the same score
            for team in teams:
                score = scoreboard[team].to_int() # this is an integer score
                if score not in clusters:
                    clusters[score] = []
                clusters[score].append(team)

            # print(clusters)

            M = len(teams) * (max(clusters) - min(clusters)) + 1 # some big constant
            # print("M = %d" % M)

            score_to_pos = {}
            pos = 0
            for score in sorted(clusters):
                score_to_pos[score] = pos
                pos += 1

            # print(score_to_pos)

            for pair in itertools.combinations(teams, 2):
                if pair not in previous_pairs:
                    # create edge between teams
                    scores = tuple(scoreboard[team].to_int() for team in pair)
                    weight = - (max(scores) - min(scores)) * M ** score_to_pos[max(scores)]
                    G.add_edge(*pair, weight=weight)

            if len(teams) % 2 == 1:
                # add bye
                G.add_node(BYE)

                for team in teams:
                    if team not in previous_byes:
                        # create bye edge
                        score = scoreboard[team].to_int()
                        weight = - score * M ** pos
                        G.add_edge(team, BYE, weight=weight)

            # compute matching
            matching = nx.max_weight_matching(G, maxcardinality=True)
            pairs = list((a, b) if a != BYE and b != BYE else (a,) if b == BYE else (b,) for (a, b) in matching)

        # print(pairs)

        ### assign tables ###
        G = nx.Graph()
        G.add_nodes_from([pair for pair in pairs if len(pair) == 2])
        G.add_nodes_from(tables)

        for table in tables:
            for pair in pairs:
                if len(pair) == 2:
                    weight = table.priority # an integer between 0 and 100

                    if any(team in previous_tables[table] for team in pair):
                        # penalize this table
                        weight -= 1000

                    # create edge
                    G.add_edge(pair, table, weight=weight)

        # compute matching
        matching = nx.max_weight_matching(G, maxcardinality=True)

        pairs_to_tables = {}
        for edge in matching:
            # print(edge)
            if isinstance(edge[0], Table):
                edge = reversed(edge)

            pair, table = edge
            pairs_to_tables[pair] = table

        ### create new round ###
        if self.num_rounds() > 0:
            round_number = Round.objects.latest().number + 1
        else:
            round_number = 1

        round = Round.objects.create(number=round_number, tournament=self, visibility=self.default_round_visibility)

        for pair in pairs:
            match = Match.objects.create(
                round=round,
                type=(NORMAL if len(pair)==2 else BYE),
                table=(pairs_to_tables[pair] if pair in pairs_to_tables else None)
            )

            for team in pair:
                # this also creates PlayerResult objects, so we cannot use bulk_create
                TeamResult.objects.create(match=match, team=team)

        # return round and success/warning
        return round, sum(len(pair) for pair in pairs) == len(teams)


    class Meta:
        ordering = ['creation_time']
        get_latest_by = 'creation_time'



class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True, help_text='Inactive teams are not considered for future turns and do not appear in the scoreboard.')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']



class Player(models.Model):
    name = models.CharField(max_length=255)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True, default=None)

    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)

    is_captain = models.BooleanField(default=False)

    def _active(self):
        return self.team.active if self.team is not None else False
    _active.boolean = True
    active = property(_active)

    def __str__(self):
        return '%s (%s)' % (self.name, self.team.name if self.team is not None else 'no team')

    class Meta:
        ordering = ['team', 'name']
        # unique_together = ('team', 'name')
        # order_with_respect_to = 'team'



def validate_priority(value):
    if not 0 <= value <= 100:
        raise ValidationError(
            _('%(value)s is not between 0 and 100'),
            params={'value': value},
        )


class Table(models.Model):
    name = models.CharField(max_length=255)
    priority = models.IntegerField(default=50, validators=[validate_priority], help_text='A number between 0 and 100. Tables with higher priority are preferred when creating a new turn.')
    description = models.TextField(null=True, blank=True, default=None)


    def __str__(self):
        return self.name

    def num_matches(self):
        return Match.objects.filter(table=self).count()

    class Meta:
        ordering = ['name']
        unique_together = ('name',)



class Round(models.Model):
    number = models.IntegerField(validators=[MinValueValidator(1)])
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    visibility = models.CharField(max_length=2, choices=VISIBILITY_CHOICES, default=SHOW)
    scheduled_time = models.DateTimeField(blank=True, null=True, default=None, help_text="Used only for displaying purposes.")

    def __str__(self):
        return 'Round %d' % self.number

    def num_matches(self):
        return self.match_set.all().count()

    def completed_matches(self):
        return sum(1 for match in self.match_set.all() if match.type == BYE or all(team_result.score is not None for team_result in match.teamresult_set.all()))

    def team_scoreboard(self, public=False, fill_results=False):
        res = sum((match.team_scoreboard(public=public, fill_results=fill_results) for match in Match.objects.filter(round=self)), Counter())
        for team in Team.objects.filter(active=True):
            if team not in res:
                res[team] = Score()
        return res

    def valid_matches(self):
        return [match for match in self.match_set.all() if match.valid()]

    # def normal_matches(self):
    #     return [match for match in self.match_set.all() if match.type == NORMAL and match.valid()]

    def show_results(self):
        return self.visibility == SHOW

    class Meta:
        ordering = ['number']
        get_latest_by = 'number'



class Match(models.Model):
    TYPE_CHOICES = ((NORMAL, 'Normal'), (BYE, 'Bye'))

    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=NORMAL)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, blank=True, null=True, default=None)
    teams = models.ManyToManyField(Team, through='TeamResult')
    players = models.ManyToManyField(Player, through='PlayerResult')

    def __str__(self):
        num_teams = self.teams.count()
        if num_teams == 0:
            return 'Empty match'
        elif num_teams == 1 and self.type == BYE:
            return '%s (Bye)' % self.teams.get().name
        else:
            return ' - '.join(team.name for team in self.teams.all())


    def valid(self):
        """
        Check that there are exactly two teams, or one team in the case of a bye.
        """
        num_teams = self.teams.count()
        return num_teams == 1 and self.type == BYE or num_teams == 2 and self.type == NORMAL
    valid.boolean = True

    def team_pair(self):
        """
        Return the pair of playing teams, ordered by primary key.
        Return None if this match was a Bye.
        """
        if self.type == NORMAL:
            return tuple(self.teams.all().order_by('pk'))
        else:
            return None


    def team_bye(self):
        """
        Return the team if this match was a Bye, otherwise return None.
        """
        return self.teams.get() if self.type == BYE else None


    def result(self):
        if self.teams.count() < 2 or any(team_result.score is None for team_result in self.teamresult_set.all()):
            return None
        else:
            return ' - '.join(str(team_result.score) for team_result in self.teamresult_set.all())

    def team_scoreboard(self, public=False, fill_results=False):
        """
        Return a Counter with the scores of this match.
        """
        if public and self.round.visibility != SHOW:
            # the results for this match should be hidden
            return Counter()

        if self.type == BYE:
            return Counter({
                team_result.team: Score(Decimal('1.0'), self.round.tournament.bye_score, 1, BYE) for team_result in self.teamresult_set.all()
            })

        elif not self.valid() or any(team_result.score is None for team_result in self.teamresult_set.all()):
            # this match is not completed
            if fill_results:
                # treat all results as victories
                return Counter({
                    team_result.team: Score(Decimal('1.0'), self.round.tournament.bye_score, 1, NORMAL) for team_result in self.teamresult_set.all()
                })

            else:
                return Counter()

        else:
            scores = set(team_result.score for team_result in self.teamresult_set.all())
            if len(scores) == 1:
                # draw
                return Counter({
                    team_result.team: Score(Decimal('0.5'), team_result.score, 1, NORMAL) for team_result in self.teamresult_set.all()
                })

            else:
                # victory for one team
                return Counter({
                    team_result.team: Score(Decimal('1.0') if team_result.score == max(scores) else Decimal('0.0'), team_result.score, 1, NORMAL) for team_result in self.teamresult_set.all()
                })


    def player_scoreboard(self, public=False):
        if public and self.round.visibility != SHOW:
            # the results for this match should be hidden
            return Counter()

        if self.type == BYE:
            return Counter({
                player_result.player: Score(Decimal('1.0'), num_matches=1, match_type=BYE) for player_result in self.playerresult_set.all()
            })

        else:
            return Counter({
                player_result.player: Score(player_result.score if player_result.score is not None else Decimal('0.0'), num_matches=1, match_type=NORMAL) for player_result in self.playerresult_set.all()
            })


    class Meta:
        ordering = ['round', '-type', 'pk']
        verbose_name_plural = 'matches'


class TeamResult(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, default=None)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # call the "real" save() method.

        # create PlayerResult objects if they do not exist
        if PlayerResult.objects.filter(match=self.match, player__team=self.team).count() == 0:
            PlayerResult.objects.bulk_create([PlayerResult(match=self.match, player=player) for player in self.team.player_set.all()])
            # for player in self.team.player_set.all():
            #     PlayerResult.objects.create(match=self.match, player=player)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)  # call the "real" delete() method.

        # delete PlayerResult objects
        PlayerResult.objects.filter(match=self.match, player__team=self.team).delete()

    class Meta:
        ordering = ['match', 'team']


class PlayerResult(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, default=None)

    class Meta:
        ordering = ['match', 'player']
