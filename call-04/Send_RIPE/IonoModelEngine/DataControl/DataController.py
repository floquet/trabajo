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

from datetime import datetime
import threading
import unittest
import os
import shutil
import Shared.Utils.HfgeoLogger as Logger
from IonoModelEngine.DataControl.NOAADataManager import NOAADataManager
from IonoModelEngine.DataControl.GIRODataManager import GIRODataManager
from IonoModelEngine.Config import ConfigDef, ConfigValues
from Shared.IonoPyIface.Pharlap import Pharlap
from IonoModelEngine.Fit.SaoPyIface import SaoPyIface
from IonoModelEngine.IRTAM.IrtamPyIface import IrtamPyIface 

logger = Logger.getLogger()

## package IonoModelEngine.DataControl.DataController 
#  Data controller for all possible data sources

## DataController class's job is to fetch data for an iono reqest and package it to a common format for ROAM
#
class DataController:

    __slots__ = ['config', 'noaaManager', 'giroManager', 'lpiManager', 'localSensorManager']

    ## Default constructor
    #
    #  @param config - DataControllerConfig() - The configuration for the data controler defined in ConfigDef.py
    #
    def __init__(self, config, saoReaderHandle=None, irtamHandle=None, pharlapHandle=None):

        self.config = config
        self.noaaManager = None
        self.giroManager = None
        self.lpiManager = None
        self.localSensorManager = None

        # Create the specific data manager that was requested in config
        if 'noaa' in self.config.sources:
            self.noaaManager = NOAADataManager(self.config.noaaConfig, saoReaderHandle, pharlapHandle)
        if 'giro' in self.config.sources:
            self.giroManager = GIRODataManager(self.config.giroConfig, pharlapHandle)

    ## Process the request by downloading + translate the data from whatever format into one that roam can use
    #
    #  @param requestDateTime - Python datetime format - the datetime of the request
    #
    def process(self, requestDateTime):
        outputFileList = {}
        outputFileList['noaa'] = []
        outputFileList['giro'] = []
        outputFileList['localSounder'] = []

        # Get the data or return None
        if self.noaaManager:
            outputFileList['noaa'] = self.noaaManager.process(requestDateTime)
        if self.giroManager:
            outputFileList['giro'] = self.giroManager.process(requestDateTime)

        return outputFileList        

class UnitTest_DataController(unittest.TestCase):

    def testNOAA(self):
        # Setup the configuration for the DataController
        dataControllerConfig = ConfigValues.DataControllerConfig()
        # Use only noaa
        dataControllerConfig.sources = ['noaa']               
        # Need to stand this up, usually the Manager has it
        saoReaderHandle = SaoPyIface()
        pharlapHandle = Pharlap()
        # Create an instance of DataController and let it go
        dataController = DataController(dataControllerConfig, saoReaderHandle=saoReaderHandle, pharlapHandle=pharlapHandle)
        listOfOutputFiles = dataController.process(datetime(2015, 10, 20))
        self.assertEqual(len(listOfOutputFiles['noaa']), 4)

    def testGIRO(self):
        # Setup the configuration for the DataController
        dataControllerConfig = ConfigValues.DataControllerConfig()
        # Use only giro
        dataControllerConfig.sources = ['giro']         
        # Need to stand this up, usually the Manager has it
        pharlapHandle = Pharlap()
        irtamHandle = IrtamPyIface()
        # Create an instance of DataController and let it go
        dataController = DataController(dataControllerConfig, irtamHandle=irtamHandle, pharlapHandle=pharlapHandle)
        listOfOutputFiles = dataController.process(datetime(2015, 10, 20))
        self.assertEqual(len(listOfOutputFiles['giro']), 4)  

if __name__ == '__main__':
    logger.setLevel('INFO')
    unittest.main()
