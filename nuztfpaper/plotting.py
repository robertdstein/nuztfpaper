import logging
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy import constants as const
from astropy import units as u
from astropy.table import Table
from astropy.time import Time
from nuztf.ampel_api import ampel_api_name
from nuztf.parse_nu_gcn import find_gcn_no, parse_gcn_circular
from nuztf.plot import alert_to_pandas
from ztfquery.io import LOCALSOURCE

from nuztfpaper.style import (base_height, base_width, big_fontsize, cosmo,
                              dpi, plot_dir)

logger = logging.getLogger(__name__)

ALERT_MOD = 1.2


def plot_alerts(
    source_name: str,
    nu_name: list = None,
    source_coords: list = None,
    source_redshift: float = None,
    plot_mag: bool = True,
    plot_folder: str = plot_dir,
    extra_folder: str = None,
    from_cache: bool = False,
    cache_dir: str = os.path.join(LOCALSOURCE, "cache/"),
    expanded_labels: bool = True,
    ylim: tuple = None,
):
    plot_title = source_name

    # If there are no coordinates, try name resolve to get coordinates!

    if source_coords is None:

        # Try ampel to find ZTF
        res = ampel_api_name(source_name, with_history=False)[0]
        source_coords = [res["candidate"]["ra"], res["candidate"]["dec"]]
        logger.info(f"Found ZTF coordinates for source {source_name}")

    # Query IRSA, or load from cache

    try:
        os.makedirs(cache_dir)
    except OSError:
        pass

    cache_path = os.path.join(cache_dir, f'{source_name.replace(" ", "")}.csv')
    ul_cache_path = os.path.join(cache_dir, f'{source_name.replace(" ", "")}_ul.csv')

    if from_cache:
        logger.debug(f"Loading from {cache_path}")
        df = pd.read_csv(cache_path)
        logger.debug(f"Loading from {ul_cache_path}")
        ul = pd.read_csv(ul_cache_path)

    else:

        res = ampel_api_name(source_name, with_history=True)
        df, ul = alert_to_pandas(res)

        logger.debug(f"Saving to {cache_path}")
        df.to_csv(cache_path)
        df = pd.read_csv(cache_path)

        logger.debug(f"Saving to {ul_cache_path}")
        ul.to_csv(ul_cache_path)
        ul = pd.read_csv(ul_cache_path)

    data = Table.from_pandas(df)
    limdata = Table.from_pandas(ul)

    logger.info(f"There are a total of {len(data)} detections for {source_name}")

    # Start Figure

    plt.figure(figsize=(base_width * 1.15, base_height), dpi=dpi)

    if expanded_labels:

        ax2 = plt.subplot(111)

        ax = ax2.twiny()
    else:
        ax = plt.subplot(111)

    if source_redshift is not None:

        ax1b = ax.twinx()

        redshift = 1.0 + source_redshift

        if plot_mag:
            dist_mod = 5 * (
                np.log10(cosmo.luminosity_distance(z=(redshift - 1)).to(u.pc).value)
                - 1.0
            )
        else:
            conversion_factor = (
                4
                * np.pi
                * cosmo.luminosity_distance(z=(redshift - 1)).to(u.cm) ** 2.0
                / (redshift)
            )

    cmap = {"zg": "g", "zr": "r", "zi": "orange"}

    fid_map = {"zg": 1, "zr": 2, "zi": 3}

    wl = {
        "zg": 472.27,
        "zr": 633.96,
        "zi": 788.61,
    }

    markersize = 2.0

    # Plot each band (g/r/i)

    for fc in fid_map.keys():
        mask = data["fid"] == fid_map[fc]
        limmask = limdata["fid"] == fid_map[fc]

        mags = data["magpsf"][mask].data * u.ABmag

        magerrs = (data["sigmapsf"][mask] + data["magpsf"][mask]) * u.ABmag

        limmags = limdata["diffmaglim"][limmask] * u.ABmag

        if plot_mag:
            ax.errorbar(
                data["mjd"][mask],
                data["magpsf"][mask],
                yerr=data[mask]["sigmapsf"],
                marker="o",
                linestyle=" ",
                markersize=markersize,
                c=cmap[fc],
                label=f"{fc[-1]} ({wl[fc]:.0f} nm)",
            )

            ax.errorbar(
                limdata["mjd"][limmask],
                limdata["diffmaglim"][limmask],
                linestyle=" ",
                uplims=True,
                markersize=markersize,
                c=cmap[fc],
                marker="v",
                alpha=0.3,
            )

            if source_redshift is not None:
                ax1b.errorbar(
                    data["mjd"][mask],
                    data["magpsf"][mask] - dist_mod,
                    yerr=data["sigmapsf"][mask],
                    marker="o",
                    linestyle=" ",
                    markersize=markersize,
                    c=cmap[fc],
                    label=f"{fc[-1]} ({wl[fc]:.0f} nm)",
                )

        else:

            flux_j = mags.to(u.Jansky)

            f = (const.c / (wl[fc] * u.nm)).to("Hz")

            flux = (flux_j * f).to("erg cm-2 s-1")

            jerrs = magerrs.to(u.Jansky)
            ferrs = (jerrs * f).to("erg cm-2 s-1").value - flux.value

            uls = (limmags.to(u.Jansky) * f).to("erg cm-2 s-1")

            ax.errorbar(
                data["mjd"][mask],
                flux.to("erg cm-2 s-1").value,
                yerr=ferrs,
                marker="o",
                linestyle=" ",
                markersize=markersize,
                c=cmap[fc],
                label=f"{fc[-1]} ({wl[fc]:.0f} nm)",
            )

            ax.errorbar(
                limdata["mjd"][limmask],
                uls.to("erg cm-2 s-1").value,
                linestyle=" ",
                uplims=True,
                markersize=markersize,
                c=cmap[fc],
                marker="v",
                alpha=0.3,
            )

            if source_redshift is not None:
                l = flux * conversion_factor

                ax1b.errorbar(
                    data["mjd"][mask],
                    l.to("erg s-1"),
                    marker="o",
                    linestyle=" ",
                    markersize=markersize,
                    c=cmap[fc],
                    label=f"{fc[-1]} ({wl[fc]:.0f} nm)",
                )

    # You can force the y limits if you want

    if ylim is not None:
        ax.set_ylim(ylim)

    if plot_mag:
        ax.set_ylabel(r"Apparent magnitude [AB]", fontsize=big_fontsize * ALERT_MOD)

        ax.invert_yaxis()

        if source_redshift is not None:
            ax1b.set_ylabel(
                rf"Absolute magnitude [AB]", fontsize=big_fontsize * ALERT_MOD
            )

            y_min, y_max = ax.get_ylim()

            ax1b.invert_yaxis()

            ax1b.set_ylim(y_min - dist_mod, y_max - dist_mod)

    else:
        ax.set_ylabel(
            r"$\nu$F$_{\nu}$ [erg cm$^{-2}$ s$^{-1}$]",
            fontsize=big_fontsize * ALERT_MOD,
        )

        ax.set_yscale("log")

        if source_redshift is not None:
            ax1b.set_ylabel(
                r"$\nu$L$_{\nu}$ [erg s$^{-1}$]", fontsize=big_fontsize * ALERT_MOD
            )
            ax1b.set_yscale("log")

            y_min, y_max = ax.get_ylim()

            ax1b.set_ylim(
                y_min * conversion_factor.value, y_max * conversion_factor.value
            )

    ax.set_xlabel("Date (MJD)", fontsize=big_fontsize * ALERT_MOD)

    # Add neutrino

    if nu_name is None:
        nu_name = []

    if not isinstance(nu_name, list):
        nu_name = [nu_name]

    for j, nu in enumerate(nu_name):
        gcn_no = find_gcn_no(nu)
        gcn_info = parse_gcn_circular(gcn_no)

        ax.axvline(gcn_info["time"].mjd, linestyle=":", label=nu, color=f"C{j}")

    if expanded_labels:

        # Set up ISO dates

        lmjd, umjd = ax.get_xlim()

        lt = Time(lmjd, format="mjd")
        ut = Time(umjd, format="mjd")

        nt = Time.now()
        nt.format = "fits"

        mjds = []
        labs = []

        for year in range(2016, int(nt.value[:4]) + 1):
            for k, month in enumerate([1, 7]):

                t = Time(f"{year}-{month}-01T00:00:00.01", format="isot", scale="utc")
                t.format = "fits"
                t.out_subfmt = "date"

                if np.logical_and(t > lt, t < ut):
                    mjds.append(t.mjd)
                    labs.append(t.value)

        ax2.set_xticks(mjds)
        ax2.set_xticklabels(labels=labs, rotation=80)

        ax2.set_xlim(lmjd, umjd)

        ax.set_title(f'ZTF Lightcurve of {plot_title.replace("J", " J")}', y=1.4)

        ax2.tick_params(axis="both", which="major", labelsize=big_fontsize * ALERT_MOD)

    ax.tick_params(axis="both", which="major", labelsize=big_fontsize * ALERT_MOD)

    # plt.setp(ax2.get_yticklabels(), visible=True)
    # ax.yaxis.set_tick_params(visible=True)

    if source_redshift is not None:
        ax1b.tick_params(axis="both", which="major", labelsize=big_fontsize * ALERT_MOD)

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.22 + 0.2 * float(expanded_labels)),
        ncol=3 + len(nu_name),
        fancybox=True,
        fontsize=big_fontsize * ALERT_MOD,
    )

    filename = f"{source_name.replace(' ', '')}_lightcurve{['_flux', ''][plot_mag]}.png"

    output_path = os.path.join(plot_folder, f"{filename}")

    logger.info(f"Saving to {output_path}")

    plt.savefig(output_path, bbox_inches="tight", pad_inches=0.00)

    if extra_folder is not None:
        extra_path = os.path.join(extra_folder, f"{filename}")
        logger.info(f"Saving to {extra_path}")
        plt.savefig(extra_path, bbox_inches="tight", pad_inches=0.00)
