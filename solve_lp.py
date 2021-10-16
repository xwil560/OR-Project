from os import remove
from re import A
import numpy as np
from numpy.core.fromnumeric import shape
from close_stores import *
import pandas as pd
from pulp import *
import pickle as pkl
from typing import List, Tuple, Dict, Optional


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

    return list_of_routes, list_of_trucks, value(prob.objective)

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
        weekdaystores = list(df_locs.loc[df_locs.Type!="Countdown"].Store)
        weekdaystores.remove('Distribution Centre Auckland')
        A = data.drop(["cost","path", "total_time", "demand"]+weekdaystores+dropstores,axis=1)
    else: 
        A = data.drop(["cost","path", "total_time", "demand"]+dropstores,axis=1)


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

def extra_trucks_solver(input_data_filename: str, removed_store: str, weekend: bool = False, Ntrucks: Optional[int] = None) -> Tuple[List[pd.DataFrame], List[str], float]:
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
    
    # Organize the data into costs and Aki matrix
    
    data = data[data[removed_store]==0]
    data.reset_index(inplace=True)

    
    
    # Organize the data into costs and Aki matrix
    cost = data["cost"]
    if "weekend" in input_data_filename:
        df_locs = pd.read_csv("data" + os.sep + "WoolworthsLocations.csv")
        weekdaystores = list(df_locs.loc[df_locs.Type!="Countdown"].Store)
        weekdaystores.remove('Distribution Centre Auckland')
        weekdaystores = list(np.array(weekdaystores)[np.array(weekdaystores)!=removed_store])
        A = data.drop(["cost","path", "total_time", "demand", removed_store]+weekdaystores,axis=1)
    else: 
        A = data.drop(["cost","path", "total_time", "demand", removed_store],axis=1)


    cost = data["cost"]
    routes = np.arange(len(cost)) # Array to keep truck of the amount of routes

    # Generate binary variables for Amount of Trucks
    R1=LpVariable.dicts("Woolworths1",routes,0,1,LpBinary)
    R2=LpVariable.dicts("Woolworths2",routes,0,1,LpBinary)

    DF1 = LpVariable.dicts("DailyFreight1",routes,0,1,LpBinary)
    DF2 = LpVariable.dicts("DailyFreight2",routes,0,1,LpBinary)

    if Ntrucks is None:
        Ntrucks = LpVariable("NewTrucks", 0, None, LpInteger)
    # Define the cost minimization problem
    prob = LpProblem("Routes Problem",LpMinimize)

    # Objective Function
    prob += lpSum([((DF2[i]+DF1[i])*2000) + (R1[i]+R2[i])*cost[i] for i in routes]) + 5000*Ntrucks

    # Store Delivery Maximum
    for loc in A.columns:
        if loc != "index":        
            prob += lpSum([A[loc].iloc[i]*(R1[i]+R2[i]+DF1[i]+DF2[i]) for i in routes]) == 1, "Store Delivery Maximum"+loc

    prob += lpSum([R1[i] for i in routes]) - Ntrucks <= 30, 'Max trucks on Route 1'
    prob += lpSum([R2[i] for i in routes]) - Ntrucks <= 30, 'Max trucks on Route 2'

    # Solving routines
    # prob.writeLP('Routes.lp')


    #prob.solve(COIN_CMD(threads=2,msg=1,fracGap = 0.0))
    PULP_CBC_CMD(msg=0).solve(prob)
    # prob.solve()

    # The status of the solution is printed to the screen
    #print("Status:", LpStatus[prob.status])

    # Each of the variables is printed with its resolved optimum value
    # for v in prob.variables():
    #     if v.varValue == 1:
    #         print(data.path.iloc[int(v.name.split("_")[-1])], "=", v.varValue)

    # The optimised objective function valof Ingredients pue is printed to the screen
    # print("Total Cost from Routes = ", value(prob.objective))

    # Return a list of the stop numbers
    list_of_routes = [data.path.iloc[int(v.name.split("_")[-1])] for v in prob.variables() if v.varValue == 1]
    list_of_trucks = [v.name.split("_")[0] for v in prob.variables() if v.varValue == 1]
    try:
        return list_of_routes, value(prob.objective), Ntrucks.varValue
    except AttributeError:
        return list_of_routes,  value(prob.objective), Ntrucks
    


if __name__ == "__main__":
    #routes_solver("weekday_routes.pkl")
    # routes_solver("weekday_routesLOW.pkl")
    # stops = ['Countdown Airport',  'Countdown Auckland City',  'Countdown Aviemore Drive','Countdown Birkenhead','SuperValue Palomino']
    # print(route_modifier("weekday_routesLOW.pkl", stops, 2, 1))
    # stops = pd.read_csv("data" + os.sep + "WoolworthsLocations.csv")
    # stops = stops[stops["Store"] != "Distribution Centre Auckland"]
    # removed_stores = [data[3] for data in stops.itertuples()]
    # Weekday_cost = []
    # Weekend_cost = []
    # Trucks = []

    # for removed_store in removed_stores:
    #     cost_weekday, trucks = extra_trucks_solver("weekday_routesLOW.pkl", removed_store)
    #     cost_weekend, _ = extra_trucks_solver("weekend_routesLOW.pkl", removed_store, weekend=True, Ntrucks = trucks)
    #     Weekday_cost.append(cost_weekday)
    #     Weekend_cost.append(cost_weekend)
    #     Trucks.append(trucks)
    #     # print(f"Removed: {removed_store}, Weekday Cost: {cost_weekday}, Weekend Cost: {cost_weekend}, Total Cost: {cost_weekday + cost_weekend}, Trucks: {trucks}")

    # output = pd.DataFrame({
    #     "removed_stores" : removed_stores,
    #     "weekday_cost" : Weekday_cost,
    #     "weekend_cost" : Weekend_cost,
    #     "Trucks" : Trucks,
    #     "Total_Cost" : np.array(Weekend_cost) + np.array(Weekday_cost),
    # })

    # output.to_pickle("removed_stores.pkl")
    closestores = close_stores()
    with open("removed_stores.pkl", "rb") as fp:
        df = pkl.load(fp)
    print(df.loc[df.removed_stores.isin(list(closestores.index))].iloc[np.argmin(df.loc[df.removed_stores.isin(list(closestores.index))].Total_Cost)])


    # removed_store = "Countdown Hobsonville"
    # routes_wkdy, cost_weekday, trucks = extra_trucks_solver("weekday_routesLOW.pkl", removed_store)
    # routes_wknd, cost_weekend, _ = extra_trucks_solver("weekend_routesLOW.pkl", removed_store, weekend=True, Ntrucks = trucks)
