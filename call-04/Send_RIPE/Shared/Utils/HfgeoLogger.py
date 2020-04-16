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

import logging
import pprint

## @package Shared.Utils.HfgeoLogger
#  Wrapper to the python's default logger. 
#  NOTE : The default logger is a singleton

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%d-%m-%Y:%H:%M:%S',
                    level='INFO')

## Get the logger with the formated configs
#
#  @retval The logger for debug, info, etc...
#
def getLogger(name="HFGEO"):
    return logging.getLogger(name)
