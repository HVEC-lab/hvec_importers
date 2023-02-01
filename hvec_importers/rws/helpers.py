"""
Helper functions for rws waterinfo import

HVEC-lab, 2023
"""

import datetime as dt
import dateutil
import pytz
import pandas as pd


def create_selection_table(locations,
    name, quantity,
    start = '18000101',
    end = '21001231'):
    #TODO: taking input as vectors
    """
    The waterinfo data is vast and complicated. It turns out that the same
    location is often stored under several station codes.

    We expect the user to specify a station name, quantity and date range
    only. In this method, the input is used to find all codes satisfying
    the selection. Thus we ensure that no data is missed.

    Args:
       station_table: dataframe with all locations and quantities
       name, string: location name
       quantity, string: quantity code following RWS-convention
       start and end, string: start and end of interval; date written as string

    Output:
        selected, dataframe: request specification with location codes,
                             quantity codes and start and end dates
    """
    # Selection on name
    selected = locations.query('Naam == (@name)', engine = 'python')

    # Select location codes with specified quantity
    selected = selected[selected['Grootheid.Code'].isin([quantity])]
    selected.reset_index(inplace=True)

    # Add dates to specification
    selected['start'] = start
    selected['end'] = end
    return selected


def create_date_strings(start, end):
    """
    Parsing dates to strings in correct format for waterinfo requests

    Args:
        start, end; datetime: input dates

    Output:
        start_str, end_str: dates as correctly formatted strings
    """
    start_date_str = pytz.UTC.localize(start).isoformat(timespec="milliseconds")
    end_date_str = pytz.UTC.localize(end).isoformat(timespec="milliseconds")
    return start_date_str, end_date_str


def create_availability_request(location, start, end):
    """
    Prepare request to obtain data availability for given period and a single location code

    Args:
        location, dataframe: specification of a single location
        start, end, datetime: start and end of interval

    Output:
        request, dictionary formatted in accordance with requirements of waterinfo
    """
    start_date_str, end_date_str = create_date_strings(start, end)

    request = {
        "AquoMetadataLijst": [{
            "Compartiment": {"Code": location["Compartiment.Code"].squeeze()},
            "Eenheid": {"Code": location["Eenheid.Code"].squeeze()}
            }],
        "LocatieLijst": [{
            "X": location["X"].squeeze(),
            "Y": location["Y"].squeeze(),
            "Code": location["Code"].squeeze()
            }],
      "Periode": {
        "Begindatumtijd": start_date_str,
        "Einddatumtijd": end_date_str
      }
    }
    return request


def create_data_request(location, start, end):
    """
    Prepare data request for specified period and location
    """
    start_date_str, end_date_str = create_date_strings(start, end)

    request = {
        "AquoPlusWaarnemingMetadata": {
            "AquoMetadata": {
                "Eenheid": {"Code": location["Eenheid.Code"].squeeze()},
                "Grootheid": {"Code": location["Grootheid.Code"].squeeze()},
                "Hoedanigheid": {"Code": location["Hoedanigheid.Code"].squeeze()},
            }
        },
        "Locatie": {
            "X": location["X"].squeeze(),
            "Y": location["Y"].squeeze(),
            # assert code is used as index
            "Code": location["Code"].squeeze(),
        },
        "Periode": {"Begindatumtijd": start_date_str, "Einddatumtijd": end_date_str},
    }
    return request


def date_series(start, end):
    """
    Split the daterange in intervals described in pairs
    """
    #TODO: deal with edge case of short periods
    start = dateutil.parser.parse(start)
    end =   dateutil.parser.parse(end)

    # Roughly to the number of years
    # Minimum two periods to prevent exception of one-element list
    # Accept slight increase of internet-traffic in case of very small requests
    # favoring simplicity of code
    periods = (((end - start).days) // 30) + 2

    date_range = pd.date_range(start, end, periods = periods).to_pydatetime()

    starts = date_range[:-1]
    ends = date_range[1:]

    result = list(zip(starts, ends))
    return result
