import numpy as np
import pandas as pd
import itertools as iter
import json
import os
import pickle as pkl
from tqdm import trange 
import numba


def TSP_calculate(df_time,  stops, weekends=False):
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
    df_locs = pd.read_csv("data" + os.sep + "WoolworthsLocations.csv")
    if weekends:
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

    df = df_time.loc[['Distribution Centre Auckland']+stops, ['Distribution Centre Auckland']+stops] # subset the dataframe so that only relevant stores are present
    storetypes = df_locs.loc[[l in stops for l in df_locs.Store],"Type"]
    totalpalettes = sum([demands[s] for s in storetypes])
    time = lambda p: path_time(df,p) # partial function evaluates the time of a path using the subsetted dataframe

    times = list(map(time, paths)) # generate list of times by mapping the time function to each possible path

    mindex = np.argmin(times) # find the index with the shortest time

    total_time = (times[mindex])/60  +7.5*totalpalettes

    if total_time <= 240: # evaluate how expensive running this path is 
        cost = 3.75*total_time
        cost = 3.75*240 + (275/60)*(total_time -240)

    path = list(paths[mindex]) # convert the optimal path as a list 
    
    return path, cost

def path_time(df, path):
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
    
    time = lambda l1,l2: df.loc[l1][l2] # time takes two locations and outputs the time taken to go between them

    t = sum([time(*p) for p in zip(path[:-1],path[1:])]) # calculate the time taken to traverse the path by summing the distances between each pair

    return t

def import_json(filename):
    with open(filename) as fp:
        return json.loads(fp.read())

def create_LP_values(filename, weekend=False):
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
        "cost" : [0]*leng
        } # initialise dictionary to create 
    
    for store in df_t.Store: # add a column for each location
        if store != "Distribution Centre Auckland":
            dict[store] = [0]*leng
    
    df = pd.DataFrame(dict) # make into df


    for i in trange(leng): # for every route
        route = df.iloc[i] # take data for route 
        path, cost = TSP_calculate(df_t, route.path,weekend) # find the shortest path and its cost 
        df["path"].iloc[i] = path # add the optimal path and cost to the df
        df["cost"].iloc[i] = cost
        for loc in path: # for all stores the route goes through place 1 under all the columns corresponding to these stores
            df[loc].iloc[i] = 1



    return df
    

if __name__ == "__main__":
    # df = pd.read_csv("data" + os.sep + "WoolworthsTravelDurations.csv")
    
    # df.rename({'Unnamed: 0':"Store"}, axis=1, inplace=True)
    # # df = df.set_index("Store")
    
    # stops = ['Countdown Airport',  'Countdown Auckland City',  'Countdown Aviemore Drive']#,'Countdown Birkenhead','Countdown Blockhouse Bay']
    # p,c = TSP_calculate(df,  stops)
    # print(p,c)
    # # print(create_LP_values())
    df = create_LP_values("combinations_weekend.json", weekend=True)
    df.to_pickle("weekend_routes.pkl")
    # print(pd.read_pickle("weekday_routes.pkl"))
