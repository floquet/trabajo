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

#import math
#import os
#import pathlib
#import numpy
#import logging
#import scipy.optimize
import unittest
#from datetime import datetime, date, time
#from scipy.optimize import curve_fit
#from scipy.optimize import minimize
#from scipy.interpolate import interp1d
import Shared.Utils.HfgeoLogger as Logger
#import IonoModelEngine.Fit.FitProfile as FitProfile
#import IonoModelEngine.DataControl.Stations as stations

logger = Logger.getLogger()

## @package IonoModelEngine.GetProfileParameters
#
#  Module that runs profile fitting to derives B0, B1 
#  and saves the results in RIPE/ROAM - input format
  
## Method to format output according to format convention
#
#  @param[in] - fmt: format specifier
#  @param[in] - value: output value
#
def printout(fmt, value):
    if value == 0 or value == -1 or value == 9999.0:
        return "   --- "
    else:
        return fmt.format(value)

## Main method that calls ReadSao and FitProfile and saves parameters
#
#  @param - string - the full output file name
#
#  @return - list of string - list of full file name that has been translated
#






if __name__ == "__main__":
    logger.setLevel('INFO')
    unittest.main()


