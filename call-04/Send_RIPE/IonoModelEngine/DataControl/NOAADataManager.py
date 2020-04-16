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

import ftplib
from datetime import datetime
import shutil
import sys
import numpy
import os
import errno
import unittest
import warnings
import threading
import Shared.Utils.HfgeoLogger as Logger
from IonoModelEngine.Config import ConfigDef, ConfigValues
import IonoModelEngine.Fit.GetProfileParameters as GetProfileParameters
from Shared.IonoPyIface.Pharlap import Pharlap
from IonoModelEngine.Fit.SaoPyIface import SaoPyIface
import socket

logger = Logger.getLogger()

## @package IonoModelEngine.SAOdownload
#  Module that downloads sao files from NOAA database

## Class that manage downloading of NOAA SAO files
#
class NOAADataManager(threading.Thread):
  
    def __init__(self, config, saoReaderHandle, ionoPyToCHandle):
        # Init the thread
        super().__init__()
        # Kill this thread when the main thread exist
        self.daemon = True
        # Wait until start is called
        self.running = False
        # Locking mechanism
        self.lock = threading.Lock()
        # Where do we store the data locally
        self.localPath = None
        # Check internal in seconds
        self.checkInterval = 5*60

        # NOAA information
        self.url = 'ftp.ngdc.noaa.gov'
        self.username = 'anonymous'
        self.password = '123'
        self.downloadWindow = config.downloadWindow
        self.stationList = config.stationList
        self.fitB0B1 = config.fitB0B1

        # We can log in at this moment in time
        self.ftp = None
        try:
            self.ftp = ftplib.FTP(host='ftp.ngdc.noaa.gov', 
                                user='anonymous',
                                passwd='123',
                                timeout=10)
        except Exception as e:
            logger.error('Establishing connection to NOAA failed. Most likely a connection error.')
            logger.error('{}'.format(e))

        # Directory structure for local storage
        self.saoStore = config.saoStore
        self.ripeStore = config.ripeStore
        os.makedirs(self.saoStore, exist_ok=True)
        os.makedirs(self.ripeStore, exist_ok=True)

        # Handle to the cpp sao parser
        self.saoReaderHandle = saoReaderHandle
        # Handle to Pharlap interface
        self.ionoPyToCHandle = ionoPyToCHandle

        # A set of variables to control time intervals for reading daily list of files from NOAA
        self.recheckForNewData = config.recheckForNewData
        self.recheckInterval = config.recheckInterval        
        self.lastCheckTime = datetime.now()

        # Temp variable to keep track of the files on noaa database
        self.fileList = {}

    ## Destructor
    #
    def __del__(self):
        if self.ftp:
            try:
                self.ftp.quit()
            except Exception as e:
                logger.error('Quitting from NOAA failed. Most likely a connection error.')
                logger.error('{}'.format(e))
            self.ftp = None

    ## Start this thread
    #
    def start(self):
        self.runing = True
        self.run()

    ## Go to noaa and fetch the data from the provided directory at the time given
    #
    #  @param noaaDir - string - The directory structure in the remote noaa store
    #  @param ursi - string - The ursi station name
    #  @param noaaDir - string - The local directory where we are going to store the .sao files
    #  @param requestTime - datetime() - The datetime object for the request
    #  @param fileList - list of strings - The list of SAO files on NOAA server for specific station and day
    #  @return downloadedFileList - list of string - list of full path downloaded files
    #
    def fetchData(self, noaaDir, ursi, dateDir, requestTime, fileList):
        # These are the files that we downloaded to disk
        downloadedFiles = []
        # If there are no sao files then exit early
        if not fileList:
            logger.warning('No data available at ' + self.url + noaaDir)
            return downloadedFiles
        # Create the output directory if it is not made already
        outputDir = os.path.join(self.saoStore, ursi, dateDir) 
        os.makedirs(outputDir, exist_ok=True)
        # Compute the delta beween the file and the requested time
        for f in fileList:
            baseFileName = os.path.basename(f)
            timeOfFile = datetime.strptime(baseFileName[6:19], '%Y%j%H%M%S')
            timeDiff = (timeOfFile - requestTime).total_seconds()
            # Only download things that are with the time window
            if abs(timeDiff) <= self.downloadWindow:
                fileName = os.path.join(outputDir, baseFileName)
                # If we already have the file do not download however we do want to add it to the list 
                # so that the next steps can be taken
                downloadedFiles.append(fileName)
                if os.path.isfile(fileName):
                    continue
                # Create the local file
                with open(fileName, 'wb') as fileHandle:
                    try:
                        self.ftp.retrbinary('RETR ' + f, fileHandle.write)
                    except Exception as e:
                        logger.error('Fetching SAO from NOAA failed. Most likely a connection error.')
                        logger.error('{}'.format(e))
                        break

        return downloadedFiles

    ## Translate the data from SAO to internal ripe format
    #  After this function there should be txt files 
    #  in the same directory as sao file in the format that we want
    #
    #  @param downloadedFileList - list of string - list of full path downloaded files
    #
    #  @retval translatedFileLIst - list of string - list of full path to ripe input files
    #
    def translate(self, downloadedFileList):
        translatedFileList = []        
        for fname in downloadedFileList:
            # Check if the file has already been translated, skip if translation exist
            # Regardless, add the file name to the list to do concatination
            pre, ext = os.path.splitext(fname)
            translatedName = pre + ".txt"
            if not os.path.exists(translatedName):
                 GetProfileParameters.runProfileFit(fname, 
                                     self.saoReaderHandle, 
                                     self.ionoPyToCHandle,
                                     self.fitB0B1)    
            if os.path.exists(translatedName):
                   translatedFileList.append(translatedName)            

        return translatedFileList    
            
    ## Do any kind of data conditioning. Punt of this right now
    #
    def condition_data(self):
        pass

    ## Concatinate the processed file into a big one and place it in the configured location
    #
    #  @param translatedFileLIst - list of string - list of full path to ripe input files
    #
    #  @return processedFileList - list of string - list of full path to the concatinated ripe input files
    #
    def copyToSAOStore(self, translatedFileList):
        
        processedFileList = []
        # Go through all our stations
        for ursi in self.stationList:
            currentListOfFilesToCat = ''
            if ursi not in '\t'.join(translatedFileList):
               continue 
            # Now we will cat all these files into a giant one
            outputFileName = os.path.join(self.ripeStore, ursi + '_NOAA.TXT')
            # Cat the files
            with open(outputFileName, 'wb') as outfile:
                for fname in translatedFileList:
                    if ursi not in fname:
                       continue 
                    with open(fname, 'rb') as fd:
                        shutil.copyfileobj(fd, outfile, 1024*1024*10)
            # Build up the list of files that Ripe need
            processedFileList.append(outputFileName)
        return processedFileList

    ## Check if we have supporting data for the request
    #
    #  @param requestTime - datetime object - The request time
    #
    #  @retval processedFileList - list of string - The list of files ripe need to ingest
    #
    def process(self, requestTime):

        # Peform a refetch of the NOAA list or not. Boolean
        performRefresh = self.recheckForNewData and abs(self.lastCheckTime - datetime.now()).total_seconds() > self.recheckInterval

        # If we failed to estabish connection at the constructor level try to do it now.
        if not self.ftp:
            try:
                self.ftp = ftplib.FTP(host='ftp.ngdc.noaa.gov', 
                                user='anonymous',
                                passwd='123',
                                timeout=10)
            except Exception as e:
                logger.error('Establishing connection to NOAA failed. Most likely a connection error.')
                logger.error('{}'.format(e))
              
        downloadedFileList = []
        translatedFileList = []
        processedFileList = []

        # Loop through the stations and get the files
        for ursi in self.stationList:
            # Parse out the date
            year = requestTime.year
            dayOfYear = requestTime.timetuple().tm_yday   

            # this is the day before
            if (requestTime.hour * 3600 + requestTime.minute * 60) < self.downloadWindow:  
                dayBefore = str(year) + "/" + str(dayOfYear - 1).zfill(3)
                noaaFtpDir = "/ionosonde/data/" + ursi + "/individual/" + dayBefore + "/scaled/"
                list_key = ursi + '0'
 
                # If we don't have the list of file for the requested data on hand then get the list of file from NOAA
                # If we want to refresh to get a new file list then aslo fetch the list
                # In the case the communication goes down return imediately with whatever we got
                if list_key not in self.fileList or performRefresh:
                    try:
                        self.fileList[list_key] = None
                        self.fileList[list_key] = self.ftp.nlst(noaaFtpDir + "*.SAO")
                    except Exception as e:
                        logger.error('Fetching file list from NOAA failed. Most likely a connection error.')
                        logger.error('{}'.format(e))
                        return processedFileList                
                    finally:
                        self.lastCheckTime = datetime.now()

                tmpList = self.fetchData(noaaFtpDir, ursi, dayBefore, requestTime, self.fileList[list_key])                    
                downloadedFileList.extend(tmpList)

            # this is the day
            today = str(year) + "/" + str(dayOfYear).zfill(3)
            noaaFtpDir = "/ionosonde/data/" + ursi + "/individual/" + today + "/scaled/"
            list_key = ursi + '1'

            # If we don't have the list of file for the requested data on hand then get the list of file from NOAA
            # If we want to refresh to get a new file list then aslo fetch the list
            # In the case the communication goes down return imediately with whatever we got
            if list_key not in self.fileList or performRefresh:
                try:
                    self.fileList[list_key] = None
                    self.fileList[list_key] = self.ftp.nlst(noaaFtpDir + "*.SAO")
                except Exception as e:
                    logger.error('Fetching file list from NOAA failed. Most likely a connection error.')
                    logger.error('{}'.format(e))
                    return processedFileList
                finally:
                    self.lastCheckTime = datetime.now()

            tmpList = self.fetchData(noaaFtpDir, ursi, today, requestTime, self.fileList[list_key])
            downloadedFileList.extend(tmpList)

            # this is the day after
            if (86400 - (requestTime.hour * 3600 + requestTime.minute * 60)) < self.downloadWindow: 
                dayAfter = str(year) + "/" + str(dayOfYear + 1).zfill(3)
                noaaFtpDir = "/ionosonde/data/" + ursi + "/individual/" + dayAfter + "/scaled/"
                list_key = ursi + '2'

                # If we don't have the list of file for the requested data on hand then get the list of file from NOAA
                # If we want to refresh to get a new file list then aslo fetch the list
                # In the case the communication goes down return imediately with whatever we got
                if list_key not in self.fileList or performRefresh:
                    try:
                        self.fileList[list_key] = None
                        self.fileList[list_key] = self.ftp.nlst(noaaFtpDir + "*.SAO")                    
                    except Exception as e:
                        logger.error('Fetching file list from NOAA failed. Most likely a connection error.')
                        logger.error('{}'.format(e)) 
                    finally:
                        self.lastCheckTime = datetime.now()

                tmpList = self.fetchData(noaaFtpDir, ursi, dayAfter, requestTime, self.fileList[list_key])
                downloadedFileList.extend(tmpList)

        # Do the translation from sao to ripe format
        translatedFileList = self.translate(downloadedFileList)
        # Copy the files into a directory that Charlie wants
        processedFileList = self.copyToSAOStore(translatedFileList)

        return processedFileList

    ## Run the thread
    #
    def run(self):
        while self.running:
            if time.now() - self.lastUpdateTime > self.checkInterval:
                data = self.fetchData(datetime.now())
                if data:
                    self.lastUpdateTime = datetime.now()
            else:
                time.sleep(self.checkInterval)

class UnitTest_NOAADataManager(unittest.TestCase):

    def testNoRefresh(self):

        # Setup the configurations
        config = ConfigValues.NOAAConfig()
        # Remove the test dir to reset
        if os.path.isdir(config.saoStore):
            shutil.rmtree(config.saoStore)
        if os.path.isdir(config.ripeStore):
            shutil.rmtree(config.ripeStore)
        # Need to stand this up        
        saoReaderHandle = SaoPyIface()
        ionoPyToCHandle = Pharlap()
        # Perform test download
        noaaManager = NOAADataManager(config, saoReaderHandle, ionoPyToCHandle)        
        for hr in range (9,10):
           for minute in range (0,59):
               listOfOutputFiles = noaaManager.process(datetime(2015, 11, 20, hr, minute))

        self.assertEqual(len(listOfOutputFiles), 4)

if __name__ == '__main__':
    logger.setLevel('INFO')
    unittest.main()
