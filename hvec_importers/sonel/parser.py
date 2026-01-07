"""
Library for rapid processing of hand-imported Sonel files.

HVEC-lab, 2026; all rights reserved
"""


import pandas as pd


def find_row(data, field: str) -> int:
    """
    Finds the row number of a specific field in the Sonel file.

    Args:
        data (list): The data to search through.
        field (str): The field to search for.
    
    Returns:
        int: The row number of the field.
    """
    i = 0
    line = data[i]

    while field not in line:
        i += 1
        line = data[i]
    return line, i


def parse_sonel_file(filepath: str) -> pd.DataFrame:
    """
    Imports a Sonel file and returns a DataFrame with the data.

    Args:
        filepath (str): Path to the Sonel file.
    
    Returns:
        pd.DataFrame: DataFrame containing the Sonel data.
    """

    # Read input file
    with open(filepath, 'r') as file:
        data = file.readlines()

    # Get metadata
    line, _ = find_row(data, '# Site')
    site = line.split()[3]

    line, _ = find_row(data, 'Latitude')
    lat = float(line.split()[3])

    line, _ = find_row(data, 'Longitude')
    lon = float(line.split()[3])

    # Get data
    _, start_row = find_row(data, 'Year')
    df = pd.read_fwf(
          filepath
        , skiprows=start_row
    )

    # Add metadata to DataFrame
    df['Site'] = site
    df['Lat'] = lat
    df['Lon'] = lon
    df['EPSG'] = 4326

    # Clean column names
    df.columns = df.columns.str.strip('# ')
    df.rename(columns = {'Year': 'Time'}, inplace=True)
    return df
  