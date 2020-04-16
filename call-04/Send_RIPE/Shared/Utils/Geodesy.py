# Copyright (C) 2017 Systems & Technology Research, LLC.
# http://www.stresearch.com
#
# STR Proprietary Information
#
# US Government retains Unlimited Rights
# Non-Government Users – restricted usage as defined through
# licensing with STR or via arrangement with Government.
#
# In no event shall the initial developers or copyright holders be
# liable for any damages whatsoever, including - but not restricted
# to - lost revenue or profits or other direct, indirect, special,
# incidental or consequential damages, even if they have been
# advised of the possibility of such damages, except to the extent
# invariable law, if any, provides otherwise.
#
# The Software is provided AS IS with NO
# WARRANTY OF ANY KIND, INCLUDING THE WARRANTY OF DESIGN,
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

import numpy
import unittest
import Shared.Utils.HfgeoLogger as Logger

logger = Logger.getLogger()

## @package Shared.Utils.Geodesy
#  Geodesic angles and distances for the great circle between 2 points for both a circular earth and WGS84 earth models

## WGS84 Earth Ellipsoid model
# Defines earth's ellipsoid semi-major axis, semi-minor axis, flattening, exentricity and mean Radius
class wgs84Ellipsoid:
    # semi-major axis in meters
    a = 6378137.0
    # flattening = (a-b)/a
    f = 1 / 298.257223563
    # semi-minor axis, 6356752.31425
    b = a*(1 - f)
    # square of eccentricity
    e2 = 1 - (1 - f)**2
    meanRadius = (2 * a + b)/3

## (az1, az2, dist) = greatCircleBearingAndDistance(latLon1,latLon2,eparam,algo,maxIter,minTol)
# calculates the starting and ending bearings/azimuths of the great circle connecting two points given in lat/lon.
#
# ALL UNITS in SI
#
# NOTE 1.   Vincenty's algorithm and formulae for spherical earth are from
#           http://www.movable-type.co.uk/scripts/latlong-vincenty.html
#           http://www.movable-type.co.uk/scripts/latlong.html
#
# NOTE 2.   Vincenty's algorithm is iterative but more accurate than spherical; this python
#           code implements vectorized versions
#
# NOTE 3.   An even better algorithm is in C. Karney, Algorithms for geodesics, J. Geodesy, 2013
#           (https://arxiv.org/pdf/1109.4448v2.pdf)
#           See http://geographiclib.sourceforge.net/geod.html for code and lots of details
#           There is C++ and MATLAB code; we should use it for Phase 2
#
# NOTE 4.   Earth's mean radius is defined by International Union of Geodesy as
#           (2*a+b)/3
#           where a and b are the semi-major and semi-minor axes (b = a(1-f))
#
# @param latLon1    - array,  2 by K - lat/lon of starting points (in radians)
# @param latLon2    - array,  2 by K - lat/lon of final points (in radians)
# @param algo       - integer        - optional algorithm flag
#                                   algo = 1 (default)use Vincenty's algorithm for wgs84
#                                   algo = 0 uses spherical Earth
# @param maxIter    - integer        - optional, maximum number of iterations for Vincenty's algorithm
# @param minTol     - integer,       - optional, minimum difference bettwen iterations for Vincenty's algorithm
# @retval az1       - array, 1 by K  -  starting azimuths (at latLon1) (in radians)
# @retval az2       - array, 1 by K  - final azimuths (at latLon2) (in radians)
# @retval dist      - array, 1 by K  - vector of great circle distances between the points (in meters)
#
# Adapted from the Matlab version written by R. K. Prasanth, July 24, 2016
# Revision: August 2017, Constantino Rago
def greatCircleBearingAndDistance(latLon1, latLon2, algo=1, maxIter=100, minTol=1e-10):
    # Output initialization
    az1 = numpy.zeros(latLon1.shape)
    az2 = numpy.zeros(latLon1.shape)
    dist = numpy.zeros(latLon1.shape)
    if algo == 0:
        # calculate  starting az
        dlon = latLon2[1, :] - latLon1[1, :]
        x = numpy.cos(latLon1[0, :]) * numpy.sin(latLon2[0, :]) - numpy.cos(latLon2[0, :]) * numpy.sin(latLon1[0, :]) * numpy.cos(dlon)
        y = numpy.cos(latLon2[0, :]) * numpy.sin(dlon)
        az1 = numpy.arctan2(y, x)
        az1[az1 < 0] = 2*numpy.pi+az1[az1 < 0]
        # calculate ending az
        dlon = - dlon
        x = numpy.cos(latLon2[0, :]) * numpy.sin(latLon1[0, :]) - numpy.cos(latLon1[0, :]) * numpy.sin(latLon2[0, :]) * numpy.cos(dlon)
        y = numpy.cos(latLon1[0, :]) * numpy.sin(dlon)
        az2 = numpy.pi + numpy.arctan2(y, x)
        az2[az2 < 0] = 2*numpy.pi + az2[az2 < 0]
        # calculate the distance
        # haversine
        dang = (latLon1-latLon2)/2
        sang = numpy.sin(dang)**2
        a = sang[0, :] + numpy.cos(latLon1[0, :]) * numpy.cos(latLon2[0, :])*sang[1, :]
        c = 2 * numpy.arctan2(numpy.sqrt(a), numpy.sqrt(1-a))
        dist = wgs84Ellipsoid.meanRadius * c
    elif algo == 1:
        # Vincenty's iterative algo
        flat = wgs84Ellipsoid.f
        dlon = latLon2[1, :]-latLon1[1, :]
        tanu1 = (1 - flat) * numpy.tan(latLon1[0, :])
        cosu1 = 1. / numpy.sqrt(1 + tanu1**2)
        sinu1 = tanu1 * cosu1

        tanu2 = (1 - flat) * numpy.tan(latLon2[0, :])
        cosu2 = 1. / numpy.sqrt(1 + tanu2**2)
        sinu2 = tanu2 * cosu2

        csu12 = cosu1 * sinu2
        scu12 = sinu1 * cosu2
        ccu12 = cosu1 * cosu2
        ssu12 = sinu1 * sinu2

        # initialize loop variables
        nl = len(dlon)
        clam = numpy.zeros(nl)
        slam = numpy.zeros(nl)
        csig = numpy.zeros(nl)
        ssig = numpy.zeros(nl)
        sig = numpy.zeros(nl)
        salp = numpy.zeros(nl)
        calp2 = numpy.zeros(nl)
        cos2sig = numpy.zeros(nl)

        ddlon = 10*minTol*numpy.ones(nl)
        lprev = dlon

        # loop
        for i in range(len(dlon)):
            iteration = 0
            while (ddlon[i] > minTol) & (iteration <=maxIter):
                # cos, sin, lambda , sigma, alpha, etc
                clam[i]= numpy.cos(dlon[i])
                slam[i] = numpy.sin(dlon[i])

                csig[i] = ssu12[i] + ccu12[i] * clam[i]
                ssig[i] = numpy.sqrt((cosu2[i] * slam[i])**2 + (csu12[i] - scu12[i] * clam[i])**2)
                sig[i] = numpy.arctan2(ssig[i], csig[i])

                salp[i] = ccu12[i] * slam[i] / ssig[i]
                calp2[i] = 1 - salp[i]**2
                if calp2[i] != 0:
                    cos2sig[i] = csig[i] - (2 * ssu12[i] / calp2[i])
                else:
                    cos2sig[i] = 0  # equator

                # update
                CC = calp2[i] * ((flat / 4) + (flat**2 / 16) * (4 - 3 * calp2[i]))
                tmp1 = sig[i] + CC * ssig[i] * (cos2sig[i] + CC * csig[i] * (-1 + 2 * (cos2sig[i]**2)))
                dlon[i] = dlon[i] + flat * ((1 - CC) * salp[i] * tmp1)

                # convergence?
                ddlon[i] = abs(dlon[i] - lprev[i])

                # counter
                iteration = iteration + 1
                lprev[i] = dlon[i]

        # now calculate angles
        az1 = numpy.arctan2(cosu2 * slam, csu12 - scu12 * clam)
        az1[az1 < 0] = 2 * numpy.pi + az1[az1 < 0]
        az2 = numpy.arctan2(cosu1 * slam, -scu12 + csu12 * clam)
        az2[az2 < 0] = 2 * numpy.pi + az2[az2 < 0]

        # calculate distances
        semiMinor = wgs84Ellipsoid.a * (1 - wgs84Ellipsoid.f)
        u2 = calp2 * ((wgs84Ellipsoid.a**2 - semiMinor**2) / semiMinor**2)
        A = 1 + (u2 * (1 / 16384)) * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
        B = (u2 * (1 / 1024)) * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
        dsig = B * ssig * (cos2sig + (0.25 * B) * (
            csig * (-1 + 2 * (cos2sig**2)) - (B * (1 / 6)) * cos2sig * (1 - 4 * calp2) * (-3 + 4 * (cos2sig**2))))
        dist = semiMinor * (A * (sig - dsig))
    else:
        logger.error('Algorithm types values supported by the great circle bearing and distance calculation are only 0 '
                     'and 1, not : {} \n'.format(algo))

    return az1, az2, dist

class UnitTest_Geodesy(unittest.TestCase):
    def test_greatCircleBearingAndDistanceCalculation_sphericEarth(self):
        latlon1 = numpy.array([[33*numpy.pi/180, 34*numpy.pi/180, 35*numpy.pi/180, 36*numpy.pi/180],
                            [116*numpy.pi/180, 117*numpy.pi/180, 118*numpy.pi/180, 119*numpy.pi/180]])
        latlon2 = numpy.array([[43*numpy.pi/180, 44*numpy.pi/180, 45*numpy.pi/180, 46*numpy.pi/180],
                            [146*numpy.pi/180, 147*numpy.pi/180, 148*numpy.pi/180, 149*numpy.pi/180]])
        (az1, az2, dist) = greatCircleBearingAndDistance(latLon1=latlon1, latLon2=latlon2, algo=0)
        logger.info('latlon1 = \n {}'.format(latlon1*180/numpy.pi))
        logger.info('latlon2 = \n {}'.format(latlon2*180/numpy.pi))
        logger.info('Azimuth angles, point 1 = \n {}'.format(az1*180/numpy.pi))
        logger.info('Azimuth angles, point 2 = \n {}'.format(az2*180/numpy.pi))
        logger.info('Distance between point 1 and 2 = \n {}'.format(dist))
        expected_az1 = numpy.array([1.015220460542551e+00, 1.006726193328406e+00, 9.980566850337145e-01, 9.892021360927719e-01])
        expected_az2 = numpy.array([1.343434264332775e+00, 1.342087372890629e+00, 1.340456475040398e+00, 1.338529833903264e+00])
        expected_dist = numpy.array([2.834776486811963e+06, 2.800864114444255e+06, 2.766306549340698e+06, 2.731122731255875e+06])
        numpy.testing.assert_almost_equal(az1, expected_az1, decimal=15)
        numpy.testing.assert_almost_equal(az2, expected_az2, decimal=15)
        numpy.testing.assert_almost_equal(dist, expected_dist, decimal=9)

    def test_greatCircleBearingAndDistanceCalculation_WGS84Earth(self):
        latlon1 = numpy.array([[33*numpy.pi/180, 34*numpy.pi/180, 35*numpy.pi/180, 36*numpy.pi/180],
                               [116*numpy.pi/180, 117*numpy.pi/180, 118*numpy.pi/180, 119*numpy.pi/180]])
        latlon2 = numpy.array([[43*numpy.pi/180, 44*numpy.pi/180, 45*numpy.pi/180, 46*numpy.pi/180],
                               [146*numpy.pi/180, 147*numpy.pi/180, 148*numpy.pi/180, 149*numpy.pi/180]])
        (az1, az2, dist) = greatCircleBearingAndDistance(latLon1=latlon1, latLon2=latlon2, algo=1)
        logger.info('latlon1 = \n {}'.format(latlon1 * 180 / numpy.pi))
        logger.info('latlon2 = \n {}'.format(latlon2 * 180 / numpy.pi))
        logger.info('Azimuth angles, point 1 = \n {}'.format(az1 * 180 / numpy.pi))
        logger.info('Azimuth angles, point 2 = \n {}'.format(az2 * 180 / numpy.pi))
        logger.info('Distance between point 1 and 2 = \n {}'.format(dist))
        expected_az1 = numpy.array(
            [1.016279481992985e+00, 1.007769666386550e+00, 9.990837275844400e-01, 9.902118853744315e-01])
        expected_az2 = numpy.array(
            [1.343829054638948e+00, 1.342471435322193e+00, 1.340830075247057e+00, 1.338893223752600e+00])
        expected_dist = numpy.array(
            [2.834878984808767e+06, 2.801288558374810e+06, 2.767047191242227e+06, 2.732173146987394e+06])
        numpy.testing.assert_almost_equal(az1, expected_az1, decimal=15)
        numpy.testing.assert_almost_equal(az2, expected_az2, decimal=15)
        numpy.testing.assert_almost_equal(dist, expected_dist, decimal=9)

# @brief If the function is called from the command line then do the unit test
#
if __name__ == '__main__':
    logger.setLevel('CRITICAL')
    unittest.main()
