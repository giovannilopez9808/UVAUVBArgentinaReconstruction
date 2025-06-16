from os.path import join
from pandas import (
    to_datetime,
    DataFrame,
    Timestamp,
    read_csv,
)


class UVAUVBDataset:
    def __init__(
        self,
    ) -> None:
        data = self._read()
        data = self._format_data(
            data,
        )
        self.data = self._delete_useless_columns(
            data,
        )

    def _read(
        self,
    ) -> DataFrame:
        filename = join(
            "..",
            "data",
            "data.csv",
        )
        data = read_csv(
            filename,
            parse_dates=True,
            index_col=0,
        )
        return data

    @staticmethod
    def _delete_useless_columns(
        data: DataFrame,
    ) -> DataFrame:
        data = data.drop(
            columns=[
                "datetime",
                "date",
                "Hour",
            ]
        )
        return data

    def _format_data(
        self,
        data: DataFrame,
    ) -> DataFrame:
        data["date"] = data.index
        data["datetime"] = data[["date", "Hour"]].apply(
            lambda values:
            self._union_date_and_time(
                values["date"],
                values["Hour"],
            ),
            axis=1,
        )
        data["year"] = data["datetime"].apply(
            lambda datetime:
            datetime.year
        )
        data["month"] = data["datetime"].apply(
            lambda datetime:
            datetime.month
        )
        data["day"] = data["datetime"].apply(
            lambda datetime:
            datetime.day
        )
        data["hour"] = data["datetime"].apply(
            lambda datetime:
            datetime.hour
        )
        data["minute"] = data["datetime"].apply(
            lambda datetime:
            datetime.minute
        )
        return data

    @staticmethod
    def _union_date_and_time(
        date: Timestamp,
        time: str,
    ) -> Timestamp:
        date = date.strftime(
            "%Y-%m-%d"
        )
        datetime = " ".join([
            date,
            time,
        ])
        datetime = to_datetime(
            datetime,
        )
        return datetime

    def get_data(
        self,
    ) -> DataFrame:
        return self.data
