# handy-functions
Simple functions that may assist in the analysis of meteorological and oceanographic data

    - calc_dist: Calculate the distance between two points on the Earth's surface.
    - find_nearest_lonlat: Find the indexes of the nearest longitude and latitude
                           values to the coordinates of a given site in longitude
                           and latitude arrays.
    - central_date: Find the central date between the two given dates.
    - calc_mag_dec: Calculate magnetic declination.
    - uv2intdir: Convert zonal and meridional velocity components into velocity
                 speed and direction.
    - intdir2uv: Convert velocity speed and direction into zonal and meridional
                 velocity components.
    - dirstats: Calculate basic statistics of directional data.

You will need the following python libs installed: numpy, datetime, pandas, scipy, geopy, and magnetic-field-calculator
