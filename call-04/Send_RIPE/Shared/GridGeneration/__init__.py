from datetime import datetime
import numpy
import Shared.Utils.DateTime as DateTime
import igrf12
import PfProfileToEnGrid

def genBNED(latDeg, lonDeg, UT, altKm):

    yeardec = DateTime.iso8601ToDecimalYear(datetime(*UT))
    colat = 90.0 - latDeg
    elon = (360.0 + lonDeg) % 360.0
    a = altKm

    isv = 0
    itype = 1

    Bnorth, Beast, Bdown, Btotal = igrf12.igrf12syn(isv, yeardec, itype, a, colat, elon)
    Bnorth = 1.0e-9 * Bnorth
    Beast = 1.0e-9 * Beast
    Bdown = 1.0e-9 * Bdown

    return Bnorth, Beast, Bdown


def genBXYZ(date, numLat, numLon, numHt, BLatStart, BLatInc, BLonStart, BLonInc, BHtStart, BHtInc):

    Bx, By, Bz = igrf12.igrf12gridxyz(date, numLat, numLon, numHt, BLatStart, BLatInc, BLonStart, BLonInc, BHtStart, BHtInc)

    return Bx.transpose(), By.transpose(), Bz.transpose()


# def pfProfileToEnGrid(ionoPfProfile, winFun, tiltLat, tiltLon, refLat, refLon, numLat, numLon, numHt, latArr, lonArr, htArr):

#     ionoEnGrid = PfProfileToEnGrid.pfprofiletoengrid(ionoPfProfile, winFun, tiltLat, tiltLon, refLat, refLon, numLat, numLon, numHt, latArr, lonArr, htArr)

def pfProfileToEnGrid(ionoPfProfile, winFun, tiltLat, tiltLon, refLat, refLon, latArr, lonArr, htArr):

    ionoEnGrid = PfProfileToEnGrid.pfprofiletoengrid(ionoPfProfile, winFun, tiltLat, tiltLon, refLat, refLon, latArr, lonArr, htArr)

    return ionoEnGrid.transpose()