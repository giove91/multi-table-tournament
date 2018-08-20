import os
import sys
import django
import argparse
import names
import random

from decimal import Decimal



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate random results for all existing matches.')
    
    args = parser.parse_args()
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtt.settings')
    django.setup()
    
    from tournament.models import *
    
    tournament = Tournament.objects.latest()
    print(tournament)
    
    for match in Match.objects.filter(round__tournament=tournament):
        if len(match.team_scoreboard()) == 0 and match.teams.count() == 2:
            print(match)
            
            teams = list(match.teams.all())
            scores = Counter()
            
            while sum(scores.values()) < tournament.bye_score:
                # give 0.5 points to some team
                if random.random() < 1.5**(-teams[0].pk) / sum(1.5**(-team.pk) for team in teams):
                    team = teams[0]
                else:
                    team = teams[1]
                
                scores[team] += Decimal('0.5')
            
            print(scores)
            
            for team_result in match.teamresult_set.all():
                team_result.score = scores[team_result.team]
                team_result.save()
