import os
import sys
import django
import argparse
import random
from collections import Counter

TEAM_NAMES = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta', 'Iota', 'Kappa', 'Lambda', 'Mu', 'Nu', 'Xi', 'Omicron', 'Pi', 'Rho', 'Sigma', 'Tau', 'Upsilon', 'Phi', 'Chi', 'Psi', 'Omega']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simulate many tournaments.')

    parser.add_argument('-t', '--num_teams', type=int, nargs='?', default=16, help='number of teams')
    parser.add_argument('-s', '--num_simulations', type=int, nargs='?', default=100, help='number of simulations')
    parser.add_argument('-r', '--num_rounds', type=int, nargs='?', default=4, help='number of rounds per simulation')
    parser.add_argument('--num_tables', type=int, nargs='?', default=20, help='number of tables')
    parser.add_argument('alpha', type=float, nargs='?', default=0.4, help='probability that the stronger team wins')
    parser.add_argument('beta', type=float, nargs='?', default=0.4, help='probability that the weaker team wins')
    parser.add_argument('--research', action='store_true')

    args = parser.parse_args()

    print('Probability of victory of stronger team: {0:.2f}'.format(args.alpha), file=sys.stderr)
    print('Probability of victory of weaker team: {0:.2f}'.format(args.beta), file=sys.stderr)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtt.settings')
    django.setup()

    from tournament.models import *

    # clear database
    Tournament.objects.all().delete()
    Team.objects.all().delete()
    Table.objects.all().delete()

    # create tournament, teams, and tables
    tournament = Tournament.objects.create(name='Simulated tournament')

    teams = [Team(name=name) for name in TEAM_NAMES[:args.num_teams]]
    Team.objects.bulk_create(teams)
    teams = Team.objects.all()

    # tables = [Table(name='T{0:02d}'.format(i), priority=100-i) for i in range(1, args.num_tables+1)]
    tables = [Table(name='T{0:02d}'.format(i), priority=100) for i in range(1, args.num_tables+1)]
    Table.objects.bulk_create(tables)
    tables = Table.objects.all()

    # generate team strengths
    s = list(range(len(teams)))
    random.shuffle(s)
    strengths = {team: s[i] for i, team in enumerate(teams)}

    print('Teams sorted by decreasing strength: {}'.format(' '.join(team.name for team in sorted(teams, key=lambda team: -strengths[team]))), file=sys.stderr)

    # run simulations
    stats = Counter()

    if args.research:
        print(args.num_simulations)

    try:
        for i in range(args.num_simulations):
            print('Simulation {}'.format(i), end=' ', flush=True, file=sys.stderr)

            # clear rounds
            Round.objects.all().delete()

            # initialize set of used tables
            used_tables = set()
            team_tables = {team: [] for team in teams}

            for j in range(args.num_rounds):
                round, _ = tournament.create_round()

                if j == 0:
                    print('-- Round', end=' ', file=sys.stderr)
                print(round.number, end=' ', flush=True, file=sys.stderr)

                for match in round.match_set.all():
                    if match.type == NORMAL:
                        # record used table
                        used_tables.add(match.table)

                        # record team-table pairs
                        for team in match.teams.all():
                            team_tables[team].append(match.table)

                        a, b = match.teams.all()
                        if strengths[a] < strengths[b]:
                            # swap a and b
                            a, b = b, a

                        # generate outcome
                        scores = {}
                        x = random.random()

                        if x < args.alpha:
                            # stronger team wins
                            scores[a] = 1
                            scores[b] = 0

                        elif x < args.alpha + args.beta:
                            # weaker team wins
                            scores[a] = 0
                            scores[b] = 1

                        else:
                            # draw
                            scores[a] = 0.5
                            scores[b] = 0.5

                        # store result
                        for team_result in match.teamresult_set.all():
                            team_result.score = scores[team_result.team]
                            team_result.save()

            # compute used tables
            stats[len(used_tables)] += 1
            print('-- Used {} tables'.format(len(used_tables)), file=sys.stderr)

            if args.research:
                # gather description of these rounds (for each team, I remember which tables it saw)
                tables_to_id = {table: i for (i, table) in enumerate(tables)}
                # print(tables_to_id)
                # print(teams)
                for team, seen_tables in team_tables.items():
                    for table in seen_tables:
                        print(tables_to_id[table], end=' ')
                    print()
                sys.stdout.flush()

    except KeyboardInterrupt:
        pass

    print(stats, file=sys.stderr)
