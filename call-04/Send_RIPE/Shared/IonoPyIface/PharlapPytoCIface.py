# Copyright (C) 2017 Boston College and Systems & Technology Research, LLC.
# http://www.stresearch.com
# http://bc.edu
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

import platform
import unittest
import collections
import os
import ctypes as C
import threading
from ctypes import cdll, Structure
import numpy
import Shared.Utils.HfgeoLogger as Logger

logger = Logger.getLogger()

## @package Shared.IonoPyIface.PharlapPytoCIface
#  Python interface to the low-level C interfaces of IRI, IGRF, and raytrace_3d packaged in raytrace_3d

## Max number of points in a ray. This needs to be consistent with the low-level library.
#
max_pts_in_ray = 20000

## file mutex for ig_rz.dat
ig_rz_mutex = threading.Lock()
igrf_mutex  = threading.Lock()

## generic function template to be used as a function / method decorator
# Usage: Before any function / method you want to wrap with a lock.acquire()
#        and lock.release() call, add "@lock_fcn(lock)", where lock is a
#        python threading lock
# Notes: This may not be the best place for this, maybe add it to a separate file?
#        Right now, I'm only adding it around the iri2016 call which reads the ig_rz.dat
#        file. Adding too many locks can lead to unexpected deadlocking scenarios and
#        slow down the program overall
def lock_fcn(lock):

    def file_lock(f):
        def wrapper(*args, **kwargs):
            lock.acquire()
            x = f(*args, **kwargs)
            lock.release()
            return x

        return wrapper

    return file_lock

class IONOSPHERE_STRUCT(Structure):

    max_num_ht  = 401
    max_num_lon = 701
    max_num_lat = 701

    _fields_ = [
        ("eN", C.c_double * max_num_lat * max_num_lon * max_num_ht),
        ("eN_5", C.c_double * max_num_lat * max_num_lon * max_num_ht),
        ("col_freq", C.c_double * max_num_lat * max_num_lon * max_num_ht),
        ("ht_min", C.c_double),
        ("num_ht", C.c_int),
        ("ht_inc", C.c_double),
        ("ht_max", C.c_double),
        ("lat_min", C.c_double),
        ("num_lat", C.c_int),
        ("lat_inc", C.c_double),
        ("lat_max", C.c_double),
        ("lon_min", C.c_double),
        ("num_lon", C.c_int),
        ("lon_inc", C.c_double),
        ("lon_max", C.c_double)
    ]

class GEOMAG_FIELD_STRUCT(Structure):

    max_num_ht  = 201
    max_num_lon = 101
    max_num_lat = 101

    _fields_ = [
        ("Bx", C.c_double * max_num_lat * max_num_lon * max_num_ht),
        ("By", C.c_double * max_num_lat * max_num_lon * max_num_ht),
        ("Bz", C.c_double * max_num_lat * max_num_lon * max_num_ht),
        ("ht_min", C.c_double),
        ("num_ht", C.c_int),
        ("ht_inc", C.c_double),
        ("ht_max", C.c_double),
        ("lat_min", C.c_double),
        ("num_lat", C.c_int),
        ("lat_inc", C.c_double),
        ("lat_max", C.c_double),
        ("lon_min", C.c_double),
        ("num_lon", C.c_int),
        ("lon_inc", C.c_double),
        ("lon_max", C.c_double)
    ]

## IGRF IO class both input and output is in here
#
#  @param[in] glat          - lat in decimal degree
#  @param[in] glong         - long in decimal degree
#  @param[in] dec_year      - year in decimal year for example 2011.3232
#  @param[in] height        - height in kilometers
#  @param[in] dipole_moment - dipole_moment
#  @param[out] babs         - babs
#  @param[out] bnorth       - bnorth
#  @param[out] beast        - beast
#  @param[out] bdown        - bdown
#  @param[out] dip          - dip
#  @param[out] dec          - dec
#  @param[out] dip_lat      - dip_lat
#  @param[out] l_value      - l_value
#  @param[out] l_value_code - l_value_code
#
class IgrfPharlapIO:
    
    __slots__ = ('glat', 'glong', 'dec_year', 'height', 'dipole_moment', 'babs', 'bnorth', 'beast', 'bdown',
                 'dip', 'dec', 'dip_lat', 'l_value', 'l_value_code')
    def __init__(self):
        self.glat          = None 
        self.glong         = None 
        self.dec_year      = None 
        self.height        = None 
        self.dipole_moment = None 
        self.babs          = None 
        self.bnorth        = None 
        self.beast         = None 
        self.bdown         = None 
        self.dip           = None 
        self.dec           = None 
        self.dip_lat       = None 
        self.l_value       = None 
        self.l_value_code  = None 

## IRI IO class both input and output is in here
#
#  @param[in] jf     - jf
#  @param[in] jmag   - jmag
#  @param[in] glat   - lat in decimal degree
#  @param[in] glong  - long in decimal degree
#  @param[in] year   - dipole_moment
#  @param[in] mmdd   - decimal month
#  @param[in] dhour  - decimal hour
#  @param[in] heibeg - (km) starting heigh
#  @param[in] heiend - (km) ending heigh
#  @param[in] heistp - (km) step of height max 100 heights
#  @param[out] outf  - output array
#  @param[out] oarr  - output array
#
class IriPharlapIO:
    
    __slots__ = ('jf', 'jmag', 'glat', 'glong', 'year', 'mmdd', 'dhour', 'heibeg', 'heiend', 'heistp', 'outf', 'oarr')
    def __init__(self):
        self.jf     = None
        self.jmag   = None
        self.glat   = None
        self.glong  = None
        self.year   = None
        self.mmdd   = None
        self.dhour  = None
        self.heibeg = None
        self.heiend = None
        self.heistp = None
        self.outf   = None
        self.oarr   = None 

## The interface class to IRI, IGRF, and raytrace_3d
#  Contains an instance of the C interface library
#
class PharlapPytoCIface:

    slots = ['libhandle']

    ## Constructor sets up all the handle
    #
    def __init__(self):

        # First make sure the envirnoment variable is set
        #
        dataDir = os.environ.get('DIR_MODELS_REF_DAT')
        if dataDir is None:
            logger.error('Environment variable DIR_MODELS_REF_DAT is not set')
        else:
            if not os.path.isdir(dataDir + "/iri2016"):
                logger.error('The value of DIR_MODELS_REF_DAT is not valid')

        # Figure out which os this is on so that we can load the correct library
        #
        libName = os.path.join(os.path.dirname(os.path.realpath(__file__)),'lib')
        if platform.system() == 'Darwin':
            libName = os.path.join(libName,'libionopyiface_mac.dylib')
        elif platform.system() == 'Linux':
            libName = os.path.join(libName,'libionopyiface_lin.so')

        # get a library handle
        #
        self.libhandle = cdll.LoadLibrary(libName)

        # Set up igrfpharlap arguments
        #
        self.libhandle.igrfpharlap.argtypes = [C.POINTER(C.c_float),
                                               C.POINTER(C.c_float),
                                               C.POINTER(C.c_float),
                                               C.POINTER(C.c_float),
                                               C.POINTER(C.c_float),
                                               C.POINTER(C.c_float),
                                               C.POINTER(C.c_float),
                                               C.POINTER(C.c_float),
                                               C.POINTER(C.c_float),
                                               C.POINTER(C.c_float),
                                               C.POINTER(C.c_float),
                                               C.POINTER(C.c_float),
                                               C.POINTER(C.c_float),
                                               C.POINTER(C.c_int)]

        # Set up iri2016pharlap argument types
        #
        # self.IriPharlapIO = IriPharlapIO()
        self.libhandle.iri2016pharlap.argtypes = [C.POINTER(C.c_int), \
                                                  C.POINTER(C.c_int), \
                                                  C.POINTER(C.c_float), \
                                                  C.POINTER(C.c_float), \
                                                  C.POINTER(C.c_int), \
                                                  C.POINTER(C.c_int), \
                                                  C.POINTER(C.c_float), \
                                                  C.POINTER(C.c_float), \
                                                  C.POINTER(C.c_float), \
                                                  C.POINTER(C.c_float), \
                                                  C.POINTER(C.c_float), \
                                                  C.POINTER(C.c_float)]

        # Set up raytrace3d argument types
        #
        self.libhandle.raytrace3d.argtypes = [C.POINTER(C.c_double),
                                              C.POINTER(C.c_double),
                                              C.POINTER(C.c_double),
                                              C.POINTER(C.c_int),
                                              C.POINTER(C.c_double),
                                              C.POINTER(C.c_double),
                                              C.POINTER(C.c_double),
                                              C.POINTER(C.c_int),
                                              C.POINTER(C.c_int),
                                              C.POINTER(C.c_double),
                                              C.POINTER(C.c_double),
                                              C.POINTER(C.c_double),
                                              C.POINTER(IONOSPHERE_STRUCT),
                                              C.POINTER(GEOMAG_FIELD_STRUCT),
                                              C.POINTER(C.c_double),
                                              C.POINTER(C.c_int),
                                              C.POINTER(C.c_int),
                                              numpy.ctypeslib.ndpointer(dtype=numpy.double),
                                              numpy.ctypeslib.ndpointer(dtype=numpy.double),
                                              numpy.ctypeslib.ndpointer(dtype=numpy.intc),
                                              numpy.ctypeslib.ndpointer(dtype=numpy.intc),
                                              numpy.ctypeslib.ndpointer(dtype=numpy.intc),
                                              numpy.ctypeslib.ndpointer(dtype=numpy.double),
                                              numpy.ctypeslib.ndpointer(dtype=numpy.double)]
        
        return

    ## Attempt to unnload the library. It kind of works some of the time
    #
    def __del__(self):
        import _ctypes
        logger.warning('PharlapPytoCIface Destructor')
        _ctypes.dlclose(self.libhandle._handle)

    ## Return a class that represent the input to igrf.
    #
    #  @retval igrfIO A class that the user need to fill in and pass to iri2016bc()
    #
    def getIgrfPharlapIO(self):
        return IgrfPharlapIO

    ## Return a class that represent the input to iriPharlap.
    #
    #  @retval igrfIO A class that the user need to fill in and pass to iri2016bc()
    #
    def getIriPharlapIO(self):
        return IriPharlapIO()

    ## Call igrf in the lib
    #
    #  @param igrfIO - The IgrfIO class
    #
    #  @retval igrfIO - The IgrfIO class
    #
    @lock_fcn(igrf_mutex)
    def igrfPharlap(self, igrfIO):

        # Convert from python type to c type
        #
        glat          = C.byref(C.c_float(igrfIO.glat))
        glong         = C.byref(C.c_float(igrfIO.glong))
        dec_year      = C.byref(C.c_float(igrfIO.dec_year))
        height        = C.byref(C.c_float(igrfIO.height))

        # We need these as pointer for the return values
        #
        dipole_moment = C.c_float(igrfIO.dipole_moment)
        babs          = C.c_float(igrfIO.babs)
        bnorth        = C.c_float(igrfIO.bnorth)
        beast         = C.c_float(igrfIO.beast)
        bdown         = C.c_float(igrfIO.bdown)
        dip           = C.c_float(igrfIO.dip)
        dec           = C.c_float(igrfIO.dec)
        dip_lat       = C.c_float(igrfIO.dip_lat)
        l_value       = C.c_float(igrfIO.l_value)
        l_value_code  = C.c_int(igrfIO.l_value_code)

        # Call the C++ code
        #
        self.libhandle.igrfpharlap(glat, \
                                   glong, \
                                   dec_year, \
                                   height, \
                                   dipole_moment, \
                                   babs, \
                                   bnorth, \
                                   beast, \
                                   bdown, \
                                   dip, \
                                   dec, \
                                   dip_lat, \
                                   l_value, \
                                   l_value_code)

        # Set the vaues in the return object. we have to do this
        #
        igrfIO.dipole_moment = dipole_moment.value
        igrfIO.babs          = babs.value
        igrfIO.bnorth        = bnorth.value
        igrfIO.beast         = beast.value
        igrfIO.bdown         = bdown.value
        igrfIO.dip           = dip.value
        igrfIO.dec           = dec.value
        igrfIO.dip_lat       = dip_lat.value
        igrfIO.l_value       = l_value.value
        igrfIO.l_value_code  = l_value_code.value

        # Return with the updated class
        #
        return igrfIO

    ## Call IRI that is included in PHARLAP
    #
    #  @param iriIO - The IriIO class
    #
    #  @retval iriIO - The IriIO class
    #
    @lock_fcn(ig_rz_mutex)
    def iri2016pharlap(self, iriIO):

        # Convert from python type to c pointer. This is an input but this is how we pass numpy arrays
        #
        jf     = iriIO.jf.ctypes.data_as(C.POINTER(C.c_int))

        # Convert from python type to cref type for read only input
        #
        jmag   = C.byref(C.c_int(iriIO.jmag))
        glat   = C.byref(C.c_float(iriIO.glat))
        glong  = C.byref(C.c_float(iriIO.glong))
        year   = C.byref(C.c_int(iriIO.year))
        mmdd   = C.byref(C.c_int(iriIO.mmdd))
        dhour  = C.byref(C.c_float(iriIO.dhour))
        heibeg = C.byref(C.c_float(iriIO.heibeg))
        heiend = C.byref(C.c_float(iriIO.heiend))
        heistp = C.byref(C.c_float(iriIO.heistp))

        # Convert from python type to c pointer for output
        #
        outf   = iriIO.outf.ctypes.data_as(C.POINTER(C.c_float))
        oarr   = iriIO.oarr.ctypes.data_as(C.POINTER(C.c_float))

        # Calling the C interface
        #
        self.libhandle.iri2016pharlap(jf, \
                                      jmag, \
                                      glat, \
                                      glong, \
                                      year, \
                                      mmdd, \
                                      dhour, \
                                      heibeg, \
                                      heiend, \
                                      heistp, \
                                      outf, \
                                      oarr)

        # Return with the updated class
        #
        return iriIO

    ## Wrapper function handling the ctypes data conversion.
    #  The function signature is identical to the low-level raytrace_3d_ function
    #
    def raytrace_3d_(self,
                     start_lat,
                     start_long,
                     start_height,
                     num_rays,
                     elevs,
                     bearings,
                     freqs,
                     OX_mode,
                     nhops,
                     step_size_min,
                     step_size_max,
                     tol,
                     ionosphere_struct,
                     geomag_field_struct,
                     ray_state_vec_in,
                     return_ray_path_data,
                     return_ray_state_vec,
                     ray_data,
                     ray_path_data,
                     ray_label,
                     nhops_attempted,
                     npts_in_ray,
                     ray_state_vec_out,
                     elapsed_time):

        # All the necessary conversion to ctypes
        #
        start_lat = C.c_double(start_lat)
        start_long = C.c_double(start_long)
        start_height = C.c_double(start_height)
        num_rays = C.c_int(num_rays)

        #   Elevation(s), bearing(s), and freq(s) of the ray(s).
        #   Support only numpy arrays.
        #j
        if all(map(lambda x: isinstance(x, numpy.ndarray), (elevs, bearings, freqs))):
            elevs = numpy.ctypeslib.as_ctypes(elevs.ravel())
            bearings = numpy.ctypeslib.as_ctypes(bearings.ravel())
            freqs = numpy.ctypeslib.as_ctypes(freqs.ravel())
        else:
            raise TypeError("Unsupported types of (elev, bearings, freqs) = "
                            f"({type(elevs)}, {type(bearings)}, {type(freqs)}).")
        OX_mode = C.c_int(OX_mode)
        nhops = C.c_int(nhops)
        step_size_min = C.c_double(step_size_min)
        step_size_max = C.c_double(step_size_max)
        tol = C.c_double(tol)
        # ionosphere_struct,
        # geomag_field_struct,
        ray_state_vec_in = numpy.ctypeslib.as_ctypes(ray_state_vec_in.ravel())
        return_ray_path_data = C.c_int(return_ray_path_data)
        return_ray_state_vec = C.c_int(return_ray_state_vec)
        # ray_data = numpy.ctypeslib.as_ctypes(ray_data.ravel())
        # ray_path_data = numpy.ctypeslib.as_ctypes(ray_path_data.ravel())
        # ray_label = ray_label.ravel()
        # nhops_attempted = nhops_attempted.ravel()
        # npts_in_ray = npts_in_ray.ravel()
        # ray_state_vec_out = numpy.ctypeslib.as_ctypes(ray_state_vec_out.ravel())
        # elapsed_time

        # Calling the C interface
        #
        self.libhandle.raytrace3d(start_lat,
                                  start_long,
                                  start_height,
                                  num_rays,
                                  elevs,
                                  bearings,
                                  freqs,
                                  OX_mode,
                                  nhops,
                                  step_size_min,
                                  step_size_max,
                                  tol,
                                  ionosphere_struct,
                                  geomag_field_struct,
                                  ray_state_vec_in,
                                  return_ray_path_data,
                                  return_ray_state_vec,
                                  ray_data,
                                  ray_path_data,
                                  ray_label,
                                  nhops_attempted,
                                  npts_in_ray,
                                  ray_state_vec_out,
                                  elapsed_time)

        return

class UnitTest_PharlapPytoCIface(unittest.TestCase):

    def setUp(self):
        # Get the python interface
        #
        self.iface = PharlapPytoCIface()

    def test_igrf_pharlap(self):

        igrfIO = self.iface.getIgrfPharlapIO()

        # Fill out the input
        #
        igrfIO.glat          = 10.00
        igrfIO.glong         = 128.00
        igrfIO.dec_year      = 2000.723999
        igrfIO.height        = 60.00
        igrfIO.dipole_moment = -1.0
        igrfIO.babs          = -1.0 
        igrfIO.bnorth        = -1.0 
        igrfIO.beast         = -1.0 
        igrfIO.bdown         = -1.0 
        igrfIO.dip           = -1.0 
        igrfIO.dec           = -1.0 
        igrfIO.dip_lat       = -1.0 
        igrfIO.l_value       = -1.0 
        igrfIO.l_value_code  = -1 

        igrfIO = self.iface.igrfPharlap(igrfIO)

        logger.info('dipole_moment={:10.6e}, babs={:10.6e}, bnorth={:10.6e}'
                    ' beast={:10.6e}, bdown={:10.6e}, dip={:10.6e}'
                    ' dec={:10.6e}, dep_lat={:10.6e}'.format(
                    igrfIO.dipole_moment,\
                    igrfIO.babs,\
                    igrfIO.bnorth,\
                    igrfIO.beast,\
                    igrfIO.bdown,\
                    igrfIO.dip,\
                    igrfIO.dec,\
                    igrfIO.dip_lat))

        return
        
    def test_iri_pharlap(self):

        # Get the Input object so we can fill it out
        #
        iriIO = self.iface.getIriPharlapIO()

        # Fill out the jf stuff according to what is prescribed by Manuel Cervera
        #
        iriIO.jf        = numpy.zeros(50, dtype=numpy.intc)
        iriIO.jf[0:50] =  [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,\
                              1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1,\
                              1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
        iriIO.jf[38] = 0
        iriIO.jf[39] = 1

        # Filling out the rest of the values
        #
        iriIO.jmag   = 0
        iriIO.glat   = 32.479365999999999
        iriIO.glong  = 253.621491
        iriIO.year   = 2014
        iriIO.mmdd   = 119
        iriIO.dhour  = 40.833333333333333
        iriIO.heibeg = 65
        iriIO.heiend = 1064
        iriIO.heistp = 1

        # These are output
        #
        iriIO.outf = numpy.zeros((1000,20), dtype=numpy.float32)
        iriIO.oarr = numpy.zeros(100, dtype=numpy.float32)

        iriIO.oarr[0:100] = [0.000000, 0.000000, 0.000000, 0.000000, 0.000000, \
                                0.000000, 0.000000, 0.000000, 0.000000, 0.000000, \
                                0.000000, 0.000000, 0.000000, 0.000000, 0.000000, \
                                0.000000, 0.000000, 0.000000, 0.000000, 0.000000, \
                                0.000000, 0.000000, 0.000000, 0.000000, 0.000000, \
                                0.000000, 0.000000, 0.000000, 0.000000, 0.000000, \
                                0.000000, 0.000000, 100.000000, 0.000000, 0.000000, \
                                0.000000, 0.000000, 0.000000, 107.714417, 0.000000, \
                                145.449997, 0.000000, 0.000000, 0.000000, 0.000000, \
                                145.449997, 0.000000, 0.000000, 0.000000, 0.000000, \
                                0.000000, 0.000000, 0.000000, 0.000000, 0.000000, \
                                0.000000, 0.000000, 0.000000, 0.000000, 0.000000, \
                                0.000000, 0.000000, 0.000000, 0.000000, 0.000000, \
                                0.000000, 0.000000, 0.000000, 0.000000, 0.000000, \
                                0.000000, 0.000000, 0.000000, 0.000000, 0.000000, \
                                0.000000, 0.000000, 0.000000, 0.000000, 0.000000, \
                                0.000000, 0.000000, 0.000000, 0.000000, 0.000000, \
                                0.000000, 0.000000, 0.000000, 0.000000, 0.000000, \
                                0.000000, 0.000000, 0.000000, 0.000000, 0.000000, \
                                0.000000, 0.000000, 0.000000, 0.000000, 0.000000]
        iriOutput = self.iface.iri2016pharlap(iriIO)

        logger.info('foF2={:10.6e}, hmF2={:10.6e}, foF1={:10.6e}, foE={:10.6e}'
                    ', B0={:10.6e}, B1={:10.6e}'.format(
                    iriOutput.oarr[0],\
                    iriOutput.oarr[1],\
                    iriOutput.oarr[2],\
                    iriOutput.oarr[4],\
                    iriOutput.oarr[9],\
                    iriOutput.oarr[34]))

        self.assertEqual(numpy.sqrt(8.07e7*(iriOutput.oarr[0]/1.e6+.5))/1.e6, 8.047211712423925)
        self.assertAlmostEqual(iriOutput.oarr[1], 237.5094604492188 ,places = 4)
        self.assertEqual(iriOutput.oarr[2], -1)
        self.assertEqual(numpy.sqrt(8.07e7*(iriOutput.oarr[4]/1.e6+.5))/1.e6, 2.751198152708307)
        self.assertAlmostEqual(iriOutput.oarr[9], 72.368728637695312, places = 4)
        self.assertAlmostEqual(iriOutput.oarr[34], 2.827908277511597, places = 4)

        return
    
    def test_raytrace_3d(self):
        pass

if __name__ == "__main__":
    logger.setLevel('INFO')
    unittest.main()
