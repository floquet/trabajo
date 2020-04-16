# Copyright (C) 2017 Boston College
# http://www.bostoncollege.edu
#
# BC Proprietary Information
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

import os
import numpy
import unittest
from scipy import interpolate
from datetime import datetime
import Shared.Utils.Constants as Constants
from Shared.IonoPyIface.Pharlap import Pharlap
from IonoModelEngine.RIPE.RIPE import RIPE
from IonoModelEngine.IRTAM import IRTAM
from IonoModelEngine.IRTAM.IrtamPyIface import IrtamPyIface
from Shared.Utils.Geodesy import greatCircleBearingAndDistance
#import matplotlib.pyplot as plt
import Shared.Utils.HfgeoLogger as Logger
from Shared.GridGeneration import pfProfileToEnGrid
#import IonoModelEngine.DataControl.Stations
#from IonoModelEngine.DataControl.Stations import Station

logger = Logger.getLogger()
logger.setLevel('INFO')

## @package IonoModelEngine.ROAM
# Python implementation of the Regional Optimium Ionospheric Model (ROAM)

# This class contains an instance of the Pharlap interface

class ROAM:
    ## Constructor requests the python interface
    #
    def __init__(self, config=None, irtamHandle=None, pharlapHandle=None):

        # Parse the config
        self.config = config

        # Get the python interface this class should never own one
        self.pharlapHandle = pharlapHandle

        # Get the IRTAM interface this class should never own one
        self.irtamHandle = irtamHandle

        if self.config.backgroundModel == 'ripe':
        #if 'ripe' in self.config.backgroundModel:
            logger.info("ROAM will use RIPE as the background model")
            self.refreshIRI = config.refreshIRI
            self.interpolatingModel = 0
            self.ripe = RIPE(pharlapHandle=self.pharlapHandle, \
                             refreshIRI=self.refreshIRI, interpolatingModel=self.interpolatingModel)
            self.apply_RIPE_scaling = (1, 1, 1, 1)  # scale foF2, hmF2, B0, B1 (1=yes, 0=no)

        elif self.config.backgroundModel == 'irtam':
        #elif 'irtam' in self.config.backgroundModel:
            logger.info("ROAM will use IRTAM as the background model")

        elif self.config.backgroundModel == 'ripe-irtam':
        #elif 'ripe-irtam' in self.config.backgroundModel:
            logger.info("ROAM will use RIPE initialized with IRTAM as the background model")
            self.refreshIRI = 1  # force refresh
            self.interpolatingModel = 1
            self.ripe = RIPE(pharlapHandle=self.pharlapHandle, irtamHandle =self.irtamHandle, \
                             refreshIRI=self.refreshIRI, interpolatingModel=self.interpolatingModel)
            self.apply_RIPE_scaling = (1, 1, 1, 1)  # scale foF2, hmF2, B0, B1 (1=yes, 0=no)

        else:
            logger.info("ROAM will use IRI as the background model")

    ## Obtain the ionospheric state from the ROAM model
    #
    #  @param   lat    - latitude where the state is desired (degrees)
    #  @param   lon    - longitude where the state is desired (degrees)
    #  @param   DT     - python datetime struct specifying when the state is desired
    #
    #  @retval  ionoState - [foF2, hmF2, foF1, foE, hmE, B0, B1, foEs, hmEs, beta_lat, beta_lon]
    #
    def CalcIonoState(self, lat, lon, DT, listOfFiles):

        listOfFilesRIPE  = []
        listOfFilesIRTAM = []

        # assemble the list of files for RIPE
        if self.config.backgroundModel == 'ripe':
            if listOfFiles['noaa']:
                listOfFilesRIPE = listOfFiles['noaa']
            else:
                logger.warning('Cannot find NOAA input files needed for RIPE, will call IRI instead')
                self.config.backgroundModel == 'iri'

        # assemble the list of files for RIPE-IRTAM
        if self.config.backgroundModel == 'ripe-irtam':
            if listOfFiles['noaa']:
                listOfFilesRIPE = listOfFiles['noaa']
            else:
                logger.warning('Cannot find NOAA input files needed for RIPE-IRTAM, will call IRI instead')
                self.config.backgroundModel == 'iri'
            if listOfFiles['giro']:
                listOfFilesRIPE.extend(listOfFiles['giro'])
            else:
                logger.warning('Cannot find GIRO input files needed for RIPE-IRTAM, will call IRI instead')
                self.config.backgroundModel == 'iri'

        # assemble the list of files for IRTAM
        if self.config.backgroundModel == 'irtam':
            if listOfFiles['giro']:
                listOfFilesIRTAM = listOfFiles['giro']
            else:
                logger.warning('Cannot find GIRO input files needed for IRTAM, will call IRI instead')
                self.config.backgroundModel == 'iri'


        UT = numpy.array([DT.year, DT.month, DT.day, DT.hour, DT.minute])

        R12 = -1 # a placeholder for now (consider passing this as input?)

        # no sporadic-E unless we are using RIPE
        foEs = 0.0
        hmEs = 110.0

        # latitude / longitude spacing for nodes of forward difference approximation
        #dlat = 0.5 * numpy.array([1, 0, 0])
        #dlon = 0.5 * numpy.array([0, 1, 0])

        # latitude / longitude spacing for nodes of central difference approximation
        dlat = 0.5 * numpy.array([1, 0, -1, 0, 0])
        dlon = 0.5 * numpy.array([0, 1, 0, -1, 0])

        dnum = len(dlat)

        foF2_list = []

        for j in range(0, dnum):

            (iono_pf, iono_extra) = self.pharlapHandle.iri2016(lat+dlat[j], lon+dlon[j], R12, UT)

            layer_parameters = self.pharlapHandle.iono_extra_to_layer_parameters(iono_extra)

            foF2 = layer_parameters[0]
            hmF2 = layer_parameters[1]
            foF1 = layer_parameters[2]
            foE  = layer_parameters[3]
            hmE  = layer_parameters[4]
            B0   = layer_parameters[5]
            B1   = layer_parameters[6]

            if self.config.backgroundModel == 'ripe' or self.config.backgroundModel == 'ripe-irtam':
            #if 'ripe' in self.config.backgroundModel or 'ripe-irtam' in self.config.backgroundModel:
                #print('taking ripe branch in roam', self.config.backgroundModel)

                # Calculate RIPE parameters
                (foF2_ripe, hmF2_ripe, B0_ripe, B1_ripe, foEs_ripe, hmEs_ripe) = \
                    self.ripe.CalcParameters(lat+dlat[j], lon+dlon[j], DT, listOfFilesRIPE)

                # adjust IRI bottomside  parameters for consistency with sounder data
                if self.apply_RIPE_scaling[0]:
                    foF2 = foF2_ripe
                if self.apply_RIPE_scaling[1]:
                    hmF2 = hmF2_ripe
                if self.apply_RIPE_scaling[2]:
                    B0 = B0_ripe
                if self.apply_RIPE_scaling[3]:
                    B1 = B1_ripe

                foEs = foEs_ripe
                hmEs = hmEs_ripe

            if self.config.backgroundModel == 'irtam':
            #if 'irtam' in self.config.backgroundModel:
                #print('taking irtam branch in roam', self.config.backgroundModel)

                # Get the interface to IRTAM
                irtam = IRTAM.IRTAM(self.irtamHandle, self.pharlapHandle)

                # Calculate IRTAM parameters
                (foF2, hmF2, B0, B1) = irtam.CalcParameters(lat+dlat[j], lon+dlon[j], DT, listOfFilesIRTAM)
                #logger.info("IRTAM data: foF2={:.4f} hmF2={:.4f} B0={:.4f} B1={:.4f}". \
                #                            format(foF2, hmF2, B0, B1))


            #if 'irtam' in self.config.backgroundModel:
            #
            #    # check that these files exist, else skip call to IRTAM and return IRI results
            #    print(listOfFiles)
            #
            #    from pathlib import Path
            #
            #    have_all_files = 1
            #    for file in listOfFiles:
            #        my_file = Path(file)
            #        if not my_file.is_file():
            #            have_all_files = 0
            #            logger.warning('IRTAM file not found, will return IRI state!')
            #
            #        fname = my_file.name
            #        #logger.info(" Testing for {:s}".format(fname))
            #
            #        # check that filename is the right length
            #        if len(fname) < 5:
            #            have_all_files = 0
            #            logger.warning("{:s} filename is too short, skipping".format(fname))
            #            continue
            #
            #        # check that filename has the right prefix
            #        #print(fname[0:5])
            #        if fname[0:5] != 'IRTAM':
            #            have_all_files = 0
            #            logger.info(" {:s} filename is missing IRTAM prefix, skipping".format(fname))
            #            continue
            #
            #    if have_all_files:
            #
            #        irtamProcessor = IRTAM.IRTAM(self.irtamHandle, self.pharlapHandle)
            #        data = irtamProcessor.translate(lat+dlat[j], lon+dlon[j], DT, listOfFiles)
            #        logger.info("IRTAM data: foF2={:.4f} hmF2={:.4f} B0={:.4f} B1={:.4f}".\
            #                    format(data[0], data[1], data[2], data[3]))
            #        foF2 = data[0]
            #        hmF2 = data[1]
            #        B0   = data[2]
            #        B1   = data[3]

            foF2_list.append(foF2)

        if not self.config.synopticTilt:
            # return no tilt
            beta_lat = 0.0
            beta_lon = 0.0
            logger.info('NO TILT COMPUTED')
        else:

            pval = foF2_list

            # forward difference gradient at Ref_hgt, dlat = [1 0 0]; dlon = [0 1 0];
            #grad_lat = (pval[0] - pval[2]) / dlat[0]
            #grad_lon = (pval[1] - pval[2]) / dlon[1]

            # convert from absolute horizontal gradient to relative horizontal gradient
            #beta_lat = grad_lat / pval[2]
            #beta_lon = grad_lon / pval[2]

            # central difference gradient at Ref_hgt, dlat = [1 0 -1 0 0]; dlon = [0 1 0 -1 0];
            grad_lat = (pval[0] - pval[2]) / (dlat[0] - dlat[2])
            grad_lon = (pval[1] - pval[3]) / (dlon[1] - dlon[3])

            # convert from absolute horizontal gradient to relative horizontal gradient
            beta_lat = grad_lat / pval[4]
            beta_lon = grad_lon / pval[4]

            # Note that we used central differences to compute the gradient, but beta_lat, beta_lon
            # are actually defined in terms of forward differences. Maybe we should use forward
            # difference here to be fully consistent?

        # no sporadic-E for now
        #foEs = 0.0
        #hmEs = 110.0

        # Return 11-parameter IonoState vector
        IonoState = numpy.array([foF2, hmF2, foF1, foE, hmE, B0, B1, foEs, hmEs, beta_lat, beta_lon])

        logger.debug(
            "ionoState: foF2={:.4f} hmF2={:.4f} foF1={:.4f} foE={:.4f} hmE={:.4f}, B0={:.4f} B1={:.4f},foEs={:.4f} hmEs={:.4f}, beta_lat={:.4f}  beta_lon={:.4f}". \
                format(IonoState[0], IonoState[1], IonoState[2], IonoState[3], IonoState[4], IonoState[5], \
                       IonoState[6], IonoState[7], IonoState[8], IonoState[9], IonoState[10]))
        return IonoState

    ## Plasma frequency grid generator for ROAM and JIGSE
    #
    #  @param  ionoState  - ionoState vector with 8, 9 or 11 parameters with format given below:
    #
    #  len   format
    #  ---   ------
    #    8   [foF2, hmF2, foF1, foE, B0, B1, beta_lat, beta_lon]
    #    9   [foF2, hmF2, foF1, foE, hmE, B0, B1, beta_lat, beta_lon]
    #   11   [foF2, hmF2, foF1, foE, hmE, B0, B1, foEs, hmEs, beta_lat, beta_lon]
    #
    #   Note: for the 11 parameter case the user should provide the keyword SporadicE=False or True depending
    #   on whether the density grid is to be constructed without or with the sporadic E model, respectively.
    #
    #  @param  iono_grid_parms - [lat_start,lat_inc,lat_num, lon_start,lon_inc,lon_num, hgt_start,hgt_inc,hgt_num]
    #                             latitude and longitude values in degrees, height values in km
    #  @param  Ref_lat         - latitude of pivot point where imposed ionospheric tilt is zero (deg)
    #  @param  Ref_lon         - longitude of pivot point where imposed ionospheric tilt is zero (deg)
    #  @param  DT              - python datetime struct specifying when the state is valid
    #  @param  R12             - yearly averaged sunspot number (pass -1 to use model)
    #  @param SporadicE (optional) - if 11 parameter ionoState is passed, setting this flag tells routine to
    #                              construct grid with sporadic E (using foEs and hmEs in place of foE and hmE)
    #
    #  @retval  iono_pf_grid - 3D grid of plasma frequencies (MHz)
    #
    # To do: add some optional keywords for various types of plots to be generated?
    def IonoStateToGrid(self, ionoState, iono_grid_parms, Ref_lat, Ref_lon, DT, R12, SporadicE=True):

        # extract the ionospheric grid

        lat_start = iono_grid_parms[0]
        lat_inc   = iono_grid_parms[1]
        lat_num   = iono_grid_parms[2]

        lon_start = iono_grid_parms[3]
        lon_inc   = iono_grid_parms[4]
        lon_num   = iono_grid_parms[5]

        hgt_start = iono_grid_parms[6]
        hgt_inc   = iono_grid_parms[7]
        hgt_num   = iono_grid_parms[8]

        # vectors along the hgt, lat, lon directions
        hgt_arr = numpy.arange(0,hgt_num) * hgt_inc + hgt_start
        lat_arr = numpy.arange(0,lat_num) * lat_inc + lat_start
        lon_arr = numpy.arange(0,lon_num) * lon_inc + lon_start
       

        if len(ionoState) == 8:
            # old 8 parameter ionoState: [foF2, hmF2, foF1, foE, B0, B1, beta_lat, beta_lon]
            foF2     = ionoState[0]
            hmF2     = ionoState[1]
            foF1     = ionoState[2]
            foE      = ionoState[3]
            hmE      = 110 # E-layer height fixed in this model
            B0       = ionoState[4]
            B1       = ionoState[5]
            tilt_lat = ionoState[6]
            tilt_lon = ionoState[7]

        if len(ionoState) == 9:
            # 9 parameter ionoState: [foF2, hmF2, foF1, foE, hmE, B0, B1, beta_lat, beta_lon]
            foF2     = ionoState[0]
            hmF2     = ionoState[1]
            foF1     = ionoState[2]
            foE      = ionoState[3]
            hmE      = ionoState[4]  # E-layer height fixed in this model
            B0       = ionoState[5]
            B1       = ionoState[6]
            tilt_lat = ionoState[7]
            tilt_lon = ionoState[8]

        if len(ionoState) == 11:
            # new 11 parameter IonoState: [foF2, hmF2, foF1, foE, hmE, B0, B1, foEs, hmEs, beta_lat, beta_lon]
            foF2     = ionoState[0]
            hmF2     = ionoState[1]
            foF1     = ionoState[2]
            if SporadicE==0 or ionoState[7] < 0 or ionoState[8] < 0:
                # construct a normal E layer
                foE  = ionoState[3]
                hmE  = ionoState[4]
            else:
                # print(ionoState[7], ionoState[8])
                # construct a sporadic E layer
                foE  = ionoState[7]
                hmE  = ionoState[8]
                logger.debug("ROAM will use sporadic E layer with foEs={:.4f}, hmEs={:.4f}".format(float(foE),float(hmE)))
            B0       = ionoState[5]
            B1       = ionoState[6]
            tilt_lat = ionoState[9]
            tilt_lon = ionoState[10]

        lat_total = lat_inc * (lat_num - 1)
        lon_total = lon_inc * (lon_num - 1)

        # enforce bounds on the layer parameters for non-sporadic E
        if foE > foF2 * 0.95 and not SporadicE:
            foE = foF2 * 0.95

        B0_threshold = 90; # ROAM changed this value from 90 km to 80 km on 19 April 2017, JIGSE kept the value 90 km 

        # This only sets foF1 if foE > 0 (change from above made 3/15/2017)
        if B0 < B0_threshold and foE>0:
           foF1 = 1.5*foE;

        iono_layer_parms = numpy.array([foF2, hmF2, foF1, foE, hmE, B0, B1])

        UT = numpy.array([DT.year, DT.month, DT.day, DT.hour, DT.minute])

        [iono_pf_profile, iono_extra] = self.pharlapHandle.iri2016(Ref_lat, Ref_lon, R12, UT, \
            hgt_start, hgt_inc, hgt_num, iono_layer_parms)

        # If we have it, overwrite iono_pf_profile with sounder profile if len(varargin) > 0
        #if not isempty(varargin[0])
        #   iono_pf_profile = varargin[0];

        # perturbation to F - region density only
        win_hmE = 0.2 # value of the gaussian window function at hmE
        std2 = -numpy.power((hmE - hmF2),2) / (2 * numpy.log(win_hmE)) # std of the window function
        winfun = numpy.exp(-numpy.power((hgt_arr - hmF2) , 2) / (2 * std2)) # gaussian window function


        # tilt_factor = 1 + tilt_lat * winfun * (numpy.tile(lat_arr.reshape(lat_num, 1, 1), (1, lon_num, hgt_num)) - Ref_lat) + \
        #                   tilt_lon * winfun * (numpy.tile(lon_arr.reshape(1, lon_num, 1), (lat_num, 1, hgt_num)) - Ref_lon)

        # iono_pf_grid = tilt_factor * iono_pf_profile

        # # allocate space for iono_pf_grid
        # iono_pf_grid = numpy.zeros((lat_num, lon_num, hgt_num))

        # for lonidx in range(0,lon_num):
        #     rlon1 = lon_arr[lonidx]

        #     for latidx in range(0,lat_num):
        #         rlat1 = lat_arr[latidx]

        #         # Additive model
        #         tilt_factor = 1 + tilt_lat * winfun * (rlat1 - Ref_lat) + \
        #                           tilt_lon * winfun * (rlon1 - Ref_lon)

        #         # apply modulation
        #         iono_pf_grid[latidx, lonidx,:]     = iono_pf_profile * tilt_factor



        ionoEnGrid = pfProfileToEnGrid(iono_pf_profile, winfun, tilt_lat, tilt_lon, Ref_lat, Ref_lon,
                                       lat_arr, lon_arr, hgt_arr)

        return ionoEnGrid

    # ============================================================
    #       Interface to legacy MATLAB / ROAM routines below
    # ============================================================

    ## Read the 8 parameter ionospheric state from a ROAM_ionoState.txt file
    #
    # @param ionoStatefile   - Name of the ROAM_ionoState.txt file produced by ROAM
    #
    # @param desired_UT      - 5x1 array containing UTC date and time [year, month, day, hour, minute].
    #                          The year must be in the  range 1958 - 2018
    # @param (optional)      - varargin: 2x1 array containing the latitude (deg) and longitude (deg)
    #                          of the location where the ionospheric state is to be propagated.
    # @retval ionoState      - 8 element ionospheric state [foF2 (MHz), hmF2 (km), foF1 (MHz), foE (MHz),
    #                          B0 (km), B1 (unitless), beta_lat (1/deg), beta_lon (1/deg)]
    # @retval LocAssimilated - 2x1 array containing the latitude (deg) and longitude (deg)
    #                          of the location where the ionospheric state was assimilated
    # @retval, success       - True / False (quality flag)
    #
    # Given a ROAM_ionoState.txt file produced by ROAM, the desired UT, and (optionally) a desired
    # location, compute and return the ionospheric state (optionally) accounting for TID motion.
    #
    # When the desired location is not supplied, the ionospheric state returned will be the
    # state that was assimilated at this time. No propagation of the ionospheric state is performed
    # in this case to account for TID motion. The ionospheric state returned is valid at the location
    # where it was assimilated (LocAssimilated) and should only be applied when attempting to
    # geolocate transmitter close (within 10s of km) to LocAssimilated.
    #
    # When the desired location is supplied, the ionospheric state returned will be lagged/leaded
    # in time to account from TID motion from the location it was assimilated (LocAssimilated)
    # to the location where it is desired. This is the preferred mode of operation.
    #
    # Usage:
    #
    #    1. Read ionoState but do not propagate state for TIDs
    #       [ionoState, LocAssimilated, success] = read_ionoState(ionoStateFile, desired_UT);
    #
    #    2. Read ionoState and propagate state from LocAssimilated to LocDesired
    #       [ionoState, LocAssimilated, success] = read_ionoState(ionoStateFile, desired_UT, LocDesired);
    #
    # Written by: Charles Carrano, Boston College
    # Date: May 2016
    # Revision:
    # Copyright (C) 2016 Charles Carrano & Boston College, All Rights Reserved

    def read_ionoState(self, ionoStateFile, desired_UT, *varargin):

        # read the ionoState data, skipping the first header line
        data = numpy.loadtxt(ionoStateFile,skiprows=1)

        # Code block below may have a problem if file has only one row of data
        UT        = data[:,0:5]
        ionoState = data[:,5:13]  # use this for 8 element ionoState
        #ionoState = data[:,5:19] # use this for 14 element ionoState
        Vh        = data[:,19]
        Vaz       = data[:,20]
        Ref_lat   = data[:,21]
        Ref_lon   = data[:,22]
        AoAErr    = data[:,23]

        uth = UT[:,3]+ UT[:,4]/60

        # if present, compute the latitude and longitude where the state will be applied
        if len(varargin)>0:
            arg = varargin[0]
            desired_lat = arg[0]
            desired_lon = arg[1]
            logger.info("desired_lat={:10.6f} desired_lon={:10.6f}".format(desired_lat, desired_lon))

        # ut hour of the requested time
        desired_uth = desired_UT[3]+ desired_UT[4]/60

        # a note on removing NaNs before interpolating
        #x_new = x[np.isfinite(y)]
        #y_new = y[np.isfinite(y)]

        # Matlab version used nearest neighbor interpolation, here we used linear
        interpolating_function = interpolate.interp1d(uth,Ref_lat)
        Ref_lati = interpolating_function(desired_uth)
        interpolating_function = interpolate.interp1d(uth, Ref_lon)
        Ref_loni = interpolating_function(desired_uth)
        interpolating_function = interpolate.interp1d(uth, Vh)
        Vhi = interpolating_function(desired_uth)
        interpolating_function = interpolate.interp1d(uth, Vaz)
        Vazi = interpolating_function(desired_uth)

        LocAssimilated = numpy.array([Ref_lati, Ref_loni]);

        # Obtain the propagation time shift due to TID motion, given by dt = R dot V/|V|^2,
        # where R is a vector from the assimilation location to the desired location.

        if Vhi == -1 or Vhi == 0 or len(varargin)==0:
            # if velocity is missing or desired location not specified, do not propagate ionoState in time.
            dth = 0
        else:
            LatLonDesired = numpy.array([[desired_lat * numpy.pi / 180], [desired_lon * numpy.pi / 180]])
            LatLonAssimilated = numpy.array([[Ref_lati * numpy.pi / 180], [Ref_loni * numpy.pi / 180]])

            (raz, _, rrange) = greatCircleBearingAndDistance(LatLonDesired, LatLonAssimilated, algo=1)

            Rnorth = rrange*numpy.cos(raz*numpy.pi/180)  # m
            Reast  = rrange*numpy.sin(raz*numpy.pi/180)  # m

            Vnorth = Vhi*numpy.cos(Vazi*numpy.pi/180)    # m/s
            Veast  = Vhi*numpy.sin(Vazi*numpy.pi/180)    # m/s

            dt = (Rnorth * Vnorth + Reast * Veast)/numpy.power(Vhi,2)  # sec
            dth = dt/3600  # hours
            #print('dth: ',dth)

        #logger.info("dth={:10.6f}".format(dth))

        # use linear interpolation to obtain ionoState, returning 0 if extrapolating
        ns = len(ionoState[0,:])
        ionoStatei = numpy.zeros(ns)
        for i in range(0,ns):
           interpolating_function = interpolate.interp1d(uth, ionoState[:,i], fill_value=0)
           ionoStatei[i] = interpolating_function(desired_uth + dth)

        interpolating_function = interpolate.interp1d(uth, AoAErr, fill_value=0)
        AoAErri = interpolating_function(desired_uth + dth)

        # replace extrapolated values with persistence
        if desired_uth + dth < uth[0]:
            ionoStatei = ionoState[0,:]
            AoAErri    = AoAErr[0,:]
        if desired_uth + dth > uth[-1]:  # last element
            ionoStatei = ionoState[-1,:] # last element
            AoAErri    = AoAErr[-1,:]    # last element

        if ( max(ionoStatei)!=0) and ((AoAErri < 3) or (AoAErri == 999) ):
            success = True
        else:
            success = False

        return (ionoStatei, LocAssimilated, success)

    ## Query ROAM for ionospheric state vector at given time and location
    #
    # @param UT                          - UTC time [year month day hour minute]
    # @param ionoStateFile               - Name of the ROAM_ionoState.txt file produced by ROAM
    # @param (optional) lonLatRadApplied - [longitude, latitude] in rad where the ionoState is to be applied
    # @retval ionoStateJIGSE             - IonoState used gy JIGSE [foE (Hz), foF1 (Hz), foF2 (Hz), hmF2 (m),
    #                                        B0 (m), B1, BetaLon (1/deg), BetaLat (1/deg)]
    # @retval lonLatRadAssimilated       - [longitude, latitude] in rad where ionospheric state was assimilated
    # @retval success                    - True/False (quality flag)
    #
    #  Usage:
    #
    #    1. Query ROAM ionoState but do not propagate state for TIDs
    #       (ionoStateJIGSE, lonLatRadAssimilated, success) = queryROAM(UT, ionoStateFile);
    #
    #    2. Query ROAM ionoState and propagate state from lonLatRadAssimilated to lonLatRadApplied
    #       (ionoStateJIGSE, lonLatRadAssimilated, success) = queryROAM(UT, ionoStateFile, lonLatRadApplied);
    #
    def queryROAM(self, UT, ionoStateFile, *varargin):

        if len(varargin)>0:
             # If called with optional argument lonLatRad, ionoState will be propagated to this location
             # from the location (lonLatRadAssimilated) where the data was assimilated by ROAM
             lonLatRadApplied = varargin[0] # [lon lat] (rad)
             latLonDegApplied = numpy.array([lonLatRadApplied[1], lonLatRadApplied[0]])*\
                180/numpy.pi # [lat lon] (deg)
             [ionoStateROAM, latLonDegAssimilated, success] = \
                 self.read_ionoState(ionoStateFile, UT, latLonDegApplied)
        else:
            # Otherwise, the ionospheric state will not be propagated. Instead, it is valid at the
            # location (lonLatRadAssimilated) where the data was assimilated by ROAM.
            [ionoStateROAM, latLonDegAssimilated, success] = self.read_ionoState(ionoStateFile, UT)

        # convert IonoState
        # from ROAM format [foF2(MHz), hmF2(km), foF1(MHz), foE(MHz), B0(km), B1, BetaLon(1/deg), BetaLat(1/deg)]
        # to JIGSE format [foE(Hz), foF1(Hz), foF2(Hz), hmF2(m), B0(m), B1, BetaLon(1/deg), BetaLat(1/deg)]
        ionoStateJIGSE = numpy.array([ionoStateROAM[3]*1.e6, ionoStateROAM[2]*1.e6, ionoStateROAM[0]*1.e6, \
           ionoStateROAM[1]*1000, ionoStateROAM[4]*1000, ionoStateROAM[5], ionoStateROAM[6],  \
           ionoStateROAM[7]])

        #print('queryROAM latLonRadAssimilated: ', latLonDegAssimilated)
        lonLatRadAssimilated = numpy.array([latLonDegAssimilated[1], latLonDegAssimilated[0]])*\
            numpy.pi/180 # [lon lat] in radians
        #print('queryROAM lonLatRadAssimilated: ', lonLatRadAssimilated)

        return (ionoStateJIGSE, lonLatRadAssimilated, success)

    ## Create electron density grid from a IonoState state vector in JIGSE format
    #
    # @param ionoGridParams  - Parameters of the voxel grid in PHaRLAP convention:
    #                          [latStart, latInc, numLat, lonStart, lonInc, numLon, htStart, htInc, numHt].
    #                          Note that the values are NOT in SI units. Latitude and longitude are in degrees,
    #                          Height is in km.
    #
    # @param UT              - UTC time as [year month day hour minute]
    #
    # @param ionoStateJIGSE  - ionospheric state vector used to construct electron density grid in JIGSE format. The
    #                          format differs depending on the length of the vector as noted below:
    # len  JIGSE Format
    # ---  ------------
    #  8   [foE(Hz), foF1(Hz), foF2(Hz), hmF2(km), B0(km), B1, BetaLon(1/deg), BetaLat(1/deg)]
    #  9   [foE(Hz), foF1(Hz), foF2(Hz), hmE(km), hmF2(km), B0(km), B1, BetaLon(1/deg), BetaLat(1/deg)]
    # 11   [foEs(Hz), foE(Hz), foF1(Hz), foF2(Hz), hmEs(km), hmE(km), hmF2(km), B0(km), B1, BetaLon(1/deg), BetaLat(1/deg)]
    #
    # @param lonLatRadApplied - [longitude, latitude] of the location where the state is valid in radians. This is
    #                        where delta lat and delta lon are zero when imposing the linear gradient perturbation
    #
    # @retval ionoEnGrid      - voxel grid of electron density in PHaRLAP convention. The unit is num / cm ^ 3

    def genElectronDensityGridROAM(self, ionoGridParams, UT, ionoStateJIGSE, lonLatRadApplied, SporadicE=False):

        # [ionoStateROAM] = [foF2, hmF2, foF1, foE, B0, B1, beta_lat, beta_lon], 8 element form,
        #                or [foF2, hmF2, foF1, foE, hmE, B0, B1, beta_lat, beta_lon], 9 element form
        #                or [foF2, hmF2, foF1, foE, hmE, B0, B1, foEs, hmEs, beta_lat, beta_lon], 11 element form
        #                    with plasma frequencies in MHz, heights and thicknesses in km

        if len(ionoStateJIGSE)==8:
            ionoStateROAM = numpy.array(
               [ionoStateJIGSE[2] / 1.e6, ionoStateJIGSE[3] / 1000, ionoStateJIGSE[1] / 1.e6,   # foF2, hmF2, foF1
                ionoStateJIGSE[0] / 1.e6, ionoStateJIGSE[4] / 1000, ionoStateJIGSE[5],          # foE, B0, B1
                ionoStateJIGSE[6], ionoStateJIGSE[7]])                                          # beta_lat, beta_lon

        if len(ionoStateJIGSE)==9:
            ionoStateROAM = numpy.array(
               [ionoStateJIGSE[2] / 1.e6, ionoStateJIGSE[4] / 1000, ionoStateJIGSE[1] / 1.e6,   # foF2, hmF2, foF1
                ionoStateJIGSE[0] / 1.e6, ionoStateJIGSE[3] / 1000,                             # foE, hmE
                ionoStateJIGSE[5] / 1000, ionoStateJIGSE[6],                                    # B0, B1
                ionoStateJIGSE[7], ionoStateJIGSE[8]])                                          # beta_lat, beta_lon

#        if len(ionoStateJIGSE) == 11:
#            ionoStateROAM = numpy.array(
#                [ionoStateJIGSE[3] / 1.e6, ionoStateJIGSE[6] / 1000, ionoStateJIGSE[2] / 1.e6,  # foF2, hmF2, foF1
#                 ionoStateJIGSE[1] / 1.e6, ionoStateJIGSE[5] / 1000,                            # foE, hmE
#                 ionoStateJIGSE[7] / 1000, ionoStateJIGSE[8],                                   # B0, B1
#                 ionoStateJIGSE[0] / 1.e6, ionoStateJIGSE[4] / 1000,                            # foEs, hmEs
#                 ionoStateJIGSE[9], ionoStateJIGSE[10]])                                        # beta_lat, beta_lon

        if len(ionoStateJIGSE) == 11:
            ionoStateROAM = numpy.array(
                [ionoStateJIGSE[2] / 1.e6, ionoStateJIGSE[4] / 1000, ionoStateJIGSE[1] / 1.e6,  # foF2, hmF2, foF1
                 ionoStateJIGSE[0] / 1.e6, ionoStateJIGSE[3] / 1000,                            # foE, hmE
                 ionoStateJIGSE[5] / 1000, ionoStateJIGSE[6],                                   # B0, B1
                 ionoStateJIGSE[9] / 1.e6, ionoStateJIGSE[10] / 1000,                            # foEs, hmEs
                 ionoStateJIGSE[7], ionoStateJIGSE[8]])                                        # beta_lat, beta_lon


        Ref_lat = lonLatRadApplied[1] * 180 / numpy.pi # latitude in degrees
        Ref_lon = lonLatRadApplied[0] * 180 / numpy.pi # longitude in degrees

        R12 = -1
        DT = datetime(UT[0],UT[1],UT[2],UT[3],UT[4],0)
        ionoEnGrid = self.IonoStateToGrid(ionoStateROAM, ionoGridParams, Ref_lat, Ref_lon, DT, R12, SporadicE=SporadicE)

        # # convert from plasma freq (MHz) to electron density in cm ^ -3
        # pftoden = 80.6164e-6
        # ionoEnGrid = numpy.power(ionoPfGrid,2) / pftoden # cm ^ -3
        # return ionoEnGrid.transpose()
        return ionoEnGrid

#
# Unit tests
#

class UnitTest_ROAM(unittest.TestCase):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # get the Pharlap interface
        self.pharlapHandle = Pharlap()

        # get the IRTAM interface
        self.irtamHandle = IrtamPyIface()

    def test_CalcIonoState_RIPE(self):
        import IonoModelEngine.Config.ConfigValues as ConfigValues
        from numpy.testing import assert_approx_equal
        logger.info("test_CalcIonoState_RIPE")

        # Location of test files
        directory = os.path.dirname(os.path.realpath(__file__)) + "/../RIPE"

        # Setup the input into ROAM
        listOfFiles = {}
        listOfFiles['noaa'] = [directory + '/TestFiles/AU930_NOAA.TXT', \
                               directory + '/TestFiles/BC840_NOAA.TXT', \
                               directory + '/TestFiles/EG931_NOAA.TXT']
        listOfFiles['giro'] = []
        listOfFiles['localDigisonde'] = []

        # First construct a config file for ROAM
        self.config = ConfigValues.ROAMConfig()

        # Tell roam to use RIPE
        self.config.backgroundModel = 'ripe'

        # instantiate ROAM
        self.roam = ROAM(self.config, self.irtamHandle, self.pharlapHandle)

        self.roam.refreshIRI = 0

        # G10 receiver location
        lat = 32.4824
        lon = -106.3809
        UT = numpy.array([2015, 10, 20, 0, 0])
        DT = datetime(UT[0], UT[1], UT[2], UT[3], UT[4], 0)

        state = self.roam.CalcIonoState(lat, lon, DT, listOfFiles)

        logger.info(
            "ROAM foF2={:.4f} hmF2={:.4f} foF1={:.4f} foE={:.4f} hmE={:.4f} B0={:.4f} B1={:.4f} foEs={:.4f} hmEs={:.4f} beta_lat={:.4f} beta_lon={:.4f}". \
                format(state[0], state[1], state[2], state[3], state[4], state[5], \
                       state[6], state[7], state[8], state[9], state[10]))

        # Output from Matlab run of roam_using_ripe_testfiles_20151020.m followed by roam_using_ripe.m
        # YEAR MON DAY  HR MIN       foF2      hmF2      foF1       foE        B0        B1   gradLat   gradLon    ... Ref_lat   Ref_lon    AoAErr
        # 2015  10  20  00  00     9.2822  257.5859   -1.0000    1.8131   61.7588    2.5061   -0.0144   -0.0038        32.4824 -106.3809    0.0000

        assert_approx_equal(state[0],   9.2822,  significant=3)   # foF2
        assert_approx_equal(state[1], 257.5859, significant=3)    # hmF2
        assert_approx_equal(state[2],     -1.0,  significant=3)   # foF1
        assert_approx_equal(state[3],   1.8131,  significant=3)   # foE
        assert_approx_equal(state[5],  61.7588,  significant=1)   # B0
        assert_approx_equal(state[6],   2.5061,  significant=2)   # B1
        assert_approx_equal(state[9],  -0.0144,  significant=3)   # gradLat
        assert_approx_equal(state[10], -0.0038,  significant=3)   # gradLon

        return

    def test_CalcIonoState_RIPEwithIRTAM(self):
        import IonoModelEngine.Config.ConfigValues as ConfigValues
        from numpy.testing import assert_approx_equal
        logger.info("test_CalcIonoState_RIPEwithIRTAM")

        # Location of test files
        directory = os.path.dirname(os.path.realpath(__file__))  + '/'

        # Setup the input into ROAM
        listOfFiles = {}
        listOfFiles['noaa'] = [directory + '../RIPE/TestFiles/AU930_NOAA.TXT', \
                               directory + '../RIPE/TestFiles/BC840_NOAA.TXT', \
                               directory + '../RIPE/TestFiles/EG931_NOAA.TXT']
        listOfFiles['giro'] = [directory + '../IRTAM/UnitTestData/IRTAM_foF2_COEFFS_20151020_0000.ASC', \
                               directory + '../IRTAM/UnitTestData/IRTAM_hmF2_COEFFS_20151020_0000.ASC', \
                               directory + '../IRTAM/UnitTestData/IRTAM_B0_COEFFS_20151020_0000.ASC', \
                               directory + '../IRTAM/UnitTestData/IRTAM_B1_COEFFS_20151020_0000.ASC']
        listOfFiles['localDigisonde'] = []

        # First construct a config file for ROAM
        self.config = ConfigValues.ROAMConfig()

        # Tell roam to use RIPE with IRTAM
        self.config.backgroundModel = 'ripe-irtam'
        #self.config.synopticTilt = 0

        # instantiate ROAM
        self.roam = ROAM(self.config, self.irtamHandle, self.pharlapHandle)

        self.roam.refreshIRI = 0


        # G10 receiver location
        lat = 32.4824
        lon = -106.3809
        UT = numpy.array([2015, 10, 20, 0, 0])
        DT = datetime(UT[0], UT[1], UT[2], UT[3], UT[4], 0)

        state = self.roam.CalcIonoState(lat, lon, DT, listOfFiles)

        logger.info(
            "ROAM foF2={:.4f} hmF2={:.4f} foF1={:.4f} foE={:.4f} hmE={:.4f} B0={:.4f} B1={:.4f} foEs={:.4f} hmEs={:.4f} beta_lat={:.5f} beta_lon={:.5f}". \
                format(state[0], state[1], state[2], state[3], state[4], state[5], \
                       state[6], state[7], state[8], state[9], state[10]))

        # Output from Matlab run of roam_using_ripe_testfiles_20151020.m followed by roam_using_ripe.m
        # YEAR MON DAY  HR MIN       foF2      hmF2      foF1       foE        B0        B1   gradLat   gradLon    ... Ref_lat   Ref_lon    AoAErr
        # 2015  10  20  00  00     9.2822  257.5859   -1.0000    1.8131   61.7588    2.5061   -0.0144   -0.0038        32.4824 -106.3809    0.0000
        # foF2, hmF2, B0, B1 in this unit test are from RIPE.py using ripe-irtam option
        # [RIPE.py: 666] RIPE foF2 = 9.5167 hmF2 = 259.2598 B0 = 69.4209 B1 = 2.3416
        # [ROAM.py:759] ROAM  foF2 = 9.5167 hmF2 = 259.2598 foF1 = -1.0000 foE = 1.8131 hmE = 110.0000 B0 = 69.4209 B1 = 2.3416 \
        #        foEs = 0.0000 hmEs = 110.0000 beta_lat=-0.01840 beta_lon=-0.00578

        assert_approx_equal(state[0],   9.5167,  significant=3)   # foF2
        assert_approx_equal(state[1], 259.2598, significant=3)    # hmF2
        assert_approx_equal(state[2],     -1.0,  significant=3)   # foF1
        assert_approx_equal(state[3],   1.8131,  significant=3)   # foE
        assert_approx_equal(state[5],  69.4209,  significant=1)   # B0
        assert_approx_equal(state[6],   2.3416,  significant=2)   # B1
        assert_approx_equal(state[9],  -0.01840,  significant=3)   # gradLat
        assert_approx_equal(state[10], -0.00578,  significant=3)   # gradLon

        return

    def test_CalcIonoState_IRTAM(self):
        import IonoModelEngine.Config.ConfigValues as ConfigValues
        from numpy.testing import assert_approx_equal
        logger.info("test_CalcIonoState_IRTAM")

        directory = os.path.dirname(os.path.realpath(__file__)) + "/UnitTestData/"
        
        # Setup the input into ROAM
        listOfFiles = {}
        listOfFiles['giro'] = [directory + 'IRTAM_foF2_COEFFS_20151020_0000.ASC', \
                               directory + 'IRTAM_hmF2_COEFFS_20151020_0000.ASC', \
                               directory + 'IRTAM_B0_COEFFS_20151020_0000.ASC', \
                               directory + 'IRTAM_B1_COEFFS_20151020_0000.ASC']
        listOfFiles['noaa'] = []
        listOfFiles['localDigisonde'] = []

        # First construct a config file for ROAM
        self.config = ConfigValues.ROAMConfig()
        # Tell roam to use IRTAM
        self.config.backgroundModel = 'irtam'

        # instantiate ROAM
        self.roam = ROAM(self.config, self.irtamHandle, self.pharlapHandle)

        # G10 receiver location
        lat = 32.4824
        lon = -106.3809
        UT = numpy.array([2015, 10, 20, 0, 0])
        DT = datetime(UT[0], UT[1], UT[2], UT[3], UT[4], 0)

        #self.roam.background_model = 2  # force use of IRTAM
        #self.roam.noaaConfig = []       # force use of IRTAM

        state = self.roam.CalcIonoState(lat, lon, DT, listOfFiles)

        logger.info(
             "ROAM foF2={:.4f} hmF2={:.4f} foF1={:.4f} foE={:.4f} hmE={:.4f} B0={:.4f} B1={:.4f} foEs={:.4f} hmEs={:.4f} beta_lat={:.4f} beta_lon={:.4f}". \
                 format(state[0], state[1], state[2], state[3], state[4], state[5], \
                        state[6], state[7], state[8], state[9], state[10]))

        # Output from ROAM.py running IRTAM
        # [ROAM.py:176] IRTAM data: foF2=8.7484 hmF2=252.7329 B0=59.5018 B1=3.1669
        # [ROAM.py:734] ROAM foF2=8.7484 hmF2=252.7329 foF1=-1.0000 foE=1.8131 hmE=110.0000 B0=59.5018 B1=3.1669 ...
        #                   foEs=0.0000 hmEs=110.0000 beta_lat=-0.0085 beta_lon=-0.0116

        assert_approx_equal(state[0],   8.7484, significant=3)  # foF2
        assert_approx_equal(state[1], 252.7329, significant=3)  # hmF2
        assert_approx_equal(state[2],     -1.0, significant=3)  # foF1
        assert_approx_equal(state[3],   1.8131, significant=3)  # foE
        assert_approx_equal(state[5],  59.5018, significant=3)  # B0
        assert_approx_equal(state[6],   3.1669, significant=3)  # B1
        assert_approx_equal(state[9],  -0.0085, significant=3)  # gradLat
        assert_approx_equal(state[10], -0.0116, significant=3)  # gradLon

        return

# include tests with / without Sporadic-E, with/without desired location, grid generation using 8 and 11 element states

if __name__ == "__main__":
    unittest.main()
