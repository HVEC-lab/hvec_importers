"""
Sub-package with import functions for RWS data.

HVEC lab, 2022

Kuddos to SiggyF who developed ddlpy. Working with his code was a great learning experience
and this code was based on ddlpy.
"""

import json
import logging
import requests
import pandas as pd

from .constants import BASE, ENDPOINTS

#TODO: refactored to the same fuctionality as ddlpy (merged list). Consider applying partial lists to speed up

def _raw_catalogue():
    """
    Get the raw location and quantity information from Waterinfo
    """
    # Create request
    endpoint = ENDPOINTS["collect_catalogue"]
    msg = "{} with {}".format(endpoint["url"], json.dumps(endpoint["request"]))
    logging.info("requesting: {}".format(msg))

    # Connect website
    resp = requests.post(endpoint["url"], json=endpoint["request"], timeout = 120)

    # Parse output
    if not resp.ok:
        raise IOError("Failed to request {}: {}".format(msg, resp.text))

    result = resp.json()
    if not result["Succesvol"]:
        logging.exception(str(result))
        raise ValueError(result.get("Error", "No error returned"))
    
    return result


def _locations(raw):
    """
    Get list of measurment stations of RWS
    """
    # Get partial lists
    df = pd.DataFrame(raw["LocatieLijst"])
    df.set_index('Locatie_MessageID', inplace = True)
    return df


def _metadata_list(raw):
    """
    Get list of quantities
    """
    df = pd.json_normalize(raw["AquoMetadataLijst"])
    #df.set_index('Locatie_MessageID', inplace = True)
    return df


def _join_list(raw):
    """
    Get list coupling locations to quantities
    """
    df = pd.DataFrame(raw["AquoMetadataLocatieLijst"])
    df.set_index("Locatie_MessageID", inplace = True)
    return df


def _merged_list(raw):
    """
    Create merged list
    """
    locations = _locations(raw)
    metadata = _metadata_list(raw)
    joins = _join_list(raw)

    merged = metadata.join(locations, how="inner")

    merged = merged.set_index("AquoMetaData_MessageID").join(
        df_metadata.set_index("AquoMetadata_MessageID")
    )
    # set station id as index
    return merged.set_index("Code")


#def station_list():
#    """
#    Contact data source and create full station list
#    """
#    raw = _raw_catalogue()

#    res = _merged_list(raw)

#    return res

def station_list():
    """
    get station information from DDL (metadata from Catalogue). All metadata regarding stations.
    The response (result) retrieves more keys
    """
    raw = _raw_catalogue()
    df_locations = _locations(raw)

    df_metadata = _metadata_list(raw)

    df_metadata_location = _join_list(raw)

    merged = (
        df_metadata_location
        .join(df_locations, how="inner")
        .reset_index()
    )
    merged = merged.set_index("AquoMetaData_MessageID").join(
        df_metadata.set_index("AquoMetadata_MessageID")
    )
    # set station id as index
    return merged.set_index("Code")
