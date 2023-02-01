"""
Test cases for RWS import functions
"""

import pytest as pyt
import requests
import datetime as dt
import numpy as np

from hvec_importers.rws import rws
from hvec_importers.rws import communicators as com
from hvec_importers.rws import helpers as hlp

# Import test cases
import_tests =  [
        ('Den Helder', 'WATHTE', '1972-1-1', '31-12-1975'),
        ('Lobith', 'Q', '3-2-1925', '10-10-1928'),
        ('Vlissingen', 'WATHTE', '1953-01-01', '1953-02-28'),
        ('Yerseke', 'WATHTE', '1953-01-29', '1953-02-03')
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
    ENDPOINTS = com.ENDPOINTS
    endpoint = com.ENDPOINTS[endpoint]

    url = endpoint['url']
    req_txt = endpoint['request']

    res = requests.post(url, json = req_txt)

    assert res.ok


def test_station_list():
    """
    Test import of station catalogue
    """
    stations = rws.station_list()
    assert len(stations.columns) > 1
    assert len(stations) > 15000


@pyt.mark.parametrize("name, quantity, start, end", import_tests)
def test_create_selection_table(name, quantity, start, end):
    """
    Test creating import request from human input
    """
    locations = rws.station_list()
    req = hlp.create_selection_table(locations, name, quantity, start, end)
    assert len(req.columns) > 1

@pyt.mark.parametrize("name, quantity, start, end", import_tests)
def test_data_availability(name, quantity, start, end):
    """
    Test method for data availability with human input
    """
    res = rws.data_availability(name, quantity, start, end)
    assert len(res.columns) > 1
    assert res.dtypes[1] == 'bool'


@pyt.mark.parametrize("name, quantity, start, end", import_tests)
def test_data_single_name(name, quantity, start, end):
    """
    Test data import RWS Waterinfo
    """
    df = rws.data_single_name(name, quantity, start, end)
    assert len(df.columns) > 1