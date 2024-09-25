"""
Package hvec_climate, subpackage parsers
Prepared by HVEC lab, 2022
"""

# Public packages
import pandas as pd
from scipy.stats import norm


def ipcc_single_sheet(raw):
    """
    Takes a data table downloaded from the IPCC
    sea level projection tool and puts it into a column 
    oriented format with year, median and 90%
    bounds in columns.

    Parameters
    -------
    raw, dataframe. IPCC unformatted dataframe

    Returns
    -------
    sealevel rise in m with respect tot 1975 - 2005 (average 1990)
 
    References
    --------
    https://sealevel.nasa.gov/ipcc-ar6-sea-level-projection-tool
    """
    df = raw.melt(
          id_vars = ['psmsl_id', 'process', 'confidence', 'scenario', 'quantile']
        , var_name = 'year')

    # Modify column names for clarity  
    df['quantile'] = 'q_' + df['quantile'].astype(str) + '%'

    # Rates given in mm/yr. Set to SI units
    df.loc[df['process'] == 'totalrates', 'value'] = df.loc[df['process'] == 'totalrates', 'value'].div(1000)

    # Set to format with quantiles in columns

    # Rename column that ultimately lands as index name to avoid confusing name
    df.rename(columns = {'quantile': 'index'}, inplace = True)
    df = df.pivot(
          columns = 'index'
        , index = ['psmsl_id', 'process', 'confidence', 'scenario', 'year']
        , values = 'value')
    df.reset_index(inplace = True)
   
    return df


def ipcc_workbook(book):
    """
    Parse the 8 data sheets from IPCC into a dataframe
    in long format with subprocesses indicated in the
    correct column
    """

    # ReadMe contains no data
    del book['ReadMe']

    # Run over all sheets in the book
    df = pd.DataFrame()
    for ky in book.keys():
        tmp = ipcc_single_sheet(book[ky])
        df = pd.concat([df, tmp])

    return df
