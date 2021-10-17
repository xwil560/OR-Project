# ENGSCI 263 Operations Research Project: Truck Scheduling and Efficiency for Woolworths NZ
### Group 17

## Table of Contents
- [Description](#description)
- [Instructions](#instructions)
- [Code File Summary](#code-file-summary)
- [Data File Summary](#data-file-summary)
- [Plots & Diagrams](#plots--diagrams)


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
	- Recalculates new optimal cost of the delivery schemes with a removed store (Countdown NorthWest)
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
		- Results are written to `combinations_[weekday/weekend].json`
	
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
		- Makes dataframe for route combinations containing the stores visited by each route (as a binary matrix)
		- Returns route combination dataframe
	- function : `TSP_calculate` (called by `create_LP_values`)
		- Takes in a dataframe of times between locations
		- Takes in a list of the stops in a specific route combination
		- Evaluates the travel time for each arrangements of the given route
		- Stores the shortest time and associated pathway arrangement
		- Returns shortest path and the travel time associated with it
	- function : `path_time` (called by `TSP_calculate`)
		- Takes in dataframe containing durations between each pair of locations
		- Takes in path list containing the order in which stores are visited
		- Calculates the time taken to traverse a path in a specific order
	- function : `route_cost` 
		- Takes in dictionary representing the relevant demand scheme
		- Takes in Pandas dataframe containing stores visited by each route
		- Calculates cost of route
		- Adds cost and number of pallets columns to Pandas dataframe
		- Returns updated dataframe
	- function : `route_demand` (called by `route_cost`)
		- Takes in dictionary representing the relevant demand scheme
		- Takes in a list of the stores that are visited in the given route
		- Calculates the total number of pallets required in the route
		- Returns number of pallets for whole route
	- function : `Cost` (called by `route_cost`)
		- Takes in travel time (total time for a route minus the time taken to unload pallets)
		- Takes in number of pallets being delivered
		- Calculates the total time for the route to be processed
		- Calculates the cost for sending a Woolworths truck to complete the associated route
		- Returns cost value 
	- function : `import_json`
		- Takes in filename of json file (for route combinations)
		- Returns read/loaded data from json file
	
- `solve_lp.py` : 
	- function : `route_solver`
		- Takes in filename of pickle dataframe
		- Formulates linear program to minimise operation costs
		- Returns list of optimal routes
		- Returns list of the types of trucks used for each route (and associated time period)
		- Returns optimal minimised cost value
	- function : `route_modifier` (called by `simulation from simulation.py`)
		- Takes in filename of pickle dataframe
		- Takes in list of unsatisfied nodes due to a change in demand exceeding truck capacity
		- Takes in number of Woolworths trucks unused in each time period
		- Removes any stores that are not unsatisfied from dataframe
		- Formulates linear program to minimise operation costs
		- Returns list of routes covered by Woolworths trucks
		- Returns list of routes covered by daily freight trucks
	- function : `extra_trucks_solver`
		- Takes in filename of pickle dataframe
		- Takes in name of store to be removed
		- Takes in boolean to determine whether LP is to be solved for a weekend solution or not
		- Optionally takes in the number of extra trucks bought (if already determined)
		- Removes store to be removed from dataframe
		- Formulates linear program to minimise operation costs
		- Introduces constraint to account for extra trucks and add extra truck costs to objective function
		- Returns list of optimal routes
		- Returns number of extra trucks required if not already found

- `simulation.py` :
	- function : `change_demand` (called by `simulation`)
		- Takes in dictionary representing the relevant demand scheme
		- Takes in routes assigned to time period 1 and 2 as lists
		- Seperates routes that cannot be fulfilled due to a changed demand
		- Return routes assigned to time period 1 with unsatisfied stores removed
		- Return routes assigned to time period 2 with unsatisfied stores removed
		- Return list of unsatisfied stores
		- Return number of unused Woolworths trucks in time period 1
		- Return number of unused Woolworths trucks in time period 2
	- function : `calc_demand` (called by `change_demand`)
		- Takes in dictionary representing the relevant demand scheme
		- Takes in list of stores to visit in route
		- Return the total number of pallets for that route
	- function : `random_times` (called by `simulation`)
		- Takes in Pandas dataframe of time taken to travel between stops
		- Takes in number of runs of simulation
		- Based on total travel time for route, generate new time based on traffic adjustment with PERT-Beta distribution (Most optimistic taking 75% of the travel time, most pesimistic taking 250% more time)
		- Return list of dataframes of time taken between between all stops (number of dataframes is the number of runs)
	- function : `simulation`
		- Takes in lists of routes in time periods 1 and 2
		- Takes in boolean to determine whether simulation is for a weekend solution or not
		- Takes in number of runs of simulation
		- Takes in filename of pickle dataframe
		- Loops a set number of times
		- Each run randomises the number of pallets at each store and the travel time due to traffic
		- Each run has a resulting cost
		- Costs are returned in an array
	- function : `bootstrap_demands` (called by `simulation`)
		- Takes in Pandas dataframes of store locations and store demands
		- Takes in boolean to determine whether simulation is for a weekend solution or not
		- Takes in number of runs of simulations
		- Samples demand values from initial distribution of demands based on store type and week stage
		- Returns list of dictionaries representing demand scheme (randomised demands)
	- function : `summarise_stats` 
		- Takes in filename of pickle data for costs of each run of simulation
		- Calculates mean, median, standard deviation, 2.5-th and 97.5-th percentile values for cost
		- Plots histogram of cost values depicting 95% confidence interval
		- Saves histogram plot

- `close_stores.py` :
	- function : `close_stores`
		- Reads in the given data of the distances between stores
		- Returns a dataframe of 10 stores that are closest to other stores 

- `Lab6.py` :
	- function : `generateTaskTime` 
		- Takes in most optimistic duration
		- Takes in most pessimistic duration
		- Takes in most likely duration
		- Generates a task time based on a PERT-Beta distribution
	- function : `alphaBetaFromAmB` (called by `generateTaskTime`)
		- Takes in most optimistic duration
		- Takes in most pessimistic duration
		- Takes in most likely duration
		- Calculates the alpha and beta values to be used for a PERT-Beta distribution


## Data File Summary 
#### data 
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

#### differentDemands
- `weekday_routes[LOW/_MEDIUM/HIGH].pkl` :
	Stores the dataframe containing information on all weekday route combinations for a specific demand category and their respective costs to be used for the linear program formulation.

- `weekend_routes[LOW/HIGH].pkl` :
	Stores the dataframe containing information on all weekend route combinations for a specific demand category and their respective costs to be used for the linear program formulation.

#### cost_simulations
- `Weekday[Low/_Medium/High].pkl` :
	Stores the array of costs that are returned as a result of running a simulation for a set of optimal weekday routes for a specific demand category.
- `Weekend[Low/High].pkl` :
	Stores the array of costs that are returned as a result of running a simulation for a set of optimal weekend routes for a specific demand category.
- `NW_removed_wkdy.pkl` :
	Stores the array of costs that are returned as a result of running a simulation for a set of optimal weekday routes for a specific demand category with Countdown NorthWest removed as a store to visit.
- `NW_removed_wknd.pkl` :
	Stores the array of costs that are returned as a result of running a simulation for a set of optimal weekend routes for a specific demand category with Countdown NorthWest removed as a store to visit.


## Plots & Diagrams
#### maps
- `weekday_routes[LOW/_MEDIUM/HIGH].html` :
	Map with weekday route scheme drawn on for a specific demand category.
- `weekend_routes[LOW/HIGH].html` :
	Map with weekend route scheme drawn on for a specific demand category.

#### histograms
- `Weekday[Low/_Medium/High].png` :
	Histogram plot of costs generated from running simulations of weekday delivery scheme for a specific demand category.
- `Weekend[Low/High].png` :
	Histogram plot of costs generated from running simulations of weekend delivery scheme for a specific demand category.
- `NW_removed_wkdy.png` :
	Histogram plot of costs generated from running simulations of weekday delivery scheme for a specific demand category with Countdown NorthWest removed as a store to visit.
- `NW_removed_wknd.png` :
	Histogram plot of costs generated from running simulations of weekend delivery scheme for a specific demand category with Countdown NorthWest removed as a store to visit.