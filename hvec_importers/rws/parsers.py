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


def _reduce_table(df):
    """
    Drop excess columns and reduce sample frequency
    """
    df = df[
        [
            'Tijdstip',
            'Eenheid.code',
            'Grootheid.code',
            'Meetwaarde.Waarde_Numeriek',
            'WaarnemingMetadata.StatuswaardeLijst',
            'Parameter_Wat_Omschrijving'
            ]
    ]

    # Check for duplicates, keeping checked values if available
    # Sorting ensures that unchecked values are always the second
    df.sort_values(by = 'WaarnemingMetadata.StatuswaardeLijst', inplace = True)

    # Due to sorting, unchecked values are the duplicates, if present
    df.drop_duplicates(subset = 'Tijdstip', inplace = True)
    df = df.loc[df['Tijdstip'].dt.minute%10 == 0]  # Keep 10 minute values only
    return df


def parse_data(raw):
    """
    Parse raw waterinfo data to dataframe.

    SiggyF is gratefully acknowledged for his initial version. However,
    his nested for-loops were very slow and performance heavily downgraded
    with increasing number of rows.

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
    # Exploding the column to get the location dataframe
    LocatieLijst = df['Locatie'].apply(pd.Series)
    LocatieLijst.drop(columns = 'Locatie_MessageID', inplace = True)

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




    
    

    if "waarde" in df.columns:
        df[df["waarde"] == 999999999] = None

    

    df['Tijdstip'] = pd.to_datetime(df['Tijdstip'])

    df = _reduce_table(df)

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
        ['Naam', 'Tijdstip', 'Waarde', 'Eenheid', 'Status', 'Grootheid', 'Omschrijving']
    ]
    return df
