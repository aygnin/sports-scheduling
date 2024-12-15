# Import the library and create a model
import math
import gurobipy as gp
from gurobipy import GRB
m = gp.Model("model")


#Initialize the parameters for epsilon constrained method
lambda_val = 0.0001
E = []
min_distance = []
min_home_away = []
gamma = float("inf")


# Set up the data
# Given data from league
n_teams = 15
games = 20
# Calculated data
total_games = n_teams * games / 2
games_t = math.floor(n_teams / 2)
time = math.ceil(total_games / games_t)
minpairing = math.floor(games / n_teams)
maxpairing = math.ceil(games / n_teams)
# Import the distances between teams and round to integers
f = open("distances.txt", "r")
data = f.readlines()
f.close()
distance = []
for line in data:
    split_line = line.split(", ")
    row = []
    for i in range(0, n_teams): 
        row.append(round(float(split_line[i])))
    distance.append(row)   


# Create the variables
# Games between home team and away team at time t (1 if game occuring, 0 otherwise)
x = m.addVars(n_teams, n_teams, time, vtype = GRB.BINARY, name = "x")
# Number of home games for each team
h = m.addVars(n_teams, vtype = GRB.INTEGER, name = "h")
# Number of away games for each team
a = m.addVars(n_teams, vtype = GRB.INTEGER, name = "a")
# Difference between home and away games for each team
dif_ha = m.addVars(n_teams, vtype = GRB.INTEGER, name = "dif_ha")


# Set the weighted objective function
# Minimize the total distance travelled by all teams
total_distance = 0
for j in range(0, n_teams):
    for i in range (0, n_teams):
        for t in range (0, time):
            total_distance += x[i, j, t] * (distance[j][i] + distance[i][j])
# Minimize the home and away game imbalance
home_away = 0
for i in range (0, n_teams):
    home_away += dif_ha[i]
m.setObjective(lambda_val * home_away + (1 - lambda_val) * total_distance, GRB.MINIMIZE)


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
# Take the absolute difference between home and away games for each team
for i in range(0, n_teams):
    m.addConstr(dif_ha[i] >= h[i] - a[i], f"dif_ha{i}")
    m.addConstr(dif_ha[i] >= a[i] - h[i], f"dif_ah{i}")
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


# Solve the model using the epsilon constrained method for IPs (modified for minimizing problem)
count = 0
while True:
    x_sum = 0
    for i in range(0, n_teams):
        for j in range (0, n_teams):
            for t in range (0, time):
                x_sum += x[i, j, t]
    m.addConstr(x_sum <= gamma, name="e-constrained")
    m.optimize()
    if m.status == GRB.OPTIMAL:     # Save the obtained solution if it is optimal
        x_star = {v.varName: v.x for v in m.getVars()}
        E.append(x_star)
        min_distance.append(total_distance.getValue())
        min_home_away.append(home_away.getValue())
        ctx = 0
        for i in range (0, n_teams):
            ctx += dif_ha[i].x
        gamma = ctx - 1             # Update gamma for the next iteration
        
        # Print the results to a file
        with open("scheduling_output.txt", "w") as file:
            print(m.status == GRB.OPTIMAL)
            # Optimal values
            print(f"Minimum total distance: {total_distance.getValue()}", file=file)
            print(f"Minimum home and away difference: {home_away.getValue()}", file=file)
            # Schedule grouped by teams
            print("\nSchedule grouped by teams: \n", file=file)
            for i in range(0, n_teams):
                print(f"Team {i}:", file=file)
                for j in range(0, n_teams):
                    if (i == j):
                            pass
                    else:
                        print(f" Game times vs Team {j:=2}: ", end="", file=file)
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
                        
    else:                           # If the problem is infeasible, stop
        break
    
