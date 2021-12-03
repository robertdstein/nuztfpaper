import pandas as pd
import numpy as np
from nuztfpaper.alerts import obs, base_file

candidates = None

maxb = []
maxr = []
base_class = []
sub_class = []

for index, row in obs.iterrows():
    name = row["Event"]

    new = pd.read_excel(base_file, sheet_name=name, skiprows=range(6), header=0)
    if len(new) > 2:

        new["neutrino"] = name

        if candidates is None:
            candidates = new
        else:
            candidates = candidates.append(new, ignore_index=True)

        for _, crow in new.iterrows():

            maxb.append(float(crow['max brightness'].split(" ")[0]))

            if isinstance(crow['max range'], str):
                r = float(crow['max range'].split(" ")[0])
            else:
                r = 0.0

            maxr.append(r)

            if crow['Classification'] in ['AGN\n', 'AGN?', 'AGN']:
                base_class.append("AGN")
                sub_class.append("AGN Flare")

            elif crow['Classification'] in ['AGN Variability', 'AGN Variability?']:
                base_class.append("AGN")
                sub_class.append("AGN Variability")

            elif crow['Classification'] in ['AGN Variability (FP)']:
                base_class.append("AGN")
                sub_class.append("AGN Variability")

            elif str(crow['Classification']) in ["CV", "Star?", "CV???", "Star"]:
                base_class.append("Star")
                sub_class.append("Star")

            elif crow['Classification'] in ["???", np.nan, "?", "???\n\n"]:
                base_class.append("Unclassified")
                sub_class.append("Unclassified")

            elif crow['Classification'] in ["artifact?", "Artifact\n"]:
                base_class.append("Artifact")
                sub_class.append("Artifact")

            elif "Ia" in crow['Classification']:
                base_class.append("Transient")
                sub_class.append("SN Ia")

            elif "SN" in crow['Classification']:
                base_class.append("Transient")
                sub_class.append(crow['Classification'])

            elif crow['Classification'] in ["II/IIb"]:
                base_class.append("Transient")
                sub_class.append("SN II/IIb")

            elif crow['Classification'] in ["TDE", "Dwarf Nova"]:
                base_class.append("Transient")
                sub_class.append(crow['Classification'])

            else:
                base_class.append(crow['Classification'])
                sub_class.append(crow['Classification'])

candidates["max_brightness"] = maxb
candidates["max_range"] = maxr
candidates["base_class"] = base_class
candidates["sub_class"] = sub_class
