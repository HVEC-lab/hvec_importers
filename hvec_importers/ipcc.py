"""
Import of data from NASA AR6 sealevel projection tool.

Sub-package of hvec_importers.

Only PSMSL points covered.
Several tools of the psmsl subpackage are used.

Developed by HVEC-lab, 2022
"""


# Public packages
import pandas as pd
import requests
import warnings


# Company packages
import hvec_importers.psmsl as psmsl
import hvec_importers.parsers as parse


url = 'https://d3qt3aobtsas2h.cloudfront.net/edge/ws/search/projection?psmsl_id='


def data_single_id(id):
    """
    Get ipcc scenario data of a PSMSL station selected by station_ID
    """
    try:
        stations = psmsl.station_list(include_metric = False)
        name = stations.loc[stations['ID'] == id, "Station Name"].squeeze()
    except:
        warnings.warn('Station with id ', id, ' not found')
        return

    # Assemble url and read file
    data_url = url + str(id) + '&format=csv'
    data = pd.read_excel(data_url, sheet_name = None)

    # If scenario data is provided, the file contains nine sheets
    # and else only 1. We are interested in files with data only
    if len(data) == 1:
        warnings.warn(f'Only one sheet found. File for {id, name} contains no scenario data')
        return pd.DataFrame()
    else:
        df = parse.ipcc_workbook(data)
        return df


def data_single_name(name):
    """
    Get scenarios of a PSMSL station selected by name
    """
    try:
        id = psmsl.id_from_name(name, include_metric = False).item()
        df = data_single_id(id)
    except:
        raise NameError('No data found for ' + name)
    return df


