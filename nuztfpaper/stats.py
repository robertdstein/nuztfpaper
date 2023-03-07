import numpy as np
from scipy.stats import chi2, norm


def poisson_interval(x, sigma=1, cl=None):

    x = np.array(x)

    if cl is not None:
        onesided = 1.0 - 0.5 * (1.0 - cl)
    else:
        onesided = norm.cdf(sigma)

    lower = chi2.ppf(1.0 - onesided, 2 * x) / 2.0
    lower[np.isnan(lower)] = 0.0
    upper = chi2.ppf(onesided, 2 * (x + 1)) / 2.0

    return lower, upper
