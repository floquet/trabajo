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

import datetime

import numpy
import IonoModelEngine.Config.ConfigValues as IonoConfig
from Shared.Config import ConfigDef
import Shared.IonoPropagation.RayData as RayData
from Shared.IonoPyIface.Pharlap import Pharlap
from IonoModelEngine.ROAM.ROAM import ROAM
from Shared.IonoPropagation import GeoMagGrid

## @package Shared.Config.ConfigValues
#  Module that populate the standard values of the config classes

## Function to generate a RayManagerConfig object with standard values
#
def RayManagerConfig(parameterization="pharlap", pharlap=None):

    rayManagerConfig = ConfigDef.RayManagerConfig()

    ## Paramerization of the ionospheric model. Valid value: "mirror"
    rayManagerConfig.parameterization = parameterization
    ## Config object for the construction of PharlapRayProcessor
    if parameterization.lower() == "pharlap":
        rayManagerConfig.pharlapRayProcessorConfig = PharlapRayProcessorConfig(pharlap=pharlap)
    else:
        rayManagerConfig.pharlapRayProcessorConfig = None

    return rayManagerConfig


## Config data object of PharlapRayProcessor.
#
def PharlapRayProcessorConfig(pharlap=None):

    pharlapRayProcessorConfig = ConfigDef.PharlapRayProcessorConfig()

    # The footprints of the voxel grids are squares with an incribed circle with this radius. (Meter)
    pharlapRayProcessorConfig.grids.radiusMeter = 900e3

    # The electron density grid's increment in latitude (degrees)
    pharlapRayProcessorConfig.grids.latInc = numpy.deg2rad(0.10048)
    # The electron density grid's increment in longitude (degrees)
    pharlapRayProcessorConfig.grids.lonInc = numpy.deg2rad(0.10048)
    # The electron density grid's lowest height (km)
    pharlapRayProcessorConfig.grids.htStart = 60e3
    # The electron density grid's increment in height (km)
    pharlapRayProcessorConfig.grids.htInc = 2e3
    # The electron density grid's number of voxels in height
    pharlapRayProcessorConfig.grids.numHt = 201

    # The geomagnetic field grid's increment in latitude (degrees)
    pharlapRayProcessorConfig.grids.bLatInc = numpy.deg2rad(0.2)
    # The geomagnetic field grid's increment in longitude (degrees)
    pharlapRayProcessorConfig.grids.bLonInc = numpy.deg2rad(0.2)
    # The geomagnetic field grid's lowest height (km)
    pharlapRayProcessorConfig.grids.bHtStart = 60e3
    # The geomagnetic field grid's increment in height (km)
    pharlapRayProcessorConfig.grids.bHtInc = 10e3
    # The geomagnetic field grid's number of voxels in height
    pharlapRayProcessorConfig.grids.bNumHt = 41

    # Parameters of PHaRLAP
    pharlapRayProcessorConfig.pharlap.tolPharlapMin = numpy.array([1e-7, 0.01, 1])
    # Root solver for ray homing

    elLimits = numpy.array([0, 90.0])                             
    elSpan = 180.0
    azSpan = 30.0

    # 1D Ray Shooting
    options1d = {"fatol": 1e-2, "maxNumIter": 10, "nfev": 50}
    elLimits = pharlapRayProcessorConfig.elLimits
    pharlapRayProcessorConfig.elMaxSolver = RayData.genRootSolver("rayShooting1d",option=options1d,
                 elLimits=elLimits)
    #pharlapRayProcessorConfig.solver = RayData.genRootSolver("minimize")
    #pharlapRayProcessorConfig.solver = RayData.genRootSolver("krylov", options={"fatol": 1.0e-3})

    # 2D Bisectioning
    #solverOptions = {"fatol": 20, "maxNumIter": 100, "func1d": pharlapRayProcessorConfig.elMaxSolver}
    # pharlapRayProcessorConfig.solver = RayData.genRootSolver("bisect2d", options=solverOptions,
    #             elLimits=elLimits, elSpan=elSpan, azSpan=azSpan)

    # 2D Ray Shooting
    solverOptions = {"fatol": 10000, "maxNumIter": 50, "nfev": 100, "nInit": 200}
    pharlapRayProcessorConfig.solver = RayData.genRootSolver("rayShooting2d", options=solverOptions,
                 elLimits=elLimits, elSpan=elSpan, azSpan=azSpan)

    # If no Pharlap object is provided, construct a new one.
    if not isinstance(pharlap, Pharlap):
        pharlap = Pharlap()

    # Construct a ROAM object
    roamConfig = IonoConfig.ROAMConfig()
    roam = ROAM(roamConfig, pharlapHandle=pharlap)
    # Set the model to IRI
    roam.background_model = 0

    pharlapRayProcessorConfig.raytrace_3d = pharlap.raytrace_3d
    pharlapRayProcessorConfig.genGeoMagGrid = GeoMagGrid.genGridIGRF12
    pharlapRayProcessorConfig.genElectronDensityGridROAM = roam.genElectronDensityGridROAM

    # Number of days as the threshold to trigger the regeneration of geomagnetic fields.
    pharlapRayProcessorConfig.deltaDaysRegenGeomagGrid = datetime.timedelta(90) # Regenerate the geomagnetic fields if it is outdated by more than 90 days.

    return pharlapRayProcessorConfig

## Function to generate an IonoInterfaceConfig object with standard values
def IonoInterfaceConfig():
    from IonoModelEngine.Config.ConfigValues import TICSConfig
    ionoInterfaceConfig = ConfigDef.IonoInterfaceConfig()
    ionoInterfaceConfig.ticsConfig = TICSConfig()
    return ionoInterfaceConfig


