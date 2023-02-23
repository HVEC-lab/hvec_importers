"""
Helper functions for rws waterinfo import

HVEC-lab, 2023
"""

import datetime as dt
import dateutil
import pytz
import pandas as pd

from hvec_importers.rws.constants import CHUNK


def create_selection_table(locations,
    name, quantity,
    start = '1800-01-01',
    end = '2100-12-31'):
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


def date_series(start, end):
    """
    Split the daterange in intervals described in pairs. Select
    only pairs containing data.
    """
    start = dateutil.parser.parse(start)
    end =   dateutil.parser.parse(end)

    # Prevent looking for data after today
    end = min(end, dt.datetime.today())

    #interval = end - start
    #if interval < dt.timedelta(days = 366):
    #    return list(zip(start, end))
    interval = dateutil.relativedelta.relativedelta(end, start)
    if interval.months < CHUNK:
        return [(start, end)]

    starts = pd.date_range(start, end, freq = f'{CHUNK}MS').to_pydatetime()
    ends = starts + dateutil.relativedelta.relativedelta(months = CHUNK, days = -1)
    return list(zip(starts, ends))


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


def create_number_of_points_request(location, start, end):
    """
    Prepare request to obtain number of points per year for given period
    and a single location code

    Args:
        location, dataframe: specification of a single location
        start, end, datetime: start and end of interval

    Output:
        request, dictionary formatted in accordance with requirements of waterinfo
    """
    start_date_str, end_date_str = create_date_strings(start, end)

    request = {
        "AquoMetadataLijst": [{
            "Compartiment": { "Code": location["Compartiment.Code"].squeeze()},
            "Grootheid": {"Code": location["Grootheid.Code"].squeeze()},
            "Eenheid": { "Code": location["Eenheid.Code"].squeeze()}
        }],
      "Groeperingsperiode": "Jaar",
      "LocatieLijst": [{
          "X": location['X'].squeeze(),
          "Y": location['Y'].squeeze(),
          "Code": location['Code'].squeeze()
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
