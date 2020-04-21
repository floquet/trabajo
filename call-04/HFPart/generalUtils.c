/*
 *-----------------------------------------------------------------------------
 *
 *  HF Propagation Observation Toolkit (HF-POET) Analytic Ray Trace (HF-PART)
 *
 *  Source Code for the AFRL adaptation of R.J. Norman and P.S. Cannon
 *     Segmented Method for Analytic Ray Trace (SMART).  Routines have been
 *     coded based on publication "A two-dimensional analytic ray trace technique
 *     accommodating horizontal gradiants" Radio Science, Volume 32, Number 2,
 *     Pages 387-396, March-April 1997, "An evaluation of a new two-dimensional
 *     analytic ionospheric ray-tracing technique: Segmented method for analytic
 *     ray trace (SMART)" Radio Science, Volume 34, Number 2, Pages 489-499,
 *     March-April 1999.
 *     Additional information was provided by C.C. Mercer Masters Thesis, "The
 *     search for an ionospheric model suitable for real-time applications in
 *     HF radio communication", December 1993.
 *
 *  AFRL source code was included in the development of this version.  The
 *     techniques and source code used originate from prior work performed by
 *     the Radio Science and Propagation Group, Defence Research Agency, England.
 *     The software may not be used or copied for any non-government or commercial
 *     purpose without the written agreement from AFRL/RVB.
 *
 *  Algorithms for QPS model are based on Chen 1990 and found in C.C. Mercer
 *      Masters Thesis, 1993
 *     
 *-----------------------------------------------------------------------------
 *
 *  HF-PART Development
 *  -------------------
 *  Initial baseline code using provided papers and AFRL source code.
 *     Nelson A. Bonito, AFRL/RVB
 *     20 February 2020
 *
 *-----------------------------------------------------------------------------
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <math.h>

#include "hfpart_constants.h"

/*
 *-----------------------------------------------------------------------------
 *
 *  Routine converts density (/m3) to plasma frequency,  Result is Hz based.
 *
 *   8.978659167 == m-3 to Hz
 *-----------------------------------------------------------------------------
 */

double Ne_to_fp (double density)
{
   float plasmaFreq  = 0.0;

   if (density > 0.0) {
      plasmaFreq = NE_M3_TO_PLASMA_FREQUENCY * sqrt (density);
   }

   return (plasmaFreq);
}

/*
 *-----------------------------------------------------------------------------
 *
 *  Routine converts density (/cm3) to plasma frequency,  Result is Hz based.
 *
 *   0.008978659167 == cm-3 to Hz
 *-----------------------------------------------------------------------------
 */

double Ne_cm3_to_fp (double density)
{
   float plasmaFreq  = 0.0;

   if (density > 0.0) {
      plasmaFreq = NE_CM3_TO_PLASMA_FREQUENCY * sqrt (density);
   }
   return (plasmaFreq);
}
/*
 *-----------------------------------------------------------------------------
 *
 *  Routine converts plasma frequency to density with the knowledge the input 
 *     frequency is in MHz since the result will be in m-3.  
 *
 *-----------------------------------------------------------------------------
 */

double fp_to_Ne (double plasmaFreq)
{
   float density     = 0.0;

   density = PLASMA_FREQUENCY_TO_NE * plasmaFreq * plasmaFreq;

   return (density);
}

/*
 *-----------------------------------------------------------------------------
 *
 *  Routine expects the input ray elevation for the MUF result to be in radians.
 *
 *-----------------------------------------------------------------------------
 */

float fp_to_MUF (float criticalFreq, float rayElev)
{
   float sinElev = 0.0;
   float freqMUF = 0.0;

   sinElev = sin (rayElev);
   if (sinElev > 0.0) {
      if (criticalFreq > 0.0) {
         freqMUF = criticalFreq / sinElev;
      }
   }

   return (freqMUF);
}

/*
 *-----------------------------------------------------------------------------
 *
 *  Routine returns the ray elevation for the MUF in radians.
 *
 *-----------------------------------------------------------------------------
 */

float elevation_MUF (float freqMUF, float freqCritical) 
{
   float rayElev = 0.0;

   if (freqMUF > 0.0) {
      rayElev = asin (freqCritical / freqMUF);
   }

   return (rayElev);
}
 
/*
 *-----------------------------------------------------------------------------
 *
 *  Optimum Working Frequency (OWF)
 *
 *-----------------------------------------------------------------------------
 */

float OWF_for_MUF (float freqMUF)
{
   float OWFreq        = 0.0;

   OWFreq = OPTIMUM_WORK_FREQ_PERCENT * freqMUF;

   return (OWFreq);
}

/*
 *-----------------------------------------------------------------------------
 *
 *  Index of refraction  80.616
 *
 *-----------------------------------------------------------------------------
 */

float indexRefraction (float rayFreq, float density) 
{
   float refraction    = 1.0;

   if (rayFreq > 0.0) {
      if (density > 0.0) {
         refraction = sqrt ( 1.0 - ((INDEX_REFRACTION_PLASMA * density) / 
                                    (rayFreq * rayFreq)));
      } 
   }

   return (refraction);
}

/*
 *-----------------------------------------------------------------------------
 *
 *
 *
 *-----------------------------------------------------------------------------
 */

double height_to_radial (double profHeight) 
{
   float profRadial = MEAN_RADIUS_EARTH + profHeight;

   return (profRadial);
}

/*
 *-----------------------------------------------------------------------------
 *
 *
 *
 *-----------------------------------------------------------------------------
 */

double fob_to_fvert (double phi0, double freqOblique) 
{
   double freqVert    = 0.0;
   double cosPhi0     = cos (phi0);

   if (fabs (cosPhi0) < 1.0) {
      freqVert = freqOblique / cosPhi0;
   }

   return (freqVert);
}

/*
 *-----------------------------------------------------------------------------
 *
 *
 *
 *-----------------------------------------------------------------------------
 */

double fvert_to_fob (double phi0, double freqVert) 
{
   double freqOblique = freqVert * cos (phi0);

   return (freqOblique);
}

/*
 *-----------------------------------------------------------------------------
 *
 *
 *
 *-----------------------------------------------------------------------------
 */

double rangeHt_to_elev (double range, double height) 
{
   double theta = theta_angle (range);
   double phi0  = phi0_angle (theta, height);
   double elev  = M_PI / 2.0 - theta - phi0;

   return (elev);
}

/*
 *-----------------------------------------------------------------------------
 *
 *
 *
 *-----------------------------------------------------------------------------
 */

double radial_to_height (double profRadial)
{
   float profHeight = 0.0;

   if (profRadial != 0.0) profHeight = profRadial - MEAN_RADIUS_EARTH;

   return (profHeight);
}

/*
 *-----------------------------------------------------------------------------
 *
 * Angle of ray entering the defined height, representing the ionosphere.
 *    Measured from horizontal to the ray.
 *
 *-----------------------------------------------------------------------------
 */

double gamma_angle (double elevation, double radial_height)
{
   double arc_length = MEAN_RADIUS_EARTH * cos (elevation) / radial_height;
   double beta       = 0.0;

   if (arc_length >= 0.0 && arc_length <= 1.0) {
      beta = acos (arc_length);
   }

   return (beta);
}

/*
 *-----------------------------------------------------------------------------
 *
 * Complement gamma (phi0) ray entry angle as part of the Secant law calculation
 *
 *-----------------------------------------------------------------------------
 */

double phi0_angle (double theta, double height)
{
   double tan_phi0 = sin (theta) / (1.0 + height / MEAN_RADIUS_EARTH - cos(theta));
   double phi0     = atan (tan_phi0);

   return (phi0);
}

/*
 *-----------------------------------------------------------------------------
 *
 * Angle at center of earth (for half of the ground range.) 
 *
 *-----------------------------------------------------------------------------
 */

double theta_angle (double rangeDistance)
{
   double theta = rangeDistance / (2.0 * MEAN_RADIUS_EARTH);

   return (theta);
}

/*
 *-----------------------------------------------------------------------------
 *
 * Range to ray entering the defined height.
 *
 *-----------------------------------------------------------------------------
 */

double beta_to_range (double beta, double radial_height)
{
   double theta    = gamma_angle (beta, radial_height);
   double range_km = 0.0;

   if (theta >= beta) {
      range_km = (theta - beta) * MEAN_RADIUS_EARTH;
   }

   return (range_km);
}

/*
 *-----------------------------------------------------------------------------
 *
 * Simple parabolic fitting routine with no real extras and mostly intended
 *    to obtain a solution for small number of point.  Equally expecting the
 *    input to be representative of a possible parabolic function.  The results 
 *    are not quality checked to determine impact from outliers. No RMS or CHI-SQ
 *
 *-----------------------------------------------------------------------------
 */

int Parabolic_Fit (double *xValues, double *yValues, int nptsFit, double *coeff)
{
   int     index    = 0;
   double  sumX     = 0.0;
   double  sumY     = 0.0;
   double  sumXY    = 0.0;
   double  sumX2    = 0.0;
   double  sumX3    = 0.0;
   double  sumX4    = 0.0;
   double  sumX2Y   = 0.0;
   double  tempX    = 0.0;
   double  tempX2   = 0.0;

   double  denomD   = 0.0;
   double  denomD0  = 0.0;
   double  denomD1  = 0.0;
   double  denomD2  = 0.0;

   double  comp1    = 0.0;
   double  comp2    = 0.0;
   double  comp3    = 0.0;
   double  comp4    = 0.0;

   for (index = 0; index < nptsFit; index++) {
      tempX   = xValues[index];
      tempX2  = xValues[index] * xValues[index];

      sumX   += tempX;
      sumX2  += tempX2;
      sumX3  += (tempX * tempX2);
      sumX4  += (tempX2 * tempX2);

      sumY   +=  yValues[index];
      sumXY  += (xValues[index] * yValues[index]);
      sumX2Y += (tempX2 * yValues[index]);
   }

   comp1 = sumX2 * sumX4  - sumX3 * sumX3;
   comp2 = sumX  * sumX4  - sumX2 * sumX3;
   comp3 = sumX  * sumX3  - sumX2 * sumX2;
   comp4 = sumX  * sumX2Y - sumX2 * sumXY;

   denomD  = (double)(nptsFit) * comp1 -
                         sumX  * comp2 +
                         sumX2 * comp3;
   if (denomD != 0.0) {
      denomD0 =             sumY  * comp1 -
                            sumX  * (sumXY * sumX4  - sumX2Y * sumX3) +
                            sumX2 * (sumXY * sumX3  - sumX2  * sumX2Y);
      denomD1 = (double)(nptsFit) * (sumXY * sumX4  - sumX3  * sumX2Y) -
                            sumY  * comp2 +
                            sumX2 * comp4;
      denomD2 = (double)(nptsFit) * (sumX2 * sumX2Y - sumX3  * sumXY) -
                            sumX  * comp4 +
                            sumY  * comp3;
      coeff[0] = denomD0 / denomD;
      coeff[1] = denomD1 / denomD;
      coeff[2] = denomD2 / denomD;
   } else {
      coeff[0] = 0.0;
      coeff[1] = 0.0;
      coeff[2] = 0.0;
   }
   return (0);
}

/*
 *-----------------------------------------------------------------------------
 *
 *
 *
 *-----------------------------------------------------------------------------
 */

