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

import platform
import unittest
import numpy
import collections
import os
import ctypes as C
from ctypes import cdll
import Shared.Utils.HfgeoLogger as Logger

logger = Logger.getLogger()

## @package IonoModelEngine
#  Python interface to FOUT1

## The interface class to IrtamPyIface
#  Contains an instance of the C interface library
#
class IrtamPyIface:

    ## Constructor sets up all the handle
    #
    def __init__(self):

        # Figure out which os this is on so that we can load the correct library
        #
        libName = os.path.join(os.path.dirname(os.path.realpath(__file__)),'lib')
        if platform.system() == 'Darwin':
            libName = os.path.join(libName,'libirtampy_mac.dylib')
        elif platform.system() == 'Linux':
            libName = os.path.join(libName,'libirtampy_lin.so')
 
        self.libhandle = cdll.LoadLibrary( libName )
        self.libhandle.processirtam.argtypes = C.POINTER(C.c_double), \
                                            C.POINTER(C.c_double), \
                                            C.POINTER(C.c_double), \
                                            C.POINTER(C.c_double), \
                                            C.POINTER(C.c_double), \
                                            C.POINTER(C.c_double), \
                                            C.POINTER(C.c_double)
 
        self.irtamInput = collections.namedtuple('processirtam_input', \
                            'alati, along, xmodip, hourut, tov, param, param_local')

    def __del__(self):
        import _ctypes
        logger.warning('IrtamPyIface Destructor')
        _ctypes.dlclose(self.libhandle._handle)

    ## Return a named tuple object that represent the input to sao reader.
    #  For example:    
    #    param_local, irtam_tov = processirtam(irtamInput)
    #  
    #  @retval irtamInput A named tuple that the user need to fill in and pass to procesirtam()
    #
    def getIrtamInput(self):
        return self.irtamInput

    ## Call processirtam in the lib 
    #
    #  @param irtamInput - The named tuple input to getprofile
    #
    #  @retval param_local, irtam_tov  - IRTAM coefficients and Time of Validity
    #                                    
    def processirtam(self, irtamInput):

        # Convert from python type to c type
        #
        alati = C.byref(C.c_double(irtamInput.alati))
        along = C.byref(C.c_double(irtamInput.along))
        xmodip = C.byref(C.c_double(irtamInput.xmodip))
        hourut = C.byref(C.c_double(irtamInput.hourut))
        tov = C.byref(C.c_double(irtamInput.tov))
        param = irtamInput.param.ctypes.data_as(C.POINTER(C.c_double))
        param_local = C.c_double(irtamInput.param_local)        

        # Calling the C interface
        #
        self.libhandle.processirtam(alati, \
                                 along, \
                                 xmodip, \
                                 hourut, \
                                 tov, \
                                 param,\
                                 param_local)
        
        return param_local.value

class UnitTest_IrtamPyIface(unittest.TestCase):

    def test_irtam(self):

        iface = IrtamPyIface()

	      # Get the Input object so we can fill it out
	      #
        irtamInput = iface.getIrtamInput()
        irtamInput.alati = 32.42
        irtamInput.along = 253.71
        irtamInput.xmodip = 25.0
        irtamInput.hourut = 12.
        irtamInput.tov = 12.
        irtamInput.param = numpy.zeros(1064)
        logger.info(irtamInput.param[0:10])

        irtamfile = os.path.dirname(os.path.abspath(__file__)) + '/test_data/IRTAM_hmF2_COEFFS_20140119_1545.ASC'        
        data = numpy.genfromtxt(irtamfile)
        irtamInput.param = numpy.reshape(data,1064)
        logger.info(irtamInput.param[0:10])
        irtamInput.param_local  = numpy.zeros(1)
        (param_local) = iface.processirtam(irtamInput)
        logger.info(param_local)

if __name__ == "__main__":
    logger.setLevel('INFO')
    unittest.main()
    








