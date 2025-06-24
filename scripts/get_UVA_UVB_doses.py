from scipy.integrate import trapezoid
from modules.OMI import OMIData
from matplotlib import pyplot
from modules.TUV import TUV
from os.path import join
from pandas import (
    to_datetime,
    DataFrame,
    read_csv,
    merge,
)


def get_hour_from_hour_decimal(
    hour_decimal: float,
) -> int:
    hour = hour_decimal//1
    hour = int(hour)
    return hour


def get_minure_from_hour_decimal(
    hour_decimal: float,
) -> int:
    minute = round(
        hour_decimal % 1 * 60
    )
    return minute


def format_hour(
    data: DataFrame,
    column: str,
) -> DataFrame:
    data[column] = data[column].apply(
        lambda hour_decimal:
        "{}:{}".format(
            get_hour_from_hour_decimal(
                hour_decimal,
            ),
            get_minure_from_hour_decimal(
                hour_decimal,
            )
        )
    )
    return data


def get_time_to_hour_decimal(
    time: str,
) -> float:
    hour, minute = time.split(":")
    hour = int(hour)
    minute = int(minute)
    time = hour+minute/60
    return time


dataset = read_csv(
    "../data/data.csv",
    parse_dates=True,
    index_col=0,
)
dataset["Hours"] = dataset["Hour"].apply(
    get_time_to_hour_decimal
)
filename = join(
    "..",
    "results",
    "AOD.csv",
)
data = read_csv(
    filename,
)
data = data[[
    "date",
    "hour",
    "minute",
    "AOD",
]]
data["date"] = to_datetime(
    data["date"],
)
data["hour_decimal"] = data["hour"] + data["minute"]/60
data = data.sort_values(
    by=[
        "date",
        "hour_decimal",
    ],
)
first_ocurrence = data.groupby(
    "date",
).first()
last_ocurrence = data.groupby(
    "date",
).last()
print(data)
exit(1)
mean = data.groupby(
    "date"
).max()
data = DataFrame()
data.index = mean.index
data["hour_initial"] = first_ocurrence["hour_decimal"]
data["hour_final"] = last_ocurrence["hour_decimal"]
data["AOD"] = mean["AOD"]
data["first_hour"] = data["hour_initial"].apply(
    get_hour_from_hour_decimal
)
data["first_minute"] = data["hour_initial"].apply(
    get_minure_from_hour_decimal
)
data["last_hour"] = data["hour_final"].apply(
    get_hour_from_hour_decimal
)
data["last_minute"] = data["hour_final"].apply(
    get_minure_from_hour_decimal
)
data["year"] = data.index.year
data["month"] = data.index.month
data["day"] = data.index.day
data = data.reset_index()
omi = OMIData()
omi = omi.get_data()
omi = omi[[
    "Ozone",
]]
omi = omi.reset_index()
omi = omi.rename(
    columns={
        "index": "date"
    }
)
omi["date"] = to_datetime(
    omi["date"],
)
data = merge(
    data,
    omi,
    on=[
        "date"
    ],
)
model = TUV()
for index in data.index:
    daily_data = data.loc[index]
    temp_data = DataFrame()
    hours = range(
        daily_data["first_hour"],
        daily_data["last_hour"]+1,
    )
    temp_data["hour"] = hours
    temp_data["AOD"] = daily_data["AOD"]
    temp_data["Ozone"] = daily_data["Ozone"]
    temp_data["year"] = daily_data["year"]
    temp_data["month"] = daily_data["month"]
    temp_data["day"] = daily_data["day"]
    results = model.run(
        temp_data,
    )
    results = results[
        (
            results["Hours"] >= daily_data["hour_initial"]
        ) &
        (
            results["Hours"] <= daily_data["hour_final"]
        )
    ]
    daily_dataset = dataset[
        dataset.index.date == daily_data["date"].date()
    ]
    print(daily_data)
    pyplot.plot(
        results["Hours"],
        results["UVA+UVB"],
    )
    pyplot.plot(
        daily_dataset["Hours"],
        daily_dataset["UVA+UVB"],
    )
    pyplot.show()
    doses = trapezoid(
        results["UVA+UVB"],
        results["Hours"]*3600,
    )
    doses = round(
        doses,
    )
    data.loc[index, "Doses"] = doses
data = format_hour(
    data,
    "hour_initial",
)
data = format_hour(
    data,
    "hour_final",
)
data = data[[
    "date",
    "hour_initial",
    "hour_final",
    "Doses",
]]
print(data)
