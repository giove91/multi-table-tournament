import networkx as nx
import itertools
from collections import Counter
from decimal import Decimal

from django.db import models
from django.core.validators import RegexValidator

NORMAL = 'N'
BYE = 'B'


class Score:
    """
    A score of a team or a player.
    This class comprises a primary (more important) and a secondary (less important) score.
    It also keeps track of the number of matches and (in the case of one match)
    of the type of match (normal/bye).
    """
    def __init__(self, primary=0, secondary=0, num_matches=0, match_type=None):
        self.primary = primary
        self.secondary = secondary
        self.num_matches = num_matches
        self.match_type = match_type
    
    
    def __repr__(self):
        return "(%r, %r)" % (self.primary, self.secondary)
    
    def __le__(self, other):
        return self.primary < other.primary or self.primary == other.primary and self.secondary <= other.secondary
    
    def to_int(self):
        """
        Integer representation of the score, used in round creation.
        The primary score weights much more than the secondary score.
        """
        return int(10*(100 * self.primary + self.secondary))
    
    
    def __add__(self, other):
        return Score(self.primary + other.primary, self.secondary + other.secondary, self.num_matches + other.num_matches)
    
    def __radd__(self, other):
        if other is 0:
            return self
        else:
            return self + other


class Tournament(models.Model):
    name = models.CharField(max_length=1024)
    creation_time = models.DateTimeField(auto_now_add=True)
    bye_score = models.DecimalField(max_digits=4, decimal_places=1, default=3, help_text='Score to assign for a bye.')
    
    def __str__(self):
        return self.name
    
    def num_rounds(self):
        return Round.objects.filter(tournament=self).count()
    
    
    def create_round(self):
        """
        Create a new round for this tournament.
        """
        teams = Team.objects.filter(active=True).order_by('pk')
        tables = Table.objects.all()
        # rounds = Round.objects.filter(tournament=self)
        matches = Match.objects.filter(round__tournament=self)
        
        BYE = 'BYE'
        
        previous_pairs = set(match.team_pair() for match in matches)
        previous_byes = set(match.team_bye() for match in matches)
        
        # pair teams
        G = nx.Graph()
        G.add_nodes_from(teams)
        
        # TODO: set correct weights based on the scoreboard
        
        for pair in itertools.combinations(teams, 2):
            if pair not in previous_pairs:
                G.add_edge(*pair, weight=1)

        if len(teams) % 2 == 1:
            # add bye
            G.add_node(BYE)
            G.add_weighted_edges_from((team, BYE, 1) for team in teams if team not in previous_byes)

        
        print(G.edges(data=True))

    
    class Meta:
        ordering = ['creation_time']
        get_latest_by = 'creation_time'



class Team(models.Model):
    name = models.CharField(max_length=1024)
    active = models.BooleanField(default=True, help_text='Inactive teams are not considered for future turns and do not appear in the scoreboard.')
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
    


class Player(models.Model):
    name = models.CharField(max_length=256)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True, default=None)
    
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    is_captain = models.BooleanField(default=False)
    
    
    def __str__(self):
        return '%s (%s)' % (self.name, self.team.name)
    
    class Meta:
        order_with_respect_to = 'team'



class Table(models.Model):
    name = models.CharField(max_length=256)
    priority = models.IntegerField(default=100, help_text='Tables with higher priority are preferred when creating a new turn.')
    

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        unique_together = ('name',)



class Round(models.Model):
    number = models.PositiveIntegerField()
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField(blank=True, null=True, default=None, help_text="Used only for displaying purposes.")
    
    
    def __str__(self):
        return 'Round %d' % self.number
    
    class Meta:
        ordering = ['number']
        get_latest_by = 'number'



class Match(models.Model):
    TYPE_CHOICES = ((NORMAL, 'Normal'), (BYE, 'Bye'))
    
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=NORMAL)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, blank=True, null=True, default=None)
    teams = models.ManyToManyField(Team, through='TeamResult')
    players = models.ManyToManyField(Player, through='PlayerResult')
    
    def __str__(self):
        return ' - '.join(team.name for team in self.teams.all()) if self.teams.count() > 0 else 'Empty match'
    
    
    def team_pair(self):
        """
        Return the pair of playing teams, ordered by primary key.
        Return None if this match was a Bye.
        """
        if self.type == NORMAL:
            return self.teams.all().order_by('pk')
        else:
            return None
    
    
    def team_bye(self):
        """
        Return the team if this match was a Bye, otherwise return None.
        """
        return self.teams.get() if self.type == BYE else None
    
    
    def team_score_counter(self, fill_results=False):
        """
        Return a Counter with the scores of this match.
        """
        if self.type == BYE:
            return Counter({
                team_result.team: Score(1, self.round.tournament.bye_score, 1, BYE) for team_result in self.teamresult_set.all()
            })
        
        elif any(team_result.score is None for team_result in self.teamresult_set.all()):
            # this match is not completed
            if fill_results:
                # treat all results as victories
                return Counter({
                    team_result.team: Score(1, self.round.tournament.bye_score, 1, NORMAL) for team_result in self.teamresult_set.all()
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
                    team_result.team: Score(1 if team_result.score == max(scores) else 0, team_result.score, 1, NORMAL) for team_result in self.teamresult_set.all()
                })
    
    
    class Meta:
        ordering = ['round', '-type', 'pk']
        verbose_name_plural = 'matches'


class TeamResult(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, default=None)
    
    class Meta:
        ordering = ['match', 'team']


class PlayerResult(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, default=None)
    
    class Meta:
        ordering = ['match', 'player']


