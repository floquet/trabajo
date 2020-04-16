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

import unittest
import time
import os
import threading
import shutil
from datetime import datetime
import Shared.IonoPyIface.Pharlap as IonoPyIface
from IonoModelEngine.Config import ConfigDef, ConfigValues
from IonoModelEngine.DataControl.DataController import DataController
from IonoModelEngine.ROAM.ROAM import ROAM
import Shared.Utils.HfgeoLogger as Logger
from Shared.IonoPyIface.Pharlap import Pharlap
from IonoModelEngine.Fit.SaoPyIface import SaoPyIface
from IonoModelEngine.IRTAM.IrtamPyIface import IrtamPyIface 

logger = Logger.getLogger()

## @package IonoModelnEngine.Framework.Manager
#  The manager for IonoModelnEngine

## The manager class. It creates and owns all threaded modules
#
class Manager():
    __slots__ = ['config', 'heartbeatChannel', 'ionoChannel', 'saoReaderHandle', 'irtamHandle', 'pharlapHandle', 'dataController', 'roam', 'running']

    ## Constructor
    #
    def __init__(self, config, saoReaderHandle=None, irtamHandle=None, pharlapHandle=None):

        self.config = config

        # Comms channels
        self.heartbeatChannel = None
        self.ionoChannel      = None

        # Create handle to SAO reader 
        if saoReaderHandle:
            self.saoReaderHandle = saoReaderHandle
        else:
            self.saoReaderHandle = SaoPyIface()

        # Create handle to IRTAM Processor
        if irtamHandle:
            self.irtamHandle = irtamHandle
        else:
            self.irtamHandle = IrtamPyIface()

        # Create handle to Pharlap
        if pharlapHandle:
            self.pharlapHandle = pharlapHandle
        else:
            self.pharlapHandle = Pharlap()

        # Standup the data controler which does the downloading and massaging of external data        
        self.dataController = DataController(self.config.dataControllerConfig,
                                             self.saoReaderHandle, 
                                             self.irtamHandle,
                                             self.pharlapHandle)

        self.roam = ROAM(self.config.roamConfig,
                         self.irtamHandle, 
                         self.pharlapHandle)

        # Set this method up to run
        self.running = True

    ## Return the ionostate for the location and time specified in the request
    #
    def queryIonoState(self, requestLat, requestLon, requestDateTime):
        # Check the if there are supporting data to answer the request.
        # If yes then just return so that roam can continue to process
        # If no then fetch the data, massage it and then put it in a locaiton that roam wants
        # Only do this if the background model is NOT IRI
        dataControlerOutput = []
        if not 'iri' in self.config.roamConfig.backgroundModel:
            dataControlerOutput = self.dataController.process(requestDateTime)
        # Tell roam to process the request provided that the data is in place.
        # If there is no data default to using IRI        
        reply = self.roam.CalcIonoState(requestLat, requestLon, requestDateTime, dataControlerOutput)
        logger.debug(reply)
        # Return the reply
        return reply

    def shutdown(self):
        self.running = False    

    ## Run loop DO NOT CALL THIS
    #
    def run(self):
        # Keep running forever
        while self.running:
            # Wait for the zmq message blocking call
            xmlIonoRequest = self.comms.recv()
            # Need to implement this
            request = xmlToIonoRequest(xmlIonoRequest)
            # Process the request
            reply = queryIonoState(request)
            # Need to implement this
            xmlIonoReply = xmlToIonoReply(reply)
            # Respond via comms channel
            self.comms.send(reply)

class UnitTest_Manager(unittest.TestCase):

    def testRIPE(self):
        # Top level manager config
        managerConfig = ConfigValues.TICSConfig()
        # Tell the datacontroller to use noaa and roam to use ripe
        managerConfig.dataControllerConfig.sources = ['noaa']
        managerConfig.roamConfig.backgroundModel = ['ripe']
        manager = Manager(managerConfig)
        manager.queryIonoState(37.2321, 256.2323, datetime(2015, 10, 20))

    def testIRTAM(self):
        # Top level manager config
        managerConfig = ConfigValues.TICSConfig()
        # Tell the datacontroller to use giro and roam to use irtam
        managerConfig.dataControllerConfig.sources = ['giro']
        managerConfig.roamConfig.backgroundModel = ['irtam']
        manager = Manager(managerConfig)
        manager.queryIonoState(37.2321, 256.2323, datetime(2015, 10, 20)) 

    def testRIPEandIRTAM(self):
        logger.info("testRIPEandIRTAM")
        # Top level manager config
        managerConfig = ConfigValues.TICSConfig()
        # Tell the datacontroller to use giro and roam to use irtam
        managerConfig.dataControllerConfig.sources = ['noaa','giro']
        managerConfig.roamConfig.backgroundModel = ['ripe-irtam']
        manager = Manager(managerConfig)
        manager.queryIonoState(37.2321, 256.2323, datetime(2015, 10, 20)) 

if __name__ == '__main__':
    logger.setLevel('DEBUG')
    unittest.main()
