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
#    noaaConfig.stationList = ['BC840', 'AU930', 'EG931', 'PA836', 'IF843', 'MHJ45', 'AL945']
    noaaConfig.stationList = ['BC840']
    noaaConfig.fitB0B1 = False
    noaaConfig.recheckForNewData = False
    noaaConfig.recheckInterval = 60*5
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
    #dataControllerConfig.sources = ['noaa'] #['noaa'] , ['giro'] or both ['noaa', 'giro']
    dataControllerConfig.sources = ['noaa', 'giro']
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
    roamConfig.backgroundModel = 'irtam' # 'iri', 'ripe', 'irtam', 'ripe-irtam'
    roamConfig.refreshIRI = False
    roamConfig.synopticTilt = True
    return roamConfig

## Default values for TICSConfig
#
def TICSConfig():
    ticsConfig = ConfigDef.TICSConfig()
    ticsConfig.dataControllerConfig = DataControllerConfig()
    ticsConfig.roamConfig = ROAMConfig()
    # Condition the input source based upon the background model
    if ticsConfig.roamConfig.backgroundModel == 'ripe':
        ticsConfig.dataControllerConfig.sources = ['noaa']
    elif ticsConfig.roamConfig.backgroundModel == 'irtam':
        ticsConfig.dataControllerConfig.sources = ['giro']
    elif ticsConfig.roamConfig.backgroundModel == 'ripe-irtam':
        ticsConfig.dataControllerConfig.sources = ['noaa', 'giro']
    else:
        ticsConfig.dataControllerConfig.sources = []
    return ticsConfig
