"""
Import of data from the Permanent Service for
Mean Sea Level (PSMSL).

Sub-package of hvec_importers.

Developed by HVEC-lab, 2022
"""


# Public packages
import warnings
import pandas as pd
import requests


url = {
    'rlr': 'https://psmsl.org/data/obtaining/index.php',
    'met': 'https://psmsl.org/data/obtaining/metric.php',
    'annual_rlr': 'https://psmsl.org/data/obtaining/rlr.annual.data/',
    'monthly_rlr': 'https://psmsl.org/data/obtaining/rlr.monthly.data/',
    'monthly_met': 'https://psmsl.org/data/obtaining/met.monthly.data/'
}


def station_list(include_metric = False):
    """
    Obtain the list of stations and station ID from
    the PSMSL website.

    Points of attention
    -------------------
    -   The "rlr" stations have data that is corrected for
        reference level changes. "metric" stations do not.
    -   PSMSL suggests not to use metric stations. However,
        this function allows for metric stations to be imported
    -   Not importing "metric" is default
    -   Station type is added as a column to the output if metric
        is included
    -   We use pandas to read tables from the website. Output is a
        list of dataframes. We know that there is only a single
        dataframe present on each site and select it
    """
    stations = pd.read_html(
        url['rlr'])[0]
    
    stations['type'] = 'rlr'

    if include_metric:
        tmp = pd.read_html(
            url['met']
        )[0]

        tmp['type'] = 'met'

        stations = pd.concat([stations, tmp])

    return stations


def id_from_name(name, include_metric = False):
    """
    Select station ID from a name.
    """

    name = name.upper()  # Set input to upper case, ensuring
                         # case-insensitive selection

    stations = station_list(
        include_metric
    )

    stations.columns = stations.columns.str.replace(' ', '')
    stations['StationName'] = stations['StationName'].str.upper()

    selected = stations.query(
        'StationName.str.contains(@name)', engine='python'
    )

    if len(selected) == 0:
        warnings.warn('No data found for ' + name)
        return
    elif len(selected) > 1:
        warnings.warn('Multiple locations selected for ', name, '. Specify longer name')
        return
    else:
        id = selected['ID'].squeeze()
        return id


def data_single_id(id, freq = 'annual', type = 'rlr'):
    """
    Get data of a PSMSL station selected by station_ID
    """

    # Errors and warnings
    assert (freq in ['annual', 'monthly']), 'freq should be annual or monthly'
    assert (type in ['rlr', 'met']), 'type should be rlr or met'
    assert isinstance(id, int), 'id should be integer'

    if type == 'met':
        warnings.warn('Metric data is not research quality!')

    if (freq == 'annual') and (type == 'met'):
        raise ValueError('Only monthly data for metric')

    # Get station name
    try:
        stations = station_list(include_metric = True)
        name = stations.loc[stations['ID'] == id, "Station Name"].squeeze()
    except:
        warnings.warn('Station with id ', id, ' not found')
        return

    # Assemble url
    base = url[freq + '_' + type]
    data_url = str(id) + '.' + type + 'data'

    # PSMSL contains pages without data
    # Checking for it and continue dependent on condition
    res = requests.get(base + data_url)

    if len(res.text) > 0:
        df = pd.read_csv(
            base + data_url,
            sep = ';',
            header = None,
            usecols = [0, 1],
            na_values = -99999
        )
        df.columns = ['time', 'level']
        df['id'] = id
        df['name'] = name
        df['type'] = type
    else:
        df = pd.DataFrame()

    return df


def data_single_name(
    name,
    include_metric = False,
    freq = 'annual',
    type = 'rlr'):
    """
    Get data of a PSMSL station selected by name
    """
    try:
        id = id_from_name(name, include_metric).item()
        df = data_single_id(id, freq, type)
    except:
        raise NameError('No data found for ' + name)
    return df