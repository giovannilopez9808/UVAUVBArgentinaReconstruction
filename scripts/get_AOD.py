from modules.Dataset import UVAUVBDataset
from modules.TUV import TUVSearchAOD
from modules.OMI import OMIData
from os.path import join

omi = OMIData()
omi = omi.get_data()
omi = omi[[
    "Ozone",
]]
dataset = UVAUVBDataset()
dataset = dataset.get_data()
dataset = dataset.join(
    omi,
)
dataset = dataset.reset_index()
model = TUVSearchAOD()
results = model.run(
    dataset,
)
dataset = dataset.drop(
    columns=[
        "UVA+UVB",
    ]
)
dataset = dataset.join(
    results,
)
dataset = dataset[[
    "index",
    "hour",
    "minute",
    "UVA+UVB",
    "AOD",
]]
filename = join(
    "..",
    "results",
    "AOD.csv",
)
dataset.to_csv(
    filename,
    index=False,
)
