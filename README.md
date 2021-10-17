# ENGSCI 263 Operations Research Project: Truck Scheduling and Efficiency for Woolworths NZ
### Group 17

## Table of Contents
- [Description](#description)
- [Instructions](#instructions)
- [Code File Summary](#code-file-summary)
- [Data File Summary](#data-file-summary)
- [Plots & Diagrams](#plots-&-diagrams)


## Description
- This set of programs works to model and analyse the problem of scheduling a delivery scheme for Woolworths NZ stores in Auckland.
- The objective is to determine a suitable delivery truck logistics plan that minimises operational costs.
- The overall process involves:
    - Analysing the demand data to work with a generalised, constant value for demands from each store.
	- Partitioning the store locations in such a way that selections of nodes within each region can be computed as routes.
	- Calculating the costs of each route based on the time taken for each route.
	- Formulating a linear program to select routes that minimise operation costs.
	- Applying the linear program and outputting the optimal delivery scheme.
	- Mapping out the optimal delivery scheme
	- Performs a simulation of 1000 runs
	- Plots a histogram of the results of the simulation in terms of total costs
	- Identifies stores that could are unusually close together
	- Plots a new histogram of the total costs based on a simulation where a store is closed down (and the savings costs are put into extra delivery trucks)


## Instructions
- Clone the project repository "OR-Project" from github.
- Run in prompt: `pip3 install -r requirements/main.txt`
- Run: `python3 main.py`
- A statement will require an ORS key to be input
- Allow the program to run (provides helpful time indicators for some parts)
- A output for both the weekday and weekend delivery scheme solutions will be printed


## Code File Summary
- `main.py` : Carries out overall process as described above (not including demand data analysis)
	- Takes input for ORS key from user
	- Partitions store locations associated with weekdays
	- Creates route combinations and calculates costs associated with weekdays
	- Turns route combination data into a pickle dataframe file
	- Solves linear program for weekday delivery scheme and outputs selected routes and associated cost.
	- Maps out all routes for weekday deliveries
	- Performs simulation of 1000 runs for weekday deliveries (with varied demands and time taken due to traffic)
	- Plots histogram showing costs of each run and the associated 95% confidence interval
	- Repeats process for weekend deliveries
	- Lists the 10 closest stores to each other and chooses one to remove from all delivery schemes
	- Recalculates new optimal cost of the delivery schemes with the removed store, accounting for new 
	- Runs simulation for both weekend and weekday deliveries with the removed store
	- Plots histogram showing new costs of each run and the associated 95% confidence interval 
	
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
		- Takes in name of selected routes in a list
		- Takes in dataframe of route combinations filename
		- Reads in route combinations
		- Creates HSS colour pallete to plot route lines
		- Draws routes
		- Return list of drawn routes
	
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
	- function : `route_modifier`
	- function : `extra_trucks_solver`

- `simulation.py` :
	- function : `change_demand`
	- function : `calc_demand` (called by `change_demand`)
	- function : `random_times`
	- function : `simulation`
	- function : `bootstrap_demands`
	- function : `summarise_stats`

- `close_stores.py` :
	- function : `close_stores`

- `Lab6.py` :
	- function : `generateTaskTime`
	- function : `alphaBetaFromAmB`


## Data File Summary 
#### Data 
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

### differentDemands
- `weekday_routes[LOW/_MEDIUM/HIGH].pkl` :
	Stores the dataframe containing information on all weekday route combinations for a specific demand category and their respective costs to be used for the linear program formulation.

- `weekend_routes[LOW/HIGH].pkl` :
	Stores the dataframe containing information on all weekend route combinations for a specific demand category and their respective costs to be used for the linear program formulation.

### cost_simulations
- `Weekday[Low/_Medium/High].pkl` :
	Stores the array of costs that are returned as a result of running a simulation for a set of optimal weekday routes for a specific demand category.
- `Weekend[Low/High].pkl` :
	Stores the array of costs that are returned as a result of running a simulation for a set of optimal weekend routes for a specific demand category.
- `NW_removed_wkdy.pkl` :
	Stores the array of costs that are returned as a result of running a simulation for a set of optimal weekday routes for a specific demand category with Countdown NorthWest removed as a store to visit.
- `NW_removed_wknd.pkl` :
	Stores the array of costs that are returned as a result of running a simulation for a set of optimal weekend routes for a specific demand category with Countdown NorthWest removed as a store to visit.


## Plots & Diagrams
### maps
- `weekday_routes[LOW/_MEDIUM/HIGH].html` :
	Map with weekday route scheme drawn on for a specific demand category.
- `weekend_routes[LOW/HIGH].html` :
	Map with weekend route scheme drawn on for a specific demand category.

### histograms
- `Weekday[Low/_Medium/High].png` :
	Histogram plot of costs generated from running simulations of weekday delivery scheme for a specific demand category.
- `Weekend[Low/High].png` :
	Histogram plot of costs generated from running simulations of weekend delivery scheme for a specific demand category.
- `NW_removed_wkdy.png` :
	Histogram plot of costs generated from running simulations of weekday delivery scheme for a specific demand category with Countdown NorthWest removed as a store to visit.
- `NW_removed_wknd.png` :
	Histogram plot of costs generated from running simulations of weekend delivery scheme for a specific demand category with Countdown NorthWest removed as a store to visit.