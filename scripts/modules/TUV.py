from scipy.integrate import trapezoid
from os import system as terminal
from numpy import loadtxt
from os.path import join
from tqdm import tqdm
from pandas import (
    DataFrame,
    concat,
)


class TUV:
    def __init__(
        self,
    ) -> None:
        pass

    @staticmethod
    def _create_input_TUV_file(
        input_file: str,
        output_file: str,
        aod: float,
        ozone: float,
        year: int,
        month: int,
        day: int,
        hour: int,
    ) -> None:
        file = open(
            "./input_tuv.txt",
            "w"
        )
        text = " ".join([
            input_file,
            output_file,
            str(aod),
            str(ozone),
            str(year),
            str(month),
            str(day),
            str(hour),
        ])
        file.write(
            text,
        )
        file.close()

    def run(
        self,
        data: DataFrame,
    ) -> DataFrame:
        bar = tqdm(
            data.index,
        )
        results = DataFrame()
        for index in bar:
            self._create_input_TUV_file(
                "ROS",
                "result",
                data["AOD"][index],
                data["Ozone"][index],
                data["year"][index],
                data["month"][index],
                data["day"][index],
                data["hour"][index],
            )
            terminal(
                "./tuv"
            )
            data_model = self._read_TUV_output(
                "result.txt",
            )
            results = concat([
                results,
                data_model,
            ])
        terminal(
            "rm ../results/*.txt"
        )
        return results

    @staticmethod
    def _read_TUV_output(
        filename: str,
    ) -> float:
        filename = join(
            "..",
            "results",
            filename,
        )
        data = loadtxt(
            filename,
            skiprows=133,
            max_rows=61,
        )
        data = DataFrame(
            data,
        )
        data = data[[
            0,
            2,
            3,
        ]]
        data["UVA+UVB"] = data[[2, 3]].sum(
            axis=1,
        )
        data = data.drop(
            columns=[
                2,
                3,
            ],
        )
        data.columns = [
            "Hours",
            "UVA+UVB",
        ]
        return data


class TUVSearchAOD:
    def __init__(
        self,
    ) -> None:
        self.params = dict(
            AOD_initial=0.001,
            AOD_limite=5,
            RD_limite=10,
            RD_delta=1,
        )

    @staticmethod
    def _create_input_TUV_file(
        input_file: str,
        output_file: str,
        aod: float,
        ozone: float,
        year: int,
        month: int,
        day: int,
        hour: int,
    ) -> None:
        file = open(
            "./input_tuv.txt",
            "w"
        )
        text = " ".join([
            input_file,
            output_file,
            str(aod),
            str(ozone),
            str(year),
            str(month),
            str(day),
            str(hour),
        ])
        file.write(
            text,
        )
        file.close()

    def run(
        self,
        data: DataFrame,
    ) -> DataFrame:
        bar = tqdm(
            data.index,
        )
        results = DataFrame(
            columns=[
                "UVA+UVB",
                "AOD",
                "RD",
            ]
        )
        for index in bar:
            self._initialize_aod(
                self.params["AOD_initial"],
                self.params["AOD_limite"],
            )
            stop = False
            aod = self._get_new_aod(
                self.aod_i,
                self.aod_lim,
            )
            iter = 0
            while not (stop) and iter < 10:
                self._create_input_TUV_file(
                    "ROS",
                    "result",
                    aod,
                    data["Ozone"][index],
                    data["year"][index],
                    data["month"][index],
                    data["day"][index],
                    data["hour"][index],
                )
                terminal(
                    "./tuv"
                )
                data_model = self._read_TUV_output(
                    "result.txt",
                    data["minute"][index],
                )
                measurement = data["UVA+UVB"][index]
                stop, RD = self._get_RD_decision(
                    data_model,
                    measurement,
                )
                bar.set_postfix(
                    AOD=aod,
                    RD=RD,
                )
                if not stop:
                    aod = self._aod_binary_search(
                        aod,
                        RD,
                    )
                    rd_diff = abs(RD-self.params["RD_limite"])
                    is_upper_than_limit = self.aod_lim >= aod
                    is_lower_than_delta = rd_diff < self.params["RD_delta"]
                    if is_upper_than_limit and is_lower_than_delta:
                        stop = True
                    iter += 1
            results.loc[index] = [
                data_model,
                aod,
                RD,
            ]
        terminal(
            "rm ../results/*.txt"
        )
        return results

    def _initialize_aod(
        self,
        aod_i: float,
        aod_lim: float,
    ) -> None:
        """
        Funcion que inicializa el limite inferior y superior del AOD
        """
        self.aod_i = aod_i
        self.aod_lim = aod_lim

    def _get_new_aod(
        self,
        aod_i: float,
        aod_f: float,
    ) -> float:
        return round((aod_i+aod_f)/2, 3)

    def _get_RD_decision(
        self,
        model: float,
        measurement: float,
    ) -> tuple:
        """
        Funcion que calcula la RD entre el modelo y la medicion
        """
        stop = False
        RD = round(100*(model-measurement)/measurement, 3)
        if self._is_the_right_RD(RD):
            stop = True
        return stop, RD

    def _aod_binary_search(
        self,
        aod: float,
        RD: float,
    ) -> float:
        """
        Función que calcula el AOD que se introducira en el modelo SMARTS
        este emplea una busqueda binaria para que sea más eficiente
        """
        if self._is_the_right_RD(RD):
            self.aod_i = aod
        elif RD > self.params["RD_limite"]+self.params["RD_delta"]:
            self.aod_i = aod
        else:
            self.aod_lim = aod
        aod = self._get_new_aod(
            self.aod_lim,
            self.aod_i,
        )
        return aod

    def _is_the_right_RD(
        self,
        RD: float,
    ) -> bool:
        lim_i = self.params["RD_limite"]-self.params["RD_delta"]
        lim_f = self.params["RD_limite"]+self.params["RD_delta"]
        return lim_i < RD < lim_f

    @staticmethod
    def _read_TUV_output(
        filename: str,
        minute: int,
    ) -> float:
        filename = join(
            "..",
            "results",
            filename,
        )
        data = loadtxt(
            filename,
            skiprows=134,
            max_rows=59,
        )
        data = data[
            minute+1
        ]
        data = data[3:5]
        data = sum(
            data,
        )
        return data
