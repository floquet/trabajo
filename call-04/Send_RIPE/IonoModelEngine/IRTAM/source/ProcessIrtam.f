      SUBROUTINE processirtam(alati, along, xmodip, hourut, tov, param, 
     &                        param_local)


c      DIMENSION param(1064)
      REAl alati, along, xmodip, hourut, tov, param_local, param(1064)

      COMMON/CONST/UMR,PI

c      print*, param(1)

                
      pi=ATAN(1.0)*4.
      UMR=pi/180.

      param_local = FOUT1(XMODIP,ALATI,ALONG,HOURUT,TOV,param)

c      print*, alati, along, xmodip, hourut, tov, param_local

      return
      end
c

C
      real function FOUT1(XMODIP,XLATI,XLONGI,UT,TOV,FF0)
c--------------------------------------------------------------
C CALCULATES CRITICAL FREQUENCY FOF2/MHZ USING SUBROUTINE GAMMA1.      
C XMODIP = MODIFIED DIP LATITUDE, XLATI = GEOG. LATITUDE, XLONGI=
C LONGITUDE (ALL IN DEG.), MONTH = MONTH, UT =  UNIVERSAL TIME 
C (DEC. HOURS), 
C
C FF0 = 14 x 76 ARRAY WITH IRTAM COEFFICIENTS.
C D.BILITZA,JULY 85.
c--------------------------------------------------------------
      DIMENSION FF0(1064)
      INTEGER QF(9)
      DATA QF/11,11,8,4,1,0,0,0,0/
      FOUT1=GAMMA2(XMODIP,XLATI,XLONGI,UT,TOV,6,QF,9,76,13,1064,FF0)
      RETURN
      END
C
C
        REAL FUNCTION GAMMA2(SMODIP,SLAT,SLONG,HOUR,TOV,
     &                          IHARM,NQ,K1,M,MM,M3,SFE)      
C---------------------------------------------------------------
C CALCULATES GAMMA1=FOF2, HMF2, B0, OR M3000 USING COEFFICIENTS                       
C SFE(M3) FOR MODIFIED DIP LATITUDE (SMODIP/DEG), GEOGRAPHIC 
C LATITUDE (SLAT/DEG) AND LONGITUDE (SLONG/DEG) AND UNIVERSIAL 
C TIME (HOUR/DECIMAL HOURS). 
C 
C THIS SUBROUTINE ADDS THE LINEAR TREND TERM IN EXPANSION TO
C STANDARD ITU-R (JONES-GALLET) EXPANSION DEVELOPED FOR FOF2
C
C IHARM IS THE MAXIMUM ORDER OF HARMONICS USED FOR DESCRIBING 
C DIURNAL VARIATION.
C NQ(K1) IS AN INTEGER ARRAY GIVING THE HIGHEST DEGREES IN 
C LATITUDE FOR EACH LONGITUDE HARMONIC WHERE K1 GIVES THE NUMBER 
C OF LONGITUDE HARMONICS. 
C M IS THE NUMBER OF COEFFICIENTS FOR DESCRIBING VARIATIONS WITH 
C SMODIP, SLAT, AND SLONG. 
C MM IS THE NUMBER OF COEFFICIENTS FOR THE FOURIER TIME SERIES 
C DESCRIBING VARIATIONS WITH UT.
C M=1+NQ(1)+2*[NQ(2)+1]+2*[NQ(3)+1]+... , MM=2*IHARM+1, M3=M*MM  
C SHEIKH,4.3.77.
C BILITZA,6.17.2016.      
C---------------------------------------------------------------
      REAL*8 C(12),S(12),COEF(100),SUM             
      DIMENSION NQ(K1),XSINX(13),SFE(M3)           
      COMMON/CONST/UMR,PI
      
C --- XMIN is the expansion basis function for the linear trend b0
C     XMIN goes from -720 to +720 minutes over 24 hour period
C     XMIN is 720 at time of validity TOV
      XMIN=(HOUR-TOV)*60.+720
      HOU=(15.0*HOUR-180.0)*UMR                    
C
C     S and C are sines and cosines of diurnal expansion basis 
C     Basis order is IHARM, usually 6
C
      S(1)=SIN(HOU)   
      C(1)=COS(HOU)   

      DO 250 I=2,IHARM                             
        C(I)=C(1)*C(I-1)-S(1)*S(I-1)                 
        S(I)=C(1)*S(I-1)+S(1)*C(I-1)                 
250     CONTINUE        
C
C Run diurnal synthesis first
C Mean+slope+harmonics are used
C COEF holds coefficients for the spatial basis
C Multiply odd/even coefficients SFE by S/C basis 
C M is the length of the spatial expansion, usually 76
C MM is length of the ITU-R standard diurnal expansion, usually 13
C MMM points to beginning of the slope coefficients section in SFE
      MMM=M*MM
      DO 300 I=1,M    
        MI=(I-1)*MM     
        COEF(I)=SFE(MI+1)                            
        DO 301 J=1,IHARM                             
          COEF(I)=COEF(I)+SFE(MI+2*J)*S(J)+SFE(MI+2*J+1)*C(J)                       
301       CONTINUE
        COEF(I)=COEF(I)+SFE(MMM+I)*XMIN                                      
300     CONTINUE        
        
      SUM=COEF(1)     
      SS=SIN(SMODIP*UMR)                           
      S3=SS           
      XSINX(1)=1.0    
      INDEX=NQ(1)     

      DO 350 J=1,INDEX                             
        SUM=SUM+COEF(1+J)*SS                         
        XSINX(J+1)=SS   
        SS=SS*S3        
350     CONTINUE        

      XSINX(NQ(1)+2)=SS                            
      NP=NQ(1)+1      
      SS=COS(SLAT*UMR)                             
      S3=SS           

      DO 400 J=2,K1   
        S0=SLONG*(J-1.)*UMR                          
        S1=COS(S0)      
        S2=SIN(S0)      
        INDEX=NQ(J)+1   
        DO 450 L=1,INDEX                             
          NP=NP+1         
          SUM=SUM+COEF(NP)*XSINX(L)*SS*S1              
          NP=NP+1         
          SUM=SUM+COEF(NP)*XSINX(L)*SS*S2              
450       CONTINUE        
        SS=SS*S3        
400     CONTINUE
        
      GAMMA2=SUM      

      RETURN          
      END 
C
C
      real function FOUT(XMODIP,XLATI,XLONGI,UT,FF0)
c--------------------------------------------------------------
C CALCULATES CRITICAL FREQUENCY FOF2/MHZ USING SUBROUTINE GAMMA1.      
C XMODIP = MODIFIED DIP LATITUDE, XLATI = GEOG. LATITUDE, XLONGI=
C LONGITUDE (ALL IN DEG.), MONTH = MONTH, UT =  UNIVERSAL TIME 
C (DEC. HOURS), FF0 = ARRAY WITH RZ12-ADJUSTED CCIR/URSI COEFF.
C D.BILITZA,JULY 85.
c--------------------------------------------------------------
      DIMENSION FF0(988)
      INTEGER QF(9)
      DATA QF/11,11,8,4,1,0,0,0,0/
      FOUT=GAMMA1(XMODIP,XLATI,XLONGI,UT,6,QF,9,76,13,988,FF0)
      RETURN
      END
C
C
        REAL FUNCTION GAMMA1(SMODIP,SLAT,SLONG,HOUR,
     &                          IHARM,NQ,K1,M,MM,M3,SFE)      
C---------------------------------------------------------------
C CALCULATES GAMMA1=FOF2 OR M3000 USING CCIR NUMERICAL MAP                      
C COEFFICIENTS SFE(M3) FOR MODIFIED DIP LATITUDE (SMODIP/DEG)
C GEOGRAPHIC LATITUDE (SLAT/DEG) AND LONGITUDE (SLONG/DEG)  
C AND UNIVERSIAL TIME (HOUR/DECIMAL HOURS). IHARM IS THE MAXIMUM
C NUMBER OF HARMONICS USED FOR DESCRIBING DIURNAL VARIATION.
C NQ(K1) IS AN INTEGER ARRAY GIVING THE HIGHEST DEGREES IN 
C LATITUDE FOR EACH LONGITUDE HARMONIC WHERE K1 GIVES THE NUMBER 
C OF LONGITUDE HARMONICS. M IS THE NUMBER OF COEFFICIENTS FOR 
C DESCRIBING VARIATIONS WITH SMODIP, SLAT, AND SLONG. MM IS THE
C NUMBER OF COEFFICIENTS FOR THE FOURIER TIME SERIES DESCRIBING
C VARIATIONS WITH UT.
C M=1+NQ(1)+2*[NQ(2)+1]+2*[NQ(3)+1]+... , MM=2*IHARM+1, M3=M*MM  
C SHEIKH,4.3.77.      
C---------------------------------------------------------------
      REAL*8 C(12),S(12),COEF(100),SUM             
      DIMENSION NQ(K1),XSINX(13),SFE(M3)           
      COMMON/CONST/UMR,PI
      HOU=(15.0*HOUR-180.0)*UMR
      S(1)=SIN(HOU)   
      C(1)=COS(HOU)   
      DO 250 I=2,IHARM                             
        C(I)=C(1)*C(I-1)-S(1)*S(I-1)                 
        S(I)=C(1)*S(I-1)+S(1)*C(I-1)                 
250     CONTINUE        

      DO 300 I=1,M    
        MI=(I-1)*MM     
        COEF(I)=SFE(MI+1)                            
        DO 300 J=1,IHARM                             
          COEF(I)=COEF(I)+SFE(MI+2*J)*S(J)+SFE(MI+2*J+1)*C(J)                       
300       CONTINUE        

      SUM=COEF(1)     
      SS=SIN(SMODIP*UMR)                           
      S3=SS           
      XSINX(1)=1.0    
      INDEX=NQ(1)     

      DO 350 J=1,INDEX                             
        SUM=SUM+COEF(1+J)*SS                         
        XSINX(J+1)=SS   
        SS=SS*S3        
350     CONTINUE        

      XSINX(NQ(1)+2)=SS                            
      NP=NQ(1)+1      
      SS=COS(SLAT*UMR)                             
      S3=SS           

      DO 400 J=2,K1   
        S0=SLONG*(J-1.)*UMR                          
        S1=COS(S0)      
        S2=SIN(S0)      
        INDEX=NQ(J)+1   
        DO 450 L=1,INDEX                             
          NP=NP+1         
          SUM=SUM+COEF(NP)*XSINX(L)*SS*S1              
          NP=NP+1         
          SUM=SUM+COEF(NP)*XSINX(L)*SS*S2              
450       CONTINUE        
        SS=SS*S3        
400     CONTINUE
        
      GAMMA1=SUM      

      RETURN          
      END 


		SUBROUTINE READIRTAMCOF(ISEL,IDATE,IHHMM,MFF,FF)
C -----------------------------------------------------------
C Finds and reads IRTAM coefficients (foF2, hmF2, or B0) for 
C date IDATE (yyyymmdd) and time HOURUT (decimal hours, 
C Universal Time): 
C ISEL parameter   filename
C   0    foF2    foF2coeffs_yyyymmdd_hhmm.asc 
C   1    hmF2    hmF2coeffs_yyyymmdd_hhmm.asc 
C   2    B0      B0coeffs_yyyymmdd_hhmm.asc
C The coefficient arrays that bracket the time are stored in 
C FF(988)and FFN(988).
C -----------------------------------------------------------
 
c		CHARACTER	FILNAM*28
		integer		iuccir
		CHARACTER*100	FILNAM
		CHARACTER*120	LINE
		CHARACTER*12    INAME
		DIMENSION 	    FF(MFF)
        konsol=6

        IUCCIR=10
		iname='hmF2_COEFFS_'
		if(isel.lt.1) iname='foF2_COEFFS_'
		if(isel.gt.1) iname='B0in_COEFFS_'

c read foF2 coefficients 
     
        WRITE(FILNAM,104) iname,idate,ihhmm
104     FORMAT('IRTAM_',A12,I8,'_',I4.4,'.ASC')
        OPEN(IUCCIR,FILE=FILNAM,STATUS='OLD',ERR=201,
     &          FORM='FORMATTED')
c     	print*,mff,filnam

C skip header with comments
c	    do 1,13 READ(iuccir,1289) LINE
4686	READ(iuccir,1289) LINE
1289	Format(A120)
	IF(LINE(1:12).NE."# END_HEADER") GOTO 4686

c read coefficients			
        READ(iuccir,4689) FF
4699    FORMAT(E16.8)
4689    FORMAT(4E16.8)
4690    CLOSE(10)
	
		goto 300
		
201     WRITE(6,203) FILNAM
203     FORMAT(1X////,
     &    ' The file ',A100,' is not in your directory.')
		
300		CONTINUE
		RETURN
		END
C
