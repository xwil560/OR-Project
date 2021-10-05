from re import A
import numpy as np
from numpy.core.fromnumeric import shape
import pandas as pd
from pulp import *
import pickle as pkl

def weekday_routes_solver():
    # read in the pickle
    data =pd.read_pickle("data" + os.sep + "weekday_routes.pkl")
    # data = pd.read_csv("data" + os.sep + "testdata.csv")

    #for i in range(68):
    #    print(data.columns[i]) 

    cost = data["cost"]
    A = data.drop(["cost","path"],axis=1)
    print(A)

    routes = np.arange(len(data))
    
    R1=LpVariable.dicts("Shift 1",routes,0,1,LpBinary)
    R2=LpVariable.dicts("Shift 2",routes,0,1,LpBinary)

    DF1 = LpVariable.dicts("Truck Routes Travelled 1",routes,0,1,LpBinary)
    DF2 = LpVariable.dicts("Truck Routes Travelled 2",routes,0,1,LpBinary)

    prob = LpProblem("Weekdays Routes Problem",LpMinimize)

    # Objective Function
    prob += lpSum([((DF2[i]+DF1[i])*2000) + (R1[i]+R2[i])*cost[i] for i in routes])

    
    # Store Delivery Maximum
    for loc in A.columns:
        prob += lpSum([A[loc].iloc[i]*(R1[i]+R2[i]) + A[loc].iloc[i]*(DF1[i]+DF2[i]) for i in routes]) == 1, "Store Delivery Maximum"+loc

    
    prob += lpSum([R1[i] for i in routes]) <= 30, 'Max trucks on Route 1'
    prob += lpSum([R2[i] for i in routes]) <= 30, 'Max trucks on Route 2'


    # Solving routines - no need to modify
    # prob.writeLP('Routes.lp')

    import time
    start = time.time()
    #prob.solve(COIN_CMD(threads=2,msg=1,fracGap = 0.0))
    prob.solve()
    end = time.time()
    print(end-start)

    # The status of the solution is printed to the screen
    #print("Status:", LpStatus[prob.status])

    # Each of the variables is printed with its resolved optimum value
    for v in prob.variables():
        if v.varValue == 1:
            print(data.path.iloc[int(v.name.split("_")[-1])], "=", v.varValue)

    # The optimised objective function valof Ingredients pue is printed to the screen    
    print("Total Cost from Routes = ", value(prob.objective))
    

if __name__ == "__main__":
    weekday_routes_solver()
