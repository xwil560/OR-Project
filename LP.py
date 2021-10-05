from re import A
import numpy as np
from numpy.core.fromnumeric import shape
import pandas as pd
from pulp import *
import pickle as pkl

def weekday_routes_solver():
    # read in the pickle
    # data =pd.read_pickle("data" + os.sep + "weekday_routes.pkl")
    data = pd.read_csv("data" + os.sep + "testdata.csv")

    #for i in range(68):
    #    print(data.columns[i]) 

    cost = data["cost"]
    A = data.drop(["cost","path"],axis=1)
    print(A)

    routes = np.arange(len(data))
    
    R1=LpVariable.dicts("Shift One",routes,0,1,LpBinary)
    R2=LpVariable.dicts("Shift Two",routes,0,1,LpBinary)

    DF1 = LpVariable.dicts("Truck Routes Travelled",routes,0,1,LpBinary)
    DF2 = LpVariable.dicts("Truck Routes Travelled",routes,0,1,LpBinary)

    prob = LpProblem("Weekdays Routes Problem",LpMinimize)

    prob += lpSum([((DF2[i]+DF1[i])*2000) + (R1[i]+R2[i])*cost[i] for i in routes])

    for loc in A.columns:
        prob += lpSum([A[i]*R1[i] for i in routes]) + lpSum()
    

if __name__ == "__main__":
    weekday_routes_solver()