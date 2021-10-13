import pandas as pd
import openrouteservice as ors
import folium
import json
# from functools import cache
import seaborn as sns

def create_weekday_map():
    '''
    Creates a map object with our preconfigured map type with the weekday store locations. 
    
    inputs:
    ------
    None

    outputs:
    -------
    m : folium object
        The folium map object that can be displayed/changed.
    '''
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
    '''
    Creates a map object with our preconfigured map type with the weekend store locations. 
    
    inputs:
    ------
    None

    outputs:
    -------
    m : folium object
        The folium map object that can be displayed/changed.
    '''
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
        if locations.Type[i] == "Countdown" or locations.Type[i] == "Distribution Centre":
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
    '''
    Generates a subset dataset of coordinates which can be indexed using the store numbers.

    inputs:
    ------
    locations_data : pandas dataframe
        A dataframe containing indexed "Long" and "Lat" columns (in axis 1).

    outputs:
    -------
    coords : list
        A two dimensional list of the "Long" and "Lat" columns.
    '''
    coords = locations_data[['Long', 'Lat']]
    coords = coords.to_numpy().tolist()
    return coords

def draw_route(ors_client, route_path, cd_locations_df, route_colour="White"):
    '''
    Returns a folium line object that corresponds to the route specified.

    inputs:
    ------
    ors_client : openrouteservice object
        The client object from the ORS python package.
    route_number : int
        The route number (index).
    route_df : pandas dataframe
        The routes dataframe containing the TSP calculated route path.
    cd_locations_df : pandas dataframe
        The dataframe of the locations of stores in Auckland.
    route_colour : string
        The colour of the folium line.

    outputs:
    -------
    tuple :
        routes : openrouteservice object
            Contains the route details.
        line : folium line object
            Contains the line object that can be written to the map.
    '''
    # Convert the stops into id's
    #route_data = route_df[route_df.index == route_number]
    stop_coords = cd_locations_df[cd_locations_df.index.isin(list(route_path))][['Long', 'Lat']].to_numpy().tolist()

    # Add distrubution center to stop and end
    coords_dist = cd_locations_df[cd_locations_df['Type'] == "Distribution Centre"][['Long', 'Lat']].to_numpy().tolist()[0]
    stop_coords.insert(0, coords_dist)
    stop_coords.insert(len(stop_coords), coords_dist)

    # Calculate and return the route
    routes = ors_client.directions(coordinates = stop_coords, profile = 'driving-hgv', format = 'geojson', validate = False)
    return (routes,
            folium.PolyLine(locations = [list(reversed(coord)) for coord in routes['features'][0]['geometry']['coordinates']], tooltip = str(route_path), color=route_colour, opacity=0.5))

def generate_selected_routes(ors_client, selected_routes, locations):#, route_df_filename="weekday_routes.pkl"):
    '''
    Returns a list of folium line objects that correspond to the routes specified.

    inputs:
    ------
    ors_client : openrouteservice object
        The client object from the ORS python package.
    selected_routes : list[list[str]]
        The selected route pathes (which must be present in the route_df)
    locations : pandas dataframe
        The dataframe of the locations of stores in Auckland.
    route_df_filename : string
        The filename of the route dataframe (stored as a pickle).

    outputs:
    -------
    route_lines : list[folium object]
        A python list of all the folium line object routes to be graphed to a map.
    '''
    #routes_df = pd.read_pickle(route_df_filename)
    route_lines = []
    palette = sns.color_palette("hls", len(selected_routes)).as_hex()
    for i, route_path in enumerate(selected_routes):
        print("Drawing route {}".format(str(route_path)))
        (route, line) = draw_route(ors_client, route_path, locations, route_colour=palette[i])
        route_lines.append(line)
    return route_lines

def read_keys():
    '''
    Reads the secure key set (keys that we don't want on git version control).

    inputs:
    ------
    None

    outputs:
    -------
    keys : dict
        A json dictionary of the keys file.
    '''
    with open("maps/keys.json") as fp:
        return json.loads(fp.read())

if __name__ == "__main__":
    # Load the ORS key (we don't stop this on git for security reasons)
    keys = read_keys()

    # Load the data
    locations = pd.read_csv("data/WoolworthsLocations.csv", index_col='Store')
    ors_client = ors.Client(key=keys['ORSkey'])

    ## Create the weekday map

    m = create_weekday_map()
    
    #selected_weekday_routes = [1438,1824,1939,2047,2085,2270,2330,2502,2533,2562,2636,2969,3217,332,831,903,1018,1167,1369,503,613] 
    import solve_lp as slp
    import glob
    import os

    files = glob.glob("differentDemands" + os.sep + "*.pkl")

    for demand_file in files:
        demand_file = demand_file.split(os.sep)[-1]
        m = create_weekday_map() if "weekday" in demand_file else create_weekend_map()
        selected_routes, x, y = slp.routes_solver(demand_file)
        [line.add_to(m) for line in generate_selected_routes(ors_client, selected_routes, locations)]

        m.save(f"maps/{demand_file.split('.')[0]}_map.html")

    ## Create the weekend map

    #m = create_weekend_map()

    #selected_weekend_routes = [2333, 3227, 4054, 4763, 4863, 5136, 5387, 5542, 791, 1595, 549] 
    #[line.add_to(m) for line in generate_selected_routes(ors_client, selected_weekend_routes, locations, route_df_filename="data/weekend_routes.pkl")]

    #m.save("maps/weekend_map.html")