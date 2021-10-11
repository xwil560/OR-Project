import numpy as np
import pandas as pd
import os
from calculatecost import path_time, Cost
from solve_lp import route_modifier
from Lab6 import generateTaskTime
from typing import List
import tqdm as tq
import matplotlib.pyplot as plt
import pickle as pkl 

def change_demand(demands, time_1, time_2):
    unsatisfied_nodes = []
    new_routes1 = []
    new_routes2 = []
    N1 = 30 - len(time_1)
    N2 = 30 - len(time_2)
    for route in time_1:
        while calc_demand(demands, route) > 26:
            unsatisfied_nodes.append(route.pop(-1))
        new_routes1.append(route)
    for route in time_2:
        while calc_demand(demands, route) > 26:
            unsatisfied_nodes.append(route.pop(-1))
        new_routes2.append(route)
    
    return new_routes1, new_routes2, unsatisfied_nodes, N1, N2


def calc_demand(demand, route):
    return sum([demand[r] for r in route])

def random_times(df: pd.DataFrame, Nruns: int) -> List[pd.DataFrame]:
    random_time = lambda t: t if (t==0 or isinstance(t,str)) else generateTaskTime(t/2, t, 2*t)
    dfs = [df.iloc[0:0,:].copy() for i in range(Nruns)]
    for i in tq.trange(Nruns):
        dfs[i] = df.applymap(lambda t: random_time(t))

    return dfs

def simulation(time_1,time_2, weekend=False,Nruns = 100, filename="weekday_routesLOW.pkl"):
    
    costs = np.zeros(Nruns)
    locations_df = pd.read_csv("data" + os.sep + "WoolworthsLocations.csv")
    demand_df = pd.read_csv("data" + os.sep + "WoolworthsDemands.csv")
    duration_df = pd.read_csv("data" + os.sep + "WoolworthsTravelDurations.csv")
    
    time_dfs = random_times(duration_df, Nruns)
    dem_dicts = bootstrap_demands(locations_df, demand_df, weekend, Nruns)

    for i in tq.trange(Nruns):
        demands = dem_dicts[i]
        new_routes1, new_routes2, unsatisfied_nodes, N1, N2 = change_demand(demands, time_1, time_2)
        new_paths_w, new_paths_df = route_modifier(filename, unsatisfied_nodes, N1, N2)
        for route in new_routes1+new_routes2+new_paths_w:
            costs[i] += Cost(path_time(time_dfs[i], route)/60, calc_demand(demands, route))
        costs[i] += 2000*len(new_paths_df)

    return costs



def bootstrap_demands(locations_df, demand_df, weekend=False, Nruns=100):
    locations_df.set_index('Store', inplace=True)
    locations_df = locations_df[locations_df['Type'] != "Distribution Centre"]

    # Sample randomly from the actual demands
    demand_data = demand_df.melt(id_vars = 'Store', var_name = 'Date', value_name = 'Demand')
    demand_data['Date'] = pd.to_datetime(demand_data['Date'])
    demand_data['Weekday'] = demand_data.Date.dt.dayofweek 
    demand_data['Size'] = demand_data['Store'].map(lambda store: "Big" if locations_df.loc[store]['Type'] in ["Countdown"] else "Small")

    bootstrap_val = lambda size: demand_data[(demand_data['Size'] == size) & (demand_data['Weekday'].isin([5]) if weekend else demand_data['Weekday'].isin(list(range(0,5))))].sample(n=1)['Demand']
    # Apply random samples
    demand_dict = {
        "Countdown" : "Big",
        "Countdown Metro" : "Small",
        "SuperValue" : "Small", 
        "FreshChoice" : "Small",
    }
    
    
    # Create a np array with the contents
    return [{str(ldf[0]): int(bootstrap_val(demand_dict[ldf[1]])) for ldf in locations_df.itertuples()} for i in tq.trange(Nruns)]

if __name__ == "__main__":
    # locations_df = pd.read_csv("data" + os.sep + "WoolworthsLocations.csv")
    # demand_df = pd.read_csv("data" + os.sep + "WoolworthsDemands.csv")
    # demands = bootstrap_demands(locations_df, demand_df)
    # print(demands)
    # duration_df = pd.read_csv("data" + os.sep + "WoolworthsTravelDurations.csv")
    # print(random_times(duration_df, 10))
    routs = [['Countdown Manukau', 'Countdown Papatoetoe'], ['Countdown Roselands', 'Countdown Takanini'], ['Countdown Greenlane', 'Countdown Meadowbank'], ['Countdown Mt Wellington', 'Countdown Sylvia Park'], ['Countdown St Johns', 'Countdown Pakuranga'], ['Countdown Mangere East'], ['SuperValue Flatbush', 'Countdown Howick', 'FreshChoice Half Moon Bay'], ['Countdown Highland Park', 'Countdown Aviemore Drive'], ['Countdown Meadowlands', 'Countdown Botany Downs'],['Countdown Auckland City', 'Countdown Metro Albert Street', 'Countdown Metro Halsey Street'], ['Countdown Grey Lynn', 'Countdown Ponsonby'], ['Countdown Grey Lynn Central', 'Countdown Pt Chevalier'], ['Countdown Mt Eden', 'Countdown St Lukes'], ['Countdown Mt Roskill', 'Countdown Three Kings'], ['SuperValue Papakura', 'Countdown Papakura', 'FreshChoice Otahuhu'], ['Countdown Newmarket', 'Countdown Victoria Street West'], ['Countdown Blockhouse Bay', 'Countdown Lynfield'], ['Countdown Lynmall', 'SuperValue Avondale'], ['Countdown Birkenhead', 'Countdown Glenfield'], ['Countdown Mairangi Bay', 'Countdown Browns Bay'], ['Countdown Takapuna', 'Countdown Hauraki Corner'], ['Countdown Sunnynook', 'Countdown Milford'], ['Countdown Northcote'], ['Countdown Henderson', 'SuperValue Palomino', 'FreshChoice Ranui'], ['Countdown Kelston', 'FreshChoice Glen Eden', 'SuperValue Titirangi'], ['Countdown Northwest', 'Countdown Hobsonville'], ['Countdown Mangere Mall', 'Countdown Airport'], ['Countdown Lincoln Road', 'Countdown Westgate'], ['Countdown Te Atatu South', 'Countdown Te Atatu'], ['Countdown Manukau Mall', 'Countdown Manurewa'], ['FreshChoice Mangere Bridge', 'Countdown Onehunga']]
    time_1 = routs[:len(routs)//2]
    time_2 = routs[:(len(routs)-len(routs)//2)]
    costs = simulation(time_1,time_2, weekend=False,Nruns = 2, filename="weekday_routesHIGH.pkl")
    with open("cost_simulations" + os.sep + "WeekdayHigh.pkl","wb") as fp:
        pkl.dump(costs,fp)

    with open("cost_simulations" + os.sep + "WeekdayHigh.pkl","rb") as fp:
        print(pkl.load(fp))
    