"""
Test cases for RWS import functions
"""

import pytest as pyt
import requests
import datetime as dt
import numpy as np

from hvec_importers.rws import rws
from hvec_importers.rws.constants import *
from hvec_importers.rws import communicators as com
from hvec_importers.rws import helpers as hlp

# Import test cases
import_tests =  [
        ('Den Helder', 'WATHTE', '1972-1-1', '31-12-1975', True),
        ('Lobith', 'Q', '3-2-1925', '10-10-1928', True),
        ('Vlissingen', 'WATHTE', '1968-01-01', '1968-1-31', True),
        ('Tiel Waal', 'Q', '1978-01-01', '1978-12-31', False),
        #('Roompot binnen', 'WATHTE', '1-1-1989', '31-12-1991'),
        ('Harlingen', 'WATHTE', '2023-01-01', '2023-12-31', False),
        ('Roggenplaat', 'Hm0', '2023-2-1', '2023-2-28', False),
        ('Euro platform', 'WATHTE', '1-1-2015', '31-1-2015', False),
        ('Hoek van Holland', 'WINDSHD', '1-1-1900', '31-12-2022', False),
        ('Olst', 'Q', '2022-1-1', '2022-12-31', True)
        ]

@pyt.mark.parametrize(
    "endpoint",
    [
        'collect_catalogue',
        'collect_observations',
        'collect_latest_observations',
        'check_observations_available',
        'collect_number_of_observations',
        'request_bulk_observations']
)

def test_connections(endpoint):
    """
    Testing connections
    """
    endpoint = ENDPOINTS[endpoint]

    url = endpoint['url']
    req_txt = endpoint['request']

    res = requests.post(url, json = req_txt, timeout = 60)

    assert res.ok

@pyt.mark.parametrize("renew", [False, True])
def test_station_list(renew):
    """
    Test import of station catalogue
    """
    stations = rws.station_list(renew)
    assert len(stations.columns) > 1
    assert len(stations) > 15000


@pyt.mark.parametrize("name, quantity, start, end, reduce", import_tests)
def test_create_selection_table(name, quantity, start, end, reduce):
    """
    Test creating import request from human input
    """
    locations = rws.station_list()
    req = hlp.create_selection_table(locations, name, quantity, start, end)
    assert len(req.columns) > 1

@pyt.mark.parametrize("name, quantity, start, end, reduce", import_tests)
def test_data_availability(name, quantity, start, end, reduce):
    """
    Test method for data availability with human input
    """
    res = rws.data_availability(name, quantity, start, end)
    assert len(res.columns) > 1
    assert res.dtypes[3] == 'bool'


@pyt.mark.parametrize("name, quantity, start, end, reduce", import_tests)
def test_data_single_name(name, quantity, start, end, reduce):
    """
    Test data import RWS Waterinfo
    """
    df = rws.data_single_name(name, quantity, start, end, reduce)
    assert len(df.columns) > 1
