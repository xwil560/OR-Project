from re import A
import numpy as np
from numpy.core.fromnumeric import shape
import pandas as pd
from pulp import *
import pickle as pkl
from typing import List, Tuple, Dict


def routes_solver(input_data_filename: str) -> Tuple[List[pd.DataFrame], List[str], float]:
    '''
    Takes in a file name. Solves a linear problem, returning the cheapest price
    for pallet deliveries.


    inputs:
    ------
    input_data_filename : string
        file name of the routes, costs, locations being solved

    outputs:
    -------
    List_of_routes : List
        List of selected routes.

    '''

    # Read in the pickle
    data =pd.read_pickle("differentDemands" + os.sep + input_data_filename)
    data.reset_index(inplace=True)
    
    # Organize the data into costs and Aki matrix
    cost = data["cost"]
    if "weekend" in input_data_filename:
        df_locs = pd.read_csv("data" + os.sep + "WoolworthsLocations.csv")
        weekdaystores = list(df_locs.loc[df_locs.Type!="Countdown"].Store)
        weekdaystores.remove('Distribution Centre Auckland')
        A = data.drop(["cost","path", "total_time", "demand"]+weekdaystores,axis=1)
    else: 
        A = data.drop(["cost","path", "total_time", "demand"],axis=1)

    routes = np.arange(len(cost)) # Array to keep truck of the amount of routes

    # Generate binary variables for Amount of Trucks
    R1=LpVariable.dicts("Woolworths1",routes,0,1,LpBinary)
    R2=LpVariable.dicts("Woolworths2",routes,0,1,LpBinary)

    DF1 = LpVariable.dicts("DailyFreight1",routes,0,1,LpBinary)
    DF2 = LpVariable.dicts("DailyFreight2",routes,0,1,LpBinary)

    # Define the cost minimization problem
    prob = LpProblem("Routes Problem",LpMinimize)

    # Objective Function
    prob += lpSum([((DF2[i]+DF1[i])*2000) + (R1[i]+R2[i])*cost[i] for i in routes])

    # Store Delivery Maximum
    for loc in A.columns:
        if loc != "index":        
            prob += lpSum([A[loc].iloc[i]*(R1[i]+R2[i]+DF1[i]+DF2[i]) for i in routes]) == 1, "Store Delivery Maximum"+loc

    prob += lpSum([R1[i] for i in routes]) <= 30, 'Max trucks on Route 1'
    prob += lpSum([R2[i] for i in routes]) <= 30, 'Max trucks on Route 2'

    # Solving routines
    prob.writeLP('Routes.lp')

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

    # Return a list of the stop numbers
    list_of_routes = [data.path.iloc[int(v.name.split("_")[-1])] for v in prob.variables() if v.varValue == 1]
    list_of_trucks = [v.name.split("_")[0] for v in prob.variables() if v.varValue == 1]

    return List_of_routes, List_of_trucks, value(prob.objective)

def route_modifier(input_data_filename: str, unsatisfied_nodes: List[str], N1: int, N2: int) -> Tuple[List[pd.DataFrame], List[pd.DataFrame]]:
    '''
    Takes in a file name. Solves a linear problem, returning the cheapest price
    for pallet deliveries.


    inputs:
    ------
    input_data_filename : string
        file name of the routes, costs, locations being solved

    outputs:
    -------
    List_of_routes : List
        List of selected routes.

    '''

    # Read in the pickle
    data = pd.read_pickle("differentDemands" + os.sep + input_data_filename)

    
    df_locs = pd.read_csv("data" + os.sep + "WoolworthsLocations.csv")
    dropstores = [s for s in df_locs.Store if s not in unsatisfied_nodes]
    dropstores.remove('Distribution Centre Auckland')
    for s in dropstores:
        data = data[data[s]==0]
    data.reset_index(inplace=True)

    
    
    # Organize the data into costs and Aki matrix
    cost = data["cost"]
    if "weekend" in input_data_filename:
        df_locs = pd.read_csv("data" + os.sep + "WoolworthsLocations.csv")
        weekdaystores = List(df_locs.loc[df_locs.Type!="Countdown"].Store)
        weekdaystores.remove('Distribution Centre Auckland')
        A = data.drop(["cost","path", "total_time", "demand"]+weekdaystores+dropstores,axis=1)
    else: 
        A = data.drop(["cost","path", "total_time", "demand"]+dropstores,axis=1)

    print(data)
    routes = np.arange(len(cost)) # Array to keep truck of the amount of routes

    # Generate binary variables for Amount of Trucks
    R1=LpVariable.dicts("Woolworths1",routes,0,1,LpBinary)
    R2=LpVariable.dicts("Woolworths2",routes,0,1,LpBinary)

    DF1 = LpVariable.dicts("DailyFreight1",routes,0,1,LpBinary)
    DF2 = LpVariable.dicts("DailyFreight2",routes,0,1,LpBinary)

    # Define the cost minimization problem
    prob = LpProblem("Routes Problem",LpMinimize)

    # Objective Function
    prob += lpSum([((DF2[i]+DF1[i])*2000) + (R1[i]+R2[i])*cost[i] for i in routes])

    # Store Delivery Maximum
    for loc in A.columns:
        if loc != "index":
            prob += lpSum([A[loc].iloc[i]*(R1[i]+R2[i]+DF1[i]+DF2[i]) for i in routes]) == 1, "Store Delivery Maximum"+loc

    prob += lpSum([R1[i] for i in routes]) <= N1, 'Max trucks on Route 1'
    prob += lpSum([R2[i] for i in routes]) <= N2, 'Max trucks on Route 2'
   
    # Solving routines
    # prob.writeLP('Routes.lp')
    
    import time
    start = time.time()
    #prob.solve(COIN_CMD(threads=2,msg=1,fracGap = 0.0))
    PULP_CBC_CMD(msg=0).solve(prob)
    end = time.time()
    print(end-start)

    # The status of the solution is printed to the screen
    #print("Status:", LpStatus[prob.status])

    # Each of the variables is printed with its resolved optimum value
    for v in prob.variables():
        if v.varValue == 1:
            print(data.path.iloc[int(v.name.split("_")[-1])], "=", v.varValue)

    # The optimised objective function valof Ingredients pue is printed to the screen
    # print("Total Cost from Routes = ", value(prob.objective))

    # Return a List of the stop numbers
    
    list_of_routes_w = [data.path.iloc[int(v.name.split("_")[-1])] for v in prob.variables() if (v.varValue == 1 and "Woolworths" in v.name.split("_")[0])]
    list_of_routes_df = [data.path.iloc[int(v.name.split("_")[-1])] for v in prob.variables() if (v.varValue == 1 and "DailyFreight" in v.name.split("_")[0])]
    

    return list_of_routes_w, list_of_routes_df


if __name__ == "__main__":
    #routes_solver("weekday_routes.pkl")
    # routes_solver("weekday_routesLOW.pkl")
    stops = ['Countdown Airport',  'Countdown Auckland City',  'Countdown Aviemore Drive','Countdown Birkenhead','SuperValue Palomino']
    print(route_modifier("weekday_routesLOW.pkl", stops, 2, 1))

