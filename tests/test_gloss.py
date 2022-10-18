"""
Testers for the sub-package gloss.

HVEC-lab, october 2022
"""


# Public packages
import pytest as pyt
import requests

# Company package
from hvec_importers import gloss


@pyt.mark.parametrize(
    'url', [
        gloss.url['gloss_core_network'],
        gloss.url['research_quality']+'284',
        gloss.url['fast_delivery']+'284'])

def test_connections(url):
    res = requests.get(url, timeout = 10)
    assert res.ok


@pyt.mark.parametrize("number_of_rows", [290])
def test_station_list_complete_input(number_of_rows):
    names = gloss.station_list()
    assert len(names) == number_of_rows


def test_station_list_columns_complete():
    names = gloss.station_list()
    assert 'Country' in names.columns


@pyt.mark.parametrize(
    "name, id_expected",
    [('abidjan', 257),
    ('abid', 257),
    ('ABIDJAN', 257),
    ('djan', 257),
    ('Zhapo', 78),
    ('Brest', 242),
    ('Cuxhaven', 284),
    ('Delfzijl', None)
    ]
)
def test_id_from_name(name, id_expected):
    id = gloss.id_from_name(name)
    assert (id == id_expected)


@pyt.mark.parametrize(
    "id, length",
    [(75, 130320),
    (257, 0),
    (284, 917559),
    (242, 1548552),
    (5, 0)]
)
def test_data_single_id(id, length):
    data = gloss.data_single_id(id = id)
    assert len(data) == length
