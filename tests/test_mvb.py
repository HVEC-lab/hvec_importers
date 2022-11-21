import pytest as pyt
from hvec_importers.mvb import mvb


def test_download():
    token = mvb.login(username = 'hessel@hesselvoortman.nl', password = 'F3d!uvUJW7ER5vY')
    data = mvb.get_data(token, stationparameter = 'NPTWS5', tstart = '2021-01-01', tstop = '2022-12-31')
    assert len(data) > 0