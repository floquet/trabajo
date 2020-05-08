! 3456789 123456789 223456789 323456789 423456789 523456789 623456789 723456789 823456789 923456789 023456789 123456789 223456789 32
module mWriterBatchCommand
! designed to run in directory with the executable
    use mFileHandling,                  only : safeopen_writereplace
    use mQuarry,                        only : quarry

    implicit none

contains

    subroutine updateBashScript ( myQuarry, unit )
        type ( quarry ), intent ( in ) :: myQuarry
        integer,         intent ( in ) :: unit
        character ( len = 256 ) :: cmd = ""

            write ( unit, fmt = '(  g0 )' ) "export ticks=${SECONDS}"
            write ( cmd,  fmt = '( 3g0 )' ) "new_step 'elevation angle = ", myQuarry % angle_int, " deg from North Pole'"
            write ( unit, fmt = '(  g0 )' ) trim ( cmd )

            write ( unit , * )
            write ( cmd,  fmt = '( 4g0 )' ) "cp .", trim ( myQuarry % dirInputs ), trim ( myQuarry % geoFile ), " ."
            write ( unit, fmt = '( 3g0 )' ) "sub_step '", trim ( cmd ), "'"
            write ( unit, fmt = '( 2g0 )' ) "          ", trim ( cmd )

            write ( unit , * )
            write ( cmd,  fmt = '( 6g0 )' ) "./MMoM_4.1.12 ", trim ( myQuarry % geoFile ), " > .", &
                                                trim ( myQuarry % dirOutputs ), trim ( myQuarry % outFile )
            write ( unit, fmt = '( 3g0 )' ) "sub_step '", trim ( cmd ), "'"
            write ( unit, fmt = '( 2g0 )' ) "          ", trim ( cmd )

            write ( unit , * )
            write ( cmd,  fmt = '( 5g0 )' ) "mv *.4112.* .", trim ( myQuarry % dirOutputs ), "."
            write ( unit, fmt = '( 3g0 )' ) "sub_step '", trim ( cmd ), "'"
            write ( unit, fmt = '( 2g0 )' ) "          ", trim ( cmd )

            write ( unit , * )
            write ( cmd,  fmt = '( 2g0 )' ) "rm ", trim ( myQuarry % geoFile )
            write ( unit, fmt = '( 3g0 )' ) "sub_step '", trim ( cmd ), "'"
            write ( unit, fmt = '( 2g0 )' ) "          ", trim ( cmd )

            write ( unit , * )
            write ( unit, fmt = '(  g0 )' ) 'echo ""'
            write ( cmd,  fmt = '( 3g0 )' ) 'echo "time used to run ', trim ( myQuarry % geoFile ), ' = $((SECONDS-ticks)) s"'
            write ( unit, fmt = '(  g0 )' ) trim ( cmd )

            write ( unit , * )

        return
    end subroutine updateBashScript

    subroutine grabSupportFiles ( myQuarry, unit )
        type ( quarry ), intent ( in )  :: myQuarry
        integer,         intent ( out ) :: unit
        character ( len = 256 ) :: cmd = ""

            write ( unit, fmt = '(  g0 )' ) "# # # shared files"

            write ( cmd , fmt = '( 4g0 )' ) "cp .", trim ( myQuarry % dirInputs ), trim ( myQuarry % quarry_name ), &
                                                "-Materials.lib ."
            write ( unit, fmt = '( 3g0 )' ) "echo '", trim ( cmd ), "'"
            write ( unit, fmt = '( 2g0 )' ) "      ", trim ( cmd )

            write ( cmd , fmt = '( 4g0 )' ) "cp .", trim ( myQuarry % dirInputs ), trim ( myQuarry % quarry_name ), &
                                                ".facet ."
            write ( unit, fmt = '( 3g0 )' ) "echo '", trim ( cmd ), "'"
            write ( unit, fmt = '( 2g0 )' ) "      ", trim ( cmd )

            write ( unit , * )

        return
    end subroutine grabSupportFiles

    subroutine purgeSupportFiles ( myQuarry, unit )
        type ( quarry ), intent ( in )  :: myQuarry
        integer,         intent ( out ) :: unit
        character ( len = 256 ) :: cmd = ""

            write ( unit, fmt = '(  g0 )' ) "new_step 'clear shared files'"

            write ( cmd,  fmt = '( 3g0 )' ) "rm ", trim ( myQuarry % quarry_name ), "-Materials.lib"
            write ( unit, fmt = '( 3g0 )' ) "sub_step '", trim ( cmd ), "'"
            write ( unit, fmt = '( 2g0 )' ) "          ", trim ( cmd )

            write ( cmd,  fmt = '( 3g0 )' ) "rm ", trim ( myQuarry % quarry_name ), ".facet"
            write ( unit, fmt = '( 3g0 )' ) "sub_step '", trim ( cmd ), "'"
            write ( unit, fmt = '( 2g0 )' ) "          ", trim ( cmd )

            write ( cmd,  fmt = '(  g0 )' ) "rm -r tempDir/"
            write ( unit, fmt = '( 3g0 )' ) "sub_step '", trim ( cmd ), "'"
            write ( unit, fmt = '( 2g0 )' ) "          ", trim ( cmd )
            write ( unit, * )

            write ( unit, fmt = '(  g0 )' ) 'echo ""'
            write ( unit, fmt = '(  g0 )' ) 'echo "time used = ${SECONDS} s"'
            write ( unit, fmt = '(  g0 )' ) "date"
            write ( unit, * )

        return
    end subroutine purgeSupportFiles

    subroutine openBashScript ( nameAndPath, header, io )
        character ( len = * ), intent ( in  ) :: nameAndPath, header
        integer,               intent ( out ) :: io
        ! containers for date and time
        integer :: dt_values ( 1 : 8 ) = 0

            ! execution complete - tag output
            call date_and_time ( VALUES = dt_values )

            io = safeopen_writereplace ( trim ( nameAndPath ) )
            write ( io , fmt = '( g0 )' ) "#! /bin/bash"
            write ( io , fmt = '( g0 )' ) 'printf "%s\n" "$(tput bold)$(date) ${BASH_SOURCE[0]}$(tput sgr0)"'
            write ( io , * )
            write ( io , fmt = '( 2g0 )' ) "# generated by ", header
            write ( io , fmt = 100 ) "# ", dt_values ( 1 : 3 ), dt_values ( 5 : 7 )
            write ( io , * )
            write ( io , fmt = '( g0 )' ) "# sequence of operations"
            write ( io , fmt = '( g0 )' ) "# 1. bring in geometry file for specific elevation"
            write ( io , fmt = '( g0 )' ) "# 2. run Mercury MoM - pipe into outputs folder"
            write ( io , fmt = '( g0 )' ) "# 3. move Mercury MoM results file to outputs folder"
            write ( io , fmt = '( g0 )' ) "# 4. remove geometry file"
            write ( io , * )
            write ( io , fmt = "( g0 )" ) '# sequence of operations'
            write ( io , fmt = "( g0 )" ) '# 1. bring in geometry file for specific elevation'
            write ( io , fmt = "( g0 )" ) '# 2. run Mercury MoM - pipe into outputs folder'
            write ( io , fmt = "( g0 )" ) '# 3. move Mercury MoM results file to outputs folder'
            write ( io , fmt = "( g0 )" ) '# 4. remove geometry file'
            write ( io , * )
            write ( io , fmt = "( g0 )" ) '# directory structure:'
            write ( io , * )
            write ( io , fmt = "( g0 )" ) '# ./'
            write ( io , fmt = "( g0 )" ) '#   -- bin'
            write ( io , fmt = "( g0 )" ) '#        MMoM_4.1.12'
            write ( io , fmt = "( g0 )" ) '#        elevation-sweep.sh'
            write ( io , fmt = "( g0 )" ) '#   -- inputs'
            write ( io , fmt = "( g0 )" ) '#        facet file'
            write ( io , fmt = "( g0 )" ) '#        geo files'
            write ( io , fmt = "( g0 )" ) '#        materials library (empty file)'
            write ( io , fmt = "( g0 )" ) '#   -- outputs'
            write ( io , fmt = "( g0 )" ) '#        MoM results *.4112.txt'
            write ( io , fmt = "( g0 )" ) '#        MoM run log *.out'
            write ( io , * )
            write ( io , fmt = "( g0 )" ) '# counts steps in batch process'
            write ( io , fmt = "( g0 )" ) 'export counter=0'
            write ( io , fmt = "( g0 )" ) 'export SECONDS=0'
            write ( io , fmt = "( g0 )" ) 'function new_step(){'
            write ( io , fmt = "( g0 )" ) '    export counter=$((counter+1))'
            write ( io , fmt = "( g0 )" ) '    export subcounter=0'
            write ( io , fmt = "( g0 )" ) '    echo ""; echo ""'
            write ( io , fmt = "( g0 )" ) '    echo "Step ${counter}: ${1}"'
            write ( io , fmt = "( g0 )" ) '}'
            write ( io , fmt = "( g0 )" ) 'function sub_step(){'
            write ( io , fmt = "( g0 )" ) '    subcounter=$((subcounter+1))'
            write ( io , fmt = "( g0 )" ) '    echo ""'
            write ( io , fmt = "( g0 )" ) '    echo "  Substep ${counter}.${subcounter}: ${1}"'
            write ( io , fmt = "( g0 )" ) '}'
            write ( io , * )

        return
        100 format ( g0, I5, 2 ( "-", I2.2 ), I3, 2 ( ":", I2.2 ) )
    end subroutine openBashScript


end module mWriterBatchCommand
