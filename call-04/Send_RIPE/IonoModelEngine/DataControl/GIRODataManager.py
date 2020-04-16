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
import shutil
import sys
import numpy
import os
import errno
import unittest
import requests
import warnings
import threading
import Shared.Utils.HfgeoLogger as Logger
from IonoModelEngine.Config import ConfigDef, ConfigValues
import Shared.IonoPyIface.Pharlap as IonoPyIface

logger = Logger.getLogger()

## package IonoModelEngine.DataControl.GIRODataManager
#  Data manager for GIRO data

class GIRODataManager(threading.Thread):

    def __init__(self, config, ionoPyToCHandle):

        # Init the thread
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
        # GIRO information
        self.url = config.giroURL
        # Directory structure for local storage
        self.giroStore = config.giroStore
        os.makedirs(self.giroStore, exist_ok=True)
        # Variable to keep track of which file were downloaded during process()
        self.downloadedFiles = []
        # Check internal in seconds
        self.checkInterval = 5*60
        # Handle to Pharlap interface
        self.ionoPyToCHandle = ionoPyToCHandle
        # Username and password for GIRO access
        self.username = 'HFGeo'
        self.password = 'Phase3'
    
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

    ## Check if we have supporting data for the request
    #
    def process(self, date):

        self.downloadedFiles = []

        for iono_param in ['foF2', 'hmF2', 'B0', 'B1']:

#             time_str = date.strftime('%Y/%m/%dT%H:%M:%S')       

             int15min = round((date.hour * 3600 + date.minute * 60 + date.second ) / 900)

             if int15min < 96:
                time_label = date.strftime('%Y%m%d') + "_{:02.0f}{:02.0f}".format(numpy.floor(int15min/4),(int15min/4 - numpy.floor(int15min/4)) * 60) 
             else:  
                time_label = ( date + timedelta(days=1) ).strftime('%Y%m%d') + '_0000'

             fileName = self.giroStore + '/IRTAM_' + iono_param + '_COEFFS_' + time_label + '.ASC'

             # if file exists, do not download
             if os.path.isfile(fileName):
                self.downloadedFiles.append(fileName)
                continue

             irtam_url = self.url + date.strftime('%Y/%m/%dT%H:%M:%S') + '&charName=' + iono_param + '&n=' + self.username + '&w=' + self.password
             request = requests.get(irtam_url,timeout = 100)

             if request.status_code != 200:
                logger.warning('IRTAM data is not available') 
                return
           
             for line in request.iter_lines():
                 if 'Validity' in str(line):
                   irtam_tov = datetime.strptime(line.decode('utf8')[19:35], '%Y-%m-%dT%H:%M')
                   break

             # round up time to 15 min increment to match GIRO convention

             giro_file = open(fileName, 'wb')
             giro_file.write(request.content)
             giro_file.close() 
             self.downloadedFiles.append(fileName)
 
        return self.downloadedFiles

    def run(self):
        while self.running:
            if time.now() - self.lastUpdateTime > self.checkInterval:
                data = self.fetchData(datetime.now())
                if data:
                    self.lastUpdateTime = datetime.now()
            else:
                time.sleep(self.checkInterval)

class UnitTest_GIRODataManager(unittest.TestCase):

    def test(self):
        # Setup the configurations

        config = ConfigValues.GIROConfig()
        # Remove the test dir to reset
        # if os.path.isdir(config.giroStore):
        #    shutil.rmtree(config.giroStore)
        # Need to stand this up
        ionoPyToCHandle = IonoPyIface.Pharlap()
        giroManager = GIRODataManager(config, ionoPyToCHandle)
        # Perform test donwload
        listOfOutputFiles = giroManager.process(datetime(2015, 10, 20))
        self.assertEqual(len(listOfOutputFiles),4)

if __name__ == '__main__':
    logger.setLevel('INFO')
    unittest.main()


