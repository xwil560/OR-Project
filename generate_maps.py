import pandas as pd
import openrouteservice as ors
import folium
import json
# from functools import cache
import seaborn as sns

def create_weekday_map():
    locations = pd.read_csv("data/WoolworthsLocations.csv")
    coords = get_coords_from_locations(locations)

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
    coords = get_coords_from_locations(locations)

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

#def draw_route_between_points(ors_client, stops, coords):
#    # Stops shouldn't include our distrubution centre
#    stops.insert(0, 55)
#    stops.insert(len(stops), 55)
#
#    # Calculate the route
#    routes = ors_client.directions(coordinates = [coords[stop] for stop in stops], profile = 'driving-hgv', format = 'geojson', validate = False)
#    return (routes, 
#            folium.PolyLine(locations = [list(reversed(coord)) for coord in routes['features'][0]['geometry']['coordinates']], tooltip = "", color="Red"))

def get_coords_from_locations(locations_data):
    coords = locations_data[['Long', 'Lat']]
    coords = coords.to_numpy().tolist()
    return coords

def draw_route(ors_client, route_number, route_df, cd_locations_df, route_colour="White"):
    # Convert the stops into id's
    route_data = route_df[route_df.index == route_number]
    stop_coords = cd_locations_df[cd_locations_df.index.isin(list(route_data['path'])[0])][['Long', 'Lat']].to_numpy().tolist()

    # Add distrubution center to stop and end
    coords_dist = cd_locations_df[cd_locations_df['Type'] == "Distribution Centre"][['Long', 'Lat']].to_numpy().tolist()[0]
    stop_coords.insert(0, coords_dist)
    stop_coords.insert(len(stop_coords), coords_dist)

    # Calculate and return the route
    routes = ors_client.directions(coordinates = stop_coords, profile = 'driving-hgv', format = 'geojson', validate = False)
    return (routes,
            folium.PolyLine(locations = [list(reversed(coord)) for coord in routes['features'][0]['geometry']['coordinates']], tooltip = str(route_data['path']), color=route_colour))

def generate_selected_routes(ors_client, selected_routes, locations, route_df_filename="weekday_routes.pkl"):
    routes_df = pd.read_pickle(route_df_filename)
    route_lines = []
    palette = sns.color_palette(None, len(selected_routes)).as_hex()
    for i, route in enumerate(selected_routes):
        print("Drawing route {}".format(str(route)))
        (route, line) = draw_route(ors_client, route, routes_df, locations, route_colour=palette[i])
        route_lines.append(line)
    return route_lines

if __name__ == "__main__":
    # Load the ORS key (we don't stop this on git for security reasons)

    keys = []
    with open("maps/keys.json") as fp:
        keys = json.loads(fp.read())

    # Load the data

    locations = pd.read_csv("data/WoolworthsLocations.csv", index_col='Store')
    ors_client = ors.Client(key=keys['ORSkey'])

    ## Create the weekday map

    m = create_weekday_map()
    
    selected_weekday_routes = [4,425,682,941,1024,2048,3000]
    [line.add_to(m) for line in generate_selected_routes(ors_client, selected_weekday_routes, locations, route_df_filename="data/weekday_routes.pkl")]

    m.save("maps/weekday_map.html")

    ## Create the weekend map

    m = create_weekend_map()

    selected_weekend_routes = [425,682,941,1024]
    [line.add_to(m) for line in generate_selected_routes(ors_client, selected_weekend_routes, locations, route_df_filename="data/weekend_routes.pkl")]

    m.save("maps/weekend_map.html")