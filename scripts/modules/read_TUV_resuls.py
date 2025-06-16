from numpy import loadtxt
from os.path import join
from pandas import (
    DataFrame,
    concat,
)


class TUV_results:
    def __init__(self) -> None:
        pass

    def read(
        self,
        params: dict,
        filename: str
    ) -> DataFrame:
        """
        Read TUV results and put into a dataframe

        Inputs
        ---------------
        params -> dictionary with several information
            hour initial -> hour initial from results
            hour final   -> hour final from results
            path results -> direction from TUV results
        filename -> name of the file
        """
        # Get date from filename
        self._format_date(
            filename
        )
        # Get total hours
        hours = params["hour final"]-params["hour initial"]
        # All filename
        filename = join(
            params["path results"],
            filename
        )
        # Initialization for data
        self.data = DataFrame()
        for i in range(hours):
            # Skiprows for TUV format
            skiprows = 132+194*i
            # Read data
            data = loadtxt(
                filename,
                skiprows=skiprows,
                max_rows=61
            )
            # To DataFrame
            data = DataFrame(
                data
            )
            # Concat data
            self.data = concat([
                self.data,
                data
            ])
        # Drop duplicate results
        self.data = self.data.drop_duplicates()
        # Format datetime
        self.data[0] = self.data[0].apply(
            self._format_hour
        )
        # Columns data
        self.data.columns = [
            "Date",
            0,
            "UVA",
            "Erythemal"
        ]
        # Delete useless column for SZA
        self.data = self.data.drop(
            columns=0
        )

    def _format_hour(
        self,
        hour: float
    ) -> str:
        """
        Convert float hour to the hh:mm and date in yyyy-mm-dd
        """
        minute = round(hour % 1*60)
        minute = str(minute)
        minute = minute.zfill(2)
        hour = int(hour)
        hour = str(hour)
        hour = hour.zfill(2)
        hour = "{} {}:{}".format(
            self.date,
            hour,
            minute
        )
        return hour

    def _format_date(
        self,
        filename: str
    ) -> str:
        """
        Get date from filename
        """
        date = filename.split(".")[0]
        info = [
            date[i:i+2]
            for i in range(
                0,
                len(date),
                2
            )
        ]
        info[0] = f"20{info[0]}"
        self.date = "-".join(info)
