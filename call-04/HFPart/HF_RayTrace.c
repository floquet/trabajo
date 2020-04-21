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
 *  Algorithms for Ray Trace are based on C.C. Mercer Masters Thesis, 1993 and
 *     R.J. Norman and P.S. Cannon 1997, 1999.
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
#include "QPSegment.h"
#include "QPS_Model.h"
#include "RayTrace.h"

/*
 *****************************************************************************
 *
 * Simple routine to dump the rayu trace segment points for inspection,
 *    Routine provides a demonstration of the structure content.
 * 
 *****************************************************************************
 */

int Output_RayTrace_Result (struct ray_trace_def_t *RT_Path, int verbose)
{
   int    index    = 0;

   if (verbose != VERBOSE_LEVEL0) {
      if (RT_Path->rayTraceFlag == APOGEE_DETECTED) {
          printf ("*** Frequency: %4.1lf Elevation: %4.1lf MaxRange: %6.1lf Apogee: %5.1lf\n",
               RT_Path->frequency, RT_Path->beta0 * 180.0 / M_PI, RT_Path->rangeMax,
               RT_Path->apogeeHeight);

      } else {
          printf ("*** Frequency: %4.1lf Elevation: %4.1lf MaxRange: %6.1lf\n",
               RT_Path->frequency, RT_Path->beta0 * 180.0 / M_PI, RT_Path->rangeMax);
      }  
      if (verbose == VERBOSE_LEVEL2) {
         printf (" Number of Trace Points: %d\n",RT_Path->numPoints);
         for (index = 0; index < RT_Path->numPoints; index++) {

            printf (" Range: %6.1lf Height: %5.1lf\n", RT_Path->rayPoints[index].range,
                                                 RT_Path->rayPoints[index].height);
         }
      }
   }

   return (SUCCESS_ART_SEGMENT);
}

/*
 *****************************************************************************
 *
 * Eq 9 (Norman) - Exception is the Re use instead of the segment layer Ro
 *
 *****************************************************************************
 */

double GrndRangeTraveled (double beta, double radialBase, double integralUiMLi)
{
   double rangeValue = MEAN_RADIUS_EARTH * radialBase * cos (beta) * integralUiMLi;

   return (rangeValue);
}

/*
 *****************************************************************************
 *
 * Eq 10 (Norman) 
 *
 *****************************************************************************
 */

int Solve_BoundaryIntegral (struct qps_definition_t *QPS_Segment, 
                            double lowerBound, double upperBound, double rayRadial,
                            double *integralUpper, double *integralLower,
                            int apogeeFlag)
{
   int    status          = SUCCESS_ART_SEGMENT;
   double partialLogValue = 0.0;
   double integralSegment = 0.0;
   double rValue          = 0.0;
   double xValue          = 0.0;

/*
 * Do the Lower boundary (order matters because of the negative log in eq. 10A
 *    Perform the segment integral for the upper and lower values.
 *    Lower integral (dependent on direction) can return negative X results
 *    which requires check of X-Value used in the segment integral. 
 */
   if (rayRadial > lowerBound) {
      rValue  = rayRadial;
   } else {
      rValue  = lowerBound;
   }
   xValue  = QPS_Solve_X (QPS_Segment->italA, QPS_Segment->italB, 
                          QPS_Segment->italC, rValue);

   if (QPS_Segment->italC < 0.0) {
      status = Boundary_NegC (QPS_Segment->italA, QPS_Segment->italB,
                              QPS_Segment->italC, QPS_Segment->denom_quad, 
                              rValue, &integralSegment);
   } else {
      status = Boundary_PosC (QPS_Segment->italA, QPS_Segment->italB,
                              QPS_Segment->italC, QPS_Segment->denom_quad,
                              rValue, xValue, SEGMENT_LOWER_BOUNDARY, &integralSegment, 
                              &partialLogValue); 
   }
/*
 * Inspect prior execution for exceptions in the integral
 */
   if (status == SUCCESS_ART_SEGMENT) {
      if (xValue > 0.0) {
         *integralLower += integralSegment;
/*
 * If segment flag as containing apogee the need to duplicate the integral exists
 */
         if (apogeeFlag == APOGEE_SEGMENT) {
            *integralLower += integralSegment;
         }
      }

      integralSegment = 0.0;
/*
 * Do the Upper second for Up leg Ray Trace
 */
      rValue = upperBound;
      xValue = QPS_Solve_X (QPS_Segment->italA, QPS_Segment->italB, 
                         QPS_Segment->italC, rValue);

      if (apogeeFlag == APOGEE_SEGMENT) {
         status = Solve_Apogee_Upper (QPS_Segment->italC, QPS_Segment->denom_quad,
                                      &integralSegment);
      } else {
         if (QPS_Segment->italC < 0.0) {
            status = Boundary_NegC (QPS_Segment->italA, QPS_Segment->italB,
                                 QPS_Segment->italC, QPS_Segment->denom_quad, 
                                 rValue, &integralSegment);
         } else {
            status = Boundary_PosC (QPS_Segment->italA, QPS_Segment->italB,
                                 QPS_Segment->italC, QPS_Segment->denom_quad,
                                 rValue, xValue, SEGMENT_UPPER_BOUNDARY, &integralSegment, 
                                 &partialLogValue); 
         }
      }

      if (status == SUCCESS_ART_SEGMENT) {
         *integralUpper += integralSegment;
         if (apogeeFlag == APOGEE_SEGMENT) {
/*
 * If segment flag as containing apogee the need to duplicate the integral exists
 */
            *integralUpper += integralSegment;
         }
      }
   }    

   return (status);
}

/*
 *****************************************************************************
 *
 * Eq 2.61 (Mercer) 
 *
 *****************************************************************************
 */

int Solve_Apogee_Upper (double italC, double denom_quad, double *integralValue)
{
   int    status      = SUCCESS_ART_SEGMENT;

   if (italC > 0.0) {
      (*integralValue) = -log (denom_quad) / (2.0 * sqrt (italC));
   } else {
      if (italC == 0.0) {
         (*integralValue) = 0.0;
         fprintf (stderr, " Solve_Apogee_Upper: Italic C is ZERO at APOGEE!\n");
         status = FAILURE_ART_SEGMENT;
      } else {
         (*integralValue) = M_PI / (2.0 * sqrt (-italC));
      }
   }

   return (status);
}

/*
 *****************************************************************************
 *
 * Eq. 10B (Norman) for upper boundary when italC is less than zero.
 *
 *****************************************************************************
 */

int Boundary_NegC (double italA, double italB, double italC, double denom_quad,
                   double rValue, double *integralValue)
{
   int    status      = SUCCESS_ART_SEGMENT;
   double compValue   = 0.0;

   if (italC < 0.0) {
      if (denom_quad < 0.0) {
         *integralValue = 0.0;
      } else {
         compValue = (italB * rValue + 2.0 * italC) / (rValue * sqrt(denom_quad));
         if (compValue < 1.0) {
            if (compValue < -1.0) {
                fprintf (stderr, " Boundary_NegC: Opposite Direction Invalid asin? %.4e\n",
                                 compValue);
               *integralValue = (-M_PI / 2.0) / sqrt(-italC);
            } else { 
               *integralValue = asin (compValue) / sqrt(-italC);
            }
         } else {
            fprintf (stderr, " Boundary_NegC: Invalid asin: %.4e\n",compValue);
            *integralValue = (M_PI / 2.0) / sqrt(-italC);
         }
      }
   } else {
      fprintf (stderr, " Boundary_NegC: Wrong routine for Italic C > 0.0\n");
      status = FAILURE_ART_SEGMENT;
   }

   return (status);
}

/*
 *****************************************************************************
 *
 * Eq. 10A (Norman) for upper boundary when italC is greater than zero.
 *
 *****************************************************************************
 */

int Boundary_PosC (double italA, double italB, double italC, double denom_quad,
                   double rValue, double xValue, int boundaryFlag, 
                   double *integralValue, double *partialLogValue)
{
   int    status      = SUCCESS_ART_SEGMENT;
   double compValue   = 0.0;
   double sqrtItalC   = 0.0;
   double sqrtItalC_X = 0.0;

   if (xValue < 0.0) {
      printf (" X-Value in Segment Integral < 0.0 (%lf) for r(%lf)\n", xValue, rValue);
      status = FAILURE_ART_SEGMENT;
   } else {
      if (italC > 0.0) {
         sqrtItalC   = sqrt (italC);
         sqrtItalC_X = sqrt (italC * xValue);
      } else {
         fprintf (stderr, " Boundary_PosC: Wrong routine for Italic C < 0.0\n");
         status = FAILURE_ART_SEGMENT;
      }
   }
/* 
 * Thin layer condition resulting in a negative value for Eq 10A
 */
   if (status == SUCCESS_ART_SEGMENT) {
      compValue = (2.0 * sqrtItalC_X + italB * rValue + 2.0 * italC) / rValue;
      if (compValue < 0.0) {
         if (boundaryFlag == SEGMENT_LOWER_BOUNDARY) {
            *partialLogValue = compValue;
            *integralValue   = 0.0;
         } else {
            *integralValue   = -log(compValue / (*partialLogValue)) / sqrtItalC;
            *partialLogValue = 0.0;
         }
      } else {
         *partialLogValue = 0.0;
         *integralValue   = -log (compValue) / sqrtItalC;
      }
   } else {
      *integralValue   = 0.0;
      *partialLogValue = 0.0;
   }

   return (status);
}

/*
 *****************************************************************************
 *
 * Eq. 2.63 (Mercer)
 *
 *****************************************************************************
 */

double Ray_ApogeeRadial (struct qps_definition_t *QPS_Segment)
{
   double rayTurn1     = 0.0;
   double rayTurn2     = 0.0;
   double apogeeRadial = 0.0;
/*
 * Need to resolve the near zero issue from the segment fits.
 */

   if (QPS_Segment->denom_quad > 0.0) {
/*
 * Solve for r ap in eq. (apogee occurs in a QP layer)
 */
      rayTurn1 = (-QPS_Segment->italB - sqrt (QPS_Segment->denom_quad)) /
                                       (2.0 * QPS_Segment->italA);
      rayTurn2 = (-QPS_Segment->italB + sqrt (QPS_Segment->denom_quad)) /
                                       (2.0 * QPS_Segment->italA);

      if ((rayTurn1 <= QPS_Segment->rValueUpper) && (rayTurn1 > QPS_Segment->rValueLower)) {
         if ((rayTurn2 <  QPS_Segment->rValueUpper) && (rayTurn2 >= QPS_Segment->rValueLower)) {
/*
 * Both estimates are within the segment bounds, so take the minimum
 */
            if (rayTurn1 < rayTurn2) {
               apogeeRadial = rayTurn1;
            } else {
               apogeeRadial = rayTurn2;
            }
         } else {
            apogeeRadial = rayTurn1;
         }
      } else {
/*
 * Need to check estimate 2 for inside the segment bounds
 */
         if ((rayTurn2 <  QPS_Segment->rValueUpper) && (rayTurn2 >= QPS_Segment->rValueLower)) {
            apogeeRadial = rayTurn2;
         }
      } 
   }

   return (apogeeRadial);
}

/*
 *****************************************************************************
 *
 * Implement approach defined in Norman & Cannon, 1997
 *
 *****************************************************************************
 */

int RayTrace_DownLeg_Portion (struct qps_model_profile_t *QPModel,
                              struct ray_trace_def_t     *RT_Path,
                            double gammaBottom, double radialBottom,
                            double rangeBottom, double *strtRadial,
                            int *rayDirection, double *integralUiMLi, double *rangeIono)
{
   int     index2        = 0;
   double  integralLower = 0.0;
   double  integralUpper = 0.0;
   double  rayRadial     = (*strtRadial);
   int     apogeeFlag    = APOGEE_DETECTED;

   for (index2 = 0; index2 < QPModel->numb_segments; index2++) {

      if (QPModel->qps_segments[index2].rValueUpper <=  rayRadial) {
/*
 * Set the new lower point to be the bottom of segment (exception for going below the segmenbt set.
 */
         rayRadial = QPModel->qps_segments[index2].rValueLower;

         integralLower = 0.0;
         integralUpper = 0.0;
         Solve_BoundaryIntegral (&QPModel->qps_segments[index2],
                                  QPModel->qps_segments[index2].rValueLower,
                                  QPModel->qps_segments[index2].rValueUpper, rayRadial,
                                 &integralUpper, &integralLower, apogeeFlag);
         *integralUiMLi += (integralUpper - integralLower);
         RT_Path->rayPoints[RT_Path->numPoints].rangeUiMLi = (*integralUiMLi);

         *rangeIono = GrndRangeTraveled (gammaBottom, radialBottom, *integralUiMLi);

         RT_Path->rayPoints[RT_Path->numPoints].range = (*rangeIono) + RT_Path->rangeBottom;
         RT_Path->rayPoints[RT_Path->numPoints].height =
                             radial_to_height (QPModel->qps_segments[index2].rValueLower);
         RT_Path->rayPoints[RT_Path->numPoints].gammaSegment = 0.0; //  need to calculate.
         RT_Path->numPoints++;
/*
 *       printf (" G-Range ro: %.1lf Beta: %.4lf Rt %7.1lf RangeTot: %.1lf ",
 *           radialBottom, gammaBottom, (*rangeIono), rangeBottom + (*rangeIono));
 *       printf (" Radial(L,U) %.1lf - %.1lf\n", QPModel->qps_segments[index2].rValueLower,
 *                                               QPModel->qps_segments[index2].rValueUpper);
 */
      }
   }
/*
 * Need to do the final point on the surface.
 */
   RT_Path->rayPoints[RT_Path->numPoints].rangeUiMLi = 0.0;
   RT_Path->rayPoints[RT_Path->numPoints].range = 
               RT_Path->rayPoints[RT_Path->numPoints - 1].range + beta_to_range (RT_Path->beta0, 
                           height_to_radial(RT_Path->rayPoints[RT_Path->numPoints - 1].height));

   RT_Path->rayPoints[RT_Path->numPoints].height = 0.0;
   RT_Path->rayPoints[RT_Path->numPoints].gammaSegment = RT_Path->beta0;
   RT_Path->numPoints++;

   return (apogeeFlag);
}

/*
 *****************************************************************************
 *
 * Implement approach defined in Norman & Cannon, 1997
 *
 *****************************************************************************
 */

int RayTrace_UpLeg_Portion (struct qps_model_profile_t *QPModel,
                            struct ray_trace_def_t     *RT_Path,
                            double gammaBottom, double radialBottom,
                            double rangeBottom, double *strtRadial,
                            int *rayDirection, double *integralUiMLi, double *rangeIono)
{
   int     index2        = 0;
   int     apogeeFlag    = APOGEE_SEARCH;

   double  apogRadSeg    = 0.0;
   double  integralLower = 0.0;
   double  integralUpper = 0.0;
   double  rayRadial     = (*strtRadial);

   for (index2 = QPModel->numb_segments - 1; index2 >= 0; index2--) {

      if (QPModel->qps_segments[index2].rValueUpper >= rayRadial) {

         apogRadSeg = Ray_ApogeeRadial (&QPModel->qps_segments[index2]);

         if (apogRadSeg != 0.0) {
            apogeeFlag = APOGEE_SEGMENT;
            *rayDirection = DOWNLEG_RAYTRACE;
         } else if (index2 == 0) {
            *rayDirection = EXIT_IONOSPHERE;
         }

         integralLower = 0.0;
         integralUpper = 0.0;
         Solve_BoundaryIntegral (&QPModel->qps_segments[index2],
                                  QPModel->qps_segments[index2].rValueLower,
                                  QPModel->qps_segments[index2].rValueUpper, rayRadial,
                                 &integralUpper, &integralLower, apogeeFlag);

         *integralUiMLi += (integralUpper - integralLower);
         RT_Path->rayPoints[RT_Path->numPoints].rangeUiMLi = (*integralUiMLi);

/*
 * Calculated over the integrated over QPS segments (eq 9, 1 to n)
 *    rangeIono is the Rt segment
 */
         *rangeIono = GrndRangeTraveled (gammaBottom, radialBottom, *integralUiMLi);
/*
 *       printf (" G-Range ro: %.1lf Beta: %.4lf Rt %7.1lf RangeTot: %.1lf ",
 *                 radialBottom, gammaBottom, *rangeIono, rangeBottom + (*rangeIono));
 *       printf (" Radial(L,U) %.1lf - %.1lf\n", QPModel->qps_segments[index2].rValueLower,
 *                                               QPModel->qps_segments[index2].rValueUpper);
 */
         if (apogeeFlag == APOGEE_SEGMENT) {

            apogeeFlag = APOGEE_DETECTED;
            RT_Path->apogeeHeight = radial_to_height (apogRadSeg);
            RT_Path->rayTraceFlag = APOGEE_DETECTED;
/*
 * Store Apogee point and then the lower segment point already part of the down leg
 *    average of last location and computed should be on either side of the apogee range
 */
            RT_Path->apogeeRange = (RT_Path->rayPoints[RT_Path->numPoints - 1].range + 
                                         ((*rangeIono) + RT_Path->rangeBottom)) / 2.0;
            RT_Path->rayPoints[RT_Path->numPoints].range = RT_Path->apogeeRange;
            RT_Path->rayPoints[RT_Path->numPoints].height = RT_Path->apogeeHeight;
            RT_Path->rayPoints[RT_Path->numPoints].gammaSegment = 0.0; // Actually TRUE!
            RT_Path->numPoints++;
/*
 * Store the point after apogee which is actually a downleg segment associated to the
 *    lower height calculation.
 */
            RT_Path->rayPoints[RT_Path->numPoints].rangeUiMLi = (*integralUiMLi);
            RT_Path->rayPoints[RT_Path->numPoints].range = (*rangeIono) + RT_Path->rangeBottom;
            RT_Path->rayPoints[RT_Path->numPoints].height = 
                                radial_to_height (QPModel->qps_segments[index2].rValueLower);
            RT_Path->rayPoints[RT_Path->numPoints].gammaSegment = 0.0; //  need to calculate.
            RT_Path->numPoints++;

            *strtRadial = QPModel->qps_segments[index2].rValueLower;

         } else {
            rayRadial = QPModel->qps_segments[index2].rValueUpper;

            RT_Path->rayPoints[RT_Path->numPoints].range = (*rangeIono) + RT_Path->rangeBottom;
            RT_Path->rayPoints[RT_Path->numPoints].height = 
                                radial_to_height (QPModel->qps_segments[index2].rValueUpper);
            RT_Path->rayPoints[RT_Path->numPoints].gammaSegment = 0.0; //  need to calculate.
            RT_Path->numPoints++;
         }
      }
      if (apogeeFlag == APOGEE_DETECTED) {
         return (apogeeFlag);
      }
   }

   *strtRadial = rayRadial;

   return (apogeeFlag);
}

/*
 *****************************************************************************
 *
 *
 *
 *****************************************************************************
 */

int RayTracePath (struct ray_trace_def_t *RT_Path, double frequency, 
                   double elevation, double radialBottom, 
                   struct qps_model_profile_t *QP_Model, int verbose)

{
   int    status        = SUCCESS_ART_SEGMENT;
   int    index         = 0.0;
   int    rayDirection  = UPLEG_RAYTRACE;
   int    apogeeFlag    = APOGEE_SEARCH;

   double gammaBottom   = gamma_angle (elevation, radialBottom);
   double rangeBottom   = beta_to_range (elevation, radialBottom); // Eq 3, R0
   double rayRadial     = 0.0;
   double integralUiMLi = 0.0;
   double rangeIono     = 0.0;
  
/*
 * Load output structure for use later (may be duplicated space)
 */

   RT_Path->frequency    = frequency;
   RT_Path->beta0        = elevation;
   RT_Path->gammaBottom  = gammaBottom;
   RT_Path->radialBottom = radialBottom;
   RT_Path->rangeBottom  = rangeBottom;

/*
 * Initialize the first point 
 */

   RT_Path->rayPoints[0].range        = 0.0;
   RT_Path->rayPoints[0].height       = 0.0;
   RT_Path->rayPoints[0].gammaSegment = gammaBottom;
   RT_Path->numPoints = 1;

/*
 * Set initial height for selection of QP Segments
 */
   rayRadial   = radialBottom;

   status = Build_RayTrace_Coeff (QP_Model, elevation, frequency);
/*
 * Look for break points in the up-leg direction and determine penetrated through
 *    the ionosphere or apogee.
 */

   apogeeFlag = RayTrace_UpLeg_Portion (QP_Model, RT_Path, gammaBottom, radialBottom,
                                        rangeBottom, &rayRadial, &rayDirection,
                                        &integralUiMLi, &rangeIono);
   if (rayDirection == EXIT_IONOSPHERE) {
      RT_Path->rayTraceFlag = EXIT_IONOSPHERE;
   } else {
      apogeeFlag = RayTrace_DownLeg_Portion (QP_Model, RT_Path, gammaBottom, radialBottom,
                                             rangeBottom, &rayRadial, &rayDirection,
                                             &integralUiMLi, &rangeIono);
   }
   RT_Path->rangeMax = RT_Path->rayPoints[RT_Path->numPoints - 1].range;
   RT_Path->groupPath = 0.0;
   RT_Path->spreadLoss = 0.0;

   Output_RayTrace_Result (RT_Path, verbose);

   return (status);
}
