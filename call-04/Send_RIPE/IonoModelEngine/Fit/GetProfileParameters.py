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

import math
import os
import pathlib
import numpy
import logging
import scipy.optimize
import unittest
from datetime import datetime, date, time
from scipy.optimize import curve_fit
from scipy.optimize import minimize
from scipy.interpolate import interp1d
import Shared.Utils.HfgeoLogger as Logger
import IonoModelEngine.Fit.FitProfile as FitProfile
import IonoModelEngine.DataControl.Stations as stations

logger = Logger.getLogger()

## @package IonoModelEngine.GetProfileParameters
#
#  Module that runs profile fitting to derives B0, B1 
#  and saves the results in RIPE/ROAM - input format
  
## Method to format output according to format convention
#
#  @param[in] - fmt: format specifier
#  @param[in] - value: output value
#
def printout(fmt, value):
    if value == 0 or value == -1 or value == 9999.0:
        return "   --- "
    else:
        return fmt.format(value)

## Main method that calls ReadSao and FitProfile and saves parameters
#
#  @param - string - the full output file name
#
#  @return - list of string - list of full file name that has been translated
#
def runProfileFit(fullFileName, saoReaderHandle, ionoPyToCHandle, fitB0B1):

    # Get just the base name
    baseName = os.path.basename(fullFileName)

    # Get the lat lon   
    (lat,lon) = stations.getStationLatLon(baseName[0:5])
    if not lat or not lon:
        logger.info("Unknown URSI code: " + baseName[0:5])      
        return
    
    # Get the Input object so we can fill it out
    # 
    saoInput = saoReaderHandle.getSaoInput()

    # Fill out the input
    #
    saoInput.phtab = numpy.zeros(999)
    saoInput.pftab = numpy.zeros(999)
    saoInput.paramiri = numpy.zeros(10)
    saoInput.filename = fullFileName

    # Get the date time from the file name
    fit_date = datetime.strptime(baseName[6:19], '%Y%j%H%M%S')
    # Break it down into components
    year  = fit_date.year
    month = fit_date.month
    day   = fit_date.day
    hour  = fit_date.hour
    minute  = fit_date.minute
    # This is a string which we will need for the output file later
    dayOfYear = date(year, month , day).strftime('%j')

    # We need the numpy verson of this
    UT = numpy.array([year,month,day,hour,minute])

    # Read the SAO file and parse out the relevant iri parameters
    (phtab, pftab, paramiri) = saoReaderHandle.getprofile(saoInput)

    foF2 =  paramiri[0]
    hmF2 =  paramiri[1]
    foF1 =  paramiri[2] 
    hmF1 =  paramiri[3] 
    foE  =  paramiri[4]
    hmE  =  paramiri[5] 
    B0   =  paramiri[6] 
    B1   =  paramiri[7] 
    foEs =  paramiri[8] 
    hmEs =  paramiri[9]

    R12 = -1
    hgt_start = 100
    hgt_inc = 1
    hgt_num = 199

    phtab_u, u_indices = numpy.unique(phtab[1:999], return_index = True)
    if len(phtab_u) < 3:
        return

    pftab1 = numpy.array(pftab[1:999])
    pftab_u = pftab1[numpy.array(numpy.sort(u_indices))]  

    if fitB0B1 == True:
       (xB0,xB1) = FitProfile.fitProfile(ionoPyToCHandle, phtab_u, pftab_u, paramiri, UT, lat, lon)
    else: 
       xB0 = B0
       xB1 = B1

    iono_parameters = [-1,-1,-1,-1,-1,-1,-1]
    (iono_pf_iri, iono_extra_iri) = ionoPyToCHandle.iri2016(lat,lon,R12,UT,hgt_start,hgt_inc,hgt_num,iono_parameters)
    paramiri_iri = ionoPyToCHandle.iono_extra_to_layer_parameters(iono_extra_iri)

    # Write the post SAO processed file in our format
    #
    (fullFileNameNoExt, _) = os.path.splitext(fullFileName)
    ripeInputFileName = fullFileNameNoExt + '.txt'

    with open(ripeInputFileName, 'w') as outFile:       
        outFile.write("{0:4d}.{1:02d}.{2:02d} ({3:3s}) {4:02d}:{5:02d}:{6:02d} {7:03d} ".format(year, month, day, dayOfYear, hour, minute, 0, 100))
        outFile.write(printout("{:4.3f} ",foF2))
        outFile.write(printout("{:4.3f} ",foF1))
        outFile.write(printout("{:4.3f} ",foE))
        outFile.write(printout("{:4.3f} ",foEs))
        outFile.write(printout("{:4.3f} ",hmEs))
        outFile.write(printout("{:4.3f} ",hmF2))
        outFile.write(printout("{:4.3f} ",hmF1))
        outFile.write(printout("{:4.3f} ",hmE))
        outFile.write(printout("{:4.3f} ",xB0))
        outFile.write(printout("{:4.3f} ",xB1))
        outFile.write(printout("{:4.3f} ",-1))
        outFile.write(printout("{:4.3f} ",paramiri_iri[0]))
        outFile.write(printout("{:4.3f} ",paramiri_iri[1]))
        outFile.write(printout("{:4.3f} ",paramiri_iri[5]))
        outFile.write(printout("{:4.3f}\n",paramiri_iri[6]))
        outFile.close()

    return ripeInputFileName



class UnitTest_GetProfileParameters(unittest.TestCase):


    def test(self):

        import os 
        from IonoModelEngine.Fit.SaoPyIface import SaoPyIface
        import IonoModelEngine.DataControl.Stations as stations
        from Shared.IonoPyIface.Pharlap import Pharlap

        # Setup testing configuration
        iface = SaoPyIface()
        ionoPyToCHandle = Pharlap()
        pythonRoot = os.environ['PYTHONPATH'].split(os.pathsep)[0]
        fileName = os.path.join(pythonRoot, "IonoModelEngine/Fit/test_data/BC840_2017041060005.SAO")
        fileName_out = os.path.join(pythonRoot, "IonoModelEngine/Fit/test_data/BC840_2017041060005.txt")
        
        if os.path.exists(fileName_out):
           try:  
              os.remove(fileName_out)           
           except OSError:
             pass

        # Call the fitting routine to be tested
        runProfileFit(fileName, iface, ionoPyToCHandle, False)

        testSize = os.path.getsize(fileName_out)
        self.assertEqual(testSize, 133)



if __name__ == "__main__":
    logger.setLevel('INFO')
    unittest.main()


