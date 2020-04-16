! Subroutine to generate an electron density grid from a plasma frequency profile, window function, and tilt factors.
subroutine pfProfileToEnGrid(ionoEnGrid, ionoPfProfile, winFun, tiltLat, tiltLon, refLat, refLon, &
    numLat, numLon, numHt, latArr, lonArr, htArr)

    implicit none
    integer, intent(in) :: numLat, numLon, numHt
    real(8), intent(in) :: tiltLat, tiltLon
    real(8), intent(in) :: refLat, refLon
    real(8), intent(in), dimension(numHt) :: ionoPfProfile, winFun
    real(8), intent(in), dimension(numLat) :: latArr
    real(8), intent(in), dimension(numLon) :: lonArr
    real(8), intent(in), dimension(numHt) :: htArr
    real(8), intent(out), dimension(numLat, numLon, numHt) :: ionoEnGrid

    integer :: iLat, iLon, iHt
    real(8) :: dLat, dLon, ht
    real(8) :: pfVal, pfWeighted
    real(8) :: tiltFactor
    real(8) :: winVal
    real(8), parameter :: pfToEn = 80.6164d-6 ! Conversion from plasma frequency (MHz) to electron density (cm^-3).

    !$OMP DO
    do iHt = 1, numHt
        ht = htArr(iHt)
        pfVal = ionoPfProfile(iHt)
        winVal = winFun(iHt)
        do iLon = 1, numLon
            dLon = lonArr(iLon) - refLon
            do iLat = 1, numLat
                dLat = latArr(iLat) - refLat
                ! Apply the tilt to the plasma frequency.
                tiltFactor = 1.0d0 + (tiltLat*winVal*dLat) + (tiltLon*winVal*dLon)
                pfWeighted = pfVal * tiltFactor
                ! Conversion from plasma frequency to electron density.
                ionoEnGrid(iLat, iLon, iHt) = pfWeighted*pfWeighted/pfToEn
            end do
        end do
    end do
    !$OMP END DO

end subroutine pfProfileToEnGrid