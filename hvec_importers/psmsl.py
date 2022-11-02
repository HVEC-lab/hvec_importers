"""
Import of data from the Permanent Service for Mean Sea Level (PSMSL).

Sub-package of hvec_importers.

Developed by HVEC-lab, 2022
"""


# Public packages
import logging
import io
import pandas as pd
import time

# Other sub-packages
from hvec_importers import helpers


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
    stations = pd.read_html(url['rlr'])[0]
    stations['type'] = 'rlr'

    if include_metric:
        tmp = pd.read_html(url['met'])[0]
        tmp['type'] = 'met'
        stations = pd.concat([stations, tmp])

    stations.rename(columns = {'Station Name': 'name'}, inplace = True)
    stations.set_index(keys = 'ID', inplace = True)

    return stations


def id_from_name(name, include_metric = False):
    """
    Select station ID from a name.
    """
    id = helpers.id_from_name(station_list, name, include_metric = include_metric)
    return id


def data_single_id(id, session, freq = 'annual', tp = 'rlr'):
    """
    Get data of a PSMSL station selected by station_ID
    """

    # Errors and warnings
    assert (freq in ['annual', 'monthly']), 'freq should be annual or monthly'
    assert (tp in ['rlr', 'met']), 'type should be rlr or met'
    assert isinstance(id, int), 'id should be integer'

    if type == 'met':
        logging.warning('Metric data is not research quality!')

    if (freq == 'annual') and (tp == 'met'):
        logging.warning('Only monthly data for metric. Empty dataframe returned')
        return pd.DataFrame()

    # Assemble url
    base = url[freq + '_' + tp]
    data_url = str(id) + '.' + tp + 'data'

    # PSMSL contains pages without data
    # Checking for it and continue dependent on condition
    res = session.get(base + data_url, timeout = 60)
    time.sleep(2)  # Prevent overloading the website

    if len(res.text) > 0:
        df = pd.read_csv(
            io.BytesIO(res.content),
            sep = ';',
            header = None,
            usecols = [0, 1],
            na_values = -99999
        )
        df.columns = ['time', 'level']
        df['id'] = id
        
        df['freq'] = freq
        df['type'] = tp
    else:
        logging.warning('No data available on site. Empty dataframe returned.')
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