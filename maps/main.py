from math import comb
import numpy as np
import pandas as pd
import openrouteservice as ors
import folium
import json
import itertools

from pandas.core.accessor import register_index_accessor

def create_map():
    locations = pd.read_csv("../WoolworthsLocations.csv")
    coords = locations[['Long','Lat']]
    coords = coords.to_numpy().tolist()

    m = folium.Map(location = list(reversed(coords[2])), tiles=None, zoom_start=10)

    tile_layer = folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        max_zoom=19,
        name='darkmatter',
        control=False,
        opacity=0.7
    )
    tile_layer.add_to(m)

    colour_dict = {
        'Countdown':'green',
        'FreshChoice':'blue',
        'SuperValue':'red',
        'Countdown Metro':'orange',
        'Distribution Centre':'black'
    }

    for i in range(0, len(coords)):
        folium.Circle(list(reversed(coords[i])), radius=250, fill=True, popup= locations.Store[i], color=colour_dict[locations.Type[i]]).add_to(m)

    return m


def create_weekend_map():
    locations = pd.read_csv("../WoolworthsLocations.csv")
    coords = locations[['Long','Lat']]
    coords = coords.to_numpy().tolist()

    m = folium.Map(location = list(reversed(coords[2])), tiles=None, zoom_start=10)

    tile_layer = folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        max_zoom=19,
        name='darkmatter',
        control=False,
        opacity=0.7
    )
    tile_layer.add_to(m)

    colour_dict = {
        'Countdown':'green',
        'FreshChoice':'blue',
        'SuperValue':'red',
        'Countdown Metro':'orange',
        'Distribution Centre':'black'
    }

    for i in range(0, len(coords)):
        if locations.Type[i] == "Countdown":
            folium.Circle(list(reversed(coords[i])), radius=250, fill=True, popup=locations.Store[i], color=colour_dict[locations.Type[i]]).add_to(m)

    return m

def route_between_points(ors_client, stops, coords, time_per_stop=7.5):
    # Stops shouldn't include our distrubution centre
    stops.insert(0, 55)
    stops.insert(len(stops), 55)

    # Calculate the route
    routes = ors_client.directions(coordinates = [coords[stop] for stop in stops], profile = 'driving-hgv', format = 'geojson', validate = False)
    return (routes, 
            routes['features'][0]['properties']['summary']['distance'], 
            routes['features'][0]['properties']['summary']['duration'] + time_per_stop*(len(stops)-2),  # Time traveling +  
            folium.PolyLine(locations = [list(reversed(coord)) for coord in routes['features'][0]['geometry']['coordinates']], tooltip = str(stops), color="Red"))

def solve_all_travel_permutations(ors_client, stops, coords):
    # Stops shouldn't include our distrubution centre
    stops.insert(0, 55)
    stops.insert(len(stops), 55)
    
    return ors_client.distance_matrix(
                locations = coords, 
                sources = stops, 
                destinations = stops, 
                profile = 'driving-hgv', 
                metrics = ['distance', 'duration'], 
                validate = False)

def generate_all_sets():
    partition_data = pd.read_csv('../WoolworthsRegions.csv')

    demand_dict = {
        'Countdown': 8,
        'FreshChoice': 5,
        'SuperValue': 5,
        'Countdown Metro':5
    }

    # Add the demand data directly into the table
    partition_data['Demand'] = partition_data['Type'].map(demand_dict)

    total_combinations = 0
    output = {}

    # For each region that we have defined
    for region in [col for col in partition_data.columns if "Region" in col]:
        print(region)
        # Get just the stores for that region
        stores_in_region = partition_data[partition_data[region] != 0]
        # So generate all combinations between lengths 5-2 and check if they
        # have a demand less than or equal to 26 (max demand).
        combinations = [seq for i in range(5, 1, -1) for seq in itertools.combinations(stores_in_region.index, i) if sum(partition_data.iloc[list(seq)]['Demand']) <= 26]
        # Save to dict
        output[region] = combinations
        total_combinations += len(combinations)
    output['total_combinations'] = total_combinations

    # Write to file 
    with open("combinations.json", 'w') as fp:
        fp.write(json.dumps(output, indent=4))

if __name__ == "__main__":
    keys = []
    with open("keys.json") as fp:
        keys = json.loads(fp.read())

    #locations = pd.read_csv("../WoolworthsLocations.csv")
    #coords = locations[['Long', 'Lat']]
    #coords = coords.to_numpy().tolist()

    #ors_client = ors.Client(key=keys['ORSkey'])

    #m = create_map()
    #(route, distance, duration, line) = route_between_points(ors_client, [1, 2, 3, 4], coords)
    #line.add_to(m)
    #print(distance, duration)
    #travel_perm = solve_all_travel_permutations(ors_client, list(range(0,54)), coords)
    #pd.DataFrame(travel_perm['durations']).to_csv("durations.csv")

    durations = pd.read_csv("../WoolworthsTravelDurations.csv")

    generate_all_sets()

    #m.save("map.html")

    #create_weekend_map().save("weekend_map.html")
