"""
Import of data from Rijkswaterstaat Waterinfo.
All communication with waterinfo is bundled here.

Sub-package of hvec_importers.

Developed by HVEC-lab, 2023

Based on the tool rws-ddlpy by SiggyF. Refactored, optimised parsers and
different philosophy of interfacing with the user.
"""

import logging
import json
import requests
import dateutil
import datetime as dt
from tqdm import tqdm
import pandas as pd
import time

from hvec_importers.rws import helpers as hlp
from hvec_importers.rws import parsers as parse
from hvec_importers.rws.constants import ENDPOINTS, TIMEOUT, WAIT, MAX_ATTEMPT

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


def prune_date_range(location, long_range, session):
    """
    Use information on data availabiilty to exclude empty
    date intervals from time consuming import
    """
    starts = []
    ends = []
    for (start_i, end_i) in long_range:
        data_present = assert_data_available(location, start_i, end_i, session)
        if data_present:
            starts.append(start_i)
            ends.append(end_i)
    return list(zip(starts, ends))


def get_raw_slice(location, start_i, end_i, session):
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

    for n in range(MAX_ATTEMPT):
        try:
            logging.debug("requesting: {}. Attempt {}".format(request, n))
            resp = session.post(endpoint["url"], json=request, timeout = TIMEOUT)

            if not resp.ok: # Incorrect website response; try again
                logging.info(f"Attempt {n}. Website responds with {resp}")
                continue

            result = resp.json()
            if not result["Succesvol"]: # Even in case of correct response, no data may be returned
                logging.debug("Got  invalid response: {}".format(result))
                raise NoDataException(result.get("Foutmelding", "No error returned"))

        except NoDataException as e:
            logging.debug("No data available for {} {}".format(start_i, end_i))
            raise e
        
        break  # This point is reached only if response is ok and no error is raised. So no new attempt required

    return result


def get_data(location, reduce):
    """
    Slice the requested time interval. Download data in slices, parse to dataframe
    and merge.

    Args:
        location, dataframe: location properties, quantity and time period
            The method expects a single entity in the dataframe, so use
            pd.groupby in the call to this method.
    """
    df = pd.DataFrame() # Empty dataframe to store results

    # Create re-usable session
    session = requests.Session()

    # Prepare date range
    date_range = hlp.date_series(location['start'].squeeze(), location['end'].squeeze())

    for (start_i, end_i) in tqdm(date_range):
        time.sleep(WAIT)
        try:
            raw = get_raw_slice(location, start_i, end_i, session)
            clean = parse.parse_data(raw)
            clean = parse.format_data(clean, reduce)
            df = pd.concat([df, clean])
        except NoDataException:
            logging.debug(
                "Apparent inconsistency between reported "
                "and actual availability of data on remote site")
            continue

    # Final house keeping; close session
    session.close()
    return df
