from hvec_importers.knmi.knmy import knmy


def test_parser():
    raw = knmy.get_hourly_data([209, 257], start=2017010101, end=2017010524, parse=False)
    _, _, _, df = knmy.parse_raw_weather_data(raw)

    assert df.shape == (288, 25)
