"""
Testers for the sub-package ipcc.

HVEC-lab, 2022
"""


# Public packages
import pytest as pyt
import requests

# Company package
from hvec_importers.ipcc import ipcc


@pyt.mark.parametrize(
    "id", [1, 2, 8, 9, 123]
)
def test_connections(id):
    res = requests.get(ipcc.url + str(id))
    assert res.ok


@pyt.mark.parametrize(
    "id, expected_length",
    [
        (1, 784),
        (229, 784),
        (759, 784),
        (1371, 784),
        (4, 0)
        ]
)
def test_data_single_id(id, expected_length):
    df = ipcc.data_single_id(id)
    # length is the number of sheets in the workbook
    assert len(df) == expected_length


@pyt.mark.parametrize(
    "name, expected_length",
    [
        ("Delfzijl", 784),
        ("Warnemunde 2", 784),
        ("LIVERPOOL G", 784)
    ]
)
def test_single_name(name, expected_length):
    df = ipcc.data_single_name(name)
    assert len(df) == expected_length
