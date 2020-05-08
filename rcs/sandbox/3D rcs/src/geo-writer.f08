! 3456789 123456789 223456789 323456789 423456789 523456789 623456789 723456789 823456789 923456789 023456789 123456789 223456789 32
! nb: /Users/dantopa/Mathematica_files/nb/ert/mercury/snake/fortran-01.nb
program geo_writer


! Daniel Topa, ERT Corp
! COVID-19 Prisoner

    use, intrinsic :: iso_fortran_env,  only : compiler_options, compiler_version
    use mQuarry,                        only : quarry
    use mFormatDescriptors,             only : fmt_datecom
    use mWriterBatchCommand,            only : openBashScript, grabSupportFiles, updateBashScript, purgeSupportFiles
    use mWriterGeo,                     only : writeGeoElevation

    implicit none

    type ( quarry ) :: myQuarry
    integer :: io_bash = 0, k = 0

    ! containers for date and time
    integer :: dt_values ( 1 : 8 ) = 0

        call openBashScript ( "./bash-land/elevation-sweep.sh", "geo_writer.f08.", io = io_bash )
        call myQuarry % setDirectories ( dirIn = "./inputs/", dirOut = "./outputs/" )
        call myQuarry % stemFileNames  ( quarry_name = "PTW", angle_type = "-elev-" )
        call grabSupportFiles ( myQuarry = myQuarry, unit = io_bash )

        sweep_elevation_angles: do k = -89, 90
            call myQuarry % fullFileNames  ( angle = k )
            call writeGeoElevation ( myQuarry = myQuarry, elevation = real ( k ) )
            call updateBashScript  ( myQuarry = myQuarry, unit = io_bash )
        end do sweep_elevation_angles

        call purgeSupportFiles ( myQuarry = myQuarry, unit = io_bash )

        ! execution complete - tag output
        call date_and_time ( VALUES = dt_values )
            write ( * , fmt_datecom ) dt_values ( 1 : 3 ), dt_values ( 5 : 7 )

        write ( * , '( "compiler version: ", g0, "."    )' ) compiler_version ( )
        write ( * , '( "compiler options: ", g0, ".", / )' ) compiler_options ( )

        stop 'Successful run for "geo_writer.f08."'

end program geo_writer

! dantopa:writers/geo % date                                                                                          (master)fortran-alpha
! Fri May  8 12:52:37 MDT 2020
! dantopa:writers/geo % pwd                                                                                           (master)fortran-alpha
! /Users/dantopa/primary-repos/bitbucket/fortran-alpha/rcs/writers/geo
! dantopa:writers/geo % lsb_release -a                                                                                (master)fortran-alpha
! zsh: command not found: lsb_release
! dantopa:writers/geo % make clean                                                                                    (master)fortran-alpha
! rm -rf geo-writer.o m_file_handling.o m_format_descriptors.o m_quarry.o m_string_toolkit.o m_writer_batch_command.o m_writer_geo.o geo_writer m_file_handling.mod m_format_descriptors.mod m_quarry.mod m_string_toolkit.mod m_writer_batch_command.mod m_writer_geo.mod
! rm -f *.mod *.smod *.o
! dantopa:writers/geo % make debug                                                                                    (master)fortran-alpha
! PROGRAM  = geo_writer
! PRG_OBJ  = geo_writer.o
! SRCS     = geo-writer.f08 m_file_handling.f08 m_format_descriptors.f08 m_quarry.f08 m_string_toolkit.f08 m_writer_batch_command.f08 m_writer_geo.f08
! OBJS     = geo-writer.o m_file_handling.o m_format_descriptors.o m_quarry.o m_string_toolkit.o m_writer_batch_command.o m_writer_geo.o
! MODS     = m_file_handling.f08 m_format_descriptors.f08 m_quarry.f08 m_string_toolkit.f08 m_writer_batch_command.f08 m_writer_geo.f08
! MOD_OBJS = m_file_handling.o m_format_descriptors.o m_quarry.o m_string_toolkit.o m_writer_batch_command.o m_writer_geo.o
! dantopa:writers/geo % make -k                                                                                       (master)fortran-alpha
! gfortran -g -c -Og -pedantic -Wall -Warray-temporaries -Wextra -Waliasing -Wsurprising -Wimplicit-procedure -Wintrinsics-std -Wfunction-elimination -Wc-binding-type -Wrealloc-lhs-all -Wuse-without-only -Wconversion-extra -fno-realloc-lhs -ffpe-trap=denormal,invalid,zero -fbacktrace -fmax-errors=5 -fcheck=all -fcheck=do -fcheck=pointer -fno-protect-parens -faggressive-function-elimination -fdiagnostics-color=auto -finit-derived -o geo-writer.o geo-writer.f08
! geo-writer.f08:10:8:

!    10 |     use mQuarry,                        only : quarry
!       |        1
! Fatal Error: Cannot open module file 'mquarry.mod' for reading at (1): No such file or directory
! compilation terminated.
! make: *** [geo-writer.o] Error 1
! gfortran -g -c -Og -pedantic -Wall -Warray-temporaries -Wextra -Waliasing -Wsurprising -Wimplicit-procedure -Wintrinsics-std -Wfunction-elimination -Wc-binding-type -Wrealloc-lhs-all -Wuse-without-only -Wconversion-extra -fno-realloc-lhs -ffpe-trap=denormal,invalid,zero -fbacktrace -fmax-errors=5 -fcheck=all -fcheck=do -fcheck=pointer -fno-protect-parens -faggressive-function-elimination -fdiagnostics-color=auto -finit-derived -o m_file_handling.o m_file_handling.f08
! gfortran -g -c -Og -pedantic -Wall -Warray-temporaries -Wextra -Waliasing -Wsurprising -Wimplicit-procedure -Wintrinsics-std -Wfunction-elimination -Wc-binding-type -Wrealloc-lhs-all -Wuse-without-only -Wconversion-extra -fno-realloc-lhs -ffpe-trap=denormal,invalid,zero -fbacktrace -fmax-errors=5 -fcheck=all -fcheck=do -fcheck=pointer -fno-protect-parens -faggressive-function-elimination -fdiagnostics-color=auto -finit-derived -o m_format_descriptors.o m_format_descriptors.f08
! gfortran -g -c -Og -pedantic -Wall -Warray-temporaries -Wextra -Waliasing -Wsurprising -Wimplicit-procedure -Wintrinsics-std -Wfunction-elimination -Wc-binding-type -Wrealloc-lhs-all -Wuse-without-only -Wconversion-extra -fno-realloc-lhs -ffpe-trap=denormal,invalid,zero -fbacktrace -fmax-errors=5 -fcheck=all -fcheck=do -fcheck=pointer -fno-protect-parens -faggressive-function-elimination -fdiagnostics-color=auto -finit-derived -o m_string_toolkit.o m_string_toolkit.f08
! gfortran -g -c -Og -pedantic -Wall -Warray-temporaries -Wextra -Waliasing -Wsurprising -Wimplicit-procedure -Wintrinsics-std -Wfunction-elimination -Wc-binding-type -Wrealloc-lhs-all -Wuse-without-only -Wconversion-extra -fno-realloc-lhs -ffpe-trap=denormal,invalid,zero -fbacktrace -fmax-errors=5 -fcheck=all -fcheck=do -fcheck=pointer -fno-protect-parens -faggressive-function-elimination -fdiagnostics-color=auto -finit-derived -o m_quarry.o m_quarry.f08
! gfortran -g -c -Og -pedantic -Wall -Warray-temporaries -Wextra -Waliasing -Wsurprising -Wimplicit-procedure -Wintrinsics-std -Wfunction-elimination -Wc-binding-type -Wrealloc-lhs-all -Wuse-without-only -Wconversion-extra -fno-realloc-lhs -ffpe-trap=denormal,invalid,zero -fbacktrace -fmax-errors=5 -fcheck=all -fcheck=do -fcheck=pointer -fno-protect-parens -faggressive-function-elimination -fdiagnostics-color=auto -finit-derived -o m_writer_batch_command.o m_writer_batch_command.f08
! gfortran -g -c -Og -pedantic -Wall -Warray-temporaries -Wextra -Waliasing -Wsurprising -Wimplicit-procedure -Wintrinsics-std -Wfunction-elimination -Wc-binding-type -Wrealloc-lhs-all -Wuse-without-only -Wconversion-extra -fno-realloc-lhs -ffpe-trap=denormal,invalid,zero -fbacktrace -fmax-errors=5 -fcheck=all -fcheck=do -fcheck=pointer -fno-protect-parens -faggressive-function-elimination -fdiagnostics-color=auto -finit-derived -o m_writer_geo.o m_writer_geo.f08
! make: Target `default' not remade because of errors.
! dantopa:writers/geo % make                                                                                          (master)fortran-alpha
! gfortran -g -c -Og -pedantic -Wall -Warray-temporaries -Wextra -Waliasing -Wsurprising -Wimplicit-procedure -Wintrinsics-std -Wfunction-elimination -Wc-binding-type -Wrealloc-lhs-all -Wuse-without-only -Wconversion-extra -fno-realloc-lhs -ffpe-trap=denormal,invalid,zero -fbacktrace -fmax-errors=5 -fcheck=all -fcheck=do -fcheck=pointer -fno-protect-parens -faggressive-function-elimination -fdiagnostics-color=auto -finit-derived -o geo-writer.o geo-writer.f08
! gfortran -g -framework accelerate -I/Users/dantopa/primary-repos/bitbucket/fortran-alpha/rcs/mom/beast/mods -o geo_writer geo-writer.o m_file_handling.o m_format_descriptors.o m_quarry.o m_string_toolkit.o m_writer_batch_command.o m_writer_geo.o
! dantopa:writers/geo % ./geo_writer                                                                                  (master)fortran-alpha

! completed at 2020-05-08 12:53:11

! compiler version: GCC version 9.3.0.
! compiler options: -fdiagnostics-color=auto -fPIC -feliminate-unused-debug-symbols -mmacosx-version-min=10.15.0 -mtune=core2 -auxbase-strip geo-writer.o -g -Og -Wpedantic -Wall -Warray-temporaries -Wextra -Waliasing -Wsurprising -Wimplicit-procedure -Wintrinsics-std -Wfunction-elimination -Wc-binding-type -Wrealloc-lhs-all -Wuse-without-only -Wconversion-extra -fno-realloc-lhs -ffpe-trap=denormal,invalid,zero -fbacktrace -fmax-errors=5 -fcheck=all -fcheck=do -fcheck=pointer -fno-protect-parens ! -faggressive-function-elimination -finit-derived.

! STOP Successful run for "geo_writer.f08."
