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

import unittest
from datetime import datetime
import Shared.Utils.HfgeoLogger as Logger

logger = Logger.getLogger()

## @package Shared.Utils.DateTime
#  Utility to do date time

## Return a datetime object as decimal year
#
#  @param dt - The datetime object provided by Python
#
#  @return decimal_year - Time in fraction of year
#
def iso8601ToDecimalYear(dt):
    year_part = dt - datetime(year=dt.year, month=1, day=1)
    year_length = datetime(year=dt.year+1, month=1, day=1) - datetime(year=dt.year, month=1, day=1)
    decimal_year = dt.year + year_part/year_length
    return decimal_year

## dateTimeObj = iso8601ToDateTimeObj(iso8601Str)
#  Converts a string in iso8601 format to a python datetime.datetime object
#
#  @param iso8601Str String in ISO 8601 format
#
#  @retval dateTimeObj datetime.datetime object
#
def iso8601ToDateTimeObj(iso8601Str):
    dateTimeObj = datetime.strptime(iso8601Str,'%Y-%m-%dT%H:%M:%S.%fZ') 
    return dateTimeObj

## iso8601Str = DateTimeObjTois8601(dateTimeObj)
#  Converts a python datetime.datetime object to a string in iso8601 format
#
#  @param dateTimeObj datetime.datetime object
#
#  @retval iso8601Str String in ISO 8601 format
#
def DateTimeObjToiso8601(dateTimeObj):
    iso8601Str = dateTimeObj.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    return iso8601Str

## dateVec = iso8601ToDateVec(iso8601Str)
#  Converts a string in iso8601 format to a python datetime.datetime object
#
#  @param iso8601Str String in ISO 8601 format
#
#  @retval dateVec list in format [year month day hour minute]
#
def iso8601ToDateVec(iso8601Str):
    dateObj = iso8601ToDateTimeObj(iso8601Str)
    dateVec = [dateObj.year, dateObj.month, dateObj.day, dateObj.hour, dateObj.minute] 
    return dateVec

## dateVec = dtToDateVec(dt)
#  Converts a python datetime.datetime object to the date vector format
#
#  @param dateTimeObj datetime.datetime object
#
#  @retval dateVec list in format [year month day hour minute]
#
def dtToDateVec(dt):
    dateVec = [dt.year, dt.month, dt.day, dt.hour, dt.minute]
    return dateVec

class UnitTest_DateTime(unittest.TestCase):
    def test_dateTime2year(self):
        a = iso8601ToDecimalYear(datetime(2000, 9, 21, 0, 0))
        logger.info(a)
        self.assertAlmostEqual(a, 2000.7213, places=4)

if __name__ == '__main__':
    logger.setLevel('INFO')
    unittest.main()
