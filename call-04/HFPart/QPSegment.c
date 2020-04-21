/*
 *-----------------------------------------------------------------------------
 *
 *  HF-POET Analytic Ray Trace
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
 *     	Masters Thesis, 1993
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

#include "QPSegment.h"

/*
 *-----------------------------------------------------------------------------
 *
 * Solve equation 5.24 in Mercer, 1993 for the Cap-A coefficient, using Cap-A
 *    to solve for Cap-B (Eq 5.15) and then Cap-C (Eq 5.14) from Mercer, 1993
 *
 * The approach starts at the top of the profile working down the number of points
 *    to use in the QPS segment section.  
 *    R is the height (in radius) and Y is the plasma frequency squared
 *
 * Values input to the fit routine must be non-zero and positive.
 *
 *-----------------------------------------------------------------------------
 */

int QP_LSq_Segment (double *rValues, double *yValues, int nFitPts, 
                    double rInitial, double yInitial, double dydr,
                    double *capA, double *capB, double *capC)
{

   int index          = 0;
   int status         = SUCCESS_QPS_SEGMENT;

   double sum_dy      = 0.0;
   double sum_dydr2   = 0.0;
   double sum_dr2     = 0.0;
   double tempValue   = 0.0;
   double r1sq        = 0.0;
   double dydr_r2     = 0.0;
   double r1_recip    = 0.0;

   int    zeroIndex   = nFitPts - 1;

   r1_recip    = 1.0 / rInitial;
   r1sq        = rInitial * rInitial;
   dydr_r2     = dydr * r1sq;

   for (index = nFitPts - 1; index >= 0; index--) {

      tempValue  = (r1_recip - 1.0 / rValues[index]);
      sum_dy    -= (yInitial - yValues[index]);
      sum_dydr2 -= (dydr_r2 * tempValue);
      sum_dr2   += (tempValue * tempValue);
   }
/* 
 * Control sum_dx2 solving to a zero.
 */
   if (sum_dr2 != 0.0) {
      *capA = (sum_dy + sum_dydr2) / sum_dr2;
      *capB = -2.0 * (*capA) / rInitial - dydr * r1sq;
      *capC = yInitial + (*capA) / r1sq + dydr * rInitial;

   } else {
      *capA = 0.0;
      *capB = 0.0;
      *capC = 0.0;
      status = FAILURE_QPS_SEGMENT;
   }

   return (status);
}

/*
 ******************************************************************************
 *
 * Solving Eq 5.13 in Mercer, 1993
 *
 ******************************************************************************
 */

double QPS_Start_dydr (double capA, double capB, double rValue)
{
   double tempValue = rValue * rValue;
   double dydr      = 0.0;

   if (rValue != 0.0) {
      dydr = (-2.0 * capA / rValue - capB) / tempValue;
   }

   return (dydr);
}

/*
 ******************************************************************************
 *
 * Solving Eq 5.12 in Mercer, 1993
 *
 ******************************************************************************
 */

double QPS_Start_yValue (double capA, double capB, double capC, double rValue)
{
   double yValue    = 0.0;

   yValue = QPS_Solve_Fn2 (capA, capB, capC, rValue);

   return (yValue);
}

/*
 ******************************************************************************
 * Solving the y(ri) which should be plasma frequency squared
 * Eq 5.11
 ******************************************************************************
 */

double QPS_Solve_Fn2 (double capA, double capB, double capC, double rValue)
{

   double yValue = 0.0;

   if (rValue != 0.0) {
      yValue = (capA / rValue + capB) / rValue + capC;
   }

   return (yValue);
}

/*
 ******************************************************************************
 * Equation 5.12
 ******************************************************************************
 */

double QPS_Gradient (double *rValues, int nFitPts, double capA, double capB)
{
   double dydr    = 0.0;
   double rlast   = rValues[nFitPts - 1];
   double rlast2  = rlast * rlast;
   double rlast3  = rlast * rlast2;

   if (rlast != 0.0) {
      dydr = (-2.0 * capA) / rlast3 - capB / rlast2;
   }

   return (dydr);
}

/*
 ******************************************************************************
 * Solving the y(ri) which should be plasma frequency squared
 * Eq 5.11
 ******************************************************************************
 */

double QPS_Solve_X (double capA, double capB, double capC, double rValue)
{

   double xValue = (capA * rValue + capB) * rValue + capC;

   return (xValue);
}

/*
 ******************************************************************************
 * Solve for the segment ray tracing coefficients based on segment
 *    definition of A, B, C obtained by least squares.
 *
 * Eq. 2.57, 2.58, 2.59 (derivation), Eq 4.21, 4.22, 4.23 (segment coefficents)
 ******************************************************************************
 */

int QPS_RTrace_Coef (float frequency, float beta, float r0base, 
                     double capA, double capB, double capC,
                     double *italA, double *italB, double *italC)
{

   double freq2      = frequency * frequency;
   double cosBeta    = cos(beta);
   double r0cosBeta  = r0base * cosBeta;
   double r2cosBeta2 = r0cosBeta * r0cosBeta;

   if (freq2 != 0.0) {
      *italA = 1.0 - capC / freq2;
      *italB = -capB / freq2;
      *italC = -r2cosBeta2 - capA / freq2;
   } else {
      *italA = 0.0;
      *italB = 0.0;
      *italC = 0.0;
   }

   return (0);
}
/*
 ******************************************************************************
 *
 * Solve for the denominator portion of the integral within the layer.
 * Eq. 4.32
 *
 ******************************************************************************
 */
double QPS_RTrace_Quad (double italA, double italB, double italC)
{
   double denom_quad = italB * italB - 4.0 * italA * italC;

   return (denom_quad);
}

/*
 ******************************************************************************
 *
 * Routine to examine the quality of the estimation and return based on 
 *    the input an indication the data and the fit meet tolerance. 
 *
 ******************************************************************************
 */
int QPS_Compare (double *rValues, double *yValues, double *fpValues, 
                 int nFitPts, double perError, double maxMHz, 
                 double capA, double capB, double capC)
{
   int    status    = PASSED_RMS_TOL_TEST;
   int    index     = 0;
   double sum_diff2 = 0.0;
   double yValue    = 0.0;
   double rmsError  = 0.0;
   double yDiff     = 0.0;
   double fpDiff    = 0.0;
   double tolerance = 0.1;

   for (index = nFitPts - 1; index >= 0; index--) {
      yValue     = QPS_Solve_Fn2 (capA, capB, capC, rValues[index]);
      yDiff      = yValue - yValues[index];
      fpDiff     = sqrt(fabs(yValue)) - fpValues[index];
/*
 * Percent error rule is a tough rule below a tolerance of 1MHz in fp. 
 *    Also this is against the lowest altitude which might be the lower 
 *    density.
 */
      tolerance = perError * fpValues[index];
      if (tolerance > maxMHz) tolerance = maxMHz;
      if (fpDiff > tolerance) {
         status = FAILED_TOL_TEST;
      }
      sum_diff2 += (yDiff * yDiff);
   }

   if (status == PASSED_RMS_TOL_TEST) {
      rmsError = sum_diff2 / (nFitPts - 1);
/*
 * An RMS error check against a percent rule is equally tough on low fp
 */
      if (rmsError > tolerance) {
         status = FAILED_RMS_TEST;
      }
   }

   return (status);
}
