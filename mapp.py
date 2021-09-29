import numpy as np
import pandas as pd
import folium 

locations = pd.read_csv("WoolworthsLocations.csv")

coords = locations[['Long','Lat']]
coords = coords.to_numpy().tolist()

m = folium.Map(location = list(reversed(coords[2])), zoom_start=10)

folium.Circle(list(reversed(coords[0])), popup = locations.Store[0], icon = folium.Icon(color ='green')).add_to(m)

# for i in range(0,len(coords)):
#     if locations.Type[i] == "Countdown":
#         iconCol="green"
#     elif locations.Type[i] == "FreshChoice":
#         iconCol="blue"
#     elif locations.Type[i] == "SuperValue":
#         iconCol="red"        
#     elif locations.Type[i] == "Countdown Metro":
#         iconCol="orange"
#     elif locations.Type[i] == "Distribution Centre":
#         iconCol="black"                
#     folium.Circle(list(reversed(coords[i])), popup = locations.Store[i], icon = folium.Icon(color = iconCol)).add_to(m)

colour_dict = {
    'Countdown':'green',
    'FreshChoice':'blue',
    'SuperValue':'red',
    'Countdown Metro':'orange',
    'Distribution Centre':'black'
    }

for i in range(1, len(coords)):
    folium.Circle(list(reversed(coords[i])), radius=100, popup= locations.Store[i], color=colour_dict[locations.Type[i]]).add_to(m)

m.save('test.html')