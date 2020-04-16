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

## package IonoModelEngine.Config.ConfigDef
#  Definition (only) for configs

## The configuration of data sources
#
class NOAAConfig:
    __slots__ = ('saoStore', 'ripeStore', 'stationList', 'downloadWindow','fitB0B1', 'recheckForNewData', 'recheckInterval')

    def __init__(self):
        ## The local directories to store the downloaded SAO files
        self.saoStore = None
        ## The local directories to store the RIPE format input
        self.ripeStore = None
        ## The names and locations of the stations
        self.stationList = None
        ## The time window that we want to download
        self.downloadWindow = None
        ## Option to do the profile fitting to determine B0 B1
        self.fitB0B1 = None
        ## True or False to check for new data after the initial 'ls' has been processed
        self.recheckForNewData = None
        ## Time duration between recheck in seconds
        self.recheckInterval = None

## Data controler config
#
class DataControllerConfig:
    __slots__ = ('noaaConfig', 'giroConfig', 'lpiConfig', 'localSounderConfig', 'sources')
    
    def __init__(self):
        ## Config for noaa db
        self.noaaConfig = None
        ## Config for giro db
        self.giroConfig = None
        ## Config for lpi
        self.lpiConfig = None
        ## Config for local sounder
        self.localSounderConfig = None
        ## A list of the sources that we are going to use, for example ['noaa', 'giro']
        self.sources = None

## Config for ROAM
#
class ROAMConfig:
    __slots__ = ('ripeStore', 'irtamStore', 'localStore', 'noaaConfig','giroConfig','backgroundModel','refreshIRI','synopticTilt')

    def __init__(self):
        ## The local directories to store the RIPE format input
        self.ripeStore = None
        ## The local directories to store the IRTAM format input
        self.irtamStore = None
        ## The local directories to store the LOCAL format input
        self.localStore = None
        ## The names and locations of the NOAA stations
        ## The configuration for NOAA data
        self.noaaConfig = None
        ## The configuration for GIRO data
        self.giroConfig = None
        ## Choose the background iono models to use ('ripe', 'irtam', 'iri') or combination of them
        self.backgroundModel = None
        ## Flag to force RIPE to refresh its IRI parameters (0=no, 1=yes)
        self.refreshIRI = None
        ## Flag to use synotic tilt
        self.synopticTilt = None

## Configuration for TICS
#         
class TICSConfig:
    __slots__ = ('dataControllerConfig', 'roamConfig')

    def __init__(self):
        ## Configuration for the DataController
        self.dataControllerConfig = None
        ## Configuration for ROAM
        self.roamConfig  = None

## Configuration for GIRO
#
class GIROConfig:
    __slots__ = ('giroStore', 'giroURL')

    def __init__(self):
        ## The local directories to store the downloaded SAO files
        self.giroStore = None
        ## The time window that we want to download
        self.giroURL = None


