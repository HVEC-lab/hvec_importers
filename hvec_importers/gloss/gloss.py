"""
Importers for Global Sealevel Observing System (GLOSS) data (high frequency sea level data).

Sub-packages of hvec_importers.

Developed by HVEC lab, 2022

Notes
----------------------------
Wide date range prescribed aiming to download all available data. Selection on location
by name and GLOSS id implemented.
"""

# Public packages
import warnings
import io
import logging
import requests
import time
import pandas as pd
import datetime as dt

from hvec_importers import helpers
from hvec_importers import parsers as parse


max_attempt = 5
timeout = 20  # Maximum number of tries to contact a website


url = {
    'gloss_core_network': 'https://www.gloss-sealevel.org/gloss-station-handbook',
    'fast_delivery':
        'https://uhslc.soest.hawaii.edu/erddap/tabledap/global_hourly_fast.csv?sea_level%2Ctime'
        '%2Cstation_name%2Crecord_id%2Cuhslc_id%2Cgloss_id%2Cssc_id%2Clast_rq_date&time'
        '%3E=1700-1-1T00%3A00%3A00Z&time%3C=2050-12-31T22%3A59%3A59Z&gloss_id=',
    'research_quality':
        'https://uhslc.soest.hawaii.edu/erddap/tabledap/global_hourly_rqds.csv?sea_level'
        '%2Ctime%2Cstation_name%2Crecord_id%2Cuhslc_id%2Cversion%2Cgloss_id%2Cssc_id'
        '%2Creference_code%2Creference_offset&time%3E=1700-01-01T00%3A00%3A00Z&time'
        '%3C=2050-12-31T13%3A59%3A59Z&gloss_id='
    }


def station_list():
    """
    Obtain the list of stations and station data from the GLOSS station handbook

    Points of attention
    -------------------
    - The GLOSS website is being reorganised. The list possbilly moves to a new location in
      the near future
    """
    stations = pd.read_html(url['gloss_core_network'])[0]

    stations.rename(
        columns = {
            'Station': 'name',
            'GLOSS number': 'id',
            'Longitude (+ve\xa0E)': 'longitude',
            'Latitude (+ve\xa0N)': 'latitude'},
            inplace = True)

    stations = parse.parseStationList(stations)
    return stations


def id_from_name(name):
    """
    Select gloss id from name
    """
    id = helpers.id_from_name(station_list, name)
    return id


def data_single_id(id, session, type = 'fast_delivery', drop_current_year = True):
    """
    Get data of a gloss station selected by station_ID.

    The website foresees delivery of quality-checked data (reseach quality) or 
    fast delivery. The difference being that the latter contains the last two years
    of data.

    We allow selection of one of the two options with 'fast_delivery' as default.
    """
    # Errors and warnings
    assert type in ['research_quality', 'fast_delivery'], ('type should be research_quality'
                                                        '    or fast_delivery')
    assert isinstance(id, int), 'id should be integer'

    if type == 'fast_delivery':
        warnings.warn('Last few years are not research quality!')

    # Assemble url
    base = url[type]
    data_url = str(id)

    # Get data
    for n in range(max_attempt):  # Make repeated requests to website
        try:
            res = session.get(base + data_url, timeout = timeout)
            time.sleep(2)
            if res.ok: 
                break
            logging.warning(f'gloss.data_single_id: Attempt {n}')
        except Exception as e:
            logging.warning('gloss.data_single_id: Attempt ' + str(n) + ';' + str(e)) # Wait before trying again

    if res.ok:
        df = pd.read_csv(io.BytesIO(res.content), header = 0, skiprows = [1])

        df.dropna(axis = 'rows', how = 'any', inplace = True)
        #TODO check timezone definitiions in original data
        df['time'] = pd.to_datetime(df['time'], yearfirst = True).dt.tz_convert(None)
        if drop_current_year:
            df = df.loc[df['time'].dt.year < dt.date.today().year]

        df['sea_level'] = df['sea_level'].div(1000)
        df.rename(columns = {'gloss_id': 'id', 'sea_level': 'level'}, inplace = True)
    else:
        df = pd.DataFrame()

    return df




