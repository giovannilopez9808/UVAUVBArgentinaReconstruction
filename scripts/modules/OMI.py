from os.path import join
from pandas import (
    to_datetime,
    date_range,
    DataFrame,
    read_fwf,
)


class OMIData:
    def __init__(
        self,
    ) -> None:
        self._read()

    def _read(
        self,
    ) -> DataFrame:
        filename = "data.txt"
        filename = join(
            "../",
            "data",
            "OMI",
            filename
        )
        data = read_fwf(
            filename,
            skiprows=27,
        )
        data = self._format_date(
            data,
        )
        data = self.get_data(
            data,
        )
        self.data = DataFrame(
            0,
            index=date_range(
                "2005-01-01",
                "2025-12-31"
            ),
            columns=["Empty"]
        )
        self.data = self.data.join(
            data,
            how="left"
        )
        self.data = self.data.resample("d").mean()
        self.data = self.data.drop(
            columns="Empty",
            axis=1
        )

    def _format_date(
        self,
        data: DataFrame,
    ) -> DataFrame:
        data["Datetime"] = data["Datetime"].str[:8]
        data["Datetime"] = to_datetime(
            data["Datetime"],
            format='%Y%m%d',
        )
        data.index = data["Datetime"]
        data = data.drop(
            columns=["Datetime"],
            axis=1,
        )
        return data

    def get_data(
        self,
        data: DataFrame = None,
        year_i: int = 2005,
        year_f: int = 2025,
    ):
        if data is None:
            data = self.data.copy()
        data = data[data.index.year >= year_i]
        data = data[data.index.year <= year_f]
        return data
