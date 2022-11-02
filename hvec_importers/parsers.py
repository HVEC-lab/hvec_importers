"""
General parsers for input functions

HVEC lab, 2022
"""


def parseStationList(stations):
    """
    Set details of the data structure
    """
    stations.set_index(keys = 'ID', inplace = True)
    stations.sort_values(by = 'name', inplace = True)
    return stations
