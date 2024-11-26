# Import the library and create a model
import math
import gurobipy as gp
from gurobipy import GRB
m = gp.Model("model")


# Set up the data
# Given data from league
n_teams = 15
games = 20
# Calculated data
total_games = n_teams * games / 2
games_t = math.floor(n_teams / 2)
time = math.ceil(total_games / games_t) # TBD, may increase to include breaks
minpairing = math.floor(games / n_teams)
maxpairing = math.ceil(games / n_teams)
# Import the distances between teams
f = open("distances.txt", "r")
data = f.readlines()
f.close()
distance = []
for line in data:
    split_line = line.split(", ")
    row = []
    for i in range(0, n_teams): 
        row.append(float(split_line[i]))
    distance.append(row)   


# Create the variables
# Games between home team and away team at time t (1 if game occuring, 0 otherwise)
x = m.addVars(n_teams, n_teams, time, vtype = GRB.BINARY, name = "x")
# Number of home games for each team
h = m.addVars(n_teams, vtype = GRB.INTEGER, name = "h")
# Number of home games for each team
a = m.addVars(n_teams, vtype = GRB.INTEGER, name = "a")


# Set the objective function to minimize total distance travelled by all teams
total_distance = 0
for j in range(0, n_teams):
    for i in range (0, n_teams):
        for t in range (0, time):
            total_distance += x[i, j, t] * (distance[j][i] + distance[i][j])
m.setObjective(total_distance, GRB.MINIMIZE)


# Add the constraints
# Define the number of home games for each team
for i in range(0, n_teams):
    home = 0
    for j in range(0, n_teams):
        for t in range (0, time): 
            home += x[i, j, t]
    m.addConstr(h[i] == home, f"home{i}")
# Define the number of away games for each team
for j in range(0, n_teams):
    away = 0
    for i in range(0, n_teams):
        for t in range (0, time): 
            away += x[i, j, t]
    m.addConstr(a[j] == away, f"away{i}")
# Each team cannot play itself
for i in range(0, n_teams):
    for j in range (0, n_teams):
        for t in range (0, time):
            if (i == j):
                m.addConstr(x[i,j,t] == 0, f"itself{i}{j}") 
# Each team plays a set number of games
for i in range(0, n_teams):
    games_played = 0
    for j in range (0, n_teams):
            for t in range (0, time):
                games_played += x[i, j, t] + x[j, i, t]
    m.addConstr(games_played == games, f"games{i}")
# Each team plays at most one game at a time
for i in range(0, n_teams):    
    for t in range (0, time):
        games_t = 0
        for j in range(0, n_teams):
            games_t += x[i, j, t] + x[j, i, t]
        m.addConstr(games_t <= 1, f"time{i}{t}")
# Each team plays every other team a minimum and maximum number of times
for i in range(0, n_teams):
    for j in range(0, n_teams):
        pairings = 0
        for t in range (0, time):
            pairings += x[i ,j, t] + x[j, i, t]
        if (i != j):
            m.addConstr(pairings >= minpairing, f"minpairing{i}{j}")
            m.addConstr(pairings <= maxpairing, f"maxpairing{i}{j}")
# If one team plays another team multiple times, proportion of home/away games must be equal
    # TO DO
            

# Solve the model!
m.optimize()
# m.computeIIS()
# m.write("iis_report.ilp")


# Print the results to a file
with open("scheduling_output.txt", "w") as file:
    # Optimal value
    print(m.status == GRB.OPTIMAL)
    print(f"Minimum distance: {m.objVal}", file=file)
    # Schedule grouped by teams
    print("\nSchedule grouped by teams: \n", file=file)
    for i in range(0, n_teams):
        print(f"Team {i}:", file=file)
        for j in range(0, n_teams):
            if (i == j):
                    pass
            else:
                print(f" Games vs Team {j:=2}: ", end="", file=file)
                for t in range(0, time):
                    if x[i, j, t].x == 1:
                        print(f"{t:=2} (Home) ", end="", file=file)
                    elif x[j, i, t].x == 1:
                        print(f"{t:=2} (Away) ", end="", file=file)
                print("", file=file)
    # Schedule grouped by timeslots
    print("\nSchedule grouped by timeslots: \n", file=file)
    for t in range(time):
        print(f"Time Slot {t}:", file=file)
        playing_teams = set()
        for i in range(0, n_teams):
            for j in range(0, n_teams):
                if x[i, j, t].x == 1:
                    print(f" Team {i:=2} (Home) vs Team {j:=2} (Away)", file=file)
                    playing_teams.add(i)
                    playing_teams.add(j)
        for team in range(n_teams):
            if team not in playing_teams:
                print(f" Team {team:=2} not playing", file=file)
