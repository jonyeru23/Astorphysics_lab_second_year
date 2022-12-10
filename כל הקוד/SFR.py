import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import astropy.units as u
import astropy.constants as consts

"""
hubbles law : v = H_0 * r
"""

H_0 = 2.20e-18 / u.s
H_0_err = 2.5e-20 / u.s

wave_lengths = {
    "u": 3000 * u.AA,
    "b": 4500 * u.AA,
    "v": 606 * u.AA,
    "i": 814 * u.AA
}

"""i have a bug with the units, fuck"""
def v(z):
    """
    :param z: dimensionless
    :param c: m / s
    :return: v [m/s]
    """
    # return consts.c * ((1 + z)**2 - 1) / ((1 + z)**2 + 1)
    return consts.c * z

def D(z):
    """
    :param z: dimensionless
    :param H_0: 1 / s
    :param v : m / s
    :return: Distance to galaxy in [m]
    """
    return v(z) / H_0


def D_err(z):
    """
    error of D, these are always together [m]
    """
    return abs((v(z) / H_0**2) * H_0_err)


def back_in_time(z):
    """
    :param z: dimensionless
    :param v: m / s
    :param c: m / s
    :param H_0: 1 / s
    :return: how much we see back in time [s]
    """
    return v(z) / (consts.c * H_0)


def back_in_time_err(z):
    """
    the error of back in time [s]
    """
    return abs(v(z) / (consts.c * H_0**2) * H_0_err)


def L_lambda(z, flux_lambda):
    """
    :param z: dimensionless
    :param flux_lambda: [erg / s / cm^2 / A]
    :return: luminosity_lambda of the galaxy in a specific wave length [erg / s / A]
    """
    return flux_lambda * 4 * np.pi * D(z).to(u.cm)**2 * (1 + z)**2


def L_lambda_err(z, flux_lambda, flux_lambda_err):
    """
    the error of L_lambda [erg / s / A]
    """
    A = 4 * np.pi * (1 + z)**2
    return np.sqrt((A * flux_lambda_err * D(z)**2)**2 + (2 * A * flux_lambda * D(z) * D_err(z))**2)


def SFR(L_lambda, wave_length):
    """
    equation 1
    :param L_lambda: [erg / s / A]
    :param wave_length: [A]
    :param c: m / s
    :return: [solarM / year]
    """
    return (1.4e-28 * wave_length**2 / consts.c.to(u.AA / u.s) * L_lambda).value * u.solMass / u.year


def SFR_err(L_lambda_err, wave_length):
    """
    :param L_lambda: [erg / s / A]
    :param L_lambda_err: [erg / s / A]
    :param wave_length: [A]
    :return: [solarM / year]
    """
    return (1.4e-28 * wave_length**2 / consts.c.to(u.AA / u.s) * L_lambda_err).value * u.solMass / u.year


def partial_universe_volume(z):
    """
    the integral we developde, 75 is arcseconds
    return units: Mpc**3
    """
    return (4 * np.pi**2 * 75**2 * D(z).to(10**6 * u.pc)**3) / (360 * 60**2 * 3)


def partial_universe_volume_err(z):
    """the error in the volume"""
    return abs((4 * np.pi**2 * 75**2 * D(z).to(10**6 * u.pc)**2 * D_err(z).to(10**6 * u.pc)) / (360 * 60**2))

def get_SFRD(df):
    """
    @pre the data is sorted by z
    @ get_SFR returns np.array
    return [solMass / year / Mpc**3]
    """
    z = df["z"]
    SFR_galaxies, SFR_galaxies_err = clean(*get_SFR(df))
    SFR_galaxies, SFR_galaxies_err = np.array(SFR_galaxies)*u.solMass / u.year, np.array(SFR_galaxies_err) *u.solMass / u.year

    accumultive = []
    accumulative_error = []
    for i in range(len(z)):
        #explenation in the word
        accumultive.append(sum(SFR_galaxies[:i]) / partial_universe_volume(z[i]))

        # derivation in the word
        accumulative_error.append(
            np.sqrt(sum((SFR_galaxies_err[:i]/partial_universe_volume(z[i]))**2) +
                    (sum(SFR_galaxies[:i]) * partial_universe_volume_err(z[i]) / partial_universe_volume(z[i])**2)**2)
        )
    return accumultive, accumulative_error


def convert_series(series, unit):
    for i in range(len(series)):
        series[i] = series[i].to(unit)
    return series


def clean(y, yerr):
    return [float(y_point.value) for y_point in y], [float(y_point.value) for y_point in yerr]


def get_SFR(df):
    """
    according to eq 1 we need the range to be: 1500 - 2800 A
    """
    SFR_points = []
    SFR_points_err = []
    z = np.array(df["z"])
    flux = get_flux(df)
    # print(flux)
    for i in range(len(df)):
        for filter_, wave_length in wave_lengths.items():
            if 1500 * u.AA < wave_length / (1 + z[i]) < 2800 * u.AA:
                SFR_points.append(SFR(L_lambda(z[i], flux[filter_]["value"][i]), wave_length))
                SFR_points_err.append(SFR_err(L_lambda_err(z=z[i], flux_lambda=flux[filter_]["value"][i],
                                                            flux_lambda_err=flux[filter_]["error"][i]), wave_length))
                break
            if filter_ == 'v':
                # need to take care of the ones with too much redshift
                SFR_points.append(0 * u.solMass / u.year)
                SFR_points_err.append(0 * u.solMass / u.year)
    return SFR_points, SFR_points_err


def get_flux(df):
    flux = {}
    for filter_ in wave_lengths.keys():
        flux[filter_] = {
            "value": np.array(df[f"flux {filter_}"]) * u.erg / u.s / u.cm**2 / u.AA,
            "error": np.array(df[f"dFlux {filter_}"]) * u.erg / u.s / u.cm**2 / u.AA
        }
    return flux


def phi_SFRD(z):
    """
    eq 15 from the long paper, this is the function of SFRdensity solMass / year / Mpc
    i want to see if it can fit our data.
    """
    return 0.015 * (1 + z)**2.7 / (1 + ((1 + z)/2.9)**5.6)

