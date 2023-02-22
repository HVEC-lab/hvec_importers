"""
Sub-package helpers. Supporting multiple other packages in hvec_importers.

Developed by HVEC-lab, october 2022
"""

import logging


def id_from_name(StationLister, name, **kwargs):
    """
    Select station ID from a name. In properly structured data, the identifier is unique.

    Used for PSMSL and GLOSS.

    Args:
        StationLister: function importing the station list
        name, string of desired location

    Output:
        id, integer: station id number
    """

    name = name.upper()  # Set input to upper case, ensuring
                         # case-insensitive selection

    stations = StationLister(**kwargs)

    stations.columns = stations.columns.str.replace(' ', '')
    stations['name'] = stations['name'].str.upper()

    selected = stations.query('name.str.contains(@name)', engine='python')

    if len(selected) == 0:
        logging.info('No data found for ' + name)
        return
    if len(selected) > 1:
        logging.info('Multiple locations selected for ', name, '. Specify longer name')
        return
    #TODO find better solution
    id = selected.reset_index()['id'].squeeze()
    return id
