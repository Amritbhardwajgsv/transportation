#code
import gurobipy as gp
from gurobipy import GRB

# Supply available at each factory
supply = [130, 150, 100, 130, 110]

# Demand at each warehouse
demand = [
    20, 30, 40, 30, 18,
    22, 30, 40, 10, 30,
    20, 60, 10, 30, 50,
    40, 10, 20, 40, 30
]

# Transportation cost
# Rows = Factories F1-F5
# Columns = Warehouses W1-W20
cost = [
    [13, 9, 15, 10, 12, 13, 11, 12, 13, 13,
     13, 9, 15, 10, 11, 11, 9, 15, 10, 12],

    [11, 10, 12, 12, 9, 9, 10, 9, 12, 9,
     11, 10, 12, 12, 9, 10, 10, 9, 12, 9],

    [12, 9, 11, 12, 9, 15, 12, 11, 13, 15,
     12, 11, 11, 10, 9, 12, 9, 11, 15, 9],

    [13, 12, 13, 12, 10, 10, 12, 12, 12, 10,
     12, 9, 10, 12, 10, 10, 12, 11, 12, 10],

    [13, 9, 15, 10, 12, 12, 9, 9, 10, 12,
     10, 15, 15, 10, 8, 13, 9, 10, 10, 12]
]

# Sets of factories and warehouses
I = range(len(supply))
J = range(len(demand))

# Create model
m = gp.Model("Transportation")

# Display optimization progress
m.setParam("OutputFlag", 1)

# Decision variables
# x[i,j] = units shipped from factory i to warehouse j
x = m.addVars(I, J, lb=0.0, name="x")

# Objective function: Minimize total transportation cost
m.setObjective(
    gp.quicksum(cost[i][j] * x[i, j] for i in I for j in J),
    GRB.MINIMIZE
)

# Supply constraints
for i in I:
    m.addConstr(
        gp.quicksum(x[i, j] for j in J) <= supply[i],
        name=f"supply_{i+1}"
    )

# Demand constraints
for j in J:
    m.addConstr(
        gp.quicksum(x[i, j] for i in I) >= demand[j],
        name=f"demand_{j+1}"
    )

# Optimize the model
m.optimize()

# Results
if m.Status == GRB.OPTIMAL:
    print(f"\nOptimal total cost: {m.ObjVal:g}\n")

    print("Shipment plan:")
    for i in I:
        for j in J:
            if x[i, j].X > 0:
                print(
                    f"F{i+1} -> W{j+1}: "
                    f"{x[i, j].X:g} units"
                )

    print("\nSupply usage:")
    for i in I:
        used = sum(x[i, j].X for j in J)
        print(
            f"F{i+1}: {used:g} / {supply[i]} units used"
        )

    print("\nDemand fulfillment:")
    for j in J:
        fulfilled = sum(x[i, j].X for i in I)
        print(
            f"W{j+1}: {fulfilled:g} / {demand[j]} units received"
        )

elif m.Status == GRB.INFEASIBLE:
    print("The model is infeasible.")

else:
    print("No optimal solution found. Status:", m.Status)