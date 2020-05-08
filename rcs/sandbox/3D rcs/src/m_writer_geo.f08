! 3456789 123456789 223456789 323456789 423456789 523456789 623456789 723456789 823456789 923456789 023456789 123456789 223456789 32
module mWriterGeo

    use mFileHandling,                  only : safeopen_writereplace
    use mFormatDescriptors,             only : fmt_one
    use mQuarry,                        only : quarry

    implicit none

    character ( len = * ), parameter :: fmt_incAngles  = '( f10.6, 2X, f10.6, I5 )'
    character ( len = * ), parameter :: fmt_loneAngle  = '( f11.6 )'

contains

    subroutine writeGeoElevation ( myQuarry, elevation )
        type ( quarry ), intent ( in ) :: myQuarry
        real,            intent ( in ) :: elevation
        integer :: unit = 0

            unit = safeopen_writereplace ( filename = trim ( myQuarry % dirInputs ) // trim ( myQuarry % geoFile ) )

            call writeInitiator ( unit = unit, tag = trim ( myQuarry % quarry_name ) )
            call writeMM_MOM ( unit = unit )
            call writeScratch_Memory ( unit = unit )
            call writeQUADRATURE ( unit = unit )
            call writeFREQUENCY ( unit = unit, mhzStart = 3.0, mhzStop = 30.0, mhzStep = 28 )
            call writeExcitation ( unit = unit )
            call writeAngleAzimuth ( unit = unit, yawStart = 0.0, yawStop = 359.0, yawStep = 360, elevation = elevation )
            call writeBoundary_Conditions ( unit = unit, materialsLib = trim ( myQuarry % materialsFile ) )
            call writeSpecifiers ( unit = unit, IE = "SIE", facetFile = trim ( myQuarry % facetFile ), unitsDimensions = "m" )
            call writeTerminator ( unit = unit )

        return
    end subroutine writeGeoElevation

    subroutine writeGeo ( myQuarry )
        type ( quarry ), intent ( in ) :: myQuarry

            call writeGeoElevation ( myQuarry, elevation = 90.0 )

        return
    end subroutine writeGeo

    subroutine writeAngleAzimuth ( unit, yawStart, yawStop, yawStep, elevation )
        real,    intent ( in ) :: yawStart, yawStop, elevation
        integer, intent ( in ) :: yawStep
        integer, intent ( in ) :: unit

            write ( unit , fmt_one ) "Angle Cut"
            write ( unit , fmt_one ) "  1"
            write ( unit , fmt_incAngles ) yawStart, yawStop, yawStep
            write ( unit , fmt_one ) "  AZIMUTH"
            write ( unit , fmt_loneAngle ) elevation
            write ( unit , * )

        return
    end subroutine writeAngleAzimuth

    subroutine writeAngleElevation ( unit, pitchStart, pitchStop, pitchStep, azimuth )
        real,    intent ( in ) :: pitchStart, pitchStop, azimuth
        integer, intent ( in ) :: pitchStep
        integer, intent ( in ) :: unit

            write ( unit , fmt_one ) "Angle Cut"
            write ( unit , fmt_one ) "  1"
            write ( unit , fmt_incAngles ) pitchStart, pitchStop, pitchStep
            write ( unit , fmt_one ) "  ELEVATION"
            write ( unit , fmt_loneAngle ) azimuth
            write ( unit , * )

        return
    end subroutine writeAngleElevation

    subroutine writeSpecifiers ( unit, IE, facetFile, unitsDimensions )
        integer,               intent ( in ) :: unit
        character ( len = * ), intent ( in ) :: IE, facetFile, unitsDimensions

            write ( unit , fmt_one ) trim ( IE )
            write ( unit , fmt_one ) trim ( facetFile )
            write ( unit , fmt_one ) trim ( unitsDimensions )
            write ( unit , * )

        return
    end subroutine writeSpecifiers

    subroutine writeBoundary_Conditions ( unit, materialsLib )
        integer,               intent ( in ) :: unit
        character ( len = * ), intent ( in ) :: materialsLib

            write ( unit , fmt_one ) "Boundary Conditions"
            write ( unit , fmt_one ) trim ( materialsLib )
            write ( unit , fmt_one ) "4"
            write ( unit , fmt_one ) "V_FREE_SPACE => Free_Space"
            write ( unit , fmt_one ) "V_PEC => PEC"
            write ( unit , fmt_one ) "V_PMC => PMC"
            write ( unit , fmt_one ) "V_NULL => NULL"
            write ( unit , fmt_one ) "1"
            write ( unit , fmt_one ) "0 BC_PEC V_FREE_SPACE"
            write ( unit , * )

        return
    end subroutine writeBoundary_Conditions

    subroutine writeExcitation ( unit )
        integer, intent ( in ) :: unit

            write ( unit , fmt_one ) "Excitation"
            write ( unit , fmt_one ) "  MONOSTATIC"
            write ( unit , * )

        return
    end subroutine writeExcitation

    subroutine writeFREQUENCY ( unit, mhzStart, mhzStop, mhzStep )
        real,    intent ( in ) :: mhzStart, mhzStop
        integer, intent ( in ) :: unit, mhzStep

            write ( unit , fmt_one ) "FREQUENCY"
            write ( unit , fmt_one ) "  mhz"
            write ( unit , 100 ) mhzStart, mhzStop, mhzStep
            write ( unit , * )

        return
        100 format ( 2( F10.6, 1X ), I6, 3X, "!Freq Start, Freq Stop, Number of Frequencies" )
    end subroutine writeFREQUENCY

    subroutine writeQUADRATURE ( unit )
        integer, intent ( in ) :: unit

            write ( unit , fmt_one ) "&QUADRATURE"
            write ( unit , fmt_one ) "  NTRISELF    = 7,"
            write ( unit , fmt_one ) "  NTRINEAR    = 3,"
            write ( unit , fmt_one ) "  NTRIFAR     = 3,"
            write ( unit , fmt_one ) "  NTETSELF    = 11,"
            write ( unit , fmt_one ) "  NTETNEAR    = 4,"
            write ( unit , fmt_one ) "  NTETFAR     = 4,"
            write ( unit , fmt_one ) "  NQGAUSS  = 4,"
            write ( unit , fmt_one ) "/"
            write ( unit , * )

        return
    end subroutine writeQUADRATURE

    subroutine writeScratch_Memory ( unit )
        integer, intent ( in ) :: unit

            write ( unit , fmt_one ) "&Scratch_Memory"
            write ( unit , fmt_one ) "  Scratch_RankFraction_Z     = 0.300000,"
            write ( unit , fmt_one ) "  Scratch_RankFraction_LU    = 0.600000,"
            write ( unit , fmt_one ) "  Scratch_RankFraction_RHS   = 2.000000,"
            write ( unit , fmt_one ) "  Scratch_RankFraction_Solve = 1.000000,"
            write ( unit , fmt_one ) "  MemoryFraction_Z           = 0.950000,"
            write ( unit , fmt_one ) "  MemoryFraction_Scratch_LU  = 0.500000,"
            write ( unit , fmt_one ) "  MemoryFraction_LU          = 1.000000,"
            write ( unit , fmt_one ) "  MemoryFraction_RHS         = 0.500000,"
            write ( unit , fmt_one ) "  MemoryFraction_Solve       = 0.900000,"
            write ( unit , fmt_one ) "/"
            write ( unit , * )

        return
    end subroutine writeScratch_Memory

    subroutine writeMM_MOM ( unit )
        integer, intent ( in ) :: unit

            write ( unit , fmt_one ) "&MM_MOM"
            write ( unit , fmt_one ) "  bUseACA = .TRUE.,"
            write ( unit , fmt_one ) "  bSolve_ACA = .TRUE.,"
            write ( unit , fmt_one ) "  bOutOfCore = .TRUE.,"
            write ( unit , fmt_one ) "  bNormalizeToWaveLength = .FALSE.,"
            write ( unit , fmt_one ) "  bNormalize             = .FALSE.,"
            write ( unit , fmt_one ) "  dCloseLambda  = 0.100000,"
            write ( unit , fmt_one ) "  ACA_Factor_Tol = 0.000010,"
            write ( unit , fmt_one ) "  ACA_RHS_Tol = 0.000100,"
            write ( unit , fmt_one ) "  Point_Tolerance = 0.001000,"
            write ( unit , fmt_one ) "  nLargestBlockSize = -1,"
            write ( unit , fmt_one ) "  MemorySize_GB = -1.000000,"
            write ( unit , fmt_one ) "  stackSize_GB = -1.000000,"
            write ( unit , fmt_one ) "  nFillThreads = -1,"
            write ( unit , fmt_one ) "  nFillMKLThreads = 1,"
            write ( unit , fmt_one ) "  nLUThreads = -1,"
            write ( unit , fmt_one ) "  nLUMKLThreads = 1,"
            write ( unit , fmt_one ) "  nRHSThreads = 1,"
            write ( unit , fmt_one ) "  nRHSMKLThreads = 1,"
            write ( unit , fmt_one ) "  bOutputACAGrouping     = .FALSE.,"
            write ( unit , fmt_one ) "  bOutputRankFraction    = .FALSE.,"
            write ( unit , fmt_one ) "  bLimitLUColumns        = .FALSE.,"
            write ( unit , fmt_one ) "  Lop_Admissibility = WEAK,"
            write ( unit , fmt_one ) "  Kop_Admissibility = CLOSE"
            write ( unit , fmt_one ) "/"
            write ( unit , * )

        return
    end subroutine writeMM_MOM

    subroutine writeInitiator ( unit, tag )
        integer,               intent ( in ) :: unit
        character ( len = * ), intent ( in ) :: tag

            write ( unit , fmt_one ) trim ( tag )
            write ( unit , * )
            write ( unit , fmt_one ) "!Mercury MoM input file, VIE/SIE Version 4.x compatible (VIE/Dual Sided SIE)"
            write ( unit , * )

        return
    end subroutine writeInitiator

    subroutine writeTerminator ( unit )
        integer, intent ( in ) :: unit

            write ( unit , fmt_one ) "Geometry_End"
            write ( unit , * )

        return
    end subroutine writeTerminator

end module mWriterGeo
