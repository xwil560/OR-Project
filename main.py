from re import I
import pandas as pd
import numpy as np
import openrouteservice as ors
import os

import generate_maps as maps
import generate_partitions as partitions
import calculatecost as costs
import solve_lp as lp 

demands = {
    "weekday_routesLOW" : {
        "Countdown" : 8,
        "Countdown Metro" : 5,
        "SuperValue" : 5,
        "FreshChoice" : 5,
    },
    "weekend_routesLOW" : {
        "Countdown" : 4,
        "Countdown Metro" : 0,
        "SuperValue" : 0,
        "FreshChoice" : 0,
    }
}

if __name__ == "__main__":
    # Generate the partitions
    partition_data = pd.read_csv('data/WoolworthsRegions.csv')

    keys = {}
    keys['ORSkey'] = input("Please enter your ORS Key: ")
    
    for routing_type in ["weekday_routesLOW", "weekend_routesLOW"]:
        print(f"Generating all project components for {routing_type}.")
        print("------------------------")
        
        # Determine if it is a weekend
        weekend = True if "weekend" in routing_type else False

        week_stage = "weekend" if weekend else "weekday"

        # We start with "WoolworthsRegions.csv" which contains our stores
        # segmented into smaller regions based on geographical qualities.

        # Generate the partitions from our regions.
        if not weekend:
            partitions.generate_partitions(partition_data, weekend=False) 

        else:
            # Subset data
            weekend_data = partition_data[partition_data['Type'] == 'Countdown']

            partitions.generate_partitions(partition_data, weekend=True) 
        
        # Create routes and apply cost function
        df = costs.create_LP_values(f"combinations_{week_stage}.json")

        df_rc = costs.route_cost(demands[routing_type], df)

        df_rc.to_pickle("differentDemands" + os.sep + f"{routing_type}.pkl")

        # Solve LP for routes
        route_numbers = lp.routes_solver(f"{routing_type}.pkl")
        
        ors_client = ors.Client(key=keys['ORSkey'])

        locations = pd.read_csv("data" + os.sep + "WoolworthsLocations.csv", index_col='Store')

        # Map the resulting routes
        m = getattr(maps, f"create_{week_stage}_map")()
        
        [line.add_to(m) for line in maps.generate_selected_routes(ors_client, route_numbers, locations, route_df_filename=f"data/{week_stage}_routes.pkl")]

        m.save(f"maps/{week_stage}_map.html")
