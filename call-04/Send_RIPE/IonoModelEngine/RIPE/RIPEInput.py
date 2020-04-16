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

class RIPEInput(Object):

    __slots__ = ['stationName', 'stationLat', 'stationLon', 'datetime', 'cscore', 'foF2', 'hmF2', 'B0', 'B1']
    
    def __init__:
        
        self.stationName = None
        self.stationLat = None
        self.stationLon = None
        self.datetime = []
        self.cscore = []
        self.foF2 = []
        self.hmF2 = []
        self.B0 = []
        self.B1 = []

    def parseFromFile(self, filename):
        stationName = os.path.basename(filename)
        self.stationName = stationName[0:5]
        self.stationLat = 
        self.stationLon = 
