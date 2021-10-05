import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import re

demand = pd.read_csv("data/WoolworthsDemands.csv")
locations = pd.read_csv("data/WoolworthsLocations.csv")
travelDur = pd.read_csv("data/WoolworthsTravelDurations.csv")

demand_long = demand.melt(id_vars = 'Store',var_name='Date', value_name='Demand' ) # pivot longer on dates

demand_long.Date = pd.to_datetime(demand_long.Date) # convert dates to datetime format

demand_long['Weekday'] = demand_long.Date.dt.dayofweek # add a day of the week column to the df

# day class is Weekend if the day is in the weekend, weekday otherwise
demand_long = demand_long.assign(DayClass=["Weekend" if day in (5,6) else "Weekday" for day in demand_long.Weekday]) 

demand_long["StoreClass"] = [
        ("Big","Small")[re.search("(FreshChoice|SuperValue|Countdown Metro).*", store) is not None] for store in demand_long.Store
    ] # Class the Freshchoice, countdown metro and Super Value stores as "small" and all other countdowns as "big" using regular expressions


# demand_long[[re.search("(FreshChoice|SuperValue|Countdown Metro).*", store) is not None for store in demand_long.Store]]

small_df = demand_long[demand_long.StoreClass=="Small"][demand_long.DayClass=="Weekday"] # df of all 'small stores' on days they are open
big_wkday_df = demand_long[demand_long.StoreClass=="Big"][demand_long.DayClass=="Weekday"] # df of all 'big stores' on weekdays
big_wkend_df = demand_long[demand_long.StoreClass=="Big"][demand_long.Weekday==5] # df of all 'big stores' on saturdays


f, ax = plt.subplots(3,1, sharex=True)
# small_df.Demand.hist(bins=np.arange(0.5,9.5))
print(small_df.Demand.mean())
h1 = sns.histplot(ax = ax[0], x=small_df.Demand, bins=np.arange(1.5,10.5), palette="Blues")
ax[0].set_title("Small Stores")

# big_wkday_df.Demand.hist(bins=np.arange(0.5,15.5))
print(big_wkday_df.Demand.mean())
h2 = sns.histplot(ax = ax[1], x=big_wkday_df.Demand, bins=np.arange(1.5,15.5),color="Green")
ax[1].set_title("Big Stores, Weekdays")

# big_wkend_df.Demand.hist(bins=np.arange(1.5,6.5))
print(big_wkend_df.Demand.mean())
h3 = sns.histplot(ax = ax[2], x=big_wkend_df.Demand, bins=np.arange(1.5,6.5),color="Purple")
ax[2].set_title("Big Stores, Weekends")
plt.legend()
plt.show()

