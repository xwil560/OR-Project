from re import I
import pandas as pd
import numpy as np
import openrouteservice as ors
import os
import pickle as pkl

import generate_maps as maps
import generate_partitions as partitions
import calculatecost as costs
import solve_lp as lp 
import simulation as sim

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
    
    simulation_iterations = 10
    
    for routing_type in ["weekday_routesLOW", "weekend_routesLOW"]:
        print(f"Generating all project components for {routing_type}.")
        print("------------------------")
        
        # Determine if it is a weekend
        weekend = True if "weekend" in routing_type else False

        week_stage = "weekend" if weekend else "weekday"

        # We start with "WoolworthsRegions.csv" which contains our stores
        # segmented into smaller regions based on geographical qualities.

        print("Generating region partitions")
        # Generate the partitions from our regions.
        if not weekend:
            partitions.generate_partitions(partition_data, weekend=False) 

        else:
            # Subset data
            weekend_data = partition_data[partition_data['Type'] == 'Countdown']

            partitions.generate_partitions(partition_data, weekend=True) 
        
        print("Generating routes and applying cost function")
        # Create routes and apply cost function
        df = costs.create_LP_values(f"combinations_{week_stage}.json")

        df_rc = costs.route_cost(demands[routing_type], df)

        df_rc.to_pickle("differentDemands" + os.sep + f"{routing_type}.pkl")

        print("Solving LP for routes to find inital optimal solution")
        # Solve LP for routes
        routes, _, _ = lp.routes_solver(f"{routing_type}.pkl")
        
        ors_client = ors.Client(key=keys['ORSkey'])

        print("Plotting solution on a map for visualisation")
        # Plot solution on map
        locations = pd.read_csv("data" + os.sep + "WoolworthsLocations.csv", index_col='Store')

        # Map the resulting routes
        m = getattr(maps, f"create_{week_stage}_map")()
        
        [line.add_to(m) for line in maps.generate_selected_routes(ors_client, routes, locations)]

        m.save(f"maps/{routing_type}_map.html")

        print("Simulating different demands for route selection")
        # Simulation
        costs = sim.simulation(
                            routes[:len(routes) // 2], 
                            routes[:(len(routes) - len(routes) // 2)], 
                            weekend = False, 
                            Nruns = simulation_iterations, 
                            filename = f"{routing_type}.pkl"
                            )

        with open("cost_simulations" + os.sep + f"{routing_type}.pkl", "wb") as fp:
            pkl.dump(costs, fp)

        print("Simulating the removal of a store")
        # Removed store simulation
        removed_store = "Countdown Northwest"

        routes_with_removed, _, _ = lp.extra_trucks_solver(
                                                    f"{routing_type}.pkl", 
                                                    removed_store, 
                                                    weekend = weekend, 
                                                    Ntrucks = 0
                                                    )

        costs = sim.simulation(
                            routes_with_removed[:len(routes_with_removed) // 2], 
                            routes_with_removed[:(len(routes_with_removed) - len(routes_with_removed) // 2)], 
                            weekend = weekend, 
                            Nruns = simulation_iterations, 
                            filename = f"{routing_type}.pkl"
                            )

        save_filename = "NW_removed_wknd.pkl" if weekend else "NW_removed_wkdy.pkl"
        with open("cost_simulations" + os.sep + save_filename, "wb") as fp:
            pkl.dump(costs,fp)

        print(f"All done for {routing_type}") 