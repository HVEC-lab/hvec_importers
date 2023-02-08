"""
Import of data from Rijkswaterstaat Waterinfo.
All communication with waterinfo is bundled here.

Sub-package of hvec_importers.

Developed by HVEC-lab, 2023

Based on the tool rws-ddlpy by SiggyF. Refactored, optimised parsers and
different philosophy of interfacing with the user.
"""

import logging
import pathlib
import json
import requests
from tqdm import tqdm
import pandas as pd
import time

from hvec_importers.rws import helpers as hlp
from hvec_importers.rws import parsers as parse

HEADERS = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
    ' Chrome/105.0.0.0 Safari/537.36')

BASE_URL = "https://waterwebservices.rijkswaterstaat.nl/"
ENDPOINTS_PATH = pathlib.Path(__file__).with_name("endpoints.json")

with ENDPOINTS_PATH.open() as f:
    ENDPOINTS = json.load(f)

TIMEOUT = 60

class NoDataException(ValueError):
    pass


def station_list_raw():
    """
    Get station information from DDL (metadata from Catalogue). All metadata regarding stations.
    The response (result) retrieves more keys
    """
    endpoint = ENDPOINTS["collect_catalogue"]
    msg = "{} with {}".format(endpoint["url"], json.dumps(endpoint["request"]))
    logging.debug("requesting: {}".format(msg))

    resp = requests.post(endpoint["url"], json=endpoint["request"], timeout = TIMEOUT)

    if not resp.ok:
        raise IOError("Failed to request {}: {}".format(msg, resp.text))

    result = resp.json()

    if not result["Succesvol"]:
        logging.exception(str(result))
        raise ValueError(result.get("Foutmelding", "No error returned"))

    return result


def assert_data_available(location, start_i, end_i, session):
    """
    Check data availability on the waterinfo site.

    Args:
        location, dataframe: location properties, quantity and time period
            The method expects a single entity in the dataframe, so use
            pd.groupby in the call to this method.
        start_i, end_i; datetime: start and end of interval

    Output:
        Single boolean indicating data availability
    """
    endpoint = ENDPOINTS["check_observations_available"]

    request = hlp.create_availability_request(location, start_i, end_i)
    resp = session.post(endpoint["url"], json = request, timeout = TIMEOUT)

    result = resp.json()
    if not result["Succesvol"]:
        logging.debug("Got  invalid response: {}".format(result))
        raise NoDataException(result.get("Error requesting availability", "No error returned"))

    return result['WaarnemingenAanwezig'] == 'true'


def _get_raw_slice(location, start_i, end_i, session):
    """
    Get raw data from the waterinfo site for a given slice

    Args:
        location, dataframe: location properties, quantity and time period
            The method expects a single entity in the dataframe, so use
            pd.groupby in the call to this method.
        start_i, end_i: start and end of interval
        session: request session
    """
    endpoint = ENDPOINTS["collect_observations"]

    request = hlp.create_data_request(location, start_i, end_i)

    try:
        logging.debug("requesting:  {}".format(request))

        resp = session.post(endpoint["url"], json=request, timeout = TIMEOUT)
        result = resp.json()

        if not result["Succesvol"]:
            logging.debug("Got  invalid response: {}".format(result))
            raise NoDataException(result.get("Foutmelding", "No error returned"))

    except NoDataException as e:
        logging.debug("No data available for {} {}".format(start_i, end_i))
        raise e

    return result


def get_data(location):
    """
    Slice the requested time interval. Download data in slices, parse to dataframe
    and merge.

    Args:
        location, dataframe: location properties, quantity and time period
            The method expects a single entity in the dataframe, so use
            pd.groupby in the call to this method.
    """
    # TODO: investigate further optimisation by joining the jsons and parse to dataframe only once
    
    # Create re-usable session
    session = requests.Session()

    date_range = hlp.date_series(location['start'].squeeze(), location['end'].squeeze())

    df = pd.DataFrame() # Empty dataframe to store results

    for (start_i, end_i) in tqdm(date_range):

        data_present = assert_data_available(location, start_i, end_i, session)
        if data_present:
            try:
                raw = _get_raw_slice(location, start_i, end_i, session)
                clean = parse.parse_data(raw)
                df = pd.concat([df, clean])

            except NoDataException:
                logging.debug("Data availability is checked beforehand, so this should not have happened")
                continue
            #time.sleep(2) # Prevent overloading website

    # Final house keeping; close session
    session.close()

    return df
