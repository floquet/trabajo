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
#  Python interface to readsao

## The interface class to SaoPyIface
#  Contains an instance of the C interface library
#
class SaoPyIface:

    ## Constructor sets up all the handle
    #
    def __init__(self):
        # Figure out which os this is on so that we can load the correct library
        #
        libName = os.path.join(os.path.dirname(os.path.realpath(__file__)),'lib')
        if platform.system() == 'Darwin':
            libName = os.path.join(libName,'libsaopy_mac.dylib')
        elif platform.system() == 'Linux':
            libName = os.path.join(libName,'libsaopy_lin.so')
        
        # get a library handle
        #
        self.libhandle = cdll.LoadLibrary(libName)

        # Set arguments
        #
        self.libhandle.getprofile.argtypes = C.POINTER(C.c_double), \
                                             C.POINTER(C.c_double), \
                                             C.POINTER(C.c_double), \
                                             (C.c_char_p)
 
        self.saoInput = collections.namedtuple('getprofile_input', \
                                               'htab ftab paramiri filename')

    def __del__(self):
        import _ctypes
        logger.warning('SaoPyIface Destructor')
        _ctypes.dlclose(self.libhandle._handle)

    ## Return a named tuple object that represent the input to sao reader.
    #  For example:
    #    saoInput.phtab = numpy.zeros(1000)
    #    saoInput.fhtab = numpy.zeros(1000)
    #    saoInput.paramiri = numpy.zeros(40)
    #    saoInput.filename = filenameunicode.encode('utf-8')
    #    ...
    #    (phtab, pftab, paramiri) = getprofile(saoInput)
    #  
    #  @retval saoInput A named tuple that the user need to fill in and pass to getprofile()
    #
    def getSaoInput(self):
        return self.saoInput

    ## Call getprofile in the lib 
    #
    #  @param saoInput - The named tuple input to getprofile
    #
    #  @retval (phtab, pftab, paramiri) - first two are height and frequency arrays, the third one
    #                                     is iono parameter array
    #
    def getprofile(self, saoInput):

        # Convert from python type to c type
        #
        phtab = saoInput.phtab.ctypes.data_as(C.POINTER(C.c_double))
        pftab = saoInput.pftab.ctypes.data_as(C.POINTER(C.c_double))
        paramiri = saoInput.paramiri.ctypes.data_as(C.POINTER(C.c_double))        
        filename = ((C.c_char_p(saoInput.filename.encode('utf-8'))))

        # Calling the C interface
        #
        self.libhandle.getprofile(phtab, \
                                  pftab, \
                                  paramiri, \
                                  filename)
        
        return phtab, pftab, paramiri

class UnitTest_SaoPyIface(unittest.TestCase):

    def test_sao(self):
        import os

        # Handle to the sao parser        
        iface = SaoPyIface()

        pythonRoot = os.environ['PYTHONPATH'].split(os.pathsep)[0]

        # Get the Input object so we can fill it out        
        saoInput = iface.getSaoInput()
        saoInput.phtab = numpy.zeros(1000)
        saoInput.pftab = numpy.zeros(1000)
        saoInput.paramiri = numpy.zeros(10)        
        saoInput.filename = os.path.join(pythonRoot, "IonoModelEngine/Fit/test_data/BC840_2017041060005.SAO")
        (phtab, pftab, paramiri) = iface.getprofile(saoInput)

        self.assertAlmostEqual(paramiri[0],3.2, places=4)
        self.assertAlmostEqual(paramiri[1],278.2, places=4)
        self.assertAlmostEqual(paramiri[2],0, places=4)
        self.assertAlmostEqual(paramiri[3],0,places=4)
        self.assertAlmostEqual(paramiri[4],0.401, places=4)
        self.assertAlmostEqual(paramiri[5],110.0,places=4)
        self.assertAlmostEqual(paramiri[6],44.4,places=4)
        self.assertAlmostEqual(paramiri[7],4.09,places=4)
        self.assertEqual(paramiri[8],9999.0)
        self.assertEqual(paramiri[9],9999.0)

if __name__ == "__main__":
    logger.setLevel('INFO')
    unittest.main()
    








