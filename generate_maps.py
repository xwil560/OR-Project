from math import comb
import numpy as np
import pandas as pd
import openrouteservice as ors
import folium
import json

from pandas.core.accessor import register_index_accessor

def create_map():
    locations = pd.read_csv("data/WoolworthsLocations.csv")
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
    locations = pd.read_csv("data/WoolworthsLocations.csv")
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

def draw_route_between_points(ors_client, stops, coords, time_per_stop=7.5):
    # Stops shouldn't include our distrubution centre
    stops.insert(0, 55)
    stops.insert(len(stops), 55)

    # Calculate the route
    routes = ors_client.directions(coordinates = [coords[stop] for stop in stops], profile = 'driving-hgv', format = 'geojson', validate = False)
    return (routes, 
            folium.PolyLine(locations = [list(reversed(coord)) for coord in routes['features'][0]['geometry']['coordinates']], tooltip = str(stops), color="Red"))

if __name__ == "__main__":
    keys = []
    with open("maps/keys.json") as fp:
        keys = json.loads(fp.read())

    locations = pd.read_csv("data/WoolworthsLocations.csv")
    coords = locations[['Long', 'Lat']]
    coords = coords.to_numpy().tolist()

    routes = []
    with open("data/combinations_weekday.json", "r") as fp:
        routes = json.loads(fp.read())

    ors_client = ors.Client(key=keys['ORSkey'])

    m = create_map()
    for route in routes['combinations']:
        (route, line) = draw_route_between_points(ors_client, locations[locations['Store'].isin(route)].index, coords)
        line.add_to(m)

    m.save("map.html")

    create_weekend_map().save("weekend_map.html")
