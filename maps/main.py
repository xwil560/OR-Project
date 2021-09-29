import numpy as np
import pandas as pd
import folium
import json

keys = []
with open("keys.json") as fp:
    keys = json.loads(fp.read())

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
    folium.Circle(list(reversed(coords[i])), radius=100, fill=True, popup= locations.Store[i], color=colour_dict[locations.Type[i]]).add_to(m)

m.save("index.html")