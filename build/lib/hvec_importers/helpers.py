"""
Sub-package helpers. Supporting multiple other packages in hvec_importers.

Developed by HVEC-lab, october 2022
"""

import warnings


def id_from_name(StationLister, name, **kwargs):
    """
    Select station ID from a name. Used for PSMSL and GLOSS.
    """

    name = name.upper()  # Set input to upper case, ensuring
                         # case-insensitive selection

    stations = StationLister(**kwargs)

    stations.columns = stations.columns.str.replace(' ', '')
    stations['name'] = stations['name'].str.upper()

    selected = stations.query('name.str.contains(@name)', engine='python')

    if len(selected) == 0:
        warnings.warn('No data found for ' + name)
        return
    if len(selected) > 1:
        warnings.warn('Multiple locations selected for ', name, '. Specify longer name')
        return
    #TODO find better solution
    id = selected.reset_index()['id'].squeeze()
    return id.item()  # Ensure native Python integer
