import dateutil.rrule
import itertools
import pytz


def date_series(start, end, freq=dateutil.rrule.MONTHLY):
    """return a list of start and end date over the timespan start[->end following the frequency rule"""
    def pairwise(it):
        """return all sequential pairs"""
        # loop over the iterator twice.
        # tee it so we don't consume it twice
        it0, it1 = itertools.tee(it)
        i0 = itertools.islice(it0, None)
        i1 = itertools.islice(it1, 1, None)
        # merge to a list of pairs
        return zip(i0, i1)

    # go over the rrule, also include the end, return consequitive pairs
    result = list(
        pairwise(
            list(
                dateutil.rrule.rrule(dtstart=start, until=end, freq=freq)
            ) + [end]
        )
    )
    # remove last one if empty (first of month until first of month)
    if len(result) > 1 and result[-1][0] == result[-1][1]:
        # remove it
        del result[-1]
    return result


def create_date_strings(start_date, end_date):
    """
    Parse dates to strings
    """
    start_date_str = pytz.UTC.localize(start_date).isoformat(timespec="milliseconds")
    end_date_str = pytz.UTC.localize(end_date).isoformat(timespec="milliseconds")
    return start_date_str, end_date_str


def create_data_request(location, start_date, end_date):
    """
    Prepare data request for specified period.
    """
    start_date_str, end_date_str = create_date_strings(start_date, end_date)

    request = {
        "AquoPlusWaarnemingMetadata": {
            "AquoMetadata": {
                "Eenheid": {"Code": location["Eenheid.Code"]},
                "Grootheid": {"Code": location["Grootheid.Code"]},
                "Hoedanigheid": {"Code": location["Hoedanigheid.Code"]},
            }
        },
        "Locatie": {
            "X": location["X"],
            "Y": location["Y"],
            # assert code is used as index
            # TODO: use  a numpy  compatible json encoder in requests
            "Code": location.get("Code", location.name),
        },
        "Periode": {"Begindatumtijd": start_date_str, "Einddatumtijd": end_date_str},
    }

    return request


def create_availability_request(location, start_date, end_date):
    """
    Prepare request to obtain data availability for given period
    """
    start_date_str, end_date_str = create_date_strings(start_date, end_date)

    request = {
        "AquoMetadataLijst": [{
            "Compartiment": {"Code": location["Compartiment.Code"]},
            "Eenheid": {"Code": location["Eenheid.Code"]}
            }],
        "LocatieLijst": [{
            "X": location["X"],
            "Y": location["Y"],
            "Code": location["Code"]
            }],
      "Periode": {
        "Begindatumtijd": start_date_str,
        "Einddatumtijd": end_date_str
      }
    }

    return request
