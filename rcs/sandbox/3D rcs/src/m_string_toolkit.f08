! 3456789 123456789 223456789 323456789 423456789 523456789 623456789 723456789 823456789 923456789 023456789 123456789 223456789 32
module mStringToolkit

    use mFormatDescriptors,             only : fmt_one, fmt_two, fmt_three

    implicit none

contains

    subroutine stringPad ( myInteger, finalLength, padCharacter, strInteger )
        integer,               intent ( in )  :: myInteger, finalLength
        character ( len = 1 ), intent ( in )  :: padCharacter
        character ( len = * ), intent ( out ) :: strInteger

        character ( len = 256 ) :: pads = ""
        integer :: intLength = 0, lengthDeficit = 0, &
                    j = 0, k = 0

            write ( strInteger , fmt_one ) myInteger
            intLength = len_trim ( strInteger )
            lengthDeficit = finalLength - intLength

            if ( lengthDeficit < 0 ) then
                write ( * , fmt = '(  g0 )' ) "Error in the call to 'stringPad'!"
                write ( * , fmt = '( 5g0 )' ) "Requested string length ( ", finalLength, &
                                        " ) is less than length of integer ( ", intLength, " )."
                write ( * , fmt = '( 2g0 )' ) "myInteger    = ", myInteger
                write ( * , fmt = '( 2g0 )' ) "finalLength  = ", finalLength
                write ( * , fmt = '( 2g0 )' ) "padCharacter = ", padCharacter
                write ( * , fmt = '( 2g0 )' ) "strInteger   = ", strInteger
                return
            end if

            if ( lengthDeficit == 0 ) then
                return
            end if

            ! must pad left with lengthDeficit padCharacter
            do k = 1, finalLength
                pads ( k : k ) = padCharacter
            end do
            ! add characters from integer
            do k = 1, intLength
                j = finalLength - intLength + k + 1
                pads ( j : j ) = strInteger ( k : k )
            end do

            strInteger = trim ( pads )

        return
    end subroutine stringPad

end module mStringToolkit
