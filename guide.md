# Tournament guide

Follow the next steps to create and run a tournament, assuming that the web application is already up and running.


## Create a new tournament

At the moment there is no support for more than one tournament at a time.
Make sure that there is only one Tournament object in the database, to be on the safe side.

A Tournament object has the following properties. They can be changed after the tournament has started.
- Name: it appears as the title of the public page.
- Bye score: how many points to give in a bye (i.e. when a team does not play in one round, because the number of teams is odd). The score only matters if the number of victories is tied, and a bye counts as a full victory (regardless of the number of points it gives).
- Default round visibility: the visibility of newly generated rounds (hidden, revealed but with hidden results, competely revealed). You can always change the visibility of a round after it is generated, this is just the default value.
- Shown players: the number of players shown in the individual scoreboard.
- Is registration open: if true, it allows teams and single players to register through the registration forms.
- Max teams: team registration is allowed only if the current number of teams in the database is less than this number. This is not a hard limit on the number of teams: you can always add teams through the admin interface.
- Max players per team: a player can register only in teams with less than this number of players. If this number is 0, then player registration is disabled. This number is not a hard limit on the number of players in a team: you can always add players through the admin interface.


### Create teams

Teams can be added and edited through the admin interface, at any time.
A team has a (possibly empty) list of players.

Do not delete a team after the first round has been generated, because this would mess up with its matches.
Rather, at any time you can make a team _inactive_: inactive teams are not shown in the team scoreboard, and players of inactive teams are not shown in the player scoreboard.
Inactive teams can be made active again at any time.
Inactive teams are not paired when a new round is generated.


### Create tables

Each match happens at a specific table, and different matches should happen at different tables during the same round (although you are free to create or edit a match so that it violates this principle).
You should make sure that the number of tables is at least half the number of teams, before generating rounds.

Tables have a priority, which is an integer number between 0 and 100. Tables with a higher priority are preferred, during round generation.

Tables can be added and edited also during the tournament. If the priority is changed, this will only affect future round generation. If you delete a table, all the matches that use this table become table-less.


## Create new rounds

After the Tournament object, the teams, and the tables are ready, you can create the first round.
It is always possible to manually create a round with its matches, but usually you are going to _generate_ a round automatically (and possibly edit it afterwards).
You can generate (or manually create) a new round even if not all matches of the previous rounds have been completed.

A round has the following properties.
- Number: newly generated rounds get the smallest positive natural number greater than the number of all existing rounds.
- Visibility: this affects what is shown in the public page. If set to _Hide_, the round does not appear at all in the public page. If set to _Hide results_, the round appears in the public page, but the results of the matches are not shown (and they do not affect the public scoreboards). If set to _Show_, the round appears in the public page together with all the results of completed matches.
- Scheduled time: if set, this time appears in the public page.

### Matches

A round also has a list of matches, which appear in the match list page.
Each match has a table, a type, and one or two teams.
The type is either _Normal_ (if the match has two teams) or _Bye_ (if the match has only one team, which is not paired for that round).
It also has a table.

Matches can be manually added, edited, and deleted, after a round is generated.


### Add results

When a match is completed, you can add its result in the match page.
You need to provide the score of both teams (even when a score is 0), otherwise the result is not taken into account.
The team with the highest score gets the match victory; if the two teams are tied, they get half a victory each.
In the tournament scoreboard, teams are ranked based on the number of victories, and then (in case of ties) based on the sum of the scores.

You can optionally add player results for a match.
This means that some of the players get points, which count for the player scoreboard.
The sum of the scores of the players of a team (in a given match) need not be equal to the score of the team for that match.


