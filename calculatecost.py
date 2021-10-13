import numpy as np
import pandas as pd
import itertools as iter
import json
import os
import pickle as pkl
from tqdm import trange
from typing import List, Tuple, Dict

def TSP_calculate(df_time: pd.DataFrame,  stops: List[str]) -> Tuple[List[str], float]:
    '''
    Takes a list of stops and computes the best order to travel them in


    inputs:
    ------
    df_time : dataframe
        dataframe containing the time between each pair of locations
    stops : list
        list containing the stops that the route must go through

    outputs:
    -------
    path : list
        list containing the stops in order
    cost : float
        cost (in nz$) of taking the trip
    '''

    paths = list(iter.permutations(stops)) # create a list of all possible permutations
    stops = list(stops)
    df_time = df_time.set_index("Store")
    df = df_time.loc[['Distribution Centre Auckland']+stops, ['Distribution Centre Auckland']+stops] # subset the dataframe so that only relevant stores are present
    

    time = lambda p: path_time(df,p) # partial function evaluates the time of a path using the subsetted dataframe

    times = list(map(time, paths)) # generate list of times by mapping the time function to each possible path

    mindex = np.argmin(times) # find the index with the shortest time

    total_time = (times[mindex])/60

    
    path = list(paths[mindex]) # convert the optimal path as a list

    return path, total_time
 

def TSP_calculate_old(df_time: pd.DataFrame,  stops: List[str], weekend: bool = False) -> Tuple[List[str], float]:
    '''
    Takes a list of stops and computes the best order to travel them in


    inputs:
    ------
    df_time : dataframe
        dataframe containing the time between each pair of locations
    stops : list
        list containing the stops that the route must go through
    weekend : bool
        Whether the TSP calculation should be for the weekend or otherwise (demandwise).

    outputs:
    -------
    path : list
        list containing the stops in order
    cost : float
        cost (in nz$) of taking the trip
    '''

    paths = list(iter.permutations(stops)) # create a list of all possible permutations
    df_locs = pd.read_csv("data" + os.sep + "WoolworthsLocations.csv")
    if weekend:
        demands = {
            "Countdown" : 4
        }
    else:
        demands = {
            "Countdown" : 8,
            "Countdown Metro" : 5,
            "SuperValue" : 5,
            "FreshChoice" : 5,
        }       
    df_time = df_time.set_index("Store")

    locations = pd.read_csv("data/WoolworthsLocations.csv")

    df = df_time.loc[['Distribution Centre Auckland']+stops, ['Distribution Centre Auckland']+stops] # subset the dataframe so that only relevant stores are present
    
    df_locs = locations[locations['Store'].isin(list(stops))] # subset the dataframe so that only relevant stores are present

    total_stops = sum([demands[location] for location in df_locs['Type']])
    time = lambda p: path_time(df,p) # partial function evaluates the time of a path using the subsetted dataframe

    times = list(map(time, paths)) # generate list of times by mapping the time function to each possible path

    mindex = np.argmin(times) # find the index with the shortest time

    total_time = (times[mindex])/60  +7.5*total_stops

    if total_time <= 240: # evaluate how expensive running this path is
        cost = 3.75*((times[mindex])/60 + 7.5*total_stops)
    else:
        cost = 3.75*240 + (275/60)*((times[mindex])/60 + 7.5*total_stops-240)

    path = list(paths[mindex]) # convert the optimal path as a list

    return path, cost

def path_time(df: pd.DataFrame, path: List[str]) -> float:
    '''
    calculates the time taken to traverse a path in a certain order


    inputs:
    ------
    df : dataframe
        dataframe containing the time between each pair of locations
    path : list
        list showing the order in which the nodes are traversed

    outputs:
    -------
    t : float
        time taken to complete the trip in this order
    '''

    path = ["Distribution Centre Auckland"] + list(path) + ["Distribution Centre Auckland"] # make sure the path starts and ends in Favona
    df = df.set_index("Unnamed: 0")
    time = lambda l1,l2: df.loc[l1][l2] # time takes two locations and outputs the time taken to go between them

    t = sum([time(*p) for p in zip(path[:-1],path[1:])]) # calculate the time taken to traverse the path by summing the distances between each pair

    return t

def import_json(filename: str) -> Dict[str, str]:
    with open(filename) as fp:
        return json.loads(fp.read())

def create_LP_values(filename: str) -> pd.DataFrame:
    '''
    creates a dataframe to be used in the linear program formulation


    inputs:
    ------
    filename : string
        name of the json file in the data folder containing hte relevant routes being used

    outputs:
    -------
    df : pandas Dataframe
        dataframe containing all the information needed to solve the LP
    '''

    df_t = pd.read_csv("data" + os.sep + "WoolworthsTravelDurations.csv") # read in csv of times

    df_t.rename({'Unnamed: 0':"Store"}, axis=1, inplace=True) # modify to the correct format for the TSP_calculate func

    routes = import_json("data" + os.sep + filename) # import subsets from json file
    leng = routes["total_combinations"]

    dict = {
        "path" : routes["combinations"],
        "total_time" : [0]*leng
        } # initialise dictionary to create

    for store in df_t.Store: # add a column for each location
        if store != "Distribution Centre Auckland":
            dict[store] = [0]*leng

    df = pd.DataFrame(dict) # make into df

    for i in trange(leng): # for every route
        route = df.iloc[i] # take data for route
        if "weekend" in filename:
            path, cost = TSP_calculate(df_t, route.path, weekend=True) # find the shortest path and its cost
        else:
            path, cost = TSP_calculate(df_t, route.path, weekend=False) # find the shortest path and its cost

        df["path"].iloc[i] = path # add the optimal path and cost to the df
        df["total_time"].iloc[i] = cost
        for loc in path: # for all stores the route goes through place 1 under all the columns corresponding to these stores
            df[loc].iloc[i] = 1



    return df

def route_demand(dict: Dict[str, int], path: List[str]) -> int:
    df_locs = pd.read_csv("data" + os.sep + "WoolworthsLocations.csv",index_col="Store")
    df_locs["Demand"] = df_locs["Type"].map(dict)
    total_demand = sum([df_locs.loc[store].Demand for store in path])
    return total_demand

def route_cost(dict: Dict[str, int], df: pd.DataFrame) -> pd.DataFrame:
    demands = lambda path: route_demand(dict, path)
    df["demand"] = df.path.map(demands)
    df = df.loc[df.demand<=26]
    vCost = np.vectorize(Cost)

    df["cost"] = vCost(df.total_time, df.demand)
    return df 

def Cost(travel_t: float, palletes: int) -> float:
    total_time = travel_t + 7.5*palletes
    if total_time <= 240: # evaluate how expensive running this path is
        cost = 3.75*total_time
    else:
        cost = 3.75*240 + (275/60)*(total_time-240)
    return cost


if __name__ == "__main__":
    # df = pd.read_csv("data" + os.sep + "WoolworthsTravelDurations.csv")

    # df.rename({'Unnamed: 0':"Store"}, axis=1, inplace=True)
    # # df = df.set_index("Store")

    # stops = ['Countdown Airport',  'Countdown Auckland City',  'Countdown Aviemore Drive','Countdown Birkenhead','SuperValue Palomino']
    # p,c = TSP_calculate(df,  stops)
    # print(p,c)
    # print(create_LP_values())
    import time
    o=time.time()
    df = create_LP_values("combinations_weekday.json")
    df.to_pickle("data/weekday_routes.pkl")
    print(time.time()-o)
    df = pd.read_pickle("data/weekend_routes.pkl")
    

    demands = {
        "Countdown" : 4,
        "Countdown Metro" : 27,
        "SuperValue" : 27,
        "FreshChoice" : 27,
    }     

    import time
    o=time.time()
    dflow = route_cost(demands, df)
    print(time.time()-o)
    dflow.to_pickle("differentDemands/weekend_routesLOW.pkl")
    # print(route_demand(demands, stops))
