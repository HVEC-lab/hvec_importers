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
    raw = raw.melt(
        id_vars = [
            'psmsl_id', 'process',
            'confidence', 'scenario', 'quantile'
            ])
    
    df = raw.loc[raw['quantile'] == 50]
    df = df.rename(
        columns = {
        'variable': 'year',
        'value': 'median'
        })
    df = df.drop(columns = 'quantile')

    tmp = raw.loc[raw['quantile'] == 5]
    tmp = tmp.rename(
        columns = {
        'variable': 'year',
        'value': '90%_low'
        })
    tmp = tmp.drop(columns = 'quantile')
    df = df.merge(
        tmp, on = ['psmsl_id', 'process',
        'confidence', 'scenario', 'year'], 
        how = 'inner')


    tmp = raw.loc[raw['quantile'] == 95]
    tmp = tmp.rename(
        columns = {
        'variable': 'year',
        'value': '90%_high'
        })
    tmp = tmp.drop(columns = 'quantile')
    df = df.merge(
        tmp, on = ['psmsl_id', 'process',
        'confidence', 'scenario', 'year'],
        how = 'inner')

    factor = norm.ppf(0.95)  # Factor for estimating sigma
    df['sigma'] = (df['90%_high'] - df['median']) / factor            
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