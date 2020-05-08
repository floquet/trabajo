! 3456789 123456789 223456789 323456789 423456789 523456789 623456789 723456789 823456789 923456789 023456789 123456789 223456789 32
module mQuarry

    use mStringToolkit,                 only : stringPad

    implicit none

    type :: quarry
        character ( len = 256 ) :: quarry_name = ""
        character ( len = 256 ) :: stem = ""
        character ( len = 256 ) :: geoFile = ""
        character ( len = 256 ) :: outFile = ""
        character ( len = 256 ) :: momFile = ""
        character ( len = 256 ) :: facetFile = ""
        character ( len = 256 ) :: materialsFile = ""
        character ( len = 256 ) :: dirInputs = ""
        character ( len = 256 ) :: dirOutputs = ""
        character ( len = 256 ) :: angle_str = ""
        character ( len = 256 ) :: angle_type = ""
        integer                 :: angle_int = 0
    contains
        procedure, public :: setDirectories => setDirectories_sub
        procedure, public :: fullFileNames  => fullFileNames_sub
        procedure, public :: stemFileNames  => stemFileNames_sub
    end type quarry
    ! constructor
!    type ( quarry ), parameter :: quarry0 = ( quarry_name = "", stem = "", geoFile = "", outFile = "", dirInputs = "", &
!                        dirOutputs = "", angle_str = "", angle_type = "", angle_int = 0 )
!    type ( quarry ), parameter :: quarry0 = ( "", "", "", "", "", "", "", "", 0 )

    private :: setDirectories_sub, stemFileNames_sub, fullFileNames_sub

contains

    subroutine setDirectories_sub ( me, dirIn, dirOut )
        class ( quarry ), target :: me
        character ( len = * ), intent ( in ) :: dirIn, dirOut

            me % dirInputs  = trim ( dirIn )
            me % dirOutputs = trim ( dirOut )

        return
    end subroutine setDirectories_sub

    subroutine stemFileNames_sub ( me, quarry_name, angle_type )
        class ( quarry ), target :: me
        character ( len = * ), intent ( in ) :: quarry_name, angle_type

            me % quarry_name = trim ( quarry_name )
            me % angle_type  = trim ( angle_type )
            me % stem        = trim ( quarry_name ) // trim ( angle_type )

        return
    end subroutine stemFileNames_sub

    subroutine fullFileNames_sub ( me,  angle )
        class ( quarry ), target :: me
        integer, intent ( in )   :: angle
        character ( len = 256 )  :: myString = ""

            me % angle_int = angle

            call stringPad ( myInteger = angle, strInteger = myString, finalLength = 4, padCharacter = "0" )
            me % angle_str     = myString
            me % geoFile       = trim ( me % stem ) // trim ( myString ) // ".geo"
            me % outFile       = trim ( me % stem ) // trim ( myString ) // ".out"
            me % momFile       = trim ( me % stem ) // trim ( myString ) // ".4112.txt"
            me % facetFile     = trim ( me % quarry_name ) // ".facet"
            me % materialsFile = trim ( me % quarry_name ) // "-Materials.lib"

        return
    end subroutine fullFileNames_sub

end module mQuarry
