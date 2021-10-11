from solve_lp import route_modifier
import numpy as np
import pandas as pd
import os

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


def simulation(Nruns, time_1,time_2):
    
    for i in range(Nruns):
        new_routes1, new_routes2, unsatisfied_nodes, N1, N2 = 0

def bootstrap_demands(locations_df, demand_df, weekend=False):
    locations_df.set_index('Store', inplace=True)
    locations_df = locations_df[locations_df['Type'] != "Distribution Centre"]

    # Sample randomly from the actual demands
    demand_data = demand_df.melt(id_vars = 'Store', var_name = 'Date', value_name = 'Demand')
    demand_data['Date'] = pd.to_datetime(demand_data['Date'])
    demand_data['Weekday'] = demand_data.Date.dt.dayofweek 
    demand_data['Size'] = demand_data['Store'].map(lambda store: "Big" if locations_df.loc[store]['Type'] in ["Countdown"] else "Small")

    bootstrap_val = lambda size: demand_data[(demand_data['Size'] == size) & (demand_data['Weekday'].isin([5,6]) if weekend else demand_data['Weekday'].isin(list(range(0,5))))].sample(n=1)['Demand']

    # Apply random samples
    demand_dict = {
        "Countdown" : bootstrap_val("Big"),
        "Countdown Metro" : bootstrap_val("Small"),
        "SuperValue" : bootstrap_val("Small"), 
        "FreshChoice" : bootstrap_val("Small"),
    }
    
    # Create a np array with the contents
    return {str(ldf[0]): int(demand_dict[ldf[1]]) for ldf in locations_df.itertuples()}

if __name__ == "__main__":
    locations_df = pd.read_csv("data" + os.sep + "WoolworthsLocations.csv")
    demand_df = pd.read_csv("data" + os.sep + "WoolworthsDemands.csv")
    demands = bootstrap_demands(locations_df, demand_df)
    print(demands)
