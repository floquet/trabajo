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

## @package Shared.Config.KentIsland_201803
#  Config values for data collected during the KentIsland_201803 campaign

from IonoModelEngine.Config import ConfigDef

## Default values for NOAADataManager.
#
def NOAAConfig():
    import os
    noaaConfig = ConfigDef.NOAAConfig()
    pythonRoot = os.environ['PYTHONPATH'].split(os.pathsep)[0]
    noaaConfig.saoStore = os.path.join(pythonRoot, 'tmp/noaaData')
    noaaConfig.ripeStore = os.path.join(pythonRoot, 'tmp/ripeInput')
    noaaConfig.downloadWindow = 5400
    noaaConfig.stationList = ['EG931', 'PA836', 'IF843', 'AL945', 'BC840','KN761']
    noaaConfig.fitB0B1 = False
    return noaaConfig


def GIROConfig():
    import os
    giroConfig = ConfigDef.GIROConfig()
    pythonRoot = os.environ['PYTHONPATH'].split(os.pathsep)[0]
    giroConfig.giroStore = os.path.join(pythonRoot, 'tmp/giroData')
    giroConfig.giroURL = 'https://lgdc.uml.edu/rix/gambit-coeffs?time='
    return giroConfig

## Default values for DataController
#
def DataControllerConfig():
    dataControllerConfig = ConfigDef.DataControllerConfig()
    dataControllerConfig.noaaConfig = NOAAConfig()
    dataControllerConfig.giroConfig = GIROConfig()
    # Select 'noaa' or 'giro'
    dataControllerConfig.sources = ['noaa']
    return dataControllerConfig

## Default values for ROAMConfig
#
def ROAMConfig():
    import os
    pythonRoot = os.environ['PYTHONPATH'].split(os.pathsep)[0]    
    roamConfig = ConfigDef.ROAMConfig()
    roamConfig.ripeStore  = os.path.join(pythonRoot, 'tmp/ripeInput')
    roamConfig.irtamStore = os.path.join(pythonRoot, 'tmp/giroData')
    roamConfig.noaaConfig = NOAAConfig()
    roamConfig.giroConfig = GIROConfig()
    # Select 'ripe' or 'irtam'
    roamConfig.backgroundModel = ['ripe']
    roamConfig.refreshIRI = False
    roamConfig.synopticTilt = True
    return roamConfig

## Default values for TICSConfig
#
def TICSConfig():
    ticsConfig = ConfigDef.TICSConfig()
    ticsConfig.dataControllerConfig = DataControllerConfig()
    ticsConfig.roamConfig = ROAMConfig()    
    return ticsConfig
