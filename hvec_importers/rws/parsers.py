"""
Parsers for imported RWS data

HVEC-lab, 2023
"""

import logging
import pandas as pd

from hvec_importers.rws.constants import COMPARTMENT


def parse_station_list(raw):
    """
    Take the imported raw station list and parse to
    dataframe.

    The selection to the group of parameters specified in
    constants is applied here.
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

    # Limit the list to the compartment specified in the constants
    merged = merged.query('`Compartiment.Code`.isin(@COMPARTMENT)')
    # set station id as index
    return merged.set_index("Code")


def parse_data(raw):
    """
    Parse raw waterinfo data to dataframe.

    SiggyF is gratefully acknowledged for his initial version. However,
    his nested for-loops were very slow and performance heavily downgraded
    with increasing number of rows, preventing the downloading of large
    chunks of data.

    So an alternative was implemented

    Args:
        raw, json: raw waterinfo output

    Out:
        df, dataframe: flattened data
    """

    # Put raw in DataFrame
    df = pd.json_normalize(
        data = raw['WaarnemingenLijst'],
        record_path = 'MetingenLijst',
        meta = ['Locatie', 'AquoMetadata'])

    # Keep only the relevant columns
    keep = [
        'Tijdstip',
        'Meetwaarde.Waarde_Numeriek',
        'WaarnemingMetadata.StatuswaardeLijst',
        'Locatie',
        'AquoMetadata'
        ]
    df = df[keep]

    # The location column (Locatie) is a column of dictionaries
    LocatieLijst = df['Locatie'].apply(pd.Series)
    LocatieLijst.drop(columns = ['Locatie_MessageID', 'Code'], inplace = True)

    # ... and add to MetingenLijst while dropping the original column
    df = pd.concat([df.drop(columns = 'Locatie'), LocatieLijst], axis = 1)

    # Process the AquoMetadata in a similar way
    # But do not bother with unused columns
    meta = df['AquoMetadata'].apply(pd.Series)
    keep = [
        'Parameter_Wat_Omschrijving',
        'Eenheid',
        'MeetApparaat'
    ]
    meta = meta[keep]

    # Extract relevant info from Eenheid and MeetApparaat and add
    tmp = meta['Eenheid'].apply(pd.Series)['Code']
    meta['Eenheid'] = tmp # Reuse column; replace values

    tmp = meta['MeetApparaat'].apply(pd.Series)['Omschrijving']
    meta['MeetApparaat'] = tmp

    df = pd.concat(
        [df.drop(columns = 'AquoMetadata'), meta], axis = 1)

    # Shorten column names
    df.rename(
        columns = {
            'Meetwaarde.Waarde_Numeriek': 'waarde',
            'Parameter_Wat_Omschrijving': 'Parameter_Omschrijving',
            'WaarnemingMetadata.StatuswaardeLijst': 'Status'
        }, inplace = True
    )

    # Final datatype details
    df['Status'] = df['Status'].explode()

    # Set missing values to None
    if "waarde" in df.columns:
        df.loc[df["waarde"] == 999999999, 'waarde'] = None

    return df
