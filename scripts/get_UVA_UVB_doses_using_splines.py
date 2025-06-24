from scipy.interpolate import CubicSpline
from scipy.integrate import trapezoid
from matplotlib import pyplot
from pandas import read_csv
from numpy import linspace


def get_time_to_hour_decimal(
    time: str,
) -> float:
    hour, minute = time.split(":")
    hour = int(hour)
    minute = int(minute)
    time = hour+minute/60
    return time


tuv = read_csv(
    "../results/AOD.csv",
    parse_dates=True,
    index_col=0,
)
measurements = read_csv(
    "../data/data.csv",
    parse_dates=True,
    index_col=0,
)
measurements["Hours"] = measurements["Hour"].apply(
    get_time_to_hour_decimal
)
tuv["Hours"] = tuv["hour"]+tuv["minute"]/60
dates = sorted(
    set(
        tuv.index.date
    )
)
for date in dates:
    daily_measurement = measurements[
        measurements.index.date == date
    ]
    daily_tuv = tuv[
        tuv.index.date == date
    ]
    model = CubicSpline(
        daily_tuv["Hours"],
        daily_tuv["UVA+UVB"],
    )
    x = linspace(
        daily_tuv.iloc[0]["Hours"],
        daily_tuv.iloc[-1]["Hours"],
        60,
    )
    reconstruction = model(
        x
    )
    print(
        date,
        round(trapezoid(reconstruction, x*3600))
    )
    # pyplot.scatter(
    # daily_measurement["Hours"],
    # daily_measurement["UVA+UVB"],
    # label="Measurements",
    # )
    # pyplot.scatter(
    # daily_tuv["Hours"],
    # daily_tuv["UVA+UVB"],
    # label="TUV 10$\pm$1",
    # )
    pyplot.plot(
        x,
        reconstruction,
        # label="Spline cubico",
        label="TUV",
        # color="#000000",
        # ls="--",
    )
    pyplot.scatter(
        daily_measurement["Hours"],
        daily_measurement["UVA+UVB"],
        label="Mediciones",
        color="#000000",
        marker="o",
        # ls="--",
    )
    # pyplot.plot(
    # daily_tuv["Hours"],
    # daily_tuv["UVA+UVB"],
    # label="Measurements",
    # )
    pyplot.xlabel(
        "Hora local"
    )
    pyplot.ylabel(
        "Irradiancia UVA+UVB (W/m$^2$)"
    )
    pyplot.legend()
    pyplot.show()
