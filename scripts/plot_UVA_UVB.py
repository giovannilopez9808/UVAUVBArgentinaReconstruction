from matplotlib import pyplot
from os.path import join
from numpy import ptp
from pandas import (
    DataFrame,
    read_csv,
)

filename = join(
    "../results",
    "AOD.csv",
)
tuv = read_csv(
    filename,
)
filename = join(
    "../data",
    "data.csv",
)
measurements = read_csv(
    filename,
)
pyplot.plot(
    tuv["UVA+UVB"],
    label="TUV"
)
pyplot.plot(
    measurements["UVA+UVB"],
    label="Mediciones",
)
pyplot.legend()
pyplot.savefig(
    "test.png"
)
