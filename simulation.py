import numpy as np
import pandas as pd
import os

from seaborn.palettes import color_palette
from calculatecost import path_time, Cost
from solve_lp import route_modifier, routes_solver
from Lab6 import generateTaskTime
from typing import List
import tqdm as tq
import matplotlib.pyplot as plt
import pickle as pkl 
import seaborn as sns
from glob import glob
from typing import List, Dict, Optional, Tuple

def change_demand(demands: List[Dict[str, str]], time_1: List[List[str]], time_2: List[List[str]]) -> Tuple[List[str], List[str], List[str], int, int]:
    '''
    Generates a set of routes and unsatisfied nodes give a new demand distrubution. 

    inputs:
    ------
    demands: List[dict[str, str]]
        A dictionary of stores and their generated demands.

    time_1: List[List[str]]
        A List of routes in the first time slot.

    time_2: List[List[str]]) 
        A List of routes in the second time slot.
    
    outputs:
    ------
    new_routes1: List[str]
    
    new_routes2: List[str]
    
    unsatisfied_nodes: List[str]
    
    N1: int
    
    N2: int
    '''
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


def calc_demand(demand: List[Dict[str, str]], route: List) -> int:
    return sum([demand[r] for r in route])

def random_times(df: pd.DataFrame, Nruns: int) -> List[pd.DataFrame]:
    random_time = lambda t: t if (t==0 or isinstance(t,str)) else generateTaskTime(t*.75, t, 2.5*t)
    dfs = [df.iloc[0:0,:].copy() for i in range(Nruns)]
    for i in tq.trange(Nruns):
        dfs[i] = df.applymap(lambda t: random_time(t))

    return dfs

def simulation(time_1: List[List[str]], time_2: List[List[str]], weekend: Optional[bool] = False, Nruns: Optional[int] = 100, filename: Optional[str] = "weekday_routesLOW.pkl") -> List[int]:
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


def bootstrap_demands(locations_df: pd.DataFrame, demand_df: pd.DataFrame, weekend: Optional[bool] = False, Nruns: Optional[int] = 100) -> Dict[str, int]:
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


def summarise_stats(filename: str, density: Optional[bool] = False) -> None:
    with open("cost_simulations" + os.sep + filename,"rb") as fp:
        data = pkl.load(fp)    
    
    m = np.mean(data)
    med = np.median(data)
    s = np.std(data)
    lq = np.percentile(data, 2.5)
    uq = np.percentile(data, 97.5)
    
    f, ax = plt.subplots(1, 2)
    if density:
        sns.kdeplot(data/1000, ax=ax[0])
    else:
        ax[0].hist(data/1000, density=True, bins = 40, color="g") if "Weekend" in filename else ax[0].hist(data/1000, density=True, bins = 40)
    ax[0].vlines(np.percentile(data/1000, 2.5),0,.25, color = "r", linestyles = "-.")
    ax[0].vlines(np.percentile(data/1000, 97.5),0,.25, color = "r", linestyles = "-.")
    ax[0].set_title(filename.split(".")[0])
    ax[0].set_xlabel("Cost (in thousands of $)")
    ax[0].set_ylabel("Frequency")
    ax[1].text(0.1, 0.7, f"Mean : {np.round(m,2):5}\nMedian : {np.round(med,2):5}\n$\sigma$ : {np.round(s,2):.5}\n95% confidence interval :\n   [{np.round(lq,2):5},{np.round(uq,2):5}]")
    ax[1].set_xticks([])
    ax[1].set_yticks([])

    plt.savefig("histograms" + os.sep + filename.split(".")[0])

if __name__ == "__main__":
    # locations_df = pd.read_csv("data" + os.sep + "WoolworthsLocations.csv")
    # demand_df = pd.read_csv("data" + os.sep + "WoolworthsDemands.csv")
    # demands = bootstrap_demands(locations_df, demand_df)
    # print(demands)
    # duration_df = pd.read_csv("data" + os.sep + "WoolworthsTravelDurations.csv")
    # print(random_times(duration_df, 10))
    # demand_file = ""
    # routs, x, y = routes_solver(demand_file)    
    routs = [['Countdown Sylvia Park', 'Countdown Greenlane', 'Countdown Onehunga'], ['Countdown St Johns', 'Countdown Meadowbank', 'Countdown Mt Wellington'], ['Countdown Highland Park', 'Countdown Aviemore Drive', 'Countdown Pakuranga'], ['Countdown Howick', 'Countdown Meadowlands', 'Countdown Botany Downs'], ['Countdown Newmarket', 'Countdown Auckland City', 'Countdown Victoria Street West'], ['Countdown Three Kings'], ['Countdown Lynfield', 'Countdown Blockhouse Bay', 'Countdown Pt Chevalier'], ['Countdown Birkenhead', 'Countdown Glenfield', 'Countdown Northcote'], ['Countdown Browns Bay', 'Countdown Mairangi Bay', 'Countdown Sunnynook'], ['Countdown Hauraki Corner', 'Countdown Milford', 'Countdown Takapuna'], ['Countdown Lynmall', 'Countdown Kelston', 'Countdown Henderson'], ['Countdown Westgate', 'Countdown Northwest', 'Countdown Hobsonville'], ['Countdown Manurewa', 'Countdown Airport', 'Countdown Mangere Mall'], ['Countdown Takanini', 'Countdown Roselands', 'Countdown Papakura'], ['Countdown Mangere East'], ['Countdown Grey Lynn', 'Countdown Ponsonby', 'Countdown Grey Lynn Central'], ['Countdown Mt Eden', 'Countdown St Lukes', 'Countdown Mt Roskill'], ['Countdown Lincoln Road', 'Countdown Te Atatu South', 'Countdown Te Atatu'], ['Countdown Manukau Mall', 'Countdown Manukau', 'Countdown Papatoetoe']]
    time_1 = routs[:len(routs)//2]
    time_2 = routs[:(len(routs)-len(routs)//2)]
    costs = simulation(time_1,time_2, weekend=True,Nruns = 1000, filename="weekend_routesHIGH.pkl")
    with open("cost_simulations" + os.sep + "WeekendHigh.pkl","wb") as fp:
        pkl.dump(costs,fp)

    # #with open("cost_simulations" + os.sep + "WeekdayHigh.pkl","rb") as fp:
    #  #   print(pkl.load(fp))

    # costs = simulation(time_1,time_2, weekend=False,Nruns = 1000, filename="weekday_routesHIGH.pkl")
    # with open("cost_simulations" + os.sep + "WeekdayHigh.pkl","wb") as fp:
    #     pkl.dump(costs,fp)

    # with open("cost_simulations" + os.sep + "WeekdayHigh.pkl","rb") as fp:
    #     print(pkl.load(fp))
    

    files = glob("cost_simulations" + os.sep + "*")
    for f in files:
        summarise_stats(f.split(os.sep)[-1])
