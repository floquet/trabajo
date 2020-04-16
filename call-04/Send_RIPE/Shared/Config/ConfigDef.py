# Copyright (C) 2017 Systems & Technology Research, LLC.
# http://www.stresearch.com
#
# STR Proprietary Information
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

## @package Shared.Config.ConfigDef
#  Module with definitions of config classes for ray processing

## Config data object of RayManager.
#
class RayManagerConfig:
    __slots__ = ("parameterization", "pharlapRayProcessorConfig")

    def __init__(self):
        ## Paramerization of the ionospheric model. Valid value: "mirror"
        self.parameterization = None
        ## Config object for the construction of PharlapRayProcessor
        self.pharlapRayProcessorConfig = None


## Config parameters of electron density grid and geomagnetic grid
class GridParam:
    __slots__ = ("radiusMeter", "latInc", "lonInc", "htStart", "htInc", "numHt", "bLatInc", "bLonInc", "bHtStart", "bHtInc", "bNumHt")

    def __init__(self):

        ## The footprints of the voxel grids are squares with an incribed circle with this radius. (Meter)
        self.radiusMeter = None

        ## The electron density grid's increment in latitude (degrees)
        self.latInc = None
        ## The electron density grid's increment in longitude (degrees)
        self.lonInc = None
        ## The electron density grid's lowest height (km)
        self.htStart = None
        ## The electron density grid's increment in height (km)
        self.htInc = None
        ## The electron density grid's number of voxels in height
        self.numHt = None

        ## The geomagnetic field grid's increment in latitude (degrees)
        self.bLatInc = None
        ## The geomagnetic field grid's increment in longitude (degrees)
        self.bLonInc = None
        ## The geomagnetic field grid's lowest height (km)
        self.bHtStart = None
        ## The geomagnetic field grid's increment in height (km)
        self.bHtInc = None
        ## The geomagnetic field grid's number of voxels in height
        self.bNumHt = None


## Config parameters of Pharlap
class PharlapParam:
    __slots__ = ("tolPharlapMin", )

    def __init__(self):

        ## Three-elements array controller ODE solver precision.
        #  tol[0]  =  ODE solver tolerence, valid values 1e-12 to 1e-2
        #  tol[1]  =  ODE solver minimum step size to consider (0.001 to 1 km)
        #  tol[2]  =  ODE solver maximum step size to consider (1 to 100 km)
        self.tolPharlapMin = None

## Config data object of PharlapRayProcessor.
#
class PharlapRayProcessorConfig:
    __slots__ = ("grids", "pharlap", "solver", "elMaxSolver","raytrace_3d", "genGeoMagGrid", "genElectronDensityGridROAM", "deltaDaysRegenGeomagGrid", "elLimits")

    def __init__(self):
        ## Parameters of the electron density grid and the geomagnetic field grid
        self.grids = GridParam()
        ## Parameters of PHaRLAP
        self.pharlap = PharlapParam()
        ## Root solver for ray homing.
        self.solver = None
        ## Root solver for finding max elevation
        self.elMaxSolver = None
        ## Callable object to generate the geomagnetic grid
        self.genGeoMagGrid = None
        ## Callable object to generate the electron density grid
        self.genElectronDensityGridROAM = None
        ## Number of days as the threshold to trigger the regeneration of geomagnetic fields.
        self.deltaDaysRegenGeomagGrid = None
        self.elLimits = None

## IonoInterfaceConfig
class IonoInterfaceConfig:
    __slots__ = ("ticsConfig")

    ## Constructor
    def __init__(self):

        ## The configuration for TICS if we use tics
        self.ticsConfig = None


