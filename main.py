from re import I
import pandas as pd
import numpy as np
import openrouteservice as ors
import os

import generate_maps as maps
import generate_partitions as partitions
import calculatecost as costs
import solve_lp as lp 
#import data_analysis

if __name__ == "__main__":
    # Generate the partitions
    partition_data = pd.read_csv('data/WoolworthsRegions.csv')

    for week_stage in ["weekday", "weekend"]:
        print(f"Generating {week_stage} partitions, routes, solutions and visualisations")
        print("------------------------")

        # Generate the partitions
        if week_stage == "weekday":
            partitions.generate_paritions(partition_data, weekend=False) 

        else:
            weekend_data = partition_data[partition_data['Type'] == 'Countdown']

            partitions.generate_paritions(partition_data, weekend=True) 
        
        # Create routes and apply cost function
        df = costs.create_LP_values(f"combinations_{week_stage}.json")
    
        df.to_pickle("data" + os.sep + f"{week_stage}_routes.pkl")

        # Solve LP for routes
        route_numbers = lp.routes_solver(f"{week_stage}_routes.pkl")
        
        keys = maps.read_keys()
        
        ors_client = ors.Client(key=keys['ORSkey'])

        locations = pd.read_csv("data/WoolworthsLocations.csv", index_col='Store')

        # Map the resulting routes
        m = getattr(maps, f"create_{week_stage}_map")()
        
        [line.add_to(m) for line in maps.generate_selected_routes(ors_client, route_numbers, locations, route_df_filename="data/weekday_routes.pkl")]

        m.save(f"maps/{week_stage}_map.html")
