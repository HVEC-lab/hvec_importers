"""
Parsers for imported RWS data

HVEC-lab, 2023
"""

import logging
import pandas as pd


def parse_station_list(raw):
    """
    Take the imported raw station list and parse to
    dataframe
    """

    df_locations = pd.DataFrame(raw["LocatieLijst"])

    df_metadata = pd.json_normalize(raw["AquoMetadataLijst"])

    df_metadata_location = pd.DataFrame(raw["AquoMetadataLocatieLijst"])

    merged = (
        df_metadata_location.set_index("Locatie_MessageID")
        .join(df_locations.set_index("Locatie_MessageID"), how="inner")
        .reset_index()
    )
    merged = merged.set_index("AquoMetaData_MessageID").join(
        df_metadata.set_index("AquoMetadata_MessageID")
    )
    # set station id as index
    return merged.set_index("Code")


def parse_data(raw):
    """
    Parse raw waterinfo data to dataframe. SiggyF is gratefully acknowledged
    for all this hard work.

    Args:
        raw, json: raw waterinfo output

    Out:
        df, dataframe: flattened data
    """
    #TODO: skip unnecessary columns

    assert "WaarnemingenLijst" in raw

    # assert len(raw['WaarnemingenLijst']) == 1
    # flatten the datastructure
    rows = []
    for waarneming in raw["WaarnemingenLijst"]:
        for row in waarneming["MetingenLijst"]:
            # metadata is a list of 1 value, flatten it
            new_row = {}
            for key, value in row["WaarnemingMetadata"].items():
                new_key = "WaarnemingMetadata." + key
                new_val = value[0] if len(value) == 1 else value
                new_row[new_key] = new_val

            # add remaining data
            for key, val in row.items():
                if key == "WaarnemingMetadata":
                    continue
                new_row[key] = val

            # add metadata
            for key, val in list(waarneming["AquoMetadata"].items()):
                if isinstance(val, dict) and "Code" in val and "Omschrijving" in val:
                    # some values have a code/omschrijving pair, flatten them
                    new_key = key + ".code"
                    new_val = val["Code"]
                    new_row[new_key] = new_val

                    new_key = key + ".Omschrijving"
                    new_val = val["Omschrijving"]
                    new_row[new_key] = new_val
                else:
                    new_row[key] = val
            rows.append(new_row)
    # normalize and return
    df = pd.json_normalize(rows)
    # set NA value
    if "Meetwaarde.Waarde_Numeriek" in df.columns:
        df[df["Meetwaarde.Waarde_Numeriek"] == 999999999] = None

    try:
        df["t"] = pd.to_datetime(df["Tijdstip"])
    except KeyError:
        logging.exception(
            "Cannot add time variable t because variable Tijdstip is not found"
        )
    return df


def simplify_output(df):
    """
    Takes a dataframe resulting from RWS data import and shortens the 
    most used columns
    """
    df.rename(
        columns = {
            'Eenheid.code': 'Eenheid',
            'Grootheid.code': 'Grootheid',
            'Meetwaarde.Waarde_Numeriek': 'Waarde',
            'WaarnemingMetadata.StatuswaardeLijst': 'Status',
            'Parameter_Wat_Omschrijving': 'Omschrijving',
        }, inplace = True)

    df = df[
        ['Naam', 't', 'Waarde', 'Eenheid', 'Status', 'Grootheid', 'Omschrijving']
    ]
    return df
