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
from datetime import datetime
from Framework.Manager import Manager
import Shared.Utils.HfgeoLogger as Logger
from IonoModelEngine.Config.KentIsland_test_20180320 import *

logger = Logger.getLogger()

## @package IonoModelEngine.QueryIono
#  Module That run TICS Manager. Can be used to generate IonoState Files

def saveIonoState(replyState, ionoStateFileName, date, lat, lon):
    if not os.path.exists(ionoStateFileName):
       with open(ionoStateFileName, 'w') as outFile:				
         outFile.write("YEAR MON DAY  HR MIN       foF2      hmF2      foF1       foE        " + \
                     "B0        B1   gradLat   gradLon         a         C    lambda     gamma     "  + \
                     "omega       psi       Vh       Vaz   Ref_lat   Ref_lon    AoAErr\n")

    with open(ionoStateFileName, 'a') as outFile:				
         outFile.write("{0:04d}  {1:02d}  {2:02d}  {3:02d}  {4:02d} ".format(date.year, date.month, date.day, date.hour, date.minute))
         for n in range (0,11):
             if n == 4 or n == 7 or n == 8:
                continue
             outFile.write("{:10.4f}".format(replyState[n]))

         for n in range (0,8):
             outFile.write("{:10.4f}".format(0))

         outFile.write("{:10.4f}{:10.4f}{:10.4f}\n".format(lat, lon, 0))

def run():
    # Generate the top level config
    ticsConfig = TICSConfig()
    manager = Manager(ticsConfig) 

    for total_minute in range(810,875,5):
        hour = int(total_minute / 60)
        minute =  total_minute - hour * 60
#        replyState = manager.queryIonoState(40.333, 286.550, datetime(2018, 2, 28, hour, minute))
#        saveIonoState(replyState, "testIonoState_0310.txt", datetime(2018, 2, 28, hour, minute), 40.333, 286.550)
# 40.0, 254.7 - Boulder; 45.07, 276.440 - Alpena
        replyState = manager.queryIonoState(40.0, 254.7, datetime(2018, 1, 28, hour, minute))
        saveIonoState(replyState, "testIonoState_0312.txt", datetime(2018, 1, 28, hour, minute), 40.0, 254.7)
        logger.debug(replyState) 

if __name__ == "__main__":
    logger.setLevel('DEBUG')
    run()
