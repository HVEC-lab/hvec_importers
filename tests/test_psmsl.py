"""
Testers for the sub-package PSMSL.

HVEC-lab, 2022
"""


# Public packages
import pytest as pyt
import requests

# Company package
from hvec_importers.psmsl import psmsl


@pyt.mark.parametrize(
    "key",
    ['rlr',
    'met'
    ]
)
def test_connections(key):
    res = requests.get(psmsl.url[key])
    assert res.ok


@pyt.mark.parametrize(
    "include_metric, number_of_rows",
    [(False, 1548),
    (True, 2363)
    ]
)
def test_station_list_complete_input(
    include_metric,
    number_of_rows
):
    names = psmsl.station_list(include_metric)
    assert len(names) == number_of_rows


def test_station_list_columns_complete():
    names = psmsl.station_list(
        include_metric = True
        )
    assert 'type' in names.columns


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
    id = psmsl.id_from_name(
        name, include_metric)
    assert (id == id_expected).all()


def test_data_single_id():
    data = psmsl.data_single_id(session = requests.session(), id = 24)
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
    data = psmsl.data_single_name(name, include_metric = True)
    assert len(data) > 0
