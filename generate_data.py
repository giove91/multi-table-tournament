import os
import sys
import django
import argparse
import names
import random


TEAM_NAMES = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta', 'Iota', 'Kappa', 'Lambda', 'Mu', 'Nu', 'Xi']

TABLE_NAMES = ['Astratti', 'Europei', 'Africani', 'Asiatici', 'Traguardo', 'Connessione', 'Scacchi', 'Dama', 'Atipici', 'Classici']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate random teams, players, and tables.')
    
    parser.add_argument('num_teams', type=int, help='number of teams')
    parser.add_argument('num_players', type=int, help='number of players per team')
    parser.add_argument('num_tables', type=int, help='number of tables')
    
    args = parser.parse_args()
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtt.settings')
    django.setup()
    
    from tournament.models import *
    
    # create teams
    print("Create teams")
    Team.objects.all().delete()
    team_names = random.sample(TEAM_NAMES, args.num_teams)
    teams = [Team.objects.create(name=name) for name in team_names]
    
    # create players
    for team in teams:
        players = [Player.objects.create(name=names.get_full_name(), team=team) for i in range(args.num_players)]
        print(players)
    
    # create tables
    print("Create tables")
    Table.objects.all().delete()
    table_names = random.sample(TABLE_NAMES, args.num_tables)
    tables = [Table.objects.create(name=name, priority=random.randint(0,100)) for name in table_names]
    print(tables)
