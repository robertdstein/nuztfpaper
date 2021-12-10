import os
import matplotlib.pyplot as plt
from astropy.table import Table
import pandas as pd
import numpy as np
from nuztfpaper.style import output_folder, big_fontsize, base_width, base_height, dpi, data_dir, plot_dir

all_lines = {
    "H": [
        (r"$\rm{H\alpha}$", 6562.8, 0),
        (r"$\rm{H\beta}$", 4861, 0),
        (r"$\rm{H\gamma}$", 4340, 0)
    ],
}


def load_spectrum(path):
    if ".fits" in path:
        raw = Table.read(os.path.join(data_dir, path), format='fits')
        data = raw.to_pandas()

        if "wl" not in data.columns:
            if "loglam" in data.columns:
                data.insert(1, "wl", 10. ** data["loglam"])

    else:
        data = pd.read_table(os.path.join(data_dir, path), names=["wl", "flux"], sep="\s+", comment='#')

    return data


def plot_spectrum(
        source_spectrum: tuple,
        comparison_spectrum: tuple = None,
        host_spectrum: tuple = None,
        plot_lines: list = None,
        smooth: int = 12
):

    xlim = (4000., 8000)

    source_path, source_redshift, source_label = source_spectrum

    data = load_spectrum(source_path)

    mask = data["flux"] > 0.
    data["flux"][~mask] = 0.00

    f = np.array(list(data["flux"]))
    sf = np.zeros(len(f) - smooth)
    swl = np.zeros(len(f) - smooth)

    for i in range(smooth):
        sf += np.array(list(f)[i:-smooth + i])
        swl += np.array(list(data["wl"])[i:-smooth + i])

    sf /= float(smooth)
    swl /= float(smooth)

    fig = plt.figure(figsize=(base_width, 1.2 * base_height), dpi=dpi)
    ax1 = plt.subplot(111)
    cols = ["C1", "C7", "k", "k"]

    if comparison_spectrum is not None:
        comp_path, comp_redshift, comp_label = comparison_spectrum
        comp = load_spectrum(comp_path)
        plt.plot(comp["wl"] / (comp_redshift + 1.), comp["flux"] / np.mean(comp["flux"]) - 0.5, color="C3",
                 label=comp_label)

    if host_spectrum is not None:
        host_path, host_redshift, host_label = host_spectrum
        host = load_spectrum(host_path)

        mask = host["flux"] > 0.
        host["flux"][~mask] = 0.00

        mask = np.logical_and(
            host["flux"] > xlim[0],
            host["flux"] < xlim[1]
        )
        host["flux"][~mask] = 0.00

        plt.plot(host["wl"] / (host_redshift + 1.), host["flux"] / np.mean(host["flux"]) + 1.5, color="C2",
                 label=host_label)

    plt.plot(data["wl"] / (source_redshift + 1.), data["flux"] / np.mean(data["flux"]) + 0.5, linewidth=0.5, color="C0",
             alpha=0.5)
    plt.plot(swl / (source_redshift + 1.), sf / np.mean(sf) + 0.5, color="C7", label=f"{source_label} (smoothed)")

    plt.legend()

    lines = []
    if plot_lines is not None:
        for line in plot_lines:
            lines += all_lines[line]

    for (label, wl, col) in lines:
        plt.axvline(wl, linestyle=":", color=cols[col])

        bbox = dict(boxstyle="round", fc="white", ec=cols[col])

        plt.annotate(label, (wl + 40., 0.8 + 0.9 * col), fontsize=big_fontsize, bbox=bbox, color=cols[col])

    plt.ylabel(r"$F_{\lambda}$ [Arbitrary Units]", fontsize=big_fontsize)
    ax1b = ax1.twiny()
    ax1.set_xlim(left=xlim[0], right=xlim[1])
    rslim = ax1.get_xlim()
    ax1b.set_xlim((rslim[0] * (1. + source_redshift), rslim[1] * (1. + source_redshift)))
    ax1.set_xlabel(r"Rest Wavelength ($\rm \AA$)", fontsize=big_fontsize)
    ax1b.set_xlabel(fr"Observed Wavelength (z={source_redshift:.3f})", fontsize=big_fontsize)
    ax1.tick_params(axis='both', which='major', labelsize=big_fontsize)
    ax1b.tick_params(axis='both', which='major', labelsize=big_fontsize)
    plt.tight_layout()

    filename = f"{source_label}_spectrum.pdf"

    output_path = os.path.join(output_folder, f"{filename}")
    plt.savefig(os.path.join(plot_dir, filename))
    plt.savefig(output_path)

    return fig
