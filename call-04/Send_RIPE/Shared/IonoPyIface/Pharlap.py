# Copyright (C) 2017 Boston College and Systems & Technology Research, LLC.
# http://www.stresearch.com
# http://bc.edu
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

import unittest
import abc
import numpy
from scipy import interpolate
from datetime import datetime
#import matplotlib.pyplot as plt
from Shared.IonoPyIface.PharlapPytoCIface import PharlapPytoCIface
from Shared.IonoPyIface.PharlapPytoCIface import IONOSPHERE_STRUCT
from Shared.IonoPyIface.PharlapPytoCIface import GEOMAG_FIELD_STRUCT
from Shared.IonoPyIface.PharlapPytoCIface import max_pts_in_ray
import Shared.Utils.DateTime as DateTime
import Shared.Utils.HfgeoLogger as Logger

logger = Logger.getLogger()
## @package Shared.IonoPyIface.Pharlap
#  Python wrappers to IRI, IGRF, and raytrace_3d with calls mimicking those in Pharlap/Matlab

## Abstract class of data object returned from raytrace_3d.
#  Providing both the dot notation and the key access to fields.
#
class Raytrace3dData(abc.ABC):

    ## Providing dict-like interface to read fields
    def __getitem__(self, key):
        return getattr(self, key)

    ## Providing dict-like interface to write fields
    def __setitem__(self, key, value):
        setattr(self, key, value)

## ray_data returned from raytrace_3d.
#
class Raytrace3dRayData(Raytrace3dData):
    __slots__ = ("lat", "lon", "ground_range", "group_range", "phase_path",
                 "initial_elev", "final_elev", "initial_bearing", "final_bearing",
                 "deviative_absorption", "TEC_path", "Doppler_shift", "apogee",
                 "geometric_path_length", "frequency", "nhops_attempted", "ray_label",
                 "NRT_elapsed_time")

    ## Position of fields in the returend ray_data array
    fieldname_output_position = (0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14)

    ## Constructor that takes either no arguments or
    #  the arguments: ray_data_sub, freq, nhops_attempted, ray_label, elapsed_time
    def __init__(self, *args):

        if len(args) not in (0, 5):
            raise TypeError(f"Number of arguments must be 0 or 5, not {len(args)}")

        if len(args) == 0:
            # Initialize all the attributes as None
            for slot in self.__slots__:
                setattr(self, slot, None)
            return

        # Unpack the arguments
        ray_data_sub, freq, nhops_attempted, ray_label, elapsed_time = args

        # Verify the input to be a numpy array
        if not isinstance(ray_data_sub, numpy.ndarray):
            raise TypeError("ray_data_sub is not a numpy array.")

        # Set the fields with values in the array.
        # The dimensions of the sub-array are [field][hop].
        for index, iField in enumerate(self.fieldname_output_position):
            setattr(self, self.__slots__[index], ray_data_sub[iField, :])

        # Set the frequency, nhops_attempted, ray_label, and elapsed_time
        self.frequency = freq
        self.nhops_attempted = nhops_attempted
        self.ray_label = ray_label
        self.NRT_elapsed_time = elapsed_time

## ray_path_data returned from raytrace_3d.
#
class Raytrace3dRayPathData(Raytrace3dData):
    __slots__ = ("initial_elev", "initial_bearing", "frequency", "lat", "lon", "height",
                 "group_range", "phase_path", "refractive_index", "group_refractive_index",
                 "wavenorm_ray_angle", "wavenorm_B_angle", "polariz_mag",
                 "wave_Efield_tilt", "volume_polariz_tilt", "electron_density", "geomag_x",
                 "geomag_y", "geomag_z", "geometric_distance")

    ## Constructor that takes either no arguments or
    #  the arguments: ray_path_data_sub, elev, bearing, freq, npts_in_ray
    def __init__(self, *args):

        if len(args) not in (0, 5):
            raise TypeError(f"Number of arguments must be 0 or 5, not {len(args)}")

        if len(args) == 0:
            # Initialize all the attributes as None
            for slot in self.__slots__:
                setattr(self, slot, None)
            return

        # Unpack the arguments
        ray_path_data_sub, elev, bearing, freq, npts_in_ray = args

        # Verify the input to be a numpy array
        if not isinstance(ray_path_data_sub, numpy.ndarray):
            raise TypeError("ray_path_data_sub is not a numpy array.")

        # Scalar fields
        #
        # initial_elev
        self.iniinitial_elev = elev
        # initial_bearing
        self.iniinitial_bearing = bearing
        # frequency
        self.frequency = freq

        # Fields of arrays
        for iField, field in enumerate(self.__slots__[3:]):
            setattr(self, field, ray_path_data_sub[:npts_in_ray, iField])

## The interface class to IRI, IGRF, and Pharlap
#  Contains an instance of the C interface library
#
class Pharlap:
    __slots__ = ("iface", "ionosphere_struct", "geomag_field_struct", "iri_flags_type")

    ## Constructor requests the python interface
    #
    def __init__(self):
        
        # Get the python interface
        #
        self.iface = PharlapPytoCIface()

        # Reused IONOSPHERE_STRUCT and GEOMAG_FIELD_STRUCT objects
        # (They will be lazily initialized the first time Pharlap.raytrace3d is called.)
        self.ionosphere_struct = None
        self.geomag_field_struct = None

        self.iri_flags_type = 1   # (0=use flags consistent with Pharlap4.2.0, 1=use flags consistent with iri2016b)


    ## Call igrf mimicking the call used in PHaRLAP/Matlab
    #
    #  @param lat    - geographic latitude of point (degrees)
    #  @param lon    - geographic longitude of point (degrees)
    #  @param UT     - [year, month, day, hour, min] in Universal Time
    #  @param height - height (km)
    #
    #  @retval  mag_field - 1 X 10 array of IGRF magnetic field parameters
    #       mag_field(1) = North component of magnetic field (Tesla)
    #       mag_field(2) = East  component of magnetic field (Tesla)
    #       mag_field(3) = Downwards component of magnetic field (Tesla)
    #       mag_field(4) = magnetic field strength (Gauss) <-- PharLap provides this in Gauss, so we do too!
    #       mag_field(5) = dipole moment (Gauss)           <-- PharLap provides this Gauss, so we do too!
    #       mag_field(6) = L value
    #       mag_field(7) = L flag (1 = L is correct; 2 = L is not correct;
    #                              3 = approximation is used)
    #       mag_field(8) = magnetic dip (degrees)
    #       mag_field(9) = dip latitude (or magnetic latitude i.e. atan(tan(dip)/2)
    #                      (degrees)
    #       mag_field(10) = magnetic declination (degrees)
    #
    def igrf2016(self, lat, lon, UT, height):

        # Get the Input object so we can fill it out
        igrfInput = self.iface.getIgrfPharlapIO()

        igrfInput.glat = lat
        igrfInput.glong = lon
        igrfInput.dec_year = DateTime.iso8601ToDecimalYear(datetime(*UT))
        igrfInput.height = height
        igrfInput.dipole_moment = 0
        igrfInput.babs = 0
        igrfInput.bnorth = 0
        igrfInput.beast = 0
        igrfInput.bdown = 0
        igrfInput.dip = 0
        igrfInput.dec = 0
        igrfInput.dip_lat = 0
        igrfInput.l_value = 0
        igrfInput.l_value_code = 0

        igrfOutput = self.iface.igrfPharlap(igrfInput)

        mag_field = numpy.zeros(10)
        mag_field[0] = igrfOutput.bnorth / 1.e4  # convert from Gauss to Tesla
        mag_field[1] = igrfOutput.beast  / 1.e4  # convert from Gauss to Tesla
        mag_field[2] = igrfOutput.bdown  / 1.e4  # convert from Gauss to Tesla
        mag_field[3] = igrfOutput.babs   / 1.e4  # convert from Gauss to Tesla
        mag_field[4] = igrfOutput.dipole_moment 
        mag_field[5] = igrfOutput.l_value
        mag_field[6] = igrfOutput.l_value_code
        mag_field[7] = igrfOutput.dip
        mag_field[8] = igrfOutput.dip_lat
        mag_field[9] = igrfOutput.dec

        return mag_field

    ## Call iri2016 mimicking the call used in PHaRLAP/Matlab
    #
    #  @param lat       - geographic latitude (deg)
    #  @param lon       - geographic longitude (deg)
    #  @param R12       - yearly smoothed sunspot number (placeholder--ignored for now)
    #  @param UT        - [year, month, day, hour, min] in Universal Time
    #  @param hgt_start - starting height for evaluating profile (km)
    #  @param hgt_inc   - height increment for evaluating profile (km)
    #  @param hgt_num   - number of heights for evaluating profile
    #  @param (optional) layer_parameters - [foF2(Mhz), hmF2(km), foF1(MHz), fo (MHz), hmE(km), B0(km), B1(unitless)]
    #
    #  @retval iono_pf    - plasma frequency profile (MHz)
    #  @retval iono_extra - IRI output array, see detailed description in IRI2016bc source code
    #  @retval output_layer_parameters - output parameters, same format as layer_parameters
    #
    #  Notes:  layer_parameters is a 7 element array containing user specified ionospheric
    #          layer parameters. Specification of these values overrides the model
    #          model parameters in IRI. Critical frequencies must be in the range
    #          0.1MHz to 100MHz with foE < foF1 < foF2. Layer heights must be in
    #          the range 50km to 1000km with hmE < hmF1 < hmF2. Parameters set to
    #          -1 indicate to IRI2016 to use its model in that case. Note that foF1
    #          cannot be specified as input since it is derived from B0 and B1
    #
    #def iri2016(self, lat, lon, R12, UT, hgt_start, hgt_inc, hgt_num,
    #            iono_layer_parameters=[-1, -1, -1, -1, -1, -1, -1]):
    def iri2016(self,lat, lon, R12, UT, *args):

        # Verify the number of function arguments
        if len(args) not in (0, 3, 4):
            raise TypeError(f"Number of arguments should be 4, 7, or 8, not {len(args) + 4}")

        # Get the Input object so we can fill it out
        #
        iriInput = self.iface.getIriPharlapIO()

        # Summary of differences between flags for IRI2016/Pharlap4.2.0 and iri2016bc:
        #    For iri206bc we
        #       1) disable calculation of temps (jf[2]), ion composition (jf[3]), and ion drift (jf[21])
        #       2) disable use of the new hmF2 models in favor of the older hmF2 (M3000F2) model (jf[38])

        iriInput.jf = numpy.zeros(50, dtype=numpy.intc)

        if self.iri_flags_type == 0:
            # Flags for consistency with the IRI2016 provided by Manuel Cervera in Pharlap4.2.0)
            # Flag No. (FORTRAN) 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30
            iriInput.jf[0:50] = [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0,
                                 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
            #FLAG NO. (FORTRAN) 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50
            iriInput.jf[38] = 0   # (0 = use older hmF2 (M3000F2) model, 1 = disable new hmF2 models)
            iriInput.jf[39] = 1

        else:
            # Flags for consistency with Boston College's iri2016bc
            # Flag No. (FORTRAN) 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30
            iriInput.jf[0:50] = [1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0,
                                 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
            #FLAG NO. (FORTRAN) 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50


        # Filling out the rest of the values
        #
        iriInput.jmag = 0
        iriInput.glat = lat
        iriInput.glong = lon
        iriInput.year = UT[0]
        iriInput.mmdd = 100 * UT[1] + UT[2]
        iriInput.dhour = UT[3] + UT[4] / 60 + 25 # the addition of 25 tells IRI to use UT rather than LT

        #print('args: ',args)
        #print('len(args): ',len(args))
        if len(args)==0:
            # height parameters not specified, do not generate profile
            hgt_start = 80
            hgt_inc = 1
            hgt_num = 1
        else:
            # height parameters specified as input
            hgt_start = args[0]
            hgt_inc = args[1]
            hgt_num = args[2]

        iriInput.heibeg = hgt_start
        iriInput.heiend = hgt_start + hgt_inc*hgt_num
        iriInput.heistp = hgt_inc

        # These are output
        #
        iriInput.outf = numpy.zeros((1000,20), dtype=numpy.float32)
        iriInput.oarr = numpy.zeros(100, dtype=numpy.float32)

        if len(args) < 4:
            # request IRI model parameters
            foF2 = -1
            hmF2 = -1
            foF1 = -1
            foE  = -1
            hmE  = -1
            B0   = -1
            B1   = -1
        else:
            # user parameters specified
            iono_layer_parameters = args[3]
            foF2 = iono_layer_parameters[0]
            hmF2 = iono_layer_parameters[1]
            foF1 = iono_layer_parameters[2]
            foE  = iono_layer_parameters[3]
            hmE  = iono_layer_parameters[4]
            B0   = iono_layer_parameters[5]
            B1   = iono_layer_parameters[6]

        #parms = iono_layer_parameters

        # Notes from From iri2016, irisub.f (23 Feb 2017)
        #       Setting              INPUT parameter
        #    -----------------------------------------------------------------
        #    jf(8)  =.false.     OARR(1)=user input for foF2/MHz or NmF2/m-3
        #    jf(9)  =.false.     OARR(2)=user input for hmF2/km or M(3000)F2
        #    jf(10 )=.false.     OARR(15),OARR(16)=user input for Ne(300km),
        #       Ne(400km)/m-3. Use OARR()=-1 if one of these values is not
        #       available. If jf(23)=.false. then Ne(300km), Ne(550km)/m-3.
        #    jf(13) =.false.     OARR(3)=user input for foF1/MHz or NmF1/m-3
        #    jf(14) =.false.     OARR(4)=user input for hmF1/km
        #    jf(15) =.false.     OARR(5)=user input for foE/MHz or NmE/m-3
        #    jf(16) =.false.     OARR(6)=user input for hmE/km
        #    jf(17) =.flase.     OARR(33)=user input for Rz12
        #    jf(25) =.false.     OARR(41)=user input for daily F10.7 index
        #    jf(27) =.false.     OARR(39)=user input for IG12
        #    jf(43) =.false.     OARR(10)=user input for B0
        #    jf(44) =.false.     OARR(87)=user input for B1 <-- THIS IS A TYPO IN IRI DOCS, SHOULD BE OARR(35)

        if foF2 != -1:
            iriInput.jf[7] = 0
            iriInput.oarr[0] = foF2

        if hmF2 != -1:
            iriInput.jf[8] = 0
            iriInput.oarr[1] = hmF2

        if foF1 != -1:
            iriInput.jf[12] = 0
            iriInput.oarr[2] = foF1

        if foE != -1:
            iriInput.jf[14] = 0
            iriInput.oarr[4] = foE

        if hmE != -1:
            iriInput.jf[15] = 0
            iriInput.oarr[5] = hmE

        if B0 != -1:
            iriInput.jf[42] = 0
            iriInput.oarr[9] = B0

        if B1 != -1:
            iriInput.jf[43] = 0
            iriInput.oarr[34] = B1

        iriOutput = self.iface.iri2016pharlap(iriInput)

        iono_en = iriOutput.outf[0:hgt_num,0] # extract array of densities

        # IRI returns -1 if altitude is out of range (below 65 km during daytime or 80 km during nighttime)
        invalid = numpy.where(iono_en == -1)
        iono_en[invalid] = 0.0
        #print('invalid indicies: ',invalid)

        pftoden = 80.6164e-6
        iono_pf = numpy.sqrt(iono_en * 1.e6 * pftoden) / 1.e6
        iono_extra = iriOutput.oarr

        #output_layer_parameters = self.iono_extra_to_layer_parameters(iono_extra)

        return (iono_pf, iono_extra)

    ## Extract layer parameters from iono_extra array returned by iri2016_bc
    #
    #  @param iono_extra - IRI output array, see detailed description in IRI2016bc source code
    #
    #  @retval iono_layer_parameters - [foF2 (Mhz), hmF2 (km), foF1 (MHz), foE (MHz), hmE (km), B0 (km), B1 (unitless)]
    #
    def iono_extra_to_layer_parameters(self, iono_extra):
        pftoden = 80.6164e-6
        foF2 = numpy.sqrt(iono_extra[0] * 1.e6 * pftoden) / 1.e6
        hmF2 = iono_extra[1]
        if iono_extra[2] > 0:
            foF1 = numpy.sqrt(iono_extra[2] * 1.e6 * pftoden) / 1.e6
        else:
            foF1 = -1
        #hmF1 = iono_extra[3] # unused
        if iono_extra[4] > 0:
           foE = numpy.sqrt(iono_extra[4] * 1.e6 * pftoden) / 1.e6
        else:
           foE = -1
        hmE = iono_extra[5]
        B0  = iono_extra[9]
        B1  = iono_extra[34]
        return (foF2,hmF2,foF1,foE,hmE,B0,B1)

    ## Plot a plasma frequency profile returned by iri2016
    # @param iono_pf    - plasma frequency profile (MHz)
    # @param iono_extra - IRI output array, see detailed description in IRI2016 source code
    # @param hgt_start  - starting height for evaluating profile (km)
    # @param hgt_inc    - height increment for evaluating profile (km)
    # @param hgt_num    - number of heights for evaluating profile
    #
#    def plot_iri2016(self, iono_pf, iono_extra, hgt_start, hgt_inc, hgt_num):
#        hgt_arr = hgt_start + hgt_inc * numpy.arange(0, hgt_num)
#        pftoden = 80.6164e-6
#        foF2 = numpy.sqrt(iono_extra[0] * 1.e6 * pftoden) / 1.e6
#        if iono_extra[2] > 0:
#            foF1 = numpy.sqrt(iono_extra[2] * 1.e6 * pftoden) / 1.e6
#        else:
#            foF1 = -1
#        foE = numpy.sqrt(iono_extra[4] * 1.e6 * pftoden) / 1.e6
#        plt.figure(1)
#        plt.plot(iono_pf, hgt_arr, 'b-')
#        plt.plot(numpy.array([0, foF2]), numpy.array([iono_extra[1], iono_extra[1]]), '--', color='gray')
#        if iono_extra[2] > 0:
#            plt.plot(numpy.array([0, foF1]), numpy.array([iono_extra[3], iono_extra[3]]), '--', color='gray')
#        plt.plot(numpy.array([0, foE]), numpy.array([iono_extra[5], iono_extra[5]]), '--', color='gray')
#        plt.plot(numpy.array([foF2, foF2]), numpy.array([0, iono_extra[1]]), '--', color='gray')
#        plt.plot(numpy.array([foF1, foF1]), numpy.array([0, iono_extra[3]]), '--', color='gray')
#        plt.plot(numpy.array([foE, foE]), numpy.array([0, iono_extra[5]]), '--', color='gray')
#        plt.plot(iono_pf, hgt_arr, 'r-')
#        plt.xlabel('Frequency (Hz)')
#        plt.ylabel('Height (km)')
#        plt.autoscale(enable=True, axis='y', tight=True)
#        plt.xlim([0, foF2 * 1.1])
#        plt.show()

    ## Call raytrace3d provided by PHARLAP
    #
    #  @param raytrace3dInput - The named tuple input to raytrace3d
    #
    #  @retval raytrace3dInput - The same named tuple modified by the C++ lib
    #
    def raytrace_3d(self, origin_lat, origin_long, origin_ht, elev, ray_bearing,
                    freq, OX_mode, nhops, tol, *args,
                    nargout=2):

        # Verify the number of function arguments
        if len(args) not in (0, 1, 8, 9):
            raise ValueError(f"Number of arguments should be 9, 10, 17, or 18, not {len(args) + 9}")

        # Validate the value of nargout
        if nargout not in (1, 2, 3):
            raise ValueError(f"nargout should be 1, 2, or 3, not {nargout}")

        # Lazy initialization of structs
        if self.ionosphere_struct is None:
            self.ionosphere_struct = IONOSPHERE_STRUCT()
        if self.geomag_field_struct is None:
            self.geomag_field_struct = GEOMAG_FIELD_STRUCT()

        # Convert nargout to return_ray_path_data and return_ray_state_vec
        if nargout == 1:
            return_ray_path_data = False
            return_ray_state_vec = False
        elif nargout == 2:
            return_ray_path_data = True
            return_ray_state_vec = False
        elif nargout == 3:
            return_ray_path_data = True
            return_ray_state_vec = True

        # Convert from python type to c type
        #   Start point of the ray(s)
        start_lat = origin_lat
        start_long = origin_long
        start_height = origin_ht
        #   Elevation(s), bearing(s), and freq(s) of the ray(s).
        #     Support both floating point numbers and numpy arrays.
        if all(map(lambda x: isinstance(x, float), (elev, ray_bearing, freq))):
            num_rays = 1
            elevs = numpy.array([elev])
            bearings = numpy.array([ray_bearing])
            freqs = numpy.array([freq])
        elif all(map(lambda x: isinstance(x, numpy.ndarray), (elev, ray_bearing, freq))):
            num_rays             = len(elev.ravel())
            elevs                = elev.ravel()
            bearings             = ray_bearing.ravel()
            freqs                = freq.ravel()
        else:
            raise TypeError("Unsupported types of (elev, ray_bearing, freq) = "
                            f"({type(elev)}, {type(ray_bearing)}, {type(freq)}).")
        #   Wave mode (do nothing)
        #   Number of hops (do nothing)
        # Step sizes converted from km to m
        step_size_min = 1000.0 * tol[1]
        step_size_max = 1000.0 * tol[2]
        # Pharlap tolerance
        tol = tol[0]
        #TODO: implement the tol == 1, 2, or 3 for default values.

        # Reuse the IONOSPHERE_STRUCT and GEOMAG_FIELD_STRUCT objecs
        ionosphere_struct    = self.ionosphere_struct
        geomag_field_struct  = self.geomag_field_struct
        # Repopulated the voxel grids with the input arguments
        if len(args) in (8, 9):
            # Electron density and collision frequency grids
            iono_grid_parms = args[3]
            lat_min, lat_inc, num_lat = iono_grid_parms[0:3]
            lon_min, lon_inc, num_lon = iono_grid_parms[3:6]
            ht_min, ht_inc, num_ht = iono_grid_parms[6:9]
            #  (1) geodetic latitude (degrees) start
            ionosphere_struct.lat_min = lat_min
            #  (2) latitude step (degrees)
            ionosphere_struct.lat_inc = lat_inc
            #  (3) number of latitudes
            ionosphere_struct.num_lat = num_lat
            #  Max of latitude (degrees)
            ionosphere_struct.lat_max = lat_min + (float(num_lat - 1) * lat_inc)
            #  (4) geodetic lonfitude (degrees) start
            ionosphere_struct.lon_min = lon_min
            #  (5) lonfitude step (degrees)
            ionosphere_struct.lon_inc = lon_inc
            #  (6) number of longitudes
            ionosphere_struct.num_lon = num_lon
            #  Max of longitude (degrees)
            ionosphere_struct.lon_max = lon_min + (float(num_lon - 1) * lon_inc)
            #  (7) geodetic height (km) start
            ionosphere_struct.ht_min = ht_min
            #  (8) height step (km)
            ionosphere_struct.ht_inc = ht_inc
            #  (9) number of heights
            ionosphere_struct.num_ht = num_ht
            #  Max of heights (km)
            ionosphere_struct.ht_max = ht_min + (float(num_ht - 1) * ht_inc)
            # Electron density grid.
            iono_en_grid = args[0]
            eN = numpy.ctypeslib.as_array(ionosphere_struct.eN)
            eN[0:num_ht, 0:num_lon, 0:num_lat] = iono_en_grid
            # Electron density grid for 5 minutes later.
            iono_en_grid_5 = args[1]
            eN_5 = numpy.ctypeslib.as_array(ionosphere_struct.eN_5)
            eN_5[0:num_ht, 0:num_lon, 0:num_lat] = iono_en_grid_5
            # Collision frequency grid.
            collision_freq = args[2]
            col_freq = numpy.ctypeslib.as_array(ionosphere_struct.col_freq)
            col_freq[0:num_ht, 0:num_lon, 0:num_lat] = collision_freq

            # Geomagnetic grids.
            geomag_grid_parms = args[7]
            lat_min, lat_inc, num_lat = geomag_grid_parms[0:3]
            lon_min, lon_inc, num_lon = geomag_grid_parms[3:6]
            ht_min, ht_inc, num_ht = geomag_grid_parms[6:9]
            #  (1) geodetic latitude (degrees) start
            geomag_field_struct.lat_min = lat_min
            #  (2) latitude step (degrees)
            geomag_field_struct.lat_inc = lat_inc
            #  (3) number of latitudes
            geomag_field_struct.num_lat = num_lat
            #  Max of latitude (degrees)
            geomag_field_struct.lat_max = lat_min + (float(num_lat - 1) * lat_inc)
            #  (4) geodetic lonfitude (degrees) start
            geomag_field_struct.lon_min = lon_min
            #  (5) lonfitude step (degrees)
            geomag_field_struct.lon_inc = lon_inc
            #  (6) number of longitudes
            geomag_field_struct.num_lon = num_lon
            #  Max of longitude (degrees)
            geomag_field_struct.lon_max = lon_min + (float(num_lon - 1) * lon_inc)
            #  (7) geodetic height (km) start
            geomag_field_struct.ht_min = ht_min
            #  (8) height step (km)
            geomag_field_struct.ht_inc = ht_inc
            #  (9) number of heights
            geomag_field_struct.num_ht = num_ht
            #  Max of heights (km)
            geomag_field_struct.ht_max = ht_min + (float(num_ht - 1) * ht_inc)
            # Bx, By, Bz
            Bx = numpy.ctypeslib.as_array(geomag_field_struct.Bx)
            By = numpy.ctypeslib.as_array(geomag_field_struct.By)
            Bz = numpy.ctypeslib.as_array(geomag_field_struct.Bz)
            Bx[0:num_ht, 0:num_lon, 0:num_lat] = args[4]
            By[0:num_ht, 0:num_lon, 0:num_lat] = args[5]
            Bz[0:num_ht, 0:num_lon, 0:num_lat] = args[6]

        # Accept ray_state_vec_in as an input argument
        if len(args) in (1, 9):
            #TODO: convert the input struct to a 2D array
            ray_state_vec_in = args[-1]
        else:
            # Fill ray_state_vec_in with -1
            ray_state_vec_in = numpy.full((num_rays, 11), -1.0, dtype=numpy.double, order="C")
        # Flags for returning extra values (pass through)

        # Buffer of ray_data to be returned from the low-level raytrace_3d_ function.
        # The dimensions of the buffer are [field][hop][ray]
        ray_data = numpy.empty((15, nhops, num_rays), dtype=numpy.double, order="C")
        # Buffer of ray_path_data to be returned from the low-level raytrace_3d_ function.
        # The dimensions of the buffer are [pts_in_ray][field][ray]
        ray_path_data = numpy.empty((max_pts_in_ray, 17, num_rays), dtype=numpy.double, order="C")
        # Buffer of ray_label to be returned from the low-level raytrace_3d_ function.
        # The dimensions of the buffer are [hop][ray]
        # ray_label = ((C.c_int * num_rays) * nhops)()
        ray_label = numpy.empty((nhops, num_rays), dtype=numpy.intc, order="C")
        # Buffer of nhops_attempted to be returned from the low-level raytrace_3d_ function.
        nhops_attempted = numpy.empty((num_rays, ), dtype=numpy.intc, order="C")
        # Buffer of npts_in_ray to be returned from the low-level raytrace_3d_ function.
        npts_in_ray = numpy.empty((num_rays, ), dtype=numpy.intc, order="C")
        # Buffer of ray_state_vec_out to be returned from the low-level raytrace_3d_ function.
        # The dimensions of the buffer are [field][pts_in_ray][ray]
        ray_state_vec_out = numpy.empty((11, max_pts_in_ray, num_rays),
                                        dtype=numpy.double, order="C")

        elapsed_time = numpy.empty((1, ), dtype=numpy.double, order="C")

        # Calling the wrapper raytrace_3d_ that handles the ctypes data conversion
        #
        self.iface.raytrace_3d_(start_lat,
                                start_long,
                                start_height,
                                num_rays,
                                elevs,
                                bearings,
                                freqs,
                                OX_mode,
                                nhops,
                                step_size_min,
                                step_size_max,
                                tol,
                                ionosphere_struct,
                                geomag_field_struct,
                                ray_state_vec_in,
                                return_ray_path_data,
                                return_ray_state_vec,
                                ray_data,
                                ray_path_data,
                                ray_label,
                                nhops_attempted,
                                npts_in_ray,
                                ray_state_vec_out,
                                elapsed_time)

        # Create the output tuple of Raytrace3dRayData objects.
        # Only use the data for the last hop. Otherwise the fields become
        # numpy array instead of float.
        rayData = [Raytrace3dRayData(ray_data[:, :, i], f, n, l, elapsed_time[0])
                       for i, (f, n, l) in enumerate(zip(freqs.ravel(), nhops_attempted.ravel(), ray_label.ravel()))]

        if not return_ray_path_data:
            rayPathData = None
        else:
            # Create the output tuple of Raytrace3dRayPathData objects.
            rayPathData = tuple((Raytrace3dRayPathData(ray_path_data[:, :, i], el, az, f, npts)
                      for i, (el, az, f, npts) in enumerate(zip(elevs, bearings, freqs, npts_in_ray))))

        if not return_ray_state_vec:
            rayStateVec = None
        else:
            #Placeholder
            rayStateVec = None

        # Return the specified number of outputs
        if nargout == 1:
            return rayData
        elif nargout == 2:
            return rayData, rayPathData
        elif nargout == 3:
            return rayData, rayPathData, rayStateVec 


class UnitTest_Pharlap(unittest.TestCase):

    def setUp(self):
        # Get the python interface
        self.iface = Pharlap()
        self.iface.iri_flags_type = 1   # (0=use flags consistent with Pharlap4.2.0, 1=use flags consistent with iri2016b)


    def test_igrf(self):
        
        logger.info('---IGRF Test---')

        lat = 10.0
        lon = 128.0
        height = 60.0

        UT = (2000, 9, 21, 0, 0)
        logger.info("DateTime (y, m, d, m, s) = {}".format(UT))

        mag_field = self.iface.igrf2016(lat, lon, UT, height)

        logger.info('IGRF bnorth={:10.6e}, beast={:10.6e}, bdown={:10.6e},'
                    ' bmag={:10.6e}, dipole_moment={:10.6e}, l_value={:10.6e},'
                    ' l_flag={:10.6e} dip={:10.6e} dip_lat={:10.6e} dec={:10.6e}'.format(
                      mag_field[0], mag_field[1], mag_field[2],\
                      mag_field[3], mag_field[4], mag_field[5],\
                      mag_field[6], mag_field[7], mag_field[8], mag_field[9]))

        # response from Matlab/PharLap v4.2.0/igrf2016:
        #    mag_field = [ 0.000037762653828  -0.000000067041069   0.000003220479190   0.000037899792194
        #                  0.301072090864182   0.927680432796478   1.000000000000000   4.874502658843994
        #                  2.441669702529907  -0.101718649268150]

        self.assertAlmostEqual(mag_field[0],  0.000037762653828, places=6)
        self.assertAlmostEqual(mag_field[1], -0.000000067041069, places=6)
        self.assertAlmostEqual(mag_field[2],  0.000003220479190, places=6)
        self.assertAlmostEqual(mag_field[3],  0.000037899792194, places=6)
        self.assertAlmostEqual(mag_field[4],  0.301072090864182, places=6)
        self.assertAlmostEqual(mag_field[5],  0.927680432796478, places=6)
        self.assertAlmostEqual(mag_field[6],  1.000000000000000, places=6)
        self.assertAlmostEqual(mag_field[7],  4.874502658843994, places=3)
        self.assertAlmostEqual(mag_field[8],  2.441669702529907, places=3)
        self.assertAlmostEqual(mag_field[9], -0.101718649268150, places=3)

        return

    def test_iri2016(self):
        
       logger.info('---IRI Test---')

       lat = 30.5
       lon = 273.5

       UT = (2013, 4, 11, 15, 0)
       logger.info("DateTime (y, m, d, m, s) = {}".format(UT))

       R12 = -1

       logger.info("IRI year={:4d} month={:d} day={:d} hour={:d} min={:d} lat={:f} lon={:f} R12={:d}".format(
           UT[0],UT[1],UT[2],UT[3],UT[4],lat,lon,R12))

       hgt_start = 60 #80
       hgt_inc = 2
       hgt_num = 200

       iono_layer_parameters = numpy.array([8.0, 300.0, 4.0, 2.0, 110.0, 120.0, 2.1])

       # test calling sequence #1: requesting only parameters and no profile
       (iono_pf, iono_extra) = self.iface.iri2016(lat, lon, R12, UT)

       parms = self.iface.iono_extra_to_layer_parameters(iono_extra)

       logger.info(
       "IRI calling sequence 1: foF2={:10.6e}, hmF2={:10.6e}, foF1={:10.6e}, foE={:10.6e}, hmE={:10.6e}, B0={:10.6e}, B1={:10.6e}". \
           format(parms[0], parms[1], parms[2], parms[3], parms[4], parms[5], parms[6]))

       # response from Matlab/Pharlap4.2.0/iri2016:
       #    parms = [8.295069412307519,2.661335754394531e+02,4.637140100499106,3.328429285015872,110,1.186387405395508e+02,2.219027519226074]

       # response from Matlab iri2016bc
       #    parms = [8.295069412307519,2.759624328613281e+02,4.637140100499106,3.328429285015872,110,1.186387329101562e+02,2.219027280807495]

       if self.iface.iri_flags_type == 0:
           self.assertAlmostEqual(parms[0], 8.295069412307519, places=8)
           numpy.testing.assert_approx_equal(parms[1], 2.661335754394531e+02, significant=7)
           self.assertAlmostEqual(parms[2], 4.637140100499106, places=8)
           numpy.testing.assert_approx_equal(parms[3], 3.328429285015872, significant=7)
           self.assertAlmostEqual(parms[4], 110, places=8)
           self.assertAlmostEqual(parms[5], 1.186387405395508e+02, places=8)
           self.assertAlmostEqual(parms[6], 2.219027519226074, places=8)
       else:
           self.assertAlmostEqual(parms[0], 8.295069412307519, places=8)
           numpy.testing.assert_approx_equal(parms[1], 2.759624328613281e+02, significant=7)
           self.assertAlmostEqual(parms[2], 4.637140100499106, places=8)
           numpy.testing.assert_approx_equal(parms[3], 3.328429285015872, significant=7)
           self.assertAlmostEqual(parms[4], 110, places=8)
           self.assertAlmostEqual(parms[5], 1.186387329101562e+02, places=4)
           self.assertAlmostEqual(parms[6], 2.219027280807495, places=6)


       # test calling sequence #2: requesting only the profile without specifying iono_layer_parameters as input
       (iono_pf, iono_extra) = self.iface.iri2016(lat, lon, R12, UT, hgt_start, hgt_inc, hgt_num)

       parms = self.iface.iono_extra_to_layer_parameters(iono_extra)

       # response from Matlab/Pharlap4.2.0/iri2016:
       #    parms = [8.295069412307519,2.661335754394531e+02,4.637140100499106,3.328429285015872,110,1.186387405395508e+02,2.219027519226074]

       logger.info(
           "IRI calling sequence 2: foF2={:10.6e}, hmF2={:10.6e}, foF1={:10.6e}, foE={:10.6e}, hmE={:10.6e}, B0={:10.6e}, B1={:10.6e}". \
               format(parms[0], parms[1], parms[2], parms[3], parms[4], parms[5], parms[6]))

       if self.iface.iri_flags_type == 0:
           self.assertAlmostEqual(parms[0], 8.295069412307519, places=8)
           numpy.testing.assert_approx_equal(parms[1], 2.661335754394531e+02, significant=7)
           self.assertAlmostEqual(parms[2], 4.637140100499106, places=8)
           numpy.testing.assert_approx_equal(parms[3], 3.328429285015872, significant=7)
           self.assertAlmostEqual(parms[4], 110, places=4)
           self.assertAlmostEqual(parms[5], 1.186387405395508e+02, places=8)
           self.assertAlmostEqual(parms[6], 2.219027519226074, places=8)
       else:
           self.assertAlmostEqual(parms[0], 8.295069412307519, places=8)
           numpy.testing.assert_approx_equal(parms[1], 2.759624328613281e+02, significant=7)
           self.assertAlmostEqual(parms[2], 4.637140100499106, places=8)
           numpy.testing.assert_approx_equal(parms[3], 3.328429285015872, significant=7)
           self.assertAlmostEqual(parms[4], 110, places=8)
           self.assertAlmostEqual(parms[5], 1.186387329101562e+02, places=4)
           self.assertAlmostEqual(parms[6], 2.219027280807495, places=6)

       # test calling sequence #3: requesting both the profile and parameters
       (iono_pf, iono_extra) = self.iface.iri2016(lat,lon,R12,UT,hgt_start,hgt_inc,hgt_num,iono_layer_parameters)

       parms = self.iface.iono_extra_to_layer_parameters(iono_extra)

       logger.info(
          "IRI calling sequence 3: foF2={:10.6e}, hmF2={:10.6e}, foF1={:10.6e}, foE={:10.6e}, hmE={:10.6e}, B0={:10.6e}, B1={:10.6e}". \
          format(parms[0], parms[1], parms[2], parms[3], parms[4], parms[5], parms[6]))

       # python response: parms = [7.99857331279, 300.0, 3.99928665639, 1.9996433282, 110.0, 120.0, 2.1]

       # response from Matlab/Pharlap4.2.0/iri2016:
       #    parms = [7.998573312785224, 300, 3.999286656392612, 1.999643328196306, 110, 1.186387405395508e+02, 2.219027519226074]
       # Note that Pharlap returns climo values in B0 and B1 even though we specified values for them!

       self.assertAlmostEqual(parms[0], 8,   places=2)
       self.assertAlmostEqual(parms[1], 300, places=4)
       self.assertAlmostEqual(parms[2], 4,   places=2)
       self.assertAlmostEqual(parms[3], 2,   places=2)
       self.assertAlmostEqual(parms[4], 110, places=4)
       self.assertAlmostEqual(parms[5], 120, places=4)
       self.assertAlmostEqual(parms[6], 2.1, places=4)

       #self.iface.plot_iri2016(iono_pf, iono_extra, hgt_start, hgt_inc, hgt_num)
       return

if __name__ == "__main__":
    logger.setLevel('INFO')
    unittest.main()
