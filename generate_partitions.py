import json
import itertools
import pandas as pd
from tqdm import tqdm

def generate_paritions(partition_data, weekend=False):
    '''
    Generates all possible partitions of a regioned dataset and saves as a file.

    inputs:
    ------
    paritions_data : pandas dataframe
        A dataframe with each stop and a binary column for each region that the stops belong too.
    weekend : boolean
        Boolean set depending on what the input dataset time period is.

    outputs:
    -------
    paritions : file
        A json dictionary of all possible partitions written to disk.
    '''
    if weekend:
        demand_dict = {
            'Countdown': 4
        }
    else:
        demand_dict = {
            'Countdown': 8,
            'FreshChoice': 5,
            'SuperValue': 5,
            'Countdown Metro':5
        }

    # Add the demand data directly into the table
    partition_data['Demand'] = partition_data['Type'].map(demand_dict)

    total_combinations = 0
    output = {"combinations":[]}

    # For each region that we have defined
    for region in [col for col in partition_data.columns if "Region" in col]:
        
        # Get just the stores for that region
        stores_in_region = partition_data[partition_data[region] != 0]
        
        # Generate all combinations between lengths 5-2 and check if they
        # have a demand less than or equal to 26 (max demand).
        combinations = [list(seq) for i in tqdm(range(6, 0, -1)) for seq in list(itertools.combinations(stores_in_region.index, i)) if sum(partition_data.iloc[list(seq)]['Demand']) <= 26]

        for route in range(len(combinations)):
            for stop in range(len(combinations[route])):
                combinations[route][stop] = partition_data.iloc[combinations[route][stop]]['Store']

        # Save to dict
        output['combinations'] += combinations
        total_combinations += len(combinations)
    
    output['total_combinations'] = total_combinations

    # Write to file 
    if not weekend:
        with open('data/combinations_weekday.json', 'w') as fp:
            fp.write(json.dumps(output, indent=4))
    else:
        with open('data/combinations_weekend.json', 'w') as fp:
            fp.write(json.dumps(output, indent=4))


if __name__ == "__main__":
    partition_data = pd.read_csv('data/WoolworthsRegions.csv')

    generate_paritions(partition_data, weekend=False) 

    weekend_data = partition_data[partition_data['Type'] == 'Countdown']
    
    generate_paritions(weekend_data, weekend=True)