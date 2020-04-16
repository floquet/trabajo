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

import RIPE
from datetime import datetime
import numpy as np
import unittest
from Shared.IonoPyIface.Pharlap import Pharlap
from IonoModelEngine.DataControl.Stations import getStationLatLon
import Shared.Utils.HfgeoLogger as Logger
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import os

from IonoModelEngine.IRTAM import IRTAM
from IonoModelEngine.IRTAM.IrtamPyIface import IrtamPyIface

#   define the target time
logger = Logger.getLogger()
logger.setLevel('INFO')

## @package IonoModelEngine.RIPE_map
# Make contour maps of profile parameters from RIPE and (optionally) from IRI

class RIPE_map:
    ## Constructor requests the python interface
    #
    def __init__(self, pharlapHandle=None, irtamHandle=None):

        # Get the python interface this class should never own one
        self.pharlapHandle = pharlapHandle

        self.irtamHandle = irtamHandle

        self.refreshIRI = 0         # default is not to refresh

        self.interpolatingModel = 1 # default is IRI


    ## Make contour map of the specified RIPE parameter
    #
    #  @param TargetTime - the time of interest (a python datetime structure)
    #  @param listOfFiles - a list of full paths to the RIPE input files for all stations
    #  @param plotvar - the parameter to be plotted 'foF2','hmF2','b0' or 'b1'
    #
    def MakeMap(self, TargetTime, listOfFiles, plotvar):

        #   get the interface to pharlap/IRI
        #pharlapHandle = Pharlap()

        #   initialize RIPE class
        #tagger=RIPE.RIPE(pharlapHandle)

        tagger = RIPE.RIPE(pharlapHandle=self.pharlapHandle, irtamHandle=self.irtamHandle, \
                         refreshIRI=self.refreshIRI, interpolatingModel=self.interpolatingModel)

        #   set the following flag to 1 to plot IRI
        PlotIRI=1

        year   = TargetTime.year
        month  = TargetTime.month
        day    = TargetTime.day
        hour   = TargetTime.hour
        minute = TargetTime.minute

        #   get the day of year
        doy = (TargetTime - datetime(year, 1, 1)).days + 1


        #   make the image filename
        if self.interpolatingModel==0:
            ImageFile=('RIPE_'+plotvar+'_%4d%2.2d%2.2d_%2.2d%2.2d.png' % \
                (year,month,day,hour,minute))

            #   create the header
            if PlotIRI == 0:
                title = ('RIPE ' + plotvar + ' Contours (MHz) - %4d/%2.2d/%2.2d (%3.3d) %2.2d:%2.2d UT' \
                         % (year, month, day, doy, hour, minute))
            else:
                title = ('RIPE and IRI (red) ' + plotvar + ' Contours (MHz) - %4d/%2.2d/%2.2d (%3.3d) %2.2d:%2.2d UT' \
                         % (year, month, day, doy, hour, minute))

        else:
            ImageFile = ('RIPE-IRTAM_' + plotvar + '_%4d%2.2d%2.2d_%2.2d%2.2d.png' % \
                         (year, month, day, hour, minute))
            #   create the header
            if PlotIRI == 0:
                title = ('RIPE-IRTAM ' + plotvar + ' Contours (MHz) - %4d/%2.2d/%2.2d (%3.3d) %2.2d:%2.2d UT' \
                         % (year, month, day, doy, hour, minute))
            else:
                title = ('RIPE-IRTAM and IRTAM (red) ' + plotvar + ' Contours (MHz) - %4d/%2.2d/%2.2d (%3.3d) %2.2d:%2.2d UT' \
                         % (year, month, day, doy, hour, minute))

        logger.info('Plotting:%s',title)

        logger.info('Target Time is %s',str(TargetTime))

        #   get the station ratios for the target time
        (stlats,stlons,fof2_rats,hmf2_rats,b0_rats,b1_rats) = \
            RIPE.RIPE.GetRIPE5sfs(tagger, TargetTime, listOfFiles)

        #   define the arrays and vector for the data
        ripe_data=np.zeros((26,36))

        if PlotIRI == 1:
            imodel_data=np.zeros((26,36))

        longitudes = np.zeros(36)
        latitudes  = np.zeros(26)

        #   now loop through the latitudes and longitudes and compute the foF2 values
        for i in range(0,26):
            Lat=i+25
            for j in range(0,36):
                Lon=j*2+230

                #   first get the ratios there
                (fof2_rat,hmf2_rat,b0_rat,b1_rat) = \
                     RIPE.RIPE.InterpRIPE5sfs(tagger,Lat,Lon,stlats,stlons, \
                          fof2_rats,hmf2_rats,b0_rats,b1_rats)

                # Calculate RIPE parameters
                #(ripe_fof2, ripe_hmf2, ripe_b0, ripe_b1) = \
                #    RIPE.RIPE.CalcParameters(tagger, Lat, Lon, TargetTime, listOfFiles)

                #   get IRI at this location
                #UT=[year,month,day,hour,minute]

                #r12=-1

                #(pro,extra) = tagger.pharlapHandle.iri2016(Lat,Lon,r12,UT)

                #iri_parms = self.pharlapHandle.iono_extra_to_layer_parameters(extra)

                #iri_fof2 = iri_parms[0]
                #iri_hmf2 = iri_parms[1]
                #iri_b0   = iri_parms[5]
                #iri_b1   = iri_parms[6]

                #   and get the RIPE values
                #ripe_fof2 = iri_fof2*fof2_rat
                #ripe_hmf2 = iri_hmf2*hmf2_rat
                #ripe_b0   = iri_b0*b0_rat
                #ripe_b1   = iri_b1*b1_rat

                if self.interpolatingModel == 0:
                    UT = [year, month, day, hour, minute]

                    r12 = -1

                    (pro, extra) = tagger.pharlapHandle.iri2016(Lat, Lon, r12, UT)

                    iri_parms = self.pharlapHandle.iono_extra_to_layer_parameters(extra)

                    foF2 = iri_parms[0]
                    hmF2 = iri_parms[1]
                    B0   = iri_parms[5]
                    B1   = iri_parms[6]

                if self.interpolatingModel == 1:
                    # Get the interface to IRTAM
                    irtam = IRTAM.IRTAM(self.irtamHandle, self.pharlapHandle)

                    # Calculate IRTAM parameters
                    (foF2, hmF2, B0, B1) = irtam.CalcParameters(Lat, Lon, TargetTime, listOfFiles)

                # apply the ratios
                ripe_fof2 = foF2 * fof2_rat
                ripe_hmf2 = hmF2*hmf2_rat
                ripe_b0   = B0*b0_rat
                ripe_b1   = B1*b1_rat

                latitudes[i]  = Lat
                longitudes[j] = Lon

                print(Lat,Lon,ripe_fof2,ripe_hmf2,ripe_b0,ripe_b1)

                if 'foF2' in plotvar:
                    fmt = '%.2f'
                    delta = 0.25
                    offset = 0.0
                    ripe_data[i][j] = ripe_fof2
                    if PlotIRI == 1:
                        imodel_data[i][j] = foF2

                if 'hmF2' in plotvar:
                    fmt = '%d'
                    delta = 5.0
                    offset = 100.0
                    ripe_data[i][j] = ripe_hmf2
                    if PlotIRI == 1:
                        imodel_data[i][j] = hmF2

                if 'b0' in plotvar:
                    fmt = '%d'
                    delta = 5.0
                    offset = 0.0
                    ripe_data[i][j] = ripe_b0
                    if PlotIRI == 1:
                        imodel_data[i][j] = B0

                if 'b1' in plotvar:
                    fmt = '%.2f'
                    delta = 0.1
                    offset = 0.0
                    ripe_data[i][j] = ripe_b1
                    if PlotIRI == 1:
                        imodel_data[i][j] = B1

        #   setup the map boundaries
        map=Basemap(projection='cyl',llcrnrlon=230.0, \
              llcrnrlat=25.0,urcrnrlon=300.0,urcrnrlat=50.0, \
                   lat_0=30.0,lon_0=275.0,fix_aspect=0)

        #   define the figure size
        fig=plt.figure(figsize=(11,6.5),dpi=100)

        #   draw the geographical stuff
        map.drawcoastlines()
        map.drawcountries()
        map.drawstates()
        map.drawmapboundary(fill_color='aqua')
        map.fillcontinents(color='bisque',lake_color='aqua')

        #   set the levels
        vlevels=[]

        for i in range(0,41):
            vlevels.append(offset + i*delta)

        #   plot the contours
        CS = plt.contour(longitudes,latitudes,ripe_data, \
              vlevels,colors='black')

        plt.clabel(CS,inline=1,fontsize=10,fmt=fmt)

        #   (optionally) plot the IRI contours
        if PlotIRI == 1:
            CS=plt.contour(longitudes,latitudes,imodel_data, \
                vlevels,colors='red')
            plt.clabel(CS,inline=1,fontsize=10,fmt=fmt)

        #   put on the station locations
        for fname in listOfFiles:
            # get station name from the file basename
            stationName = os.path.basename(fname)

            # check that filename is the right length
            if len(stationName) != 14:
                logger.debug("{:s} filename is too short, skipping".format(stationName))
                continue

            # check that filename has the right suffix
            if stationName[5:14] != '_NOAA.TXT':
                logger.debug(" {:s} filename is missing _NOAA.TXT suffix, skipping".format(stationName))
                continue

            stationName = stationName[0:5]
            (stationLat,stationLon) = getStationLatLon(stationName)
            plt.text(stationLon,stationLat,stationName,color='blue')

        #   put on the title
        plt.title(title)

        #   make the white space narrow
        plt.tight_layout()

        #   save the image
        plt.savefig(ImageFile)
        #plt.show()

        return

class UnitTest_RIPE_map(unittest.TestCase):

    def setUp(self):

        # Instantiate the RIPE_map class
        pharlapHandle = Pharlap()

        irtamHandle = IrtamPyIface()

        self.ripemap = RIPE_map(pharlapHandle=pharlapHandle, irtamHandle=irtamHandle)


    ##   Test MakeMap
    #
    def test_RIPE_map(self):

        #   directory with input files to process
        directory = os.path.dirname(os.path.realpath(__file__)) + "/"

        #   list of input files to process
        #listOfFiles = [directory + '/TestFiles/AU930_NOAA.TXT', \
        #               directory + '/TestFiles/BC840_NOAA.TXT', \
        #               directory + '/TestFiles/EG931_NOAA.TXT']

        listOfFiles = [directory + '/TestFiles/AU930_NOAA.TXT', \
                       directory + '/TestFiles/BC840_NOAA.TXT', \
                       directory + '/TestFiles/EG931_NOAA.TXT', \
                       directory + '../IRTAM/UnitTestData/IRTAM_foF2_COEFFS_20151020_0000.ASC', \
                       directory + '../IRTAM/UnitTestData/IRTAM_hmF2_COEFFS_20151020_0000.ASC', \
                       directory + '../IRTAM/UnitTestData/IRTAM_B0_COEFFS_20151020_0000.ASC', \
                       directory + '../IRTAM/UnitTestData/IRTAM_B1_COEFFS_20151020_0000.ASC']

        #   date and time for the map
        year   = 2015
        month  = 10
        day    = 20
        hour   = 0
        minute = 0
        second = 0

        #   make this a datetime
        TargetTime = datetime(year, month, day, hour, minute, second)

        self.interpolatingModel = 1
        self.refreshIRI = 1

        # make contour plot of foF2
        plotvar = 'foF2'
        self.ripemap.MakeMap(TargetTime, listOfFiles, plotvar)

        # make contour plot of hmF2
        plotvar = 'hmF2'
        self.ripemap.MakeMap(TargetTime, listOfFiles, plotvar)

        # make contour plot of b0
        plotvar = 'b0'
        self.ripemap.MakeMap(TargetTime, listOfFiles, plotvar)

        # make contour plot of b1
        plotvar = 'b1'
        self.ripemap.MakeMap(TargetTime, listOfFiles, plotvar)



if __name__ == "__main__":
    logger.setLevel('INFO')
    unittest.main()
