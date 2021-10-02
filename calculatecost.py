from os import path
import numpy as np
import pandas as pd
import itertools as iter

def TSP_calculate(df_time,  stops):
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

    df = df_time.loc[['Distribution Centre Auckland']+stops, ['Distribution Centre Auckland']+stops] # subset the dataframe so that only relevant stores are present
    
    time = lambda p: path_time(df,p) # partial function evaluates the time of a path using the subsetted dataframe

    times = list(map(time, paths)) # generate list of times by mapping the time function to each possible path

    mindex = np.argmin(times) # find the index with the shortest time

    cost = 3.75*((times[mindex])/60 + 7.5*len(stops)) # evaluate how expensive running this path is 

    path = list(paths[mindex]) # convert the optimal path as a list 
    
    return path, cost

def path_time(df, path):
    '''
    Takes a list of stops and computes the best order to travel them in
    
    
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

if __name__ == "__main__":
    df = pd.read_csv("WoolworthsTravelDurations.csv")
    
    df.rename({'Unnamed: 0':"Store"}, axis=1, inplace=True)
    df = df.set_index("Store")
    
    stops = ['Countdown Airport',  'Countdown Auckland City',  'Countdown Aviemore Drive']#,'Countdown Birkenhead','Countdown Blockhouse Bay']
    p,c = TSP_calculate(df,  stops)
    print(p,c)