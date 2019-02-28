import os
import sys
import django
import argparse


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtt.settings')
    django.setup()
    
    from tournament.models import *
    
    parser = argparse.ArgumentParser(description='Create a new tournament.')
    parser.add_argument('name', nargs='+', help='name of the tournament')
    args = parser.parse_args()
    
    tournament = Tournament.objects.create(name=' '.join(args.name))
    print("Created tournament:", tournament)
