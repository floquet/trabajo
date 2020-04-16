      SUBROUTINE getprofile(profile_h,profile_f,paramiri,SAOFILENAME)

      REAL*8 profile_h(999), profile_f(999), paramiri(10)

C
C	 Recreate electron density profiles from Digisonde SAO files
C     Terence Bullett, Air Force Research Laboratory
C     Modification history
C     Dec 1999 - Update program to use SAO version 4.2 files
C              - Modify to work under linux g77
C              - Modify to operate as a pipe, ie: profile < saofile   > edpfile
C              - Implement command line selection of frequency step.
C
C
C SAO Format common block
C	Chris Bridgwood, Radex, Inc.
C	June 2003 - Modified to open a file, namely LATEST.SAO, read it,
C	            and generate an output file called true_hts.dat.
C		    This output file contains data that include day of year,
C		    true height of the ionosphere, and the time of this
C		    true height for the frequency of 4.0 MHz.
C       William McNeil, BC ISR
C       September 2015 - Fixed a bug READSAO() so the program worked with
C                        the gfortran compiler (windows & linux)
C       February  2016 - Tried to dump out the Chapman Layer Parameters
c       June 2017      - Dumped out the b0 and b1 parameters as well
c                      - Made revisions for RIPE4 processing
c       July 2017      - Disabled saving of the SAO parameters as we will
c                        be fitting the profiles for RIPE4 and saved only
c                        the profiles
C

      INTEGER*2 IDFI(80),IAF(60),IOTF(400),IOTHF(400),
     +  IOAF(400),IODF(400),IOTF1(150),IOThF1(150),IOAF1(150),
     +  IODF1(150),IOTE(150),IOThE(150),IOAE(150),IODE(150),
     +  IXTF(400),IXAF(400),IXDF(400),IXTF1(150),IXAF1(150),
     +  IXDF1(150),IXTE(150),IXAE(150),IXDE(150),MEDF(20),
     +  MEDE(20),MEDES(20),IEDF(120),IOTSE(150),IOASE(150),
     +  IODSE(150),IEDFTP(120)
C
      REAL*4 OTF(400),OTHF(1000),OTF1(150),OTHF1(1000),OTE(150),
     +       OTHE(1000),XTF(400),XTF1(150),XTE(150),OTsE(150),
     +       HTAB(999),FTAB(999)
C
      REAL*4 SCALED(45),GCONST(16),DTT(16),FTOF(400),FTOF1(150),
     +       FTOE(150),FTXF(400),FTXF1(150),FTXE(150),THF2(20),
     +       THF1(20),THE(20),THVAL(20),FTOSE(150)
      REAL*8 QPCOEF(121)
      CHARACTER*120 SYSDES
      CHARACTER*120 SAOFILENAME

      CHARACTER*1 IPREF(120),QL(120),DL(120)
      CHARACTER*4 YEAR
C
	COMMON /SAO/ QPCOEF,IDFI,GCONST,Sysdes,IPREF,SCALED,IAF,
     +   DTT,IOTF,IOThF,IOAF,IODF,ftOF,IOTF1,IOThF1,IOAF1,IODF1,ftOF1,
     +   IOTE,IOThE,IOAE,IODE,ftOE,IXTF,IXAF,IXDF,ftXF,IXTF1,IXAF1,
     +   IXDF1,ftXF1,IXTE,IXAE,IXDE,ftXE,MEDF,MEDE,MEDES,THF2,THF1,
     +   THE,THVAL,IedF,IOTsE,IOAsE,IODsE,ftOsE,
     +   OTF,OThF,OTF1,OThF1,OTE,OThE,XTF,XTF1,XTE,OTsE,
     +   HTAB,FTAB,QL,DL,IedFTP


C COEFS common block
C	Coefficients for reconstructing the true height profile.
C
	INTEGER NFQ,NCOEF
	REAL A(8),AE(3),AF(7),AF1(7),ATE,ATF,ATF1,HBOTM,FSTART,FEND
	COMMON/COEFS/A,AE,AF,AF1,ATE,ATF,ATF1,
     +		       HBOTM,NFQ,NCOEF,FSTART,FEND
C
C
C     Local Variables
      INTEGER IUNIT,K,IERR, I,J,IARGC,NARGS,NOE
      REAL TRUEHGT,F,ELDEN,DF,F0,ht_flag
      CHARACTER*17 TIME
      CHARACTER*3 firstDOY,DOY
      CHARACTER*2 HR,MIN,hr_flag,min_flag
      CHARACTER*30 VERSION,CMLARG
      LOGICAL EOF,HELP,SWITCH
      character*50 fin,fout,outfile,outfile2
      character*80 liner



c
      character*2 prefix
c
      character*3 mycode
c
      character*2 myhour
c
      character*2 stations(6)
c
      character*3 codes(6)
c
      data stations/"AU","BC","EG","MH","PA","WP"/
c
      data codes/"930","840","931","J45","836","937"/
c
c   set this flag to 1 to save the SAO parameters
c
      ifsao=0
c      print*,SAOFILENAME(1:23)



      call getmmdd(kyear,kdoy,kmonth,kday)
c
      istation = 1
c
      prefix=stations(istation)
      mycode=codes(istation)
      close(1)
c                 
      open(unit=1,file=SAOFILENAME,form=
     x          'formatted',status='old',err=71)
      goto 72
c
   71 continue
      print*,"SAO File does exist:",SAOFILENAME
      goto 72
c
   72 continue
c
      K = 0
      J = 0
      IUNIT = 1
      IERR = 0
      DF = 0.1
      EOF = .FALSE.
      TIME='Hello...'


c   loop through all the SAO records
c
      DO WHILE(.NOT.EOF)
C
c   zero out the f1 layer in case there isn't one
c
c        thf1(2)=0.0
c        thf1(3)=0.0
c
        CALL READSAO(EOF,IUNIT,IERR,TIME)
C
        IF (EOF) EXIT
C
        YEAR=TIME(1:4)
        HR=TIME(10:11)
        MIN=TIME(13:14)
        DOY=TIME(6:8)
      
        profile_f = ftab
        profile_h = htab
        paramiri(1) = thf2(2)
        paramiri(2) = thf2(3)
        paramiri(3) = thf1(2)
        paramiri(4) = thf1(3)
        paramiri(5) = the(2)
        paramiri(6) = the(3)
        paramiri(7) = scaled(41)
        paramiri(8) = scaled(42)
        paramiri(9) = scaled(6)
        paramiri(10) = scaled(14)

c        write(*,333),prefix,year,doy,hr,min,noe,thf2(2),thf2(3),
c     x         scaled(41),scaled(42)
c
c  333   format(1x,a2,1x,a4,1x,a3,1x,a2,1x,a2,i5,f7.3,f7.2,f7.2,f7.4)

c        do 60 i=1,idfi(51)
c        write(*,100)i,profile_h(i),profile_f(i)
c  100   format(1x,i5,2f12.4)

c   60   continue


      ENDDO
C
c
      RETURN
      END













































C
C
C  =================================================================
C
	REAL FUNCTION ELDEN(F)
C
C	Convert plasma frequency (MHz) into electron density (x10E5).
C
	REAL F
	ELDEN = F*F/8.1
	RETURN
	END


C
C  ===================================================================
C
	REAL FUNCTION TRUEHGT(F)
C
C	Using the /SAO/ coefficients for the true height, calculate
C	the TRUEHGT [km] of the profile at the given frequency F [MHz].
C
C 07Dec99 TWB  - Modify for SAO v4.2
C
C     Note: This does not reproduce any valley or topside.  To do so would
C           require significant shift from viewing this as H(F) to N(h).
C           Maybe the next version.
C
C	The method of calculating the height Z is:
C                       M
C    Z=DUM(M+1)+SQRT(XM)+SUM DUM(I)*TSTAR(XM,I)
C                      I=0
C   WHERE A=COEFFICIENTS OF POLYNOMIAL FUNCTION
C         XM=(ALOG(FN/FOF2))/(ALOG(FOE/FOF2))
C         TSTAR=SHIFTED CHEBYSHEV FUNCTION
C   INPUT: DUM=COEFFICIENTS
C          FN=PLASMA FREQ
C
C SAO Format common block

      INTEGER*2 IDFI(80),IAF(60),IOTF(400),IOTHF(400),
     +  IOAF(400),IODF(400),IOTF1(150),IOThF1(150),IOAF1(150),
     +  IODF1(150),IOTE(150),IOThE(150),IOAE(150),IODE(150),
     +  IXTF(400),IXAF(400),IXDF(400),IXTF1(150),IXAF1(150),
     +  IXDF1(150),IXTE(150),IXAE(150),IXDE(150),MEDF(20),
     +  MEDE(20),MEDES(20),IEDF(120),IOTSE(150),IOASE(150),
     +  IODSE(150),IEDFTP(120)
C
      REAL*4 OTF(400),OTHF(1000),OTF1(150),OTHF1(1000),OTE(150),
     +       OTHE(1000),XTF(400),XTF1(150),XTE(150),OTsE(150),
     +       HTAB(999),FTAB(999)
C
      REAL*4 SCALED(45),GCONST(16),DTT(16),FTOF(400),FTOF1(150),
     +       FTOE(150),FTXF(400),FTXF1(150),FTXE(150),THF2(20),
     +       THF1(20),THE(20),THVAL(20),FTOSE(150)
      REAL*8 QPCOEF(121)
      CHARACTER*120 SYSDES
      CHARACTER*1 IPREF(120),QL(120),DL(120)
C
	COMMON /SAO/ QPCOEF,IDFI,GCONST,Sysdes,IPREF,SCALED,IAF,
     +   DTT,IOTF,IOThF,IOAF,IODF,ftOF,IOTF1,IOThF1,IOAF1,IODF1,ftOF1,
     +   IOTE,IOThE,IOAE,IODE,ftOE,IXTF,IXAF,IXDF,ftXF,IXTF1,IXAF1,
     +   IXDF1,ftXF1,IXTE,IXAE,IXDE,ftXE,MEDF,MEDE,MEDES,THF2,THF1,
     +   THE,THVAL,IedF,IOTsE,IOAsE,IODsE,ftOsE,
     +   OTF,OThF,OTF1,OThF1,OTE,OThE,XTF,XTF1,XTE,OTsE,
     +   HTAB,FTAB,QL,DL,IedFTP



C COEFS common block
C	Coefficients for reconstructing the true height profile.
C
	INTEGER NFQ,NCOEF
	REAL A(8),AE(3),AF(7),AF1(7),ATE,ATF,ATF1,HBOTM,FSTART,FEND
	COMMON/COEFS/A,AE,AF,AF1,ATE,ATF,ATF1,
     +		       HBOTM,NFQ,NCOEF,FSTART,FEND
C
	INTEGER I
C
C
C       Default null value
        TRUEHGT = 0.0
C
C	Use the frequency F to select the layer to use
	IF ((F.LT.0.0).OR.(F.GT.SCALED(1))) THEN
C	   F is above or below the trace
	   TRUEHGT = 0.0
	   RETURN
C	E-Layer
	ELSE IF ((IDFI(39).GT.0).AND.
     +        (F.GE.THE(1)).AND.(F.LE.THE(2))) THEN
C	      Use the coefficients for the E layer
C             What happens here when there is a modeled or parabolic E??
	   NCOEF = 3
	   FSTART = THE(1)
	   FEND   = THE(2)
	   A(8)   = THE(3)
	   DO I = 1, NCOEF
	      A(I) = THE(I+4)
	      AE(I) = A(I)
           ENDDO
	   CALL PROF(F,TRUEHGT)
	ELSE IF ((IDFI(39).EQ.0).AND.(F.LE.SCALED(9))) THEN
C	   Parabolic E model using Hmax and Ym
	   TRUEHGT = SCALED(15) -
     +      SCALED(16)*SQRT(1.0 - (F/SCALED(9))**2)
C	F1 Layer
	ELSE IF ((IDFI(38).GT.0).AND.
     +   (F.GE.THF1(1)).AND.(F.LE.THF1(2))) THEN
	   NCOEF = 5
	   FSTART = THF1(1)
	   FEND   = THF1(2)
	   A(8)   = THF1(3)
	   DO I = 1, NCOEF
	      A(I) = THF1(I+4)
	      AF1(I) = A(I)
           ENDDO
	   CALL PROF(F,TRUEHGT)
C	F2 Layer
	ELSE IF ((IDFI(37).GT.0).AND.
     +   (F.GE.THF2(1)).AND.(F.LE.THF2(2))) THEN
	   NCOEF = 5
	   FSTART = THF2(1)
	   FEND   = THF2(2)
	   A(8)   = THF2(3)
	   DO I = 1, NCOEF
	      A(I) = THF2(I+4)
	      AF(I) = A(I)
           ENDDO
	   CALL PROF(F,TRUEHGT)
	ELSE
C	   There are no true height coefficients
	   TRUEHGT = 0.0
	   RETURN
	ENDIF
C
	RETURN
	END
C
C
C**********************************************************************
C
      SUBROUTINE PROF(FN,H)
C...FROM THE ASSUMED INITIAL PROFILE, CALCULATE
C    H ACCORDING TO THE EQUATION
C                       M
C    Z=DUM(M+1)+SQRT(XM)+SUM DUM(I)*TSTAR(XM,I)
C                      I=0
C   WHERE A=COEFFICIENTS OF POLYNOMIAL FUNCTION
C         XM=(ALOG(FN/FOF2))/(ALOG(FOE/FOF2))
C         TSTAR=SHIFTED CHEBYSHEV FUNCTION
C   INPUT: DUM=COEFFICIENTS
C          FN=PLASMA FREQ
C   OUTPUT: H
C.................................................
C
C	Coefficients for reconstructing the true height profile.
C
	INTEGER NFQ,NCOEF
	REAL A(8),AE(3),AF(7),AF1(7),ATE,ATF,ATF1,HBOTM,FSTART,FEND
	COMMON/COEFS/A,AE,AF,AF1,ATE,ATF,ATF1,
     +		       HBOTM,NFQ,NCOEF,FSTART,FEND
C
C
	REAL Y1,YS,XM,TSTAR,FN,H
	INTEGER I
C
C...BELOW IS FOR E- AND F- REGION POLYNOMIAL FITS
      H=0.
C...CHECK THE START FREQUENCY
      IF(FN.GT.FSTART) THEN
C... AND THE END FREQUENCY
         IF(FN.LT.FEND)THEN
            Y1=ALOG(FN/FEND)
            YS=ALOG(FSTART/FEND)
            XM=Y1/YS
            IF(XM.LT.0.) THEN
               WRITE(*,'(A,3F7.1)')' *****XM < 0. IN PROF,FN,FSTART,
     +         FEND=',FN,FSTART,FEND
            XM=0.
            ENDIF
C222
         ELSE
            XM=0.
C222
         ENDIF
C...CALCULATE THE TRUE HEIGHT
         DO 10 I=1,NCOEF
   10    H=H+A(I)*TSTAR(XM,I)
         H=H*SQRT(XM)
         H=H+A(8)
C111
      ENDIF
C
  300 CONTINUE
      RETURN
      END
C
C**********************************************************************
C
      REAL FUNCTION TSTAR(CD,N)
C...TSTAR CALCULATE SHIFTED CHEVBYSHEV FUNCTION
C   INPUT: CD=LN(FN/FOF2)/LN(FOE/FOF2)
C          N=INDEX OF POLYNOMIAL
C    C=COEFFICIENTS OF THE TAYLOR DEVELOPMENT OF TSTAR
C       FUNCTION
C,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
C
      REAL C(8,8),CD
	INTEGER J,N
C
      DATA C(1,1),C(1,2),C(1,3),C(1,4),C(1,5),C(1,6),C(1,7),C(1,8)
     +/1.,7*0./
C
      DATA C(2,1),C(2,2),C(2,3),C(2,4),C(2,5),C(2,6),C(2,7),C(2,8)
     +/2.,-1.,6*0./
C
      DATA C(3,1),C(3,2),C(3,3),C(3,4),C(3,5),C(3,6),C(3,7),C(3,8)
     +/8.,-8.,1.,5*0./
C
      DATA C(4,1),C(4,2),C(4,3),C(4,4),C(4,5),C(4,6),C(4,7),C(4,8)
     +/32.,-48.,18.,-1.,4*0./
C
      DATA C(5,1),C(5,2),C(5,3),C(5,4),C(5,5),C(5,6),C(5,7),C(5,8)
     +/128.,-256.,160.,-32.,1.,3*0./
C
      DATA C(6,1),C(6,2),C(6,3),C(6,4),C(6,5),C(6,6),C(6,7),C(6,8)
     +/512.,-1280.,1120.,-400.,50.,-1.,2*0./
C
      DATA C(7,1),C(7,2),C(7,3),C(7,4),C(7,5),C(7,6),C(7,7),C(7,8)
     +/2048.,-6144.,6912.,-3584.,840.,-72.,1.,0./
C
      DATA C(8,1),C(8,2),C(8,3),C(8,4),C(8,5),C(8,6),C(8,7),C(8,8)
     +/8192.,-28672.,39424.,-26880.,9408.,-1568.,98.,-1./
C...FOR THE N=1 CONDITION - TSTAR EQUALS THE TAYLOR COEFFICIENT
      TSTAR=C(N,1)
      IF (N .EQ. 1) GO TO 20
C...FOR N>1 CALCULATE TSTAR
      DO 10 J=2,N
   10 TSTAR=TSTAR*CD+C(N,J)
      RETURN
   20 CONTINUE
      RETURN
      END
C
C ====================================================================
C
C      SUBROUTINE READSAO(EOF,IDFI,GCONST,Sysdes,IPREF,SCALED,IAF,
C     +   DTT,IOTF,IOThF,IOAF,IODF,ftOF,IOTF1,IOThF1,IOAF1,IODF1,ftOF1,
C     +   IOTE,IOThE,IOAE,IODE,ftOE,IXTF,IXAF,IXDF,ftXF,IXTF1,IXAF1,
C     +   IXDF1,ftXF1,IXTE,IXAE,IXDE,ftXE,MEDF,MEDE,MEDES,THF2,THF1,
C     +   THE,QPCOEF,THVAL,IedF,IOTsE,IOAsE,IODsE,ftOsE,
C     +   OTF,OThF,OTF1,OThF1,OTE,OThE,XTF,XTF1,XTE,OTsE,
C     +   HTAB,FTAB,QL,DL,IedFTP,
C     +   IREAD,IERR)
c
c  Version 96050810
C
cc
c  Input Variables:
c    Arrays to store SAO data
c    EOF      -   end of file check
c    IU       -   file unit number  (Not used for pipe based version)
c    IERR     -   Return error code
C
C  Data in the SAO common block
c   array     code    description
c             group
c    IDFI     --      data file index
c    GCONST        1       Geophysical constants
c    Sysdes        2       System description
c    IPREF         3       ionogram sounding settings
c    SCALED        4       scaled ionogram parameters
c    IAF           5       analysis flags
c    DTT           6       Doppler translation table
c    IOTF/OTF      7       O-trace F2 virtual height
c    IOThF/OThF    8       O-trace F2 true height
c    IOAF          9       O-trace F2 amplitudes
c    IODF         10       O-trace F2 Doppler numbers
c    ftOF         11       O-trace F2 frequency table
c    IOTF1/OTF1   12       O-trace F1 virtual height
c    IOThF1/OThF1 13       O-trace F1 true height
c    IOAF1        14       O-trace F1 amplitudes
c    IODF1        15       O-trace F1 Doppler numbers
c    ftOF1        16       O-trace F1 frequency table
c    IOTE/OTE     17       O-trace E  virtual height
c    IOThE/OThE   18       O-trace E  true height
c    IOAE         19       O-trace E  amplitudes
c    IODE         20       O-trace E  Doppler numbers
c    ftOE         21       O-trace E  frequency table
c    IXTF/XTF     22       X-trace F2 virtual height
c    IXAF         23       X-trace F2 amplitudes
c    IXDF         24       X-trace F2 Doppler numbers
c    ftXF         25       X-trace F2 frequency table
c    IXTF1/XTF1   26       X-trace F1 virtual height
c    IXAF1        27       X-trace F1 amplitudes
c    IXDF1        28       X-trace F1 Doppler numbers
c    ftXF1        29       X-trace F1 frequency table
c    IXTE/XTE     30       X-trace E  virtual height
c    IXAE         31       X-trace E  amplitudes
c    IXDE         32       X-trace E  Doppler numbers
c    ftXE         33       X-trace E  frequency table
c    MEDF         34       Median amplitude of F echo
c    MEDE         35       Median amplitude of E echo
c    MEDES        36       Median amplitude of Es echo
c    THF2         37       F2 layer true height parameters
c    THF1         38       F1 layer true height parameters
c    THE          39       E layer true height parameters
c    THVAL        40       Valley parameters from Polan and NhPc version 2.01
c    IedF         41       Edit Flags
c    THVAL        42       Valley parameters from NhPc version 3.01 or higher
c    IOTsE/OTsE   43       O-trace sporadic-E  virtual height
c    IOAsE        44       O-trace sporadic-E  amplitudes
c    IODsE        45       O-trace sporadic-E  Doppler numbers
c    ftOsE        46       O-trace sporadic-E  frequency table
c
c  Output Variables
c    Arrays with corresponding SAO data
c
c  Purpose:  READ SAO files with all versions
c
c  Revision Log
c     IDFI(80) is used as an indicator of the format of the data
C              in the SAO file
c     IDFI(80) = 0 --- SAO version 3.0 format
c     IDFI(80) = 1 --- SAO version 3.0 format with true height data
c                      format enhanced
c     IDFI(80) = 2 --- SAO version 4.0 format
c     IDFI(80) = 3 --- SAO version 4.0 format, oblique ionogram
c                      converted to vertical
c
c---------------------------
C  TWB-Dec99  This version passes data through a common block called
C  /SAO/ in the include file sao.cmn
C
C**********************************************************************
C
      SUBROUTINE READSAO(EOF,IREAD,IERR,TIME)
C
C
C 07Dec99 TWB - Common block declairation for SAO 4.2 data
C  TWB-Dec99  This version passes data through a common block called
C  /SAO/ in the include file sao.cmn
C
c   array     code    description
c             group
c    IDFI     --      data file index
c    GCONST        1       Geophysical constants
c    Sysdes        2       System description
c    IPREF         3       ionogram sounding settings
c    SCALED        4       scaled ionogram parameters
c    IAF           5       analysis flags
c    DTT           6       Doppler translation table
c    IOTF/OTF      7       O-trace F2 virtual height
c    IOThF/OThF    8       O-trace F2 true height
c    IOAF          9       O-trace F2 amplitudes
c    IODF         10       O-trace F2 Doppler numbers
c    ftOF         11       O-trace F2 frequency table
c    IOTF1/OTF1   12       O-trace F1 virtual height
c    IOThF1/OThF1 13       O-trace F1 true height
c    IOAF1        14       O-trace F1 amplitudes
c    IODF1        15       O-trace F1 Doppler numbers
c    ftOF1        16       O-trace F1 frequency table
c    IOTE/OTE     17       O-trace E  virtual height
c    IOThE/OThE   18       O-trace E  true height
c    IOAE         19       O-trace E  amplitudes
c    IODE         20       O-trace E  Doppler numbers
c    ftOE         21       O-trace E  frequency table
c    IXTF/XTF     22       X-trace F2 virtual height
c    IXAF         23       X-trace F2 amplitudes
c    IXDF         24       X-trace F2 Doppler numbers
c    ftXF         25       X-trace F2 frequency table
c    IXTF1/XTF1   26       X-trace F1 virtual height
c    IXAF1        27       X-trace F1 amplitudes
c    IXDF1        28       X-trace F1 Doppler numbers
c    ftXF1        29       X-trace F1 frequency table
c    IXTE/XTE     30       X-trace E  virtual height
c    IXAE         31       X-trace E  amplitudes
c    IXDE         32       X-trace E  Doppler numbers
c    ftXE         33       X-trace E  frequency table
c    MEDF         34       Median amplitude of F echo
c    MEDE         35       Median amplitude of E echo
c    MEDES        36       Median amplitude of Es echo
c    THF2         37       F2 layer true height parameters
c    THF1         38       F1 layer true height parameters
c    THE          39       E layer true height parameters
c    THVAL        40       Valley parameters from Polan and NhPc version 2.01
c    IedF         41       Edit Flags
c    THVAL        42       Valley parameters from NhPc version 3.01 or higher
c    IOTsE/OTsE   43       O-trace sporadic-E  virtual height
c    IOAsE        44       O-trace sporadic-E  amplitudes
c    IODsE        45       O-trace sporadic-E  Doppler numbers
c    ftOsE        46       O-trace sporadic-E  frequency table
c
c  Output Variables
c    Arrays with corresponding SAO data
c
c  Purpose:  READ SAO files with all versions
c
c  Revision Log
c     IDFI(80) is used as an indicator of the format of the data
C              in the SAO file
c     IDFI(80) = 0 --- SAO version 3.0 format
c     IDFI(80) = 1 --- SAO version 3.0 format with true height data
c                      format enhanced
c     IDFI(80) = 2 --- SAO version 4.0 format
c     IDFI(80) = 3 --- SAO version 4.0 format, oblique ionogram
c                      converted to vertical
c
      INTEGER*2 IDFI(80),IAF(60),IOTF(400),IOTHF(400),
     +  IOAF(400),IODF(400),IOTF1(150),IOThF1(150),IOAF1(150),
     +  IODF1(150),IOTE(150),IOThE(150),IOAE(150),IODE(150),
     +  IXTF(400),IXAF(400),IXDF(400),IXTF1(150),IXAF1(150),
     +  IXDF1(150),IXTE(150),IXAE(150),IXDE(150),MEDF(20),
     +  MEDE(20),MEDES(20),IEDF(120),IOTSE(150),IOASE(150),
     +  IODSE(150),IEDFTP(120)
C
      REAL*4 OTF(400),OTHF(1000),OTF1(150),OTHF1(1000),OTE(150),
     +       OTHE(1000),XTF(400),XTF1(150),XTE(150),OTsE(150),
     +       HTAB(999),FTAB(999)
C
      REAL*4 SCALED(45),GCONST(16),DTT(16),FTOF(400),FTOF1(150),
     +       FTOE(150),FTXF(400),FTXF1(150),FTXE(150),THF2(20),
     +       THF1(20),THE(20),THVAL(20),FTOSE(150)
      REAL*8 QPCOEF(121)
      CHARACTER*120 SYSDES
      CHARACTER*1 IPREF(120),QL(120),DL(120)
C
	COMMON /SAO/ QPCOEF,IDFI,GCONST,Sysdes,IPREF,SCALED,IAF,
     +   DTT,IOTF,IOThF,IOAF,IODF,ftOF,IOTF1,IOThF1,IOAF1,IODF1,ftOF1,
     +   IOTE,IOThE,IOAE,IODE,ftOE,IXTF,IXAF,IXDF,ftXF,IXTF1,IXAF1,
     +   IXDF1,ftXF1,IXTE,IXAE,IXDE,ftXE,MEDF,MEDE,MEDES,THF2,THF1,
     +   THE,THVAL,IedF,IOTsE,IOAsE,IODsE,ftOsE,
     +   OTF,OThF,OTF1,OThF1,OTE,OThE,XTF,XTF1,XTE,OTsE,
     +   HTAB,FTAB,QL,DL,IedFTP

C
C     Local Variables
      LOGICAL   EOF
      INTEGER I,IREAD,IERR,IY
      character*12 fm1,fm2,fm3,fm4,fm5,fm6,fm7,fm8,fm9,fm10,fm11,fm12
      CHARACTER*17 TIME
C
c-----------------------------------------------------------------------
c...formats
 100  FORMAT (40I3)
      IERR=1
c
    1 CONTINUE
c...data file index
C     The data file index integers take two lines.
      READ(1,100,ERR=2,END=9) (IDFI(I),I=1,80)
c
      GOTO 3
    2 CONTINUE
c
      READ(1,'(A120)',END=9) Sysdes
c
      GOTO 1
C
    3 CONTINUE
c
      IF(IDFI(1).GT.0.AND.IDFI(1).LT.17) GOTO 4
c
      GOTO 99
C
    4 CONTINUE
c
      IERR=0
c
      if(IDFI(80).eq.0) then  !  Version 3 (and lower) SAO data
        write(fm1,'(4x,A8)')  '(40I3)'
        write(fm2,'(2x,A10)') '(16F7.3)'
        write(fm3,'(4x,A8)')  '(A120)'
        write(fm4,'(3x,A9)')  '(120A1)'
        write(fm5,'(2x,A10)') '(15F8.3)'
        write(fm6,'(4x,A8)')  '(60I2)'
        write(fm7,'(3x,A9)')  '(120I1)'
        write(fm8,'(2x,A10)') '(20F6.3)'
        write(fm9,'(A12)')    '(13E9.4E1)'
        write(fm10,'(3x,A8)') '(60I2)'
      endif
C
      if(IDFI(80).eq.1) then  ! Version 3 with enhanced true height data
        write(fm1,'(4x,A8)')  '(40I3)'
        write(fm2,'(2x,A10)') '(16F7.3)'
        write(fm3,'(4x,A8)')  '(A120)'
        write(fm4,'(3x,A9)')  '(120A1)'
        write(fm5,'(2x,A10)') '(15F8.3)'
        write(fm6,'(4x,A8)')  '(60I2)'
        write(fm7,'(3x,A9)')  '(120I1)'
        write(fm8,'(2x,A10)') '(20F6.3)'
        write(fm9,'(A12)')    '(10E11.6E1)' ! <--- true height data
        write(fm10,'(3x,A8)') '(60I2)'
      endif
C
      if(IDFI(80).GE.2) then                !  Version 4.00 or higher
        write(fm1,'(2x,A10)') '(15F8.3)'    ! <--- h' and z
        write(fm2,'(2x,A10)') '(16F7.3)'
        write(fm3,'(4x,A8)')  '(A120)'
        write(fm4,'(3x,A9)')  '(120A1)'     ! <--- preface
        write(fm5,'(2x,A10)') '(15F8.3)'
        write(fm6,'(4x,A8)')  '(60I2)'
        write(fm7,'(3x,A9)')  '(120I1)'
        write(fm8,'(2x,A10)') '(15F8.3)'    ! <--- frequency table
        write(fm9,'(A12)')    '(10E11.6E1)' ! <--- true height data
        write(fm10,'(3x,A8)') '(40I3)'
        write(fm11,'(A12)')   '(15E8.3E1)'
        write(fm12,'(A11)')   '(6E20.12)'
      endif
C
C...Geophysical constants -- Code 1
c
      IF(IDFI(1).GT.0) READ(1,fm2,END=9,ERR=99)
     +                      (GCONST(I),I=1,IDFI(1))
c
C...system description -- Code 2a
c
      if(IDFI(2).gt.0) READ(1,fm3,END=9,ERR=99) Sysdes
c
C...ionogram sounding settings (preface) -- Code 3A
c
      if(IDFI(3).gt.0) READ(1,fm4,END=9,ERR=99)
     +                      (IPREF(I),I=1,IDFI(3))
C
C...scaled ionogram parameters
c
      IF(IDFI(4).GT.0) READ(1,fm5,END=9,ERR=99)
     +                      (SCALED(I),I=1,IDFI(4))
C
C...ARTIST analysis flagsa
c
      IF(IDFI(5) .GT.0) READ(1,fm6,END=9,ERR=99)
     +                      (IAF(I),I=1,IDFI(5))
C
C...Doppler translation table
c
      IF(IDFI(6).GT.0) READ(1,fm2,END=9,ERR=99)
     +                      (DTT(I),I=1,IDFI(6))
C
C...O-trace F2 points
c...virtual height
c
      IF(IDFI(7).GT.0) then
        if(IDFI(80).GE.2)then
          READ(1,fm1,END=9,ERR=99) (OTF(I),I=1,IDFI(7))  ! SAO V4.0
          DO I=1,IDFI(7)
          IOTF(I)=OTF(I)
          ENDDO
        else
          READ(1,fm1,END=9,ERR=99) (IOTF(I),I=1,IDFI(7)) ! SAO V3.0
                                                          ! and lower
          DO I=1,IDFI(7)
          OTF(I)=IOTF(I)
          ENDDO
        endif
      endif
c
c...true height
c
      IF(IDFI(8).GT.0) then
        if(IDFI(80).GE.2)then
          READ(1,fm1,END=9,ERR=99) (OThF(I),I=1,IDFI(8))  ! SAO V4.0
        else
          READ(1,fm1,END=9,ERR=99) (IOThF(I),I=1,IDFI(8)) ! SAO V3.0
                                                           ! and lower
        endif
      endif
c
c...amplitudes
c
      IF(IDFI(9).GT.0) READ(1,fm10,END=9,ERR=99)
     +                      (IOAF(I),I=1,IDFI(9))
c
c...Doppler numbers
c
      IF(IDFI(10).GT.0) READ(1,fm7,END=9,ERR=99)
     +                      (IODF(I),I=1,IDFI(10))
c
c...frequency tablea
c
      IF(IDFI(11).GT.0) READ(1,fm8,END=9,ERR=99)
     +                      (ftOF(I), I=1,IDFI(11))
C
C...O-trace F1 points
c...virtual heighta
c
      IF(IDFI(12).GT.0) then
        if(IDFI(80).GE.2)then
         READ(1,fm1,END=9,ERR=99) (OTF1(I),I=1,IDFI(12))  ! SAO V4.0
         DO I=1,IDFI(12)
            IOTF1(I)=OTF1(I)
         ENDDO
        else
         READ(1,fm1,END=9,ERR=99) (IOTF1(I),I=1,IDFI(12)) ! SAO V3.0
                                                           ! and lower
         DO I=1,IDFI(12)
             OTF1(I)=IOTF1(I)
         ENDDO
        endif
      endif
c
c...true heighta
c
      IF(IDFI(13).GT.0) then
        if(IDFI(80).GE.2)then
        READ(1,fm1,END=9,ERR=99) (OThF1(I),I=1,IDFI(13))  ! SAO V4.0
        else
        READ(1,fm1,END=9,ERR=99) (IOThF1(I),I=1,IDFI(13)) ! SAO V3.0
                                                           ! and lower
        endif
      endif
c
c...amplitudesa
c
      IF(IDFI(14).GT.0) READ(1,fm10,END=9,ERR=99)
     +                      (IOAF1(I),I=1,IDFI(14))
c
c...Doppler numbera
c
      IF(IDFI(15).GT.0) READ(1,fm7,END=9,ERR=99)
     +                      (IODF1(I),I=1,IDFI(15))
c
c...frequency tablea
c
      IF(IDFI(16).GT.0) READ(1,fm8,END=9,ERR=99)
     +                      (ftOF1(I), I=1,IDFI(16))
C
C...O-trace E points
c...virtual heights
c
      IF(IDFI(17).GT.0) then
        if(IDFI(80).GE.2)then
          READ(1,fm1,END=9,ERR=99) (OTE(I),I=1,IDFI(17))  ! SAO V4.0
          DO I=1,IDFI(17)
             IOTE(I)=OTE(I)
          ENDDO
        else
          READ(1,fm1,END=9,ERR=99) (IOTE(I),I=1,IDFI(17)) ! SAO V3.0
                                                           ! and lower
          DO I=1,IDFI(17)
             OTE(I)=IOTE(I)
          ENDDO
        endif
      endif
c
c...true heighta
c
      IF(IDFI(18).GT.0) then
        if(IDFI(80).GE.2)then
         READ(1,fm1,END=9,ERR=99) (OThE(I),I=1,IDFI(18))  ! SAO V4.0
        else
         READ(1,fm1,END=9,ERR=99) (IOThE(I),I=1,IDFI(18)) ! SAO V3.0
                                                           ! and lower
        endif
      endif
c
c...amplitudes
c
      IF(IDFI(19).GT.0) READ(1,fm10,END=9,ERR=99)
     +                      (IOAE(I),I=1,IDFI(19))
c
c...Doppler numbers
c
      IF(IDFI(20).GT.0) READ(1,fm7,END=9,ERR=99)
     +                      (IODE(I),I=1,IDFI(20))
c
c...frequency table
c
      IF(IDFI(21).GT.0) READ(1,fm8,END=9,ERR=99)
     +                      (ftOE(I), I=1,IDFI(21))
C
C...X-trace F2 points
c...virtual heightsa
c
      IF(IDFI(22).GT.0) then
        if(IDFI(80).GE.2)then
          READ(1,fm1,END=9,ERR=99) (XTF(I),I=1,IDFI(22))  ! SAO V4.0
        else
          READ(1,fm1,END=9,ERR=99) (IXTF(I),I=1,IDFI(22)) ! SAO V3.0
                                                          ! and lower
        endif
      endif
c
c...amplitudes
c
      IF(IDFI(23).GT.0) READ(1,fm10,END=9,ERR=99)
     +                      (IXAF(I),I=1,IDFI(23))
c
c...Doppler numbers
c
      IF(IDFI(24).GT.0) READ(1,fm7,END=9,ERR=99)
     +                      (IXDF(I),I=1,IDFI(24))
c
c...frequency tablea
c
      IF(IDFI(25).GT.0) READ(1,fm8,END=9,ERR=99)
     +                      (ftXF(I),I=1,IDFI(25))
C
C...X-trace F1 points
c...virtual heights
c
      IF(IDFI(26).GT.0) then
        if(IDFI(80).GE.2)then
         READ(1,fm1,END=9,ERR=99) (XTF1(I),I=1,IDFI(26))  ! SAO V4.0
        else
         READ(1,fm1,END=9,ERR=99) (IXTF1(I),I=1,IDFI(26)) ! SAO V3.0
                                                           ! and lower
        endif
      endif
c
c...amplitudes
c
      IF(IDFI(27).GT.0) READ(1,fm10,END=9,ERR=99)
     +                      (IXAF1(I),I=1,IDFI(27))
c
c...Doppler numbers
c
      IF(IDFI(28).GT.0) READ(1,fm7,END=9,ERR=99)
     +                      (IXDF1(I),I=1,IDFI(28))
c
c...frequency tablea
c
      IF(IDFI(29).GT.0) READ(1,fm8,END=9,ERR=99)
     +                      (ftXF1(I),I=1,IDFI(29))
C
C...X-trace E points
c...virtual heights
c
      IF(IDFI(30).GT.0) then
        if(IDFI(80).GE.2)then
          READ(1,fm1,END=9,ERR=99) (XTE(I),I=1,IDFI(30))  ! SAO V4.0
        else
          READ(1,fm1,END=9,ERR=99) (IXTE(I),I=1,IDFI(30)) ! SAO V3.0
                                                           ! and lower
        endif
      endif
c
c...amplitudes
c
      IF(IDFI(31).GT.0) READ(1,fm10,END=9,ERR=99)
     +                      (IXAE(I),I=1,IDFI(31))
c
c...Doppler numbers
c
      IF(IDFI(32).GT.0) READ(1,fm7,END=9,ERR=99)
     +                      (IXDE(I),I=1,IDFI(32))
c
c...frequency table
c
      IF(IDFI(33).GT.0) READ(1,fm8,END=9,ERR=99)
     +                      (ftXE(I),I=1,IDFI(33))
C
C...median amplitude of F echo
c
      IF(IDFI(34).GT.0) READ(1,fm6,END=9,ERR=99)
     +                      (MEDF(I),I=1,IDFI(34))
C...median amplitude of E echo
c
      IF(IDFI(35).GT.0) READ(1,fm6,END=9,ERR=99)
     +                      (MEDE(I),I=1,IDFI(35))
C...median amplitude of Es echoa
c
      IF(IDFI(36).GT.0) READ(1,fm6,END=9,ERR=99)
     +                      (MEDES(I),I=1,IDFI(36))
C
C...F2 layer true height parameters
c
      IF(IDFI(37).GT.0) READ(1,fm9,END=9,ERR=99)
     +                      (THF2(I),I=1,IDFI(37))
c
C...F1 layer true height parameters
c
      IF(IDFI(38).GT.0) READ(1,fm9,END=9,ERR=99)
     +                      (THF1(I),I=1,IDFI(38))
C...E layer true height parameters
c
      IF(IDFI(39).GT.0) READ(1,fm9,END=9,ERR=99)
     +                      (THE(I),I=1,IDFI(39))
C
C...valley parameters from Polan and NhPc version 2.01
c
      IF(IDFI(40).GT.0) THEN
        IF(IDFI(80).LT.2) THEN
        READ(1,fm9,END=9,ERR=99)  (THVAL(I),I=1,IDFI(40))
        ELSE
        READ(1,fm12,END=9,ERR=99) (QPCOEF(I),I=1,IDFI(40))
        ENDIF
      ENDIF
C
c...edit flags
C...NOTE: FOR OLD DATA, THIS INCLUDES BOTH THE CHARACTERISTCS FLAG
C         AND THE TRACE+PROFILE FLAG
c
      IF(IDFI(41).GT.0) READ(1,fm7,END=9,ERR=99) (IedF(I),I=1,IDFI(41))
c
C...Valley parameters from NhPc version 3.01 and greater Sept. 1993
c
      IF(IDFI(42).GT.0) READ(1,fm9,END=9,ERR=99)
     +                      (THVAL(I),I=1,IDFI(42))
c
c...O-trace sporadic-E
c...virtual heights
c
      IF(IDFI(43).GT.0) then
        if(IDFI(80).GE.2)then
         READ(1,fm1,END=9,ERR=99) (OTsE(I),I=1,IDFI(43))  ! SAO V4.0
        else
         READ(1,fm1,END=9,ERR=99) (IOTsE(I),I=1,IDFI(43)) ! SAO V3.0
                                                           ! and lower
        endif
      endif
c
c...amplitudes
c
      IF(IDFI(44).GT.0) READ(1,fm10,END=9,ERR=99)
     +                      (IOAsE(I),I=1,IDFI(44))
c
c...Doppler numbers
c
      IF(IDFI(45).GT.0) READ(1,fm7,END=9,ERR=99)
     +                      (IODsE(I),I=1,IDFI(45))
c
c...frequency table
c
      IF(IDFI(46).GT.0) READ(1,fm8,END=9,ERR=99)
     +                      (ftOsE(I),I=1,IDFI(46))
c
c...O-trace - Auroral E layer
c...virtual heights
c
      IF(IDFI(47).GT.0) then
        if(IDFI(80).GE.2)then
         READ(1,fm1,END=9,ERR=99) (OTsE(I),I=1,IDFI(47))  ! SAO V4.0
         DO I=1,IDFI(47)
         IOTsE(I)=OTsE(I)
         ENDDO
        else
         READ(1,fm1,END=9,ERR=99) (IOTsE(I),I=1,IDFI(47)) ! SAO V3.0
                                                           ! and lower
         DO I=1,IDFI(47)
         OTsE(I)=IOTsE(I)
         ENDDO
        endif
      endif
c
c...amplitudes
c
      IF(IDFI(48).GT.0) READ(1,fm10,END=9,ERR=99)
     +                      (IOAsE(I),I=1,IDFI(48))
c
c...Doppler numbers
c
      IF(IDFI(49).GT.0) READ(1,fm7,END=9,ERR=99)
     +                      (IODsE(I),I=1,IDFI(49))
c
c...frequency table
c
      IF(IDFI(50).GT.0) READ(1,fm8,END=9,ERR=99)
     +                      (ftOsE(I),I=1,IDFI(50))
c
c...N(h) Tabulation
c
c
      IF(IDFI(51).GT.0) THEN
        READ(1,fm11,END=9,ERR=99) (HTAB(I),I=1,IDFI(51))
        READ(1,fm11,END=9,ERR=99) (FTAB(I),I=1,IDFI(52))
        READ(1,fm11,END=9,ERR=99) (fNTAB,I=1,IDFI(53))
      ENDIF

c        do I=1,IDFI(51)
c        write(*,200)HTAB(I)
c 200  FORMAT (15F8.3)
c	enddo

c
c...Qualifying Letters
c
      IF(IDFI(54).GT.0) READ(1,fm4,END=9,ERR=99) (QL(I),I=1,IDFI(54))
c...Descriptive Letters
c
      IF(IDFI(55).GT.0) READ(1,fm4,END=9,ERR=99) (DL(I),I=1,IDFI(55))
c...Edit Flags - Traces and Profile
c
      IF(IDFI(56).GT.0) THEN
        READ(1,fm7,END=9,ERR=99) (IedFTP(I),I=1,IDFI(56))
      ENDIF
C
C     This segement of the code places the measurement time into the
C     character variable TIME in the format: YYYY DDD HH:MM:SS
C
C
C All IPREF(I) in all sao versions are read from the SAO file with
C    format fm4='(120A1)'
C BUT the date, etc. are not in the same part of the preface in all versions:
C    for example,in older versions the preface starts with the 2-digit year;
C    the preface in version 4.2 starts with a 2-letter code followed by the
C    4-digit year...
C    Also, in the newer preface, the characters in positions 10-13 are month and day
C    This info is absent from the older format.
C
      IF (IDFI(80).GE.2) THEN
         WRITE(TIME,120) (IPREF(I),I=3,9),(IPREF(I),I=14,19)
      ELSE
C        Y2K issue:  1980/2080 ambiguity
         WRITE(TIME,'(2I1)') IPREF(1), IPREF(2)
         READ(TIME, *) IY
         IF(IY.LT.80) then
            IY=20
         ELSE
            IY=19
         ENDIF
         WRITE(TIME,121) IY,(IPREF(I),I=1,11)
      ENDIF
C     TIME format of YYYY DDD HH:MM:SS
 120  FORMAT (4A1,' ',3A1,' ',2A1,':',2A1,':',2A1)
 121  FORMAT (I2.2,2A1,' ',3A1,' ',2A1,':',2A1,':',2A1)
c
      IREAD=1
      EOF = .FALSE.
      RETURN

    9 EOF = .TRUE.
      RETURN
C
   99 CONTINUE
      print*,"Got a read error..."
c
      IERR=1
C
      RETURN
      END
      SUBROUTINE GETMMDD(IYEAR,IDOY,IMM,IDD)
C
C   THIS ROUTINE CHANGES DAY OF YEAR TO MONTH AND DAY
C
      IONE=1
C
C   GET THE MODIFIED JULIAN DAY AT THE START OF THE YEAR
C
      JDAY=JD(IYEAR,IONE,IONE)
C
C   GET THE JULIAN DAY AT THE CURRENT DAY OF YEAR
C
      JDAY=JDAY+IDOY-1
C
C   GET THE MONTH AND DAY
C
      CALL GDATE(JDAY,JYEAR,JMONTH,JDAY)
C
C   SEND THEM BACK
C
      IMM=JMONTH
      IDD=JDAY
C
      RETURN
      END
      INTEGER FUNCTION JD (YEAR,MONTH,DAY)
C
C---COMPUTES THE JULIAN DATE (JD) GIVEN A GREGORIAN CALENDAR
C   DATE (YEAR,MONTH,DAY).
C
      INTEGER YEAR,MONTH,DAY,I,J,K
C
      I= YEAR
      J= MONTH
      K= DAY
C
 
      JD= K-32075+1461*(I+4800+(J-14)/12)/4+367*(J-2-(J-14)/12*12)
     2    /12-3*((I+4900+(J-14)/12)/100)/4
C
      RETURN
      END
      SUBROUTINE GDATE (JD,YEAR,MONTH,DAY)
C
C---COMPUTES THE GREGORIAN CALENDAR DATE (YEAR,MONTH,DAY)
C   GIVEN THE JULIAN DATE (JD).
C
      INTEGER JD,YEAR,MONTH,DAY,I,J,K
C
      L= JD+68569
      N= 4*L/146097
      L= L-(146097*N+3)/4
      I= 4000*(L+1)/1461001
      L= L-1461*I/4+31
      J= 80*L/2447
      K= L-2447*J/80
      L= J/11
      J= J+2-12*L
      I= 100*(N-49)+I+L
C
      YEAR= I
      MONTH= J
      DAY= K
C
      RETURN
      END



