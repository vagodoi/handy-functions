'''
        Simple functions that may assist in the analysis of meteorological and
        oceanographic data.

    - calc_dist: Calculate the distance between two points on the Earth's surface.
    - find_nearest_lonlat: Find the indexes of the nearest longitude and latitude
                           values to the coordinates of a given site in longitude
                           and latitude arrays.
    - central_date: Find the central date between the two given dates.
    - calc_mag_dec: Calculate magnetic declination.
    - uv2intdir and intdir2uv: Convert zonal and meridional velocity components
                               into velocity speed and direction and vice versa,
                               respectively.
    - dirstats: Calculate basic statistics of directional data.

    Author: Victor A. Godoi, May/2021.
'''

import numpy as np

def calc_dist(lon1, lat1, lon2, lat2):
    '''
    Calculate the distance between two sites on the Earth's surface.
    Input:
        lon1 (float): Longitude of site 1 (decimal degrees).
        lat1 (float): Latitude of site 1 (decimal degrees).
        lon2 (float): Longitude of site 2 (decimal degrees).
        lat2 (float): Latitude of site 2 (decimal degrees).
    Output:
        dist (float): Distance between the two sites (in metres).
    '''
    from geopy import distance
    dist = distance.distance((lat1, lon1), (lat2, lon2)).m
    return dist


def find_nearest_lonlat(lon, lat, lon_arr, lat_arr):
    '''
    Find the indexes of the nearest longitude and latitude values to the
    coordinates of a given site in longitude and latitude arrays. If the
    nearest value to either "lon" or "lat" appears in two or more indexes,
    only the first occurrence is considered.
    Input:
        lon (float): Site's longitude coordinate (the one to look for).
        lat (float): Site's latitude coordinate (the one to look for).
        lon_arr (numpy array): Longitude array where to look for the nearest
                               longitude coordinate to 'lon'.
        lat_arr (numpy array): Latitude array where to look for the nearest
                               latitude coordinate to 'lat'.
    Output:
        lon_nearest, lat_nearest (tuple): Indexes of the nearest longitude and
                                          latitude values to 'lon' and 'lat',
                                          respectively, in 'lon_arr' and 'lat_arr'.
    '''
    lon_nearest = np.where(lon_arr==min(lon_arr, key=lambda x:abs(x-lon)))[0][0]
    lat_nearest = np.where(lat_arr==min(lat_arr, key=lambda x:abs(x-lat)))[0][0]
    return lon_nearest, lat_nearest


def central_date(iniDate, finDate):
    '''
    Find the central date between the two given dates. This function is convenient
    when estimating magnetic declination for a period longer than a day, for example,
    which requires the central date of the period as input.
    Input:
        iniDate (datetime object): Initial date - format: dt.datetime(YYYY, M, D, h, m, s).
        finDate (datetime object): Final date - format: dt.datetime(YYYY, M, D, h, m, s).
    Output:
        centralDate (datetime object): Central date.
    '''
    import datetime as dt
    halfPeriod = (finDate - iniDate) / 2
    centralDate = iniDate + halfPeriod
    return centralDate


def calc_mag_dec(lon, lat, date, altitude=0):
    '''
    Calculate magnetic declination. This function uses the British
    Geological Survey (BGS) API web service for calculation. The web
    service makes the World Magnetic Model (WMM), the International
    Geomagnetic Reference Field (IGRF), and the BGS Global Geomagnetic
    Model (BGGM) available as a web service. The IGRF and WMM have no
    restrictions on use, while the BGGM is only available to subscribers.
    The API provides options to select which model and revision to use.
    Values of the magnetic field at any point around the world can be
    retrieved for a given date. For more info, see:
    http://geomag.bgs.ac.uk/web_service/GMModels/help/parameters
    Input:
        lon (float): Site's longitude (decimal degrees).
        lat (float): Site's latitude (decimal degrees).
        date (string): Date in the format 'YYYY-MM-DD'.
        altitude (float): Altitude (decimal km).
    Output:
        declination (float): Magnetic declination.
    '''
    from magnetic_field_calculator import MagneticFieldCalculator
    result = MagneticFieldCalculator().calculate(latitude=lat, longitude=lon,
                                                 altitude=altitude, date=date
                                                 )
    declination = result['field-value']['declination']
    return declination


def uv2intdir(u, v, data_type, mag_decl=0.0):
    """
    Convert zonal and meridional velocity components into speed and direction.
    If you do not wish to apply the magnetic declination correction, do not
    assign any values to "mag_decl".
    Input:
        u (float or pandas.core.series.Series): Zonal velocity component.
        v (float or pandas.core.series.Series): Meridional velocity component.
        data_type (string): Specify the data type. Choose among "current",
                            "wind", and "wave".
        mag_decl (float): Magnetic declination.
    Output:
        spd (float or pandas.core.series.Series): Velocity speed.
        direc (float or pandas.core.series.Series): Velocity direction.
    """
    spd = np.sqrt(u**2 + v**2)
    if data_type.lower() == "current":
        direc = np.mod(90 - (np.rad2deg(np.arctan2(v, u)) - mag_decl), 360)
    else:
        direc = np.mod(270 - (np.rad2deg(np.arctan2(v, u)) - mag_decl), 360)
    return spd, direc


def intdir2uv(spd, direc, data_type):
    '''
    Convert velocity speed and direction into zonal and meridional velocity
    components.
    Input:
        spd (float): Velocity speed.
        direc (float): Velocity direction.
        data_type (string): Specify the data type. Choose among "current",
                            "wind", and "wave".
    Ouput:
        u, v (tuple): Zonal and meridional velocity components, respectively.
    '''
    ang = np.deg2rad(direc)
    if data_type.lower() == "current":
        u = spd * np.sin(ang)
        v = spd * np.cos(ang)
    else:
        u = spd * np.sin(ang) * (-1)
        v = spd * np.cos(ang) * (-1)
    return u, v


def dirstats(direc):
    '''
    Calculate basic statistics of directional data (e.g., wind direction,
    currents direction): mean, minimum, maximum, and standard deviation.
    This function disregards NaN values in the calculations.
    Input:
        direc (pandas.core.series.Series): Direction series (decimal degrees).
    Output:
        stats_metrics (tuple): Statistical metrics of directional data (mean,
                               standard deviation, minimum, and maximum,
                               respectively).
    '''
    import pandas as pd
    from scipy.stats import circmean, circstd
    stats_metrics = (np.rad2deg(circmean(np.deg2rad(direc.dropna()))),
                     np.rad2deg(circstd(np.deg2rad(direc.dropna()))),
                     np.nanmin(direc),
                     np.nanmax(direc)
                     )
    return stats_metrics
