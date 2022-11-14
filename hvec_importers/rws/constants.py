"""
Constants for the sub-package rws of hvec_importers.

HVEC lab, 2022
"""

import pathlib
import json


BASE = "https://waterwebservices.rijkswaterstaat.nl/"
ENDPOINTS_PATH = pathlib.Path(__file__).with_name("endpoints.json")

with ENDPOINTS_PATH.open() as f:
    ENDPOINTS = json.load(f)
