import pandas as pd
import numpy as np

demand = pd.read_csv("WoolworthsDemands.csv")
locations = pd.read_csv("WoolworthsLocations.csv")
travelDur = pd.read_csv("WoolworthsTravelDurations.csv")

demand_long = demand.melt(id_vars = 'Store',var_name='Date', value_name='Demand' )

demand_long.Date = pd.to_datetime(demand_long.Date)

ts = pd.Series(demand_long[demand_long.Store=="FreshChoice Otahuhu"].Demand.values, index = demand_long[demand_long.Store=="FreshChoice Otahuhu"].Date)

ts.plot()