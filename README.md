# ENGSCI 263 Operations Research Project: Truck Scheduling and Efficiency for Woolworths NZ
### Group 17

## Table of Contents
- [ENGSCI 263 Operations Research Project: Truck Scheduling and Efficiency for Woolworths NZ](#-engsci-263-operations-research-project-truck-scheduling-and-efficiency-for-woolworths-nz)
- [Table of Contents](#table-of-contents)
- [Description](#description)
- [Instructions](#instructions)
- [Code File Summary](#code-file-summary)
- [Data File Summary](#data-file-summary)

## Description
- This set of programs works to model and analyse the problem of scheduling a delivery scheme for Woolworths NZ stores in Auckland.
- The objective is to determine a suitable delivery truck logistics plan that minimises operational costs.
- The overall process involves:
    - Analysing the demand data to work with a generalised, constant value for demands from each store.
	- Partitioning the store locations in such a way that selections of nodes within each region can be computed as routes.
	- Calculating the costs of each route based on the time taken for each route.
	- Formulating a linear program to select routes that minimise operation costs.
	- Applying the linear program and outputting the associated delivery scheme.

## Instructions
- Clone the project repository "OR-Project" from github.
- Run in prompt: `pip3 install -r requirements/main.txt`
- Run: `python3 main.py`
- A statement will require an ORS key to be input
- Allow the program to run (it provides helpful time indicators for some parts)
- A output for both the weekday and weekend delivery scheme solutions will be printed

## Code File Summary
- `main.py` : Carries out overall process as described above (not including demand data analysis)
	- Takes input for ORS key from user
	- Partitions store locations associated with weekdays
	- Creates route combinations and calculates costs associated with weekdays
	- Turns route combination data into a pickle dataframe file
	- Solves linear program for weekday delivery scheme and outputs selected routes and associated cost.
	- Maps out all routes for weekday deliveries
	- Repeats process for weekend deliveries
	
- `data_analysis.py` :
	- Reads in demand data given
	- Classify demands as weekday (monday-friday) or weekend (saturday) demands
	- Classify small stores (SuperValue, FreshChoice, Countdown Metro) and big stores (Countdown)
	- Create dataframes for the three categories: Small stores on weekdays, Big stores on weekdays, Big stores on weekends
	- Create and plot histograms for all three categories (frequency against demand)
	- Print out average demand of the three categories
	
- `generate_partitions.py` : 
	- function : `generate_partitions`
		- Takes in dataframe with each stop and a binary column for each region that the stop belongs to.
		- Takes in boolean relating to what input dataset is being used (weekday/weekend)
		- Sets demand values as constants for each store type and adds to dataframe
		- Loops through each region and generates all combinations that produce a summed demand less than truck capacity
		- Results are saved as lists of store names
		- Results are written to combinations_[weekday OR weekend].json
	
- `generate_maps.py` : 
	- function : `create_weekday_map`
		- Initialises map plot
		- Gets latitude/longitude values
		- Plots all locations (stores and distribution centre) as circles
	- function : `create_weekend_map`
		- Initialises map plot
		- Gets latitude/longitude values
		- Plots all Countdown locations and distribution centre as circles
	- function : `get_coords_from_locations` (called by `create_weekday_map` and `create_weekend_map`)
		- Takes in location data as dataframe
		- Returns longitude and latitude values as a list
	- function : `draw_route` (called by `generate_selected_routes`)
		- Takes in Openrouteservice client
		- Takes in dataframes for routes and locations
		- Takes in route number to plot
		- Takes in colour to plot route as
		- Manipulates route data to add full route - start and end at distribution centre
		- Calculates and returns route in terms of stops as a line and plots
	- function : `generate_selected_routes`
		- Takes in Openrouteservice client
		- Takes in dataframe for locations of stores
		- Takes in ID of selected routes in a list
		- Takes in dataframe of route combinations filename
		- Reads in route combinations
		- Creates HLS colour pallete to plot route lines in
		- Return list of drawn routes
	- Loads in locations of each stop
	- Creates weekday map
	- Plots selected weekday delivery routes as lines onto map
	- Save map as html
	- Creates weekend map
	- Plots selected weekend delivery routes as lines onto map
	- Save map as html
	
- `calculatecost.py` : 
	- function : `create_LP_values`
		- Takes in filename of route combinations json file
		- Makes dataframe for durations between each pair of locations
		- Makes dataframe for route combinations containing the stores visited (as a binary matrix) and the cost associated with the shortest path of the route
		- Returns route combination dataframe
	- function : `TSP_calculate` (called by `create_LP_values`)
		- Takes in a dataframe of times between locations
		- Takes in a list of the stops in a specific route combination
		- Evaluates the total time taken to traverse all arrangements of the given route
		- Stores the shortest time and associated pathway arrangement
		- Calculates the cost associated with the shortest path
		- Returns shortest path and cost
	- function : `path_time` (called by `TSP_calculate`)
		- Takes in dataframe containing durations between each pair of locations
		- Takes in path list containing the order in which stores are visited
		- Calculates the time taken to traverse a path in a specific order
	- function : `import_json`
		- Takes in filename of json file (for route combinations)
		- Returns read/loaded data from json file
	
- `solve_lp.py` : 
	- function : `route_solver`
		- Takes in filename of pickle dataframe
		- Formulates linear program to minimise operation costs
		- Prints out routes that are selected as a part of the minimum cost solution
		- Prints out the associated cost found as solution

### Data File Summary ###
- `WoolworthsDemands.csv` :
	Data given concerning the number of pallets demanded from each Woolworths store in Auckland for each day.

- `WoolworthsLocations.csv` :
	Data given concerning the GPS latitude/longitude coordinates of each Woolworths store in Auckland.

- `WoolworthsTravelDurations.csv` :
	Data given concerning the GPS latitude/longitude coordinates of each Woolworths store in Auckland.
	Data given concerning the time taken (in seconds) for a delivery truck to travel between any pair of Woolworths store locations.

- `WoolworthsRegions.csv` :
	Data including the manual categorisation of each Woolworths store into 7 regions.

- `combinations_weekday.json` :
	A file containing all the route combinations for the weekday delivery scheme.

- `combinations_weekend.json` :
	A file containing all the route combinations for the weekend delivery scheme.

- `weekday_routes.pkl` :
	Stores the dataframe containing information on all weekday route combinations and their respective costs to be used for the linear program formulation.

- `weekend_routes.pkl` :
	Stores the dataframe containing information on all weekend route combinations and their respective costs to be used for the linear program formulation.
