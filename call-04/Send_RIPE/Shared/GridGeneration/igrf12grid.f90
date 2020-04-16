subroutine igrf12gridxyz(Bx, By, Bz, date, numLat, numLon, numHt, BLatStart, BLatInc, BLonStart, BLonInc, BHtStart, BHtInc)

    implicit none
    integer, intent(in) :: numLat, numLon, numHt
    real(8), intent(in) :: date
    real(8), intent(in) :: BLatStart, BLatInc, BLonStart, BLonInc, BHtStart, BHtInc
    real(8), intent(out), dimension(numLat, numLon, numHt) :: Bx, By, Bz

    integer :: iLat, iLon, iHt
    real(8) :: lat, lon, ht
    real(8) :: colat, elong
    integer :: isv, itype
    real(8) :: Bn, Be, Bu, Bt
    real(8), parameter :: Pi = 3.1415926535897932d0
    real(8) :: lat_r, lon_r, sin_phi, cos_phi, sin_theta, cos_theta

    isv = 0
    itype = 1

    do iHt = 1, numHt
        ht = BHtStart + real(iHt-1, 8)*BHtInc
        do iLon = 1, numLon
            lon = BLonStart + real(iLon-1, 8)*BLonInc
            lon_r = Pi/180.0*lon
            sin_theta = sin(lon_r)
            cos_theta = cos(lon_r)
            elong = MOD( 360.0 + lon, 360.0)
            do iLat = 1, numLat
                lat = BLatStart + real(iLat-1, 8)*BLatInc
                lat_r = Pi/180.0*lat
                sin_phi = sin(lat_r)
                cos_phi = cos(lat_r)
                colat = 90.0d0 - lat
                    ! Call IGRF12SVN
                call igrf12syn(isv, date, itype, ht, colat, elong, Bn, Be, Bu, Bt)
                ! Transform from NEU to XYZ
                Bx(iLat, iLon, iHt) = 1.0e-9*(-Be*sin_theta - Bn*sin_phi*cos_theta - Bu*cos_phi*cos_theta)
                By(iLat, iLon, iHt) = 1.0e-9*(Be*cos_theta - Bn*sin_phi*sin_theta - Bu*cos_phi*sin_theta)
                Bz(iLat, iLon, iHt) = 1.0e-9*(Bn*cos_phi - Bu*sin_phi)
            end do
        end do
    end do

end subroutine igrf12gridxyz