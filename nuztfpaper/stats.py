from scipy.stats import norm, chi2
import numpy as np


def poisson_interval(x, sigma=1, cl=None):

    x = np.array(x)

    if cl is not None:
        onesided = 1. - 0.5 * (1. - cl)
    else:
        onesided = norm.cdf(sigma)

    lower = chi2.ppf(1. - onesided, 2 * x) / 2.
    lower[np.isnan(lower)] = 0.
    upper = chi2.ppf(onesided, 2 * (x + 1)) / 2.

    return lower, upper
