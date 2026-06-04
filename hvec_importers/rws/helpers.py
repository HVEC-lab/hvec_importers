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
    code, quantity,
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
    selected = locations.loc[locations['Code'] == code]

    # Select location codes with specified quantity
    selected = selected[selected['Grootheid.Code'].isin([quantity])]
    selected.reset_index(inplace=True)

    # In the new data format (2026) the same quantity is available as observation, astronomical forecast and
    # operational forecast (called ProcesType). Therefore, the selection on location and quantity may duplicate.
    # The data is imported irrespective of the ProcesType where the ProcesType is part of the output for later use.
    # Therefore, the duplicated location/quantity pairs need to be taken out.
    selected.drop_duplicates(subset = ['Code', 'Grootheid.Code'], inplace = True)

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

    #interval = end - start
    #if interval < dt.timedelta(days = 366):
    #    return list(zip(start, end))
    interval = dateutil.relativedelta.relativedelta(end, start)
    if (interval.years == 0) and (interval.months < CHUNK):
        return [(start, end)]

    starts = pd.date_range(start, end, freq = f'{CHUNK}MS').to_pydatetime()
    ends = starts + dateutil.relativedelta.relativedelta(months = CHUNK, days = -1)
    return list(zip(starts, ends))


def create_data_request(location, start, end):
    """
    Prepare data request for specified period and location
    """
    start_date_str, end_date_str = create_date_strings(start, end)
    
    request = {
          "Locatie": {
              "Code": location["Code"]
          },
          "AquoPlusWaarnemingMetadata": {
            "AquoMetadata": {
                "Compartiment": {"Code": location["Compartiment.Code"]},
                "Grootheid": {"Code": location["Grootheid.Code"]}
            }
          },
        "Periode":
            {
                "Begindatumtijd": start_date_str,
                "Einddatumtijd": end_date_str
            }            
        }
    return request
