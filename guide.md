# Tournament guide

Follow the next steps to create and run a tournament, assuming that the web application is already up and running.


## Create a new tournament

At the moment there is no support for more than one tournament at a time.
Make sure that there is only one Tournament object in the database, to be on the safe side.

A Tournament object has the following properties. They can be changed after the tournament has started.
- Bye score: how many points to give in a bye (i.e. when a team does not play in one round, because the number of teams is odd). The score only matters if the number of victories is tied, and a bye counts as a full victory (regardless of the number of points it gives).
- Default round visibility: the visibility of newly generated rounds (hidden, revealed but with hidden results, competely revealed). You can always change the visibility of a round after it is generated, this is just the default value.
- Shown players: the number of players shown in the individual scoreboard.
- Is registration open: if true, it allows teams to register through the team registration form, provided that the maximum number of allowed teams was not reached (see next).
- Max teams: the registration is allowed only if the current number of teams in the database is less than this number. This is not a hard limit on the number of teams: you can always add teams from the admin interface.

