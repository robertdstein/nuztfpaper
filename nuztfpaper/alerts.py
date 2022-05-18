import os
import pandas as pd
import numpy as np
from nuztfpaper.style import data_dir
from nuztfpaper.latency import get_latency

base_file = os.path.join(data_dir, "neutrino_too_followup.xlsx")

obs = pd.read_excel(base_file, sheet_name="OVERVIEW_FU", skiprows=[0, 1, 2])

obs = obs[~np.isnan(obs["RA"])]

latency_key = "Latency (hours)"
latencies = []

for index, row in obs.iterrows():
    name = row["Event"]
    res = get_latency(name)
    if res is not None:
        latencies.append(get_latency(name).value)
    else:
        latencies.append(np.nan)

obs[latency_key] = latencies

non = pd.read_excel(base_file, sheet_name="OVERVIEW_NOT_FU", skiprows=[0, 1], usecols=range(11))

relabels = {
    "Alert retraction": "Alert Retraction",
    "Proximity to sun": "Proximity to Sun",
    "Separation from galactic plane": "Separation from Galactic Plane",
    "Poor Signalness and Localization": "Poor Signalness and Localisation"
}

for key, new in relabels.items():
    mask = non["Rejection reason"] == key
    non["Rejection reason"][mask] = new

tot_nu_area = np.sum(obs["Observed area (corrected for chip gaps)"])

joint = pd.concat([non, obs], axis=0).sort_values(by=['Event'])
