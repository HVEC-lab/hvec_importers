"""
Testers for the sub-package PSMSL.

HVEC-lab, 2022
"""


# Public packages
import pytest as pyt
import requests
import json

# Company package
from hvec_importers import catalogues


def test_constants():
    """
    Testing whether the constants are found
    """
    print(catalogues.BASE)
    print(catalogues.ENDPOINTS)
    return



def test_base():
    """
    Test base url
    """
    res = requests.get(catalogues.BASE, timeout = 10)
    assert res.ok


def test_station_list():
    names = catalogues.station_list()
    assert 'Naam' in names.columns
    assert len(names) > 100


@pyt.mark.parametrize(
    "name, include_metric, id_expected",
    [('Delfzijl', False, 24),
    ('delfzijl', False, 24),
    ('DELFZIJL', False, 24),
    ('delf', False, 24),
    ('zijl', False, 24),
    ('Brest', False, 1),
    ('Cuxhaven', False, 7)
    ]
)
def test_id_from_name(
    name, include_metric, id_expected):
    id = catalogues.id_from_name(
        name, include_metric)
    assert (id == id_expected).all()


def test_data_single_id():
    data = catalogues.data_single_id(session = requests.session(), nr = 24)
    assert len(data) > 0


@pyt.mark.parametrize(
    "name",
    ['Delfzijl',
    'delfzijl',
    'DELFZIJL',
    'delf',
    'zijl',
    'Brest',
    'Cuxhaven 2',
    ]
)
def test_data_single_name(name):
    data = catalogues.data_single_name(name, include_metric = True)
    assert len(data) > 0
