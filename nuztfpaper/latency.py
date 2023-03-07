import logging
import os
import pickle

import astropy.time
from astropy import units as u
from nuztf.neutrino_scanner import NeutrinoScanner

from nuztfpaper.alerts import data_dir

logger = logging.getLogger(__name__)

latency_cache_path = os.path.join(data_dir, "latency_cache.pkl")


def calculate_latency(nu_name: str, first_det_window_days=3):
    try:
        nu = NeutrinoScanner(nu_name)
        nu.calculate_overlap_with_observations(
            first_det_window_days=first_det_window_days
        )
        return (nu.first_obs - nu.t_min).to(u.hr)
    except ValueError:
        return None


def get_latency(nu_name):
    cache = None

    if os.path.isfile(latency_cache_path):
        with open(latency_cache_path, "rb") as f:
            cache = pickle.load(f)
            if nu_name in cache.keys():
                return cache[nu_name]

    logger.info(
        f"No cached latency value for {nu_name}."
        f"Will calculate then save value in cache."
    )

    res = calculate_latency(nu_name)

    new_entry = {nu_name: res}

    if cache is None:
        new_cache = new_entry
    else:
        new_cache = dict(cache, **new_entry)

    with open(latency_cache_path, "wb") as f:
        pickle.dump(new_cache, f)

    return res
