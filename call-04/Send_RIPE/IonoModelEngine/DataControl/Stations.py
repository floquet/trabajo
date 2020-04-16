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

## @package IonoModelEngine.DataControl.Stations
#  STATIC Ionosonde station locations; This should not change

import unittest
import Shared.Utils.HfgeoLogger as Logger

logger = Logger.getLogger()

## Class for information of stations
#
class Station:

		__slots__ = ("name", "longitude", "latitude")

		def __init__(self, name, longitude, latitude):
				## Name of the station
				self.name = name
				## Longitude in degrees
				self.longitude = longitude
				## Latitude in degrees
				self.latitude = latitude

## Get the station latlon as a tuple
#
#  @param ursi_name - string - name of the station
#
#  @retval station - Station - a station object
#
def getStation(ursi_name):
		if ursi_name == 'BC840':
				return Station('BC840', 40.0, 254.7)
		elif ursi_name == 'AU930':
				return Station('AU930', 30.4, 262.3)
		elif ursi_name == 'EG931':
				return Station('EG931', 30.5, 273.5)
		elif ursi_name == 'WP937':
				return Station('WP937', 37.9, 284.5)
		elif ursi_name == 'PA836':
				return Station('PA836', 34.8, 239.5)
		elif ursi_name == 'MHJ45':
				return Station('MHJ45', 42.6, 288.5)
		elif ursi_name == 'IF843':
				return Station('IF843', 43.8, 247.3)
		elif ursi_name == 'AL945':
				return Station('AL945', 45.07, 276.44)

## Get the station latlon as a tuple
#
#  @param ursi_name - string - name of the station
#
#  @retval latlon - (number, number) - latlon of the station
#
def getStationLatLon(ursi_name):
		if ursi_name == 'BC840':
				return (40.0, 254.7)
		elif ursi_name == 'AU930':
				return (30.4, 262.3)
		elif ursi_name == 'EG931':
				return (30.5, 273.5)
		elif ursi_name == 'WP937':
				return (37.9, 284.5)
		elif ursi_name == 'PA836':
				return (34.8, 239.5)
		elif ursi_name == 'MHJ45':
			  return (42.6, 288.5)
		elif ursi_name == 'IF843':
			  return (43.8, 247.3)
		elif ursi_name == 'AL945':
				return (45.07, 276.44)
		else:
				return (None, None)

class UnitTest_Stations(unittest.TestCase):

    def test(self):
#      stations = Station('MHJ',23,134)
      (lat,lon) = getStationLatLon('BC840')
      self.assertEqual(lat,40.0)
      self.assertEqual(lon,254.7)



if __name__ == '__main__':
    logger.setLevel('INFO')
    unittest.main()
