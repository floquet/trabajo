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

from datetime import datetime, timedelta
#import shutil
#import sys
import numpy
import os
#import errno
import unittest
#import warnings
import threading
#import urllib.request
import Shared.Utils.HfgeoLogger as Logger
#from IonoModelEngine.Config import ConfigDef, ConfigValues
from IonoModelEngine.IRTAM.IrtamPyIface import IrtamPyIface
from Shared.IonoPyIface.Pharlap import Pharlap
#import IonoModelEngine.DataControl.GIRODataManager as giroDataManager

logger = Logger.getLogger()

## package IonoModelEngine.DataControl.GIRODataManager
#  Data manager for GIRO data

class IRTAM(threading.Thread):

    def __init__(self, irtamPyToCHandle, ionoPyToCHandle):

        super().__init__()
        # Kill this thread when the main thread exist
        self.daemon = True
        # Wait until start is called
        self.running = False
        # Locking mechanism
        self.lock = threading.Lock()
        # The last time we fetch something
        self.lastUpdateTime = None
        # Where do we store the data locally
        self.localPath = None
        # Check internal in seconds
        self.checkInterval = 5*60
        # Variable to keep track of which file were downloaded during process()
        self.downloadedFiles = []
        # Check internal in seconds
        self.checkInterval = 5*60
        # Handle to Pharlap interface
        self.ionoPyToCHandle = ionoPyToCHandle
        # Handle to irtamProcess interface
        self.irtamPyToCHandle = irtamPyToCHandle

    ## Start the thread
    #
    def start(self):
        self.runing = True
        self.run()

    ## Shutdown 
    #
    def shutdown(self):
        self.running = False
        self.ftp.quit()

    ## Calculate iono parameters for specific location using GIRO coefficients 
    #
    def translate(self, lat, lon, date, downloadedFiles):
       
        processedData = numpy.zeros(4)       
        n = 0

        for inputFile in downloadedFiles:

           datain = numpy.genfromtxt( inputFile ) 
           openFile = open(inputFile) 
           for line in openFile.readlines():
             if 'Validity' in str(line):
                irtam_tov = datetime.strptime(line[19:35], '%Y-%m-%dT%H:%M')
                break
           openFile.close()
   
           irtamInput = self.irtamPyToCHandle.getIrtamInput()
           irtamInput.alati = lat
           irtamInput.along = lon

           # Call igrf to calculate modip angle
           # formula is 
           #   asin{dip/sqrt[dip^2+cos(LATI)]} 
           #   
           #  ( from igrf_dip subroutine )
           # 
  
           UT = [date.year, date.month, date.day, date.hour, date.minute] 
           mag_field = self.ionoPyToCHandle.igrf2016(lat, lon, UT, 0.)
           dip = numpy.radians( mag_field[7])
           irtamInput.xmodip = numpy.degrees( numpy.arcsin(dip / numpy.sqrt(dip*dip + numpy.cos(numpy.radians(lat))) ))

           irtamInput.hourut = date.hour + (date.minute * 60 + date.second ) / 3600
           irtamInput.param = numpy.zeros(1064)
           irtamInput.param_local  = numpy.zeros(1)
   
           irtamInput.param = numpy.reshape(datain,1064)
           irtamInput.tov = irtam_tov.hour + (irtam_tov.minute * 60 + irtam_tov.second ) / 3600
           processedData[n] = self.irtamPyToCHandle.processirtam(irtamInput)

           n = n + 1
  
        return processedData

    def run(self):
        while self.running:
            if time.now() - self.lastUpdateTime > self.checkInterval:
                data = self.fetchData(datetime.now())
                if data:
                    self.lastUpdateTime = datetime.now()
            else:
                time.sleep(self.checkInterval)

    ## Obtain the parameters foF2, hmF2, B0, B1 using the IRTAM model
    #
    #  @param lat    - latitude where the state is desired (degrees)
    #  @param lon    - longitude where the state is desired (degrees)
    #  @param DT     - python datetime struct specifying when the state is desired
    #  @param listOfStations - list of full path to IRTAM coefficient files
    #
    #  @retval [foF2, hmF2, B0, B1]
    #
    def CalcParameters(self, lat, lon, DT, listOfFiles):

        from pathlib import Path

        irtamFiles = []

        have_irtam_files = 0

        for file in listOfFiles:
            my_file = Path(file)

            if not my_file.is_file():
                logger.debug('IRTAM file {:s} not found, skipping'.format(fname))
                continue

            fname = my_file.name

            #logger.info("Testing {:s}".format(file))

            # check that filename is the right length
            if len(fname) < 5:
                logger.debug("{:s} filename is too short, skipping".format(fname))
                continue

            # check that filename has the right prefix
            if fname[0:5] != 'IRTAM':
                logger.debug(" {:s} filename is missing IRTAM prefix, skipping".format(fname))
                continue

            # test if this is the IRTAM coefficient file for foF2
            if fname[0:10] == 'IRTAM_foF2':
                have_irtam_files = have_irtam_files + 1
                irtamFiles.append(file)
                logger.info("IRTAM file {:s}".format(file))

            # test if this is the IRTAM coefficient file for hmF2
            if fname[0:10] == 'IRTAM_hmF2':
                have_irtam_files = have_irtam_files + 1
                irtamFiles.append(file)
                logger.info("IRTAM file {:s}".format(file))

            # test if this is the IRTAM coefficient file for B0
            if fname[0:8] == 'IRTAM_B0':
                have_irtam_files = have_irtam_files + 1
                irtamFiles.append(file)
                logger.info("IRTAM file {:s}".format(file))

            # test if this is the IRTAM coefficient file for B1
            if fname[0:8] == 'IRTAM_B1':
                have_irtam_files = have_irtam_files + 1
                irtamFiles.append(file)
                logger.info("IRTAM file {:s}".format(file))

        # if we have all four coefficient files, query IRTAM for the parameters
        if have_irtam_files == 4:
            #irtamProcessor = IRTAM.IRTAM(self.irtamHandle, self.pharlapHandle)
            #data = irtamProcessor.translate(lat, lon, DT, listOfFiles)
            data = self.translate(lat, lon, DT, irtamFiles)
            #data = self.irtam.translate(lat, lon, DT, irtamFiles)

            logger.info("IRTAM data: foF2={:.4f} hmF2={:.4f} B0={:.4f} B1={:.4f}". \
                        format(data[0], data[1], data[2], data[3]))
            foF2 = data[0]
            hmF2 = data[1]
            B0 = data[2]
            B1 = data[3]
        else:
            logger.warning("IRTAM could not find all its files, returning 0".format(fname))
            foF2 = 0
            hmF2 = 0
            B0   = 0
            B1   = 0

        return (foF2, hmF2, B0, B1)

class UnitTest_IRTAM(unittest.TestCase):

    def setUp(self):
        ionoPyToCHandle  = Pharlap()
        irtamPyToCHandle = IrtamPyIface()
        self.irtam = IRTAM(irtamPyToCHandle, ionoPyToCHandle)


#    def test(self):
#
#        config = ConfigValues.GIROConfig()
#        # Remove the test dir to reset
#       # if os.path.isdir(config.giroStore):
#       #     shutil.rmtree(config.giroStore)
#        # Need to stand this up
#        # Perform test donwload
#        ionoPyToCHandle = Pharlap()
#        irtamPyToCHandle = IrtamPyIface()
#
#        giroManager = giroDataManager.GIRODataManager(config, ionoPyToCHandle)
#        listofFiles = giroManager.process(datetime(2015, 10, 20))
#        irtamProcessor = IRTAM(irtamPyToCHandle, ionoPyToCHandle)
#        data = irtamProcessor.translate(32.42, 253.71, datetime(2015, 10, 20), listofFiles)
#        self.assertAlmostEqual(data[0],8.74377551, places=7)
#        self.assertAlmostEqual(data[1],252.73095405, places=7)
#        self.assertAlmostEqual(data[2],59.57357052, places=7)
#        self.assertAlmostEqual(data[3],3.1691901, places=7)

    def test_CalcParameters(self):
        from numpy.testing import assert_approx_equal
        logger.info("test_CalcIonoState")

        directory = os.path.dirname(os.path.realpath(__file__)) + "/UnitTestData/"


        # G10 receiver location
        lat = 30.40 #	262.30-19.07
        lon = 262.3 #190.07

        for utime in range(0,24):

          listOfFiles = [directory + 'IRTAM_foF2_COEFFS_20180601_'+ str(utime).zfill(2) +'00.ASC', \
                         directory + 'IRTAM_hmF2_COEFFS_20180601_'+ str(utime).zfill(2) +'00.ASC', \
                         directory + 'IRTAM_B0_COEFFS_20180601_'+ str(utime).zfill(2) +'00.ASC', \
                         directory + 'IRTAM_B1_COEFFS_20180601_'+ str(utime).zfill(2) +'00.ASC']


          UT = numpy.array([2015, 11, 1, utime, 0])
          DT = datetime(UT[0], UT[1], UT[2], UT[3], UT[4], 0)

          data = self.irtam.CalcParameters(lat, lon, DT, listOfFiles)

          logger.info(
               "IRTAM foF2={:.4f} hmF2={:.4f} B0={:.4f} B1={:.4f}". \
                   format(data[0], data[1], data[2], data[3]))

#          foF2_irtam[utime] = data[0]

        # Output from IRTAM
        # [IRTAM.py:176] IRTAM data: foF2=8.7484 hmF2=252.7329 B0=59.5018 B1=3.1669

#        assert_approx_equal(data[0],   8.7484, significant=3)  # foF2
#        assert_approx_equal(data[1], 252.7329, significant=3)  # hmF2
#        assert_approx_equal(data[2],  59.5018, significant=3)  # B0
#        assert_approx_equal(data[3],   3.1669, significant=3)  # B1

#        print (foF2_irtam)

        return

if __name__ == '__main__':
    logger.setLevel('INFO')
    unittest.main()
