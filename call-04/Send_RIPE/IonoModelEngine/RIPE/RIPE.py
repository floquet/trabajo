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

from datetime import timedelta
from datetime import datetime
from copy import copy
import os
import unittest
from numpy import median
from numpy import mean
from numpy import asscalar
from numpy import array
from scipy.interpolate import griddata
from Shared.IonoPyIface.Pharlap import Pharlap
import Shared.Utils.HfgeoLogger as Logger
from IonoModelEngine.DataControl.Stations import getStationLatLon

from IonoModelEngine.IRTAM import IRTAM
from IonoModelEngine.IRTAM.IrtamPyIface import IrtamPyIface

logger = Logger.getLogger()

## @package IonoModelEngine.RIPE
# Python implementation of the Robust Initial Profile Estimator (RIPE)

class RIPE:
    ## Constructor requests the python interface
    #
    def __init__(self, pharlapHandle=None, irtamHandle=None, refreshIRI=None, interpolatingModel=None):

        # Handle to the pharlap interface
        self.pharlapHandle = pharlapHandle

        # Handle to IRTAM
        self.irtamHandle = irtamHandle

        # (0=use IRI parameters from the input file, if present, 1=recalculate)
        if not refreshIRI:
            self.refreshIRI  = False
        else:
            self.refreshIRI = refreshIRI

        # select model used for interpolation/extrapolation (0=IRI, 1=IRTAM)
        if not interpolatingModel:
            self.interpolatingModel  = 0
        else:
            self.interpolatingModel = interpolatingModel

    ## Calculates RIPE5 scale factors from all sounders for a given target time
    #
    #  @param TargetTime - the time of interest (a python datetime structure)
    #  @param listOfFiles - a list of full paths to the RIPE input files for all stations
    #  @param stationList - a list of the tuples (Name, Latitude, Longitude) for all stations
    #
    #  @retval stlats - station latitude (deg)
    #  @relval stlons - station longitude (deg)
    #  @relval fof2_rats - sounder foF2 divided by IRI prediction for current_time and sounder location
    #  @retval hmf2_rats - sounder hmF2 divided by IRI prediction for current_time and sounder location
    #  @retval b0_rats   - sounder B0 divided by IRI prediction for current_time and sounder location
    #  @retval b1_rats   - sounder B1 divided by IRI prediction for current_time and sounder location
    #
    #  benchmark code by wjm
    #
    #  revision history
    #    2017/10/01 - original
    #    2018/01/22 - if station file is not present, process all parameter files in desired directory
    #    2018/02/05 - read input files in same format as the Matlab version of RIPE
    #    2018/10/31 - added foEs, hmEs. fixed nan handling 

    def GetRIPE5sfs(self, TargetTime, listOfFiles):

        logger.info("RIPE TargetTime {:4d}-{:2d}-{:2d} {:2d}:{:2d}:{:2d}".\
                    format(TargetTime.year,TargetTime.month,TargetTime.day,
                           TargetTime.hour,TargetTime.minute,TargetTime.second))

        #   get the start and end time for the 3-hour median taking
        start_time = TargetTime - timedelta(hours=1, minutes=31)
        end_time   = TargetTime + timedelta(hours=1, minutes=31)

        # start new lists of median values for each station
        stlats_median = []
        stlons_median = []
        fof2_rats_median = []
        hmf2_rats_median = []
        b0_rats_median = []
        b1_rats_median = []
        foEs_max       = []
        hmEs_median    = []
       
        foEs_data = []
        hmEs_data = [] 

        # Loop through each file in the list of files
        for fname in listOfFiles:

            # valid RIPE files are of the form XXXXX_NOAA.TXT, where XXXXX is the 5 character URSI code for the station

            # get station name from the file basename
            stationName = os.path.basename(fname)

            # check that filename is the right length
            if len(stationName) != 14:
                logger.debug("{:s} filename is too short, skipping".format(stationName))
                continue

            # check that filename has the right suffix
            if stationName[5:14] != '_NOAA.TXT':
                logger.debug(" {:s} filename is missing _NOAA.TXT suffix, skipping".format(stationName))
                continue

            logger.info("Processing RIPE file {:s}".format(fname))

            stationName = stationName[0:5]
            (stationLat,stationLon) = getStationLatLon(stationName)

            # get empty lists for the ratios for this station
            fof2_rats = []
            hmf2_rats = []
            b0_rats   = []
            b1_rats   = []
            foEs      = []
            hmEs      = []

            try:
                with open(fname, 'r') as f:

                    linelist = f.readlines()
                    for line in linelist:

                        # skip over an optional header line
                        if line[0:4] == 'yyyy':
                            #print('Skipping this header line')
                            continue

                        data = line.split()
                        logger.debug(line)

                        # skip over an optional blank line
                        if not data:
                            #print('Skipping this blank line')
                            continue

                        tempstr = data[0]
                        tempstr = tempstr.split('.')
                        year  = int(tempstr[0])
                        month = int(tempstr[1])
                        day   = int(tempstr[2])

                        tempstr = data[2]
                        tempstr = tempstr.split(':')

                        hour   = int(tempstr[0])
                        minute = int(tempstr[1])
                        second = int(tempstr[2])

                        data_time = datetime(year, month, day, hour, minute, second)

                        cflag = int(data[3])   # quality added 1/9/2018

                        # take only the data from a 3-hour window centered on the target time
                        if start_time < data_time < end_time:
                            #print('keep')

                            # use interpolating model (IRI or IRTAM) to compute parameters at the station locations

                            if self.interpolatingModel ==0: # IRI
                                if len(data)<16 or self.refreshIRI>0:
                                    # Call IRI to obtain the 4 parameters foF2,hmF2,b0,b1
                                    UT = array([data_time.year, data_time.month, data_time.day, \
                                                data_time.hour, data_time.minute])
                                    R12=-1
                                    (pf,extra) = self.pharlapHandle.iri2016(stationLat, stationLon, R12, UT)
                                    parms = self.pharlapHandle.iono_extra_to_layer_parameters(extra)
                                    fof2_imodel = parms[0]
                                    hmf2_imodel = parms[1]
                                    b0_imodel   = parms[5]
                                    b1_imodel   = parms[6]
                                    logger.info("IRI parameters for {:s} {:8.1f} {:8.1f} {:8.4f} {:8.4f} {:8.4f} {:8.4f}". \
                                                format(stationName, stationLat, stationLon, \
                                                       fof2_imodel, hmf2_imodel, b0_imodel, b1_imodel))
                                else:
                                    # use IRI values from the input files
                                    fof2_imodel = float(data[15])
                                    hmf2_imodel = float(data[16])
                                    b0_imodel   = float(data[17])
                                    b1_imodel   = float(data[18])

                            if self.interpolatingModel == 1: # IRTAM
                                # Call IRTAM to obtain the 4 parameters foF2,hmF2,b0,b1

                                # Get the interface to IRTAM
                                irtam = IRTAM.IRTAM(self.irtamHandle, self.pharlapHandle)

                                # Calculate IRTAM parameters
                                (fof2_imodel, hmf2_imodel, b0_imodel, b1_imodel) = \
                                    irtam.CalcParameters(stationLat, stationLon, data_time, listOfFiles)

                            # decode the parameters and check to see if they are blank (---)

                            ifgood = 1

                            fof2_temp = data[4]
                            if fof2_temp == '---':
                                ifgood = 0
                            else:
                                fof2_data = float(fof2_temp)

                            hmf2_temp = data[9]
                            if hmf2_temp == '---':
                                ifgood = 0
                            else:
                                hmf2_data = float(hmf2_temp)

                            b0_temp = data[12]
                            if b0_temp == '---':
                                ifgood = 0
                            else:
                                b0_data = float(b0_temp)

                            b1_temp = data[13]
                            if b1_temp == '---':
                                ifgood = 0
                            else:
                                b1_data = float(b1_temp)

                            ## Only get Es parameters within +/- 20 min of target time
                            timeDiff = (TargetTime - data_time).total_seconds()
                            if abs(timeDiff) <= 1200:

                               foEs_temp = data[7]
                               if foEs_temp == '---':
                                  foEs_data = []
                               else:
                                  foEs_data = float(foEs_temp)

                               hmEs_temp = data[8]
                               if hmEs_temp == '---':
                                  hmEs_data = []
                               else:
                                  hmEs_data = float(hmEs_temp)



                            # only accept records with all four parameters present
                            if ifgood == 1:
                                fof2_rats.append(fof2_data/fof2_imodel)
                                hmf2_rats.append(hmf2_data/hmf2_imodel)
                                b0_rats.append(b0_data/b0_imodel)
                                b1_rats.append(b1_data/b1_imodel)
                                if foEs_data:
                                   foEs.append(foEs_data)
                                if hmEs_data: 
                                   hmEs.append(hmEs_data) 

                    logger.info("Read {:s}".format(fname))
                    f.close()

                # calculate median values of the ratios for each station

                nratios = len(fof2_rats)

                logger.info("Read {:d} points for {:s} ".format(nratios, stationName))

                if len(foEs):
                   foEs_max.append(max(foEs))
                if len(hmEs): 
                   hmEs_median.append(median(hmEs))



                if nratios >= 3:
                    # compute median values
                    stlats_median.append(stationLat)
                    stlons_median.append(stationLon)
                    fof2_rats_median.append(median(fof2_rats))
                    hmf2_rats_median.append(median(hmf2_rats))
                    b0_rats_median.append(median(b0_rats))
                    b1_rats_median.append(median(b1_rats))
                elif nratios > 0:
                    # not enough points to compute median, use mean instead
                    stlats_median.append(stationLat)
                    stlons_median.append(stationLon)
                    fof2_rats_median.append(mean(fof2_rats))
                    hmf2_rats_median.append(mean(hmf2_rats))
                    b0_rats_median.append(mean(b0_rats))
                    b1_rats_median.append(mean(b1_rats))
                else:
                    logger.info("No data to compute median")


            except IOError:
                logger.critical("Could not open {:s}".format(fname))

        if len(foEs_max):
           foEs_max_value = max(foEs_max)
        else:
          foEs_max_value = -1 
        if len(hmEs_median): 
           hmEs_median_value = median(hmEs_median)
        else:
           hmEs_median_value = -1

        # write the median info this station to logger
        logger.info("Median ratios for {:s} {:8.1f} {:8.1f} {:8.4f} {:8.4f} {:8.4f} {:8.4f}".\
                   format(stationName, stationLat, stationLon, \
                          fof2_rats_median[-1],hmf2_rats_median[-1],b0_rats_median[-1],b1_rats_median[-1]))

        
        return (stlats_median, stlons_median, fof2_rats_median, hmf2_rats_median, b0_rats_median, b1_rats_median,\
                foEs_max_value, hmEs_median_value)


    ## Interpolate a value to some target location given its values at the stations
    #
    #  @param lats   - list of station latitudes (deg)
    #  @param lons   - list of station longitudes (deg)
    #  @param values - list of station values (some quantity that we wished to interpolate)
    #  @param TLat   - target latitude (deg)
    #  @param Tlon   - target longitude (deg)
    #
    #  @retval value - the value interpolated to the target lat and lon
    #
    #  benchmark routine by WJM
    #
    #  revision history
    #    2017/10/01 - original
    #    2017/10/06 - added the copy() routine to replace the look
    #                 that reassigned lats,lons,values to internal lists
    #                 to which we could then add boundary conditions
    #    2017/10/16 - revised to work in any longitude sector
    #
    def InterpRIPE5(self, Lats,Lons,Values,TLat,TLonIn):

        # keep the longitude positive for now
        #
        TLon=TLonIn
        if TLon < 0.0:
            TLon=TLon+360.0

        nin=len(Lats)

        # send back a one if there are no valid ratios
        #
        if nin == 0:
          return(1.0)

        # and send back the single value if there's only one ratio
        #
        if nin == 1:
          return(Values[0])

        # take an average for outside the grid
        #
        ValAve=sum(Values)/float(nin)

        # set the arrays with append as it seems that python
        # will keep the last set if we don't restart the arrays
        #
        Lats1=copy(Lats)
        Lons1=copy(Lons)
        Vals1=copy(Values)

        # first we take care of the case where the stations are on
        # both sides of the prime meridian
        #
        LonDel=max(Lons1)-min(Lons1)

        if LonDel > 180.0:
            for i in range(0,nin):
                if Lons[i] > 180.0:
                    Lons[i]=Lons[i]-360.0
 
        # now we get the midpoint for modulation of the target longitude
        #
        MidLon=sum(Lons1)/float(nin)

        # see if the target longitude is a hemisphere to the east
        # of the stations and modulate if necessary
        #
        if TLon-MidLon > 180.0:
            TLon=TLon-360.0

        # and see if the target longitude is a hemisphere west
        #
        if MidLon-TLon > 180.0:
            TLon=TLon+360.0

        # now set the corners of the theater
        #
        BLLat=min(Lats1)-45.0
        BLLon=min(Lons1)-90.0

        BRLat=min(Lats1)-45.0
        BRLon=max(Lons1)+90.0

        TRLat=max(Lats1)+45.0
        TRLon=max(Lons1)+90.0

        TLLat=max(Lats1)+45.0
        TLLon=min(Lons1)-90.0

        # append the corner locations to the arrays
        #
        Lats1.append(BLLat)
        Lons1.append(BLLon)
        Vals1.append(ValAve)

        Lats1.append(BRLat)
        Lons1.append(BRLon)
        Vals1.append(ValAve)

        Lats1.append(TRLat)
        Lons1.append(TRLon)
        Vals1.append(ValAve)

        Lats1.append(TLLat)
        Lons1.append(TLLon)
        Vals1.append(ValAve)

        # interpolate to this location
        #
        value=griddata((Lats1,Lons1),Vals1,(TLat,TLon),fill_value=ValAve,method='linear')

        # make into a scalar as griddata seems to return a matrix
        #
        value=asscalar(value)

        return(value)

    ## Call InterpRIPE5 to interpolate the four scale factors
    #
    #  @param Tlat - target latitude where RIPE ratios are desired (deg)
    #  @param Tlon - target longitude where RIPE ratios are desired (deg)
    #  @param lats - list of station latitudes (deg)
    #  @param lons - list of station longitudes (deg)
    #  @param fof2_rats - list of sounder foF2 / IRI foF2 values
    #  @param hmf2_rats - list of sounder hmF2 / IRI hmF2 values
    #  @param b0_rats - list of sounder B0 / IRI B0 values
    #  @param b1_rats - list of sounder B1 / IRI B1 values
    #
    def InterpRIPE5sfs(self, TLat, TLonIn, lats, lons, fof2_rats, hmf2_rats, b0_rats, b1_rats):

        # keep the input longitude on [0,360]
        #
        TLon=TLonIn
        if TLon < 0.0:
            TLon=TLon+360.0

        fof2_rat = self.InterpRIPE5(lats,lons,fof2_rats,TLat,TLon)

        hmf2_rat = self.InterpRIPE5(lats,lons,hmf2_rats,TLat,TLon)

        b0_rat   = self.InterpRIPE5(lats,lons,b0_rats,TLat,TLon)

        b1_rat   = self.InterpRIPE5(lats,lons,b1_rats,TLat,TLon)

        if fof2_rat==1 and hmf2_rat==1 and b0_rat==1 and b1_rat==1:
            logger.warning("All ratios are unity, result will be IRI")

        return (fof2_rat,hmf2_rat,b0_rat,b1_rat)

    ## Obtain the parameters foF2, hmF2, B0, B1 using the RIPE model
    #
    #  @param lat    - latitude where the state is desired (degrees)
    #  @param lon    - longitude where the state is desired (degrees)
    #  @param DT     - python datetime struct specifying when the state is desired
    #  @param listOfStations - list of full path to station files
    #
    #  @retval [foF2, hmF2, B0, B1]
    #
    def CalcParameters(self, lat, lon, DT, listOfFiles):

        if self.interpolatingModel == 0:

            UT = array([DT.year, DT.month, DT.day, DT.hour, DT.minute])

            R12 = -1 # a placeholder for now (consider passing this as input?)

            (iono_pf, iono_extra) = self.pharlapHandle.iri2016(lat, lon, R12, UT)

            layer_parameters = self.pharlapHandle.iono_extra_to_layer_parameters(iono_extra)

            foF2 = layer_parameters[0]
            hmF2 = layer_parameters[1]
            B0   = layer_parameters[5]
            B1   = layer_parameters[6]

        if self.interpolatingModel == 1:

            # Get the interface to IRTAM
            irtam = IRTAM.IRTAM(self.irtamHandle, self.pharlapHandle)

            # Calculate IRTAM parameters
            (foF2, hmF2, B0, B1) = irtam.CalcParameters(lat, lon, DT, listOfFiles)

        (lat_all, lon_all, \
        foF2_ratio_all, hmF2_ratio_all, \
        B0_ratio_all, B1_ratio_all, foEs, hmEs) = self.GetRIPE5sfs(DT, listOfFiles)

        nratios = len(foF2_ratio_all)
        if nratios == 0:
            logger.warning('No ratios found, returning parameters from IRI')
            return (foF2, hmF2, B0, B1)


        # Apply RIPE model
        ripe_scale_factors = self.InterpRIPE5sfs(lat, lon, lat_all, lon_all, \
                                                 foF2_ratio_all, hmF2_ratio_all, \
                                                 B0_ratio_all, B1_ratio_all)

        logger.info("Interpolated fof2_rat={:8.4f} hmf2_rat={:8.4f} b0_rat={:8.4f} b1_rat={:8.4f}". \
                    format(ripe_scale_factors[0], ripe_scale_factors[1], ripe_scale_factors[2], ripe_scale_factors[3]))

        # adjust IRI bottomside  parameters for consistency with sounder data
        foF2 = foF2 * ripe_scale_factors[0]
        hmF2 = hmF2 * ripe_scale_factors[1]
        B0   = B0   * ripe_scale_factors[2]
        B1   = B1   * ripe_scale_factors[3]

        return (foF2, hmF2, B0, B1, foEs, hmEs)

class UnitTest_RIPE(unittest.TestCase):

    def setUp(self):

        pharlapHandle = Pharlap()

        irtamHandle = IrtamPyIface()

        #irtamPyToCHandle = IrtamPyIface()
        #irtamHandle = IRTAM.IRTAM(irtamPyToCHandle, pharlapHandle)

        self.ripe = RIPE(pharlapHandle, irtamHandle)


    ##   Test evaluation of RIPE5 scale factors
    #
    def test_RIPE(self):

        from numpy.testing import assert_approx_equal
        logger.info("test_RIPE")

        year   = 2015
        month  = 10
        day    = 20
        hour   = 0
        minute = 0
        second = 0

        TargetTime = datetime(year, month, day, hour, minute, second)

        directory = os.path.dirname(os.path.realpath(__file__)) + "/"

        listOfFiles = [directory + '/TestFiles/AU930_NOAA.TXT', \
                       directory + '/TestFiles/BC840_NOAA.TXT', \
                       directory + '/TestFiles/EG931_NOAA.TXT']

        logger.info(" -------------- Test GetRIPE5sfs -------------")

        #(lats, lons, fof2_rats, hmf2_rats, b0_rats, b1_rats) \
        #    = self.ripe.GetRIPE5sfs(TargetTime, listOfFiles)

        (lats, lons, fof2_rats, hmf2_rats, b0_rats, b1_rats, foEs, hmEs) \
            = self.ripe.GetRIPE5sfs(TargetTime, listOfFiles)

        #
        #   Test interpolation of rations of location below
        #
        logger.info(" -------------- Test InterpRIPE5sfs -------------")

        Lat = 47.6
        Lon = -122.3

        (fof2_rat, hmf2_rat, b0_rat, b1_rat) \
            = self.ripe.InterpRIPE5sfs(Lat, Lon, lats, lons, fof2_rats, hmf2_rats,
                             b0_rats, b1_rats)

        logger.info(
            "RIPE foF2_rats={:.4f} hmF2_rats={:.4f} B0_rats={:.4f} B1_rats={:.4f}".\
                format(fof2_rat, hmf2_rat, b0_rat, b1_rat))

        # results from Matlab/RIPE5 at (Lat = 47.6, Lon = -122.3) when processing using coefficients dated 3,23,2017
        #    AU930_ROAM.TXT, BC840_ROAM.TXT, EG931_ROAM.TXT in TestFiles/
        #assert_approx_equal(fof2_rat, 1.129529902081697, significant=3)
        #assert_approx_equal(hmf2_rat, 0.956087445965192, significant=3)
        #assert_approx_equal(b0_rat,   0.861644772832245, significant=3)
        #assert_approx_equal(b1_rat,   0.946558610019847, significant=3)

        # results from Matlab/RIPE5 at (Lat = 47.6, Lon = -122.3) when processing
        #    AU930_ROAM.TXT, BC840_ROAM.TXT, EG931_ROAM.TXT in TestFiles/ using coefficients dated 1,21,2016
        assert_approx_equal(fof2_rat,  1.117654972527, significant=2)
        assert_approx_equal(hmf2_rat,  0.962435445414, significant=1)
        assert_approx_equal(b0_rat,    0.860382301559, significant=2)
        assert_approx_equal(b1_rat,    0.969161658709, significant=1)

        #
        # Test CalcParameters
        #
        logger.info(" -------------- Test CalcParameters -------------")
        (foF2, hmF2, B0, B1, foEs, hmEs) = self.ripe.CalcParameters(Lat, Lon, TargetTime, listOfFiles)
        logger.info("Test Location, lat={:8.1f} lon={:8.1f}".format(Lat, Lon))

        if not foEs:
           foEs = -1 
        if not hmEs:
           hmEs = -1 
      
        logger.info(
            "RIPE foF2={:.4f} hmF2={:.4f} B0={:.4f} B1={:.4f} foEs={:.4f} hmEs={:.4f}".\
                  format(foF2, hmF2, B0, B1, foEs, hmEs))

        # results from Matlab/RIPE5 at (Lat = 47.6, Lon = -122.3) when processing
        #    AU930_ROAM.TXT, BC840_ROAM.TXT, EG931_ROAM.TXT in TestFiles/ using coefficients dated  3,23,2017
        #assert_approx_equal(foF2, 8.568850986881225,     significant=3)
        #assert_approx_equal(hmF2, 2.399280262804014e+02, significant=3)
        #assert_approx_equal(B0,   62.514769788668012,    significant=3)
        #assert_approx_equal(B1,   2.344015669853408,     significant=3)

        # results from Matlab/RIPE5 at (Lat = 47.6, Lon = -122.3) when processing
        #    AU930_ROAM.TXT, BC840_ROAM.TXT, EG931_ROAM.TXT in TestFiles/ using coefficients dated 1,21,2016
        assert_approx_equal(foF2,   8.561080098985, significant=3)
        assert_approx_equal(hmF2, 258.916546420327, significant=2)
        assert_approx_equal(B0,    64.596487326092, significant=1)
        assert_approx_equal(B1,     2.333015488013, significant=2)


    def test_RIPEwithIRTAM(self):

        from numpy.testing import assert_approx_equal
        logger.info("test_RIPEwithIRTAM")

        year   = 2015
        month  = 10
        day    = 20
        hour   = 0
        minute = 0
        second = 0

        TargetTime = datetime(year, month, day, hour, minute, second)

        directory = os.path.dirname(os.path.realpath(__file__)) + "/"

        listOfFiles = [directory + '/TestFiles/AU930_NOAA.TXT', \
                       directory + '/TestFiles/BC840_NOAA.TXT', \
                       directory + '/TestFiles/EG931_NOAA.TXT', \
                       directory + '../IRTAM/UnitTestData/IRTAM_foF2_COEFFS_20151020_0000.ASC', \
                       directory + '../IRTAM/UnitTestData/IRTAM_hmF2_COEFFS_20151020_0000.ASC', \
                       directory + '../IRTAM/UnitTestData/IRTAM_B0_COEFFS_20151020_0000.ASC', \
                       directory + '../IRTAM/UnitTestData/IRTAM_B1_COEFFS_20151020_0000.ASC']


        logger.info(" -------------- Test GetRIPE5sfs -------------")

        self.ripe.interpolatingModel = 1

        #(lats, lons, fof2_rats, hmf2_rats, b0_rats, b1_rats) \
        #    = self.ripe.GetRIPE5sfs(TargetTime, listOfFiles)

        (lats, lons, fof2_rats, hmf2_rats, b0_rats, b1_rats, foEs, hmEs) \
            = self.ripe.GetRIPE5sfs(TargetTime, listOfFiles)

        #
        #   Test interpolation of rations of location below
        #
        logger.info(" -------------- Test InterpRIPE5sfs -------------")

        #Lat = 47.6
        #Lon = -122.3
        Lat = 32.4824
        Lon = -106.3809

        (fof2_rat, hmf2_rat, b0_rat, b1_rat) \
            = self.ripe.InterpRIPE5sfs(Lat, Lon, lats, lons, fof2_rats, hmf2_rats,
                             b0_rats, b1_rats)

        logger.info(
            "RIPE foF2_rats={:.4f} hmF2_rats={:.4f} B0_rats={:.4f} B1_rats={:.4f}".\
                format(fof2_rat, hmf2_rat, b0_rat, b1_rat))


        # results from Python/RIPE5 at (Lat = 47.6, Lon = -122.3) when processing
        #    AU930_ROAM.TXT, BC840_ROAM.TXT, EG931_ROAM.TXT in TestFiles/ using coefficients dated 1,21,2016
        #    and using IRTAM as the interpolating Model
        # foF2_rats = 1.0163, hmF2_rats = 1.0067, B0_rats = 1.0652, B1_rats = 0.7829
        #assert_approx_equal(fof2_rat,  1.0163, significant=2)
        #assert_approx_equal(hmf2_rat,  1.0067, significant=1)
        #assert_approx_equal(b0_rat,    1.0652, significant=2)
        #assert_approx_equal(b1_rat,    0.7829, significant=1)

        #
        # Test CalcParameters
        #
        logger.info(" -------------- Test CalcParameters -------------")
        (foF2, hmF2, B0, B1, foEs, hmEs) = self.ripe.CalcParameters(Lat, Lon, TargetTime, listOfFiles)
        logger.info("Test Location, lat={:8.1f} lon={:8.1f}".format(Lat, Lon))

        logger.info(
            "RIPE foF2={:.4f} hmF2={:.4f} B0={:.4f} B1={:.4f}".format(foF2, hmF2, B0, B1))

        if not foEs:
           foEs = -1 
        if not hmEs:
           hmEs = -1 


        logger.info(
            "RIPE foF2={:.4f} hmF2={:.4f} B0={:.4f} B1={:.4f} foEs={:.4f} hmEs={:.4f}".\
                  format(foF2, hmF2, B0, B1, foEs, hmEs))



        # results from Python/RIPE5 at (Lat = 47.6, Lon = -122.3) when processing
        #    AU930_ROAM.TXT, BC840_ROAM.TXT, EG931_ROAM.TXT in TestFiles/ using coefficients dated 1,21,2016
        #    and using IRTAM as the interpolating Model
        #foF2=8.5023 hmF2=257.5250 B0=56.4682 B1=2.1456
        #assert_approx_equal(foF2,   8.5023, significant=3)
        #assert_approx_equal(hmF2, 257.5250, significant=2)
        #assert_approx_equal(B0,    56.4682, significant=1)
        #assert_approx_equal(B1,     2.1456, significant=2)

if __name__ == "__main__":
    logger.setLevel('INFO')
    unittest.main()
