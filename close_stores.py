import pandas as pd
import numpy as np

def close_stores() -> pd.DataFrame:
    '''
    calculates the 10 stores neares to other stores

    outputs:
    -------
        df : pandas Dataframe
            Dataframe containing the 10 stores closest to other stores
    '''
    distances = pd.read_csv('data/WoolworthsDistances.csv', index_col="Unnamed: 0")
    df = pd.DataFrame({"min_dist" : 0}, index = distances.columns)
    for s in distances.columns:
        df.loc[s] = np.min(distances.loc[distances[s] != 0, s])
    return df.nsmallest(10,'min_dist')

if __name__ == "__main__":
    print(close_stores())