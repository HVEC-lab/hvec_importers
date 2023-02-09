"""
Constants used for subpackage RWS of HVEC_importers.

HVEC-lab, 2023
"""

import json
import pathlib

# Settings for communicating with the website
HEADERS = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
    ' Chrome/105.0.0.0 Safari/537.36')

BASE_URL = "https://waterwebservices.rijkswaterstaat.nl/"
ENDPOINTS_PATH = pathlib.Path(__file__).with_name("endpoints.json")

with ENDPOINTS_PATH.open() as f:
    ENDPOINTS = json.load(f)

TIMEOUT = 120

# Name of the local location file. Locally storing the location list in json
# provides considerable performance gain
LOCATION_FILE = 'locations.json'


# Select main group of parameters by pre-selecting a compartment
COMPARTMENT = ['OW', 'LT']
