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


def load_spectrum(
        path: str,
        smooth: int = 1
):
    if ".fits" in path:
        raw = Table.read(os.path.join(data_dir, path), format='fits')
        data = raw.to_pandas()

        if "wl" not in data.columns:
            if "loglam" in data.columns:
                data.insert(1, "wl", 10. ** data["loglam"])

    else:
        data = pd.read_table(os.path.join(data_dir, path), sep="\s+", comment='#')

        if len(data.columns) == 2:
            data.columns = np.array(["wl", "flux"])

    if smooth > 1:
        sx = data["wl"][0::smooth].to_numpy()
        y = data["flux"]

        sy = np.zeros_like(sx)

        for i in range(len(sx)):
            sy[i] = np.sum(y[i * smooth:((i + 1) * smooth)])

        sy = sy/float(smooth)

        return pd.DataFrame({"wl": sx, "flux": sy})

    else:
        return data


def plot_spectrum(
        source_spectrum: tuple,
        comparison_spectrum: tuple = None,
        host_spectrum: tuple = None,
        plot_lines: list = None,
        smooth: int = 6,
        host_smooth: int = 8
):

    xlim = (4000., 8000.)

    source_path, source_redshift, source_label = source_spectrum

    data = load_spectrum(source_path)

    data_smoothed = load_spectrum(source_path, smooth=smooth)

    mask = data["flux"] > 0.
    data["flux"][~mask] = 0.00

    y_point = min(data_smoothed["flux"])

    scale = np.median(data["flux"])

    # if host_spectrum is not None:
    #     fig = plt.figure(figsize=(base_width*2.1, 1.2 * base_height), dpi=dpi)
    #
    # else:
    fig = plt.figure(figsize=(base_width, 1.2 * base_height), dpi=dpi)

    ax1 = plt.subplot(111)
    cols = ["C1", "C7", "k", "k"]

    if host_spectrum is not None:
        host_path, host_redshift, host_label = host_spectrum
        host = load_spectrum(host_path)

        mask = np.logical_and(
            host["flux"] > 0.,
            host["flux"] != np.nan
        )
        host["flux"][~mask] = 0.00

        y_offset = max(data_smoothed["flux"])/scale

        hscale = np.median(host["flux"]) - 0.2

        plt.plot(host["wl"] / (host_redshift + 1.), host["flux"]/hscale + y_offset, color="C2",
                 alpha=0.5)

        host_smoothed = load_spectrum(host_path, smooth=host_smooth)

        plt.plot(host_smoothed["wl"] / (source_redshift + 1.),
                 host_smoothed["flux"]/hscale + y_offset,
                 color="C5",
                 label=f"{host_label} (smoothed)"
                 )

    plt.plot(data["wl"] / (source_redshift + 1.), data["flux"]/scale + 1.0, linewidth=0.5, color="C0",
             alpha=0.5)
    plt.plot(data_smoothed["wl"] / (source_redshift + 1.), data_smoothed["flux"]/scale + 1.0, color="C7", label=f"{source_label} (smoothed)")

    if comparison_spectrum is not None:
        comp_path, comp_redshift, comp_label = comparison_spectrum

        comp = load_spectrum(comp_path)
        y = comp["flux"] / np.median(comp["flux"]) - 0.5

        plt.plot(comp["wl"] / (comp_redshift + 1.), y, color="C3",
                 label=comp_label)

        y_point = min(y_point, min(y))

    plt.legend(framealpha=0.8)

    lines = []
    if plot_lines is not None:
        for line in plot_lines:
            lines += all_lines[line]

    for (label, wl, col) in lines:
        plt.axvline(wl, linestyle=":", color=cols[col], zorder=-4)

        bbox = dict(boxstyle="round", fc="white", ec=cols[col])

        plt.annotate(label, (wl + 40., y_point + 0.9 * col), fontsize=big_fontsize, bbox=bbox, color=cols[col])

    plt.ylabel(r"$F_{\lambda}$ [Arbitrary Units]", fontsize=big_fontsize)
    ax1b = ax1.twiny()
    ax1.set_xlim(left=xlim[0], right=xlim[1])
    rslim = ax1.get_xlim()
    ax1b.set_xlim((rslim[0] * (1. + source_redshift), rslim[1] * (1. + source_redshift)))
    ax1.set_xlabel(r"Rest Wavelength [$\rm \AA$]", fontsize=big_fontsize)
    ax1b.set_xlabel(fr"Observed Wavelength (z={source_redshift:.3f})", fontsize=big_fontsize)
    ax1.tick_params(axis='both', which='major', labelsize=big_fontsize)
    ax1b.tick_params(axis='both', which='major', labelsize=big_fontsize)
    plt.tight_layout()

    filename = f"{source_label}_spectrum.pdf"

    output_path = os.path.join(output_folder, f"{filename}")
    plt.savefig(os.path.join(plot_dir, filename), bbox_inches="tight", pad_inches=0.00)
    plt.savefig(output_path, bbox_inches="tight", pad_inches=0.00)

    return fig
