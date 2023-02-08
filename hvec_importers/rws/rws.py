"""
Importers for Rijkswaterstaat Waterinfo.

Sub-package of hvec_importers.

Data is imported from the website waterinfo.rws.nl through the api specified
for it. The input to the website consists of complex json-formatted data. The
website is sensitive to missing or incorrectly formatted fields.

This module provides three functions wich assume user-friendly input.

HVEC-lab, 2022
"""

import os
import logging
import pandas as pd
import dateutil
import requests

# The code is organised in thematic sub-packages
from hvec_importers.rws import communicators as com
from hvec_importers.rws import parsers as parse
from hvec_importers.rws import helpers as hlp


def station_list(renew = False):
    """
    Get list of station and parameter combinations

    Args:
        None

    Outputs:
        Station list as dataframe
    """
    FILE = 'locations.json'

    if renew or not os.path.isfile(FILE):
        logging.info("Contacting waterinfo for location lists")
        raw = com.station_list_raw()
        clean = parse.parse_station_list(raw)
        # Store in json file
        clean.reset_index().to_json(r'locations.json', orient='records', index = True)
        return clean

    clean = pd.read_json(FILE, orient='records')
    clean.set_index("Code", inplace = True)
    return clean


def data_availability(
    name, quantity,
    start = '1800-01-01',
    end   = '2100-12-31'):
    """
    Show data availability using human input

    Args:
        name, string
        quantity, string; specified in accordance with RWS specs
        start, string or datetime; start date
        end, string or datetime; end date

    Output:

    """
    session = requests.session()

    start = dateutil.parser.parse(start)
    end   = dateutil.parser.parse(end)

    locations = station_list()
    selected  = hlp.create_selection_table(locations, name, quantity, start, end)

    # A location may be stored under multiple codes; check for all
    res = selected.groupby('Code').apply(
        lambda x: com.assert_data_available(x, start, end, session)).reset_index()
    res.columns = ["Code", "Data_present"]

    session.close()
    return res


def data_single_name(
    name, quantity,
    start = '1850-01-01',
    end = '2100-12-31'):
    """
    Take natural input, process it and harvest data

    Args:
        name, string
        quantity, string; specified in accordance with RWS specs
        start, string or datetime; start date
        end, string or datetime; end date
    """
    stations = station_list()
    selected = hlp.create_selection_table(stations, name, quantity, start, end)

    df = selected.groupby('Code').apply(
        lambda x: com.get_data(x))

    # The data from all codes is combined in a single dataframe
    # Drop the resulting multi-index
    df.reset_index(inplace = True)
    df.drop(columns = 'level_1', inplace = True)

    return df
