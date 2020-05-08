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
#include "QPSegment.h"
#include "QPS_Model.h"

/*
 *****************************************************************************
 *
 *  Model provides aolution to the multi-quasiparabolic segments [MQPS) for 
 *     for the ionosphere profile provided as input.  The model will construct 
 *     a connected series of QP layers to build a smoothly varying electron
 *     density profile. 
 *
 *  Model will accept the output of other routines generating a profile in 
 *     height versus either plasma frequency or number density.  Internal test 
 *     will determine the correction for the data points before accessing the 
 *     least square segment calculation.
 *
 *****************************************************************************
 */

int QPS_Model_Profile (double *profHeight, double *profValues, int num_pts, int dataType,
                       struct qps_model_profile_t *QPModel)
{
   int     index         = 0;
   int     status        = SUCCUSS_QPS_MODEL;
   int     numb_segments = 0;
   int     edp_pts       = num_pts;

   double *prof_fp       = NULL;
   double *prof_fp2      = NULL;
   double *prof_radial   = NULL;

   double  dydr_qps_segment = 0.0;
   double  rInitial         = 0.0;
   double  yInitial         = 0.0;
   int     rmsError         = PASSED_RMS_TOL_TEST;

   float   ionoBottom    = 0.0;

/*
 * Selection of number of points to fit can result in more segments (lower number) versus 
 *    the possibility for multiple iterations at a higher number to account for less 
 *    smooth structures in the input EDP.
 *
 *    Four points was used as an advantage, since the result of valleys (lower part of 
 *    the profile demonstrated a 2 point fit in the end.  The interation to a low RMS 
 *    from a higher number of points was resulting in excessive steps to get a low RMS. 
 *    It should be examined further where a higher number of points can be used at the 
 *    upper profile, while a lower number can be applied for the F1 to E layer segment. 
 */

   int npts_fit      = OPT_FIT_POINTS;
   int maxPts_fit    = npts_fit;
   int strt_profile  = edp_pts - npts_fit; 
   int match_point   = strt_profile + npts_fit - 1;
   int npts_inc      = npts_fit - 1;

/*
 * Special condition to prevent overflow of the segments produced.  Internal structure
 *    has a limit in the number of segments produced.  The assessment for number of
 *    points is based on the selection of 4 for the number of points in a fit segment.
 *    Changing the number could effect the number of segments produced.  The check 
 *    performed below has a factor of two applied to correct for segments generated 
 *    by only 2 input points.
 */

   if ((num_pts / MAX_QPS_SEGMENTS) > (maxPts_fit - 2)) {
      npts_fit = (num_pts / MAX_QPS_SEGMENTS) * 2;
      fprintf (stderr, " WARNING: ",
                "Force number of Fit Points from %d to %d to fit QPS Model List of %d\n",
                                      maxPts_fit, npts_fit, MAX_QPS_SEGMENTS);
      maxPts_fit    = npts_fit;
      strt_profile  = edp_pts - npts_fit;
      match_point   = strt_profile + npts_fit - 1;
      npts_inc      = npts_fit - 1;
   }
/*
 * Pick a point to be the bottom of the ionosphere where fitting beyond is not necessary
 *    Also many models produce ionosphere below the selected ionosphere and provided 
 *    zero or unreal values.  This should be a height below the E-Layer at about
 *    90 - 110 km.  
 * This code uses the profile to control the bottom of the ionosphere.
 */

   ionoBottom = height_to_radial(profHeight[0]);

/*
 * Assign temporary memory for the profile.
 */
   prof_radial = (double *)(malloc (sizeof (double) * edp_pts));
   if (prof_radial == (double *)(NULL)) {
      fprintf (stderr, "Failed MALLOC for profile heights in QPS_MOdel\n");
      status = FAILED_QPS_MODEL;
   }

   if (status == SUCCUSS_QPS_MODEL) {
      prof_fp2 = (double *)(malloc (sizeof (double) * edp_pts));
      if (prof_fp2 == (double *)(NULL)) {
         fprintf (stderr, "Failed MALLOC for profile Fp2 in QPS_MOdel\n");
         status = FAILED_QPS_MODEL;
      }
   }

   if (status == SUCCUSS_QPS_MODEL) {
      prof_fp  = (double *)(malloc (sizeof (double) * edp_pts));
      if (prof_fp == (double *)(NULL)) {
         fprintf (stderr, "Failed MALLOC for profile Fp in QPS_MOdel\n");
         status = FAILED_QPS_MODEL;
      }
   }

   if (status == SUCCUSS_QPS_MODEL) {

/*
 * Load the temporary memory for processing through the least squares and
 *    convert values into the correct units for the QPS 
 */
      if (dataType == PLASMA_FREQUENCY) {
         for (index = 0; index < edp_pts; index++) {
            if (profValues[index] < 1.0E-1) {
               profValues[index] = 1.0E-1;
            } else {
               prof_fp[index]     = profValues[index];
            }
            prof_fp2[index]    = profValues[index] * profValues[index];
            prof_radial[index] = height_to_radial(profHeight[index]);
         }
/*
 * TODO: Need to have data types for both cm-3 and m-3
 */
      } else if (dataType == ELECTRON_DENSITY_M3) {
         for (index = 0; index < edp_pts; index++) {
            prof_fp[index]   = Ne_to_fp (profValues[index]) * HZ_TO_MHZ;
            prof_fp2[index]  = prof_fp[index] * prof_fp[index];
            prof_radial[index] = height_to_radial(profHeight[index]);
         }

      } else {
         fprintf (stderr, "Data Type for QPS_Model_Profile not Supported\n");
         status = FAILED_QPS_MODEL;
      }
   }

   if (status == SUCCUSS_QPS_MODEL) {

/*
 * Method for defining QPS segment parts is to start at the top of the profile and work 
 *    down in height until below the E-Region.
 *    QPS definition for A, B, and C are tailored for working down the profile 
 *    to account for the number of segments increasing toward the bottom of the
 *    profile. 
 *
 * Initialize the base values used in the least square spline fitting approach.
 */
      rInitial = prof_radial[edp_pts - 1];
      yInitial = prof_fp2[edp_pts - 1];

      for (index = strt_profile - 1; index >= 0; index -= npts_inc) {
/*
 * Clear the segment structure to prevent use of rejected estimates.
 */
         memset (&(QPModel->qps_segments[numb_segments]), 0, sizeof (struct qps_definition_t));

/*
 * Define the original profile data point used to join segments and hold the 
 *    adjusted y'(rt) and derivative used in the joined segment.
 */
         match_point = index + 1;
         QP_LSq_Segment (&prof_radial[index], &prof_fp2[index], npts_fit, 
                         rInitial, yInitial, dydr_qps_segment,
                         &QPModel->qps_segments[numb_segments].capA, 
                         &QPModel->qps_segments[numb_segments].capB, 
                         &QPModel->qps_segments[numb_segments].capC);
/*
 * Need to verify the quality of the QP fit obtained. 
 */
         rmsError = QPS_Compare(&prof_radial[index], &prof_fp2[index], &prof_fp[index], 
                                npts_fit, PERCENT_FP_ERROR, MAX_MHZ_ERROR,
                                QPModel->qps_segments[numb_segments].capA, 
                                QPModel->qps_segments[numb_segments].capB, 
                                QPModel->qps_segments[numb_segments].capC);

/*
 * Check the quality of fit result and the status of 1 point fit still not
 *   providing a sufficient quality.
 */
         if (rmsError != PASSED_RMS_TOL_TEST && npts_inc > 1) {
            index += npts_inc;
            npts_fit--;
            npts_inc--;
            
         } else {
/*
 * Compute the join point derivative, y'(rt), and initial values for the next 
 *    segment to use in the least squares calculation.
 * Note: The previous test implies a 1 point fiut must be good and used for the 
 *    segment.
 */
            dydr_qps_segment   = QPS_Start_dydr  (QPModel->qps_segments[numb_segments].capA, 
                                                  QPModel->qps_segments[numb_segments].capB, 
                                                (double)(prof_radial[match_point]));

            prof_fp2[match_point] = QPS_Start_yValue (QPModel->qps_segments[numb_segments].capA, 
                                                    QPModel->qps_segments[numb_segments].capB, 
                                                    QPModel->qps_segments[numb_segments].capC, 
                                                    prof_radial[match_point]);

            rInitial = prof_radial[match_point];
            yInitial = prof_fp2[match_point];
/*
 * Need to store the join point information for use later in the segment process.
 */
            QPModel->qps_segments[numb_segments].rValueLower = prof_radial[match_point];
            QPModel->qps_segments[numb_segments].yValueLower = prof_fp[match_point];
            QPModel->qps_segments[numb_segments].rValueUpper = prof_radial[match_point + npts_inc];
            QPModel->qps_segments[numb_segments].yValueUpper = prof_fp[match_point + npts_inc];
            QPModel->qps_segments[numb_segments].nFitPts     = npts_fit;

            numb_segments++;
/*
 * Check the status of the point list provided for end of ionosphere or number 
 *   of points.
 */
            if (ionoBottom >= prof_radial[match_point]) {
/*
 * If the end point is below the defined bottom of the ionosphere, need to exit the loop
 *    by setting the index to negative.
 */
               index = -1;  // force end of the loop
            } else {
/*
 * Always try to use the maximum points to fit in a segment. Especially after having 
 *   decremented based on prior quality of fit.
 */
               npts_fit++;
               if (npts_fit > maxPts_fit) npts_fit = maxPts_fit;
               npts_inc = npts_fit - 1;

               if (index - npts_fit < 0 && index > 0) {
                  npts_fit = match_point;
                  npts_inc = index;
               }

            } /* End of the checking for end of EDP */

         } /* End of condition on quality of estimate */

      } /*  End of the loop over EDP points */

//      printf ("Number Segments %d\n",numb_segments);
      QPModel->numb_segments = numb_segments;
   }
/*
 * Clear temporary memory assignment.
 */
   if (prof_fp != (double *)(NULL)) {
      free (prof_fp);
      prof_fp = (double *)(NULL);
   }

   if (prof_fp2 != (double *)(NULL)) {
      free (prof_fp2);
      prof_fp2 = (double *)(NULL);
   }

   if (prof_radial != (double *)(NULL)) {
      free (prof_radial);
      prof_radial= (double *)(NULL);
   }

   return (status);
}

/*
 *****************************************************************************
 *
 *  Routine used to list the input and computed values.
 *
 *****************************************************************************
 */

int QPS_Model_SegmentList (double *profHeight, double *ne_prof, int num_pts, 
                           struct qps_model_profile_t *QPModel, int verbose)
{

   int index       = 0;
   int index2      = 0;
   int status      = SUCCUSS_QPS_MODEL;
   float  rValue   = 0.0;
   double yValue   = 0.0;
/*
 * List Top down or bottom up -- Doesn't really matter.
 */
   if (verbose) {
      index2 = 0;
      while (height_to_radial(profHeight[index2]) < 
          QPModel->qps_segments[QPModel->numb_segments - 1].rValueLower && index2 < num_pts) {
         index2++;
      };
      
      printf (" QPS Model Number of Segments: %d\n", QPModel->numb_segments);

      if (verbose == VERBOSE_LEVEL2) {
/*
 * Skip the bottom count and also ignore th etop height
 */
         printf (" Number of Profile Heights: %d\n", num_pts - index2 - 1);
         printf (" Ht(km)  Ym(MHz)  qp_Ne(m-3)     Ne(m-3)     diff-Ne\n");

         for (index = QPModel->numb_segments - 1; index >= 0; index--) {

            rValue = height_to_radial(profHeight[index2]);
            do {
         
               yValue = QPS_Solve_Fn2 (QPModel->qps_segments[index].capA,
                                       QPModel->qps_segments[index].capB,
                                       QPModel->qps_segments[index].capC, (double)(rValue));
               if (yValue > 0.0) {
                  printf (" %6.1lf %8.4lf %11.4e %11.4e %11.4e\n",radial_to_height(rValue), 
                            sqrt(yValue), fp_to_Ne(sqrt(yValue)), ne_prof[index2],
                            fp_to_Ne(sqrt(yValue)) - ne_prof[index2]);
               } else {
                  printf (" %6.1lf %8.4lf %11.4e %11.4e\n",radial_to_height(rValue),
                                                       0.0,0.0,ne_prof[index2]);
               }
               index2++;
               rValue = height_to_radial(profHeight[index2]);

            } while (rValue < QPModel->qps_segments[index].rValueUpper);  
         }  
      }
   }

   return (status);
}

/*
 *****************************************************************************
 *
 * Reference Mercer for detailson the Coefficient generation.
 * Initialize the QPS coefficents used in Cannon eq 9, 10 based on the definition 
 *    of eq 7 and 8 
 *
 * These coefficients are frequency and Beta angle dependent unlike the capA,B,C
 *    representing the density as a function of height.
 *
 *****************************************************************************
 */

int Build_RayTrace_Coeff (struct qps_model_profile_t *QP_Model, double elevation,
                          double frequency)
{
   int    status        = SUCCESS_QPS_SEGMENT;
   int    index         = 0.0;
   double hmProfile     = 0.0;
/*
 * Preset values used to determine critical reflection in Homing process
 */
   QP_Model->hmeProfile  = 0.0;
   QP_Model->foeProfile  = 0.0;
   QP_Model->hmf2Profile = 0.0;
   QP_Model->fof2Profile = 0.0;

   for (index = 0; index < QP_Model->numb_segments; index++) {
      QPS_RTrace_Coef ((float)(frequency), (float)(elevation), (float)(MEAN_RADIUS_EARTH),
                                         QP_Model->qps_segments[index].capA,
                                         QP_Model->qps_segments[index].capB,
                                         QP_Model->qps_segments[index].capC,
                                        &QP_Model->qps_segments[index].italA,
                                        &QP_Model->qps_segments[index].italB,
                                        &QP_Model->qps_segments[index].italC);
      QP_Model->qps_segments[index].denom_quad =
                        QPS_RTrace_Quad (QP_Model->qps_segments[index].italA,
                                         QP_Model->qps_segments[index].italB,
                                         QP_Model->qps_segments[index].italC);

      hmProfile = Max_ApogeeHeight (QP_Model->qps_segments[index].capB,
                                    QP_Model->qps_segments[index].capC,
                                    frequency);
/*
 * Need to confirm within the segment
 */
      if ((hmProfile >= QP_Model->qps_segments[index].rValueLower) &&
          (hmProfile <= QP_Model->qps_segments[index].rValueUpper)) {

         if (hmProfile > MINIMUM_HMF_RADIAL) {
            QP_Model->hmf2Profile = hmProfile;
            QP_Model->fof2Profile = QPS_Solve_Fn2 (QP_Model->qps_segments[index].capA,
                                                   QP_Model->qps_segments[index].capB,
                                                   QP_Model->qps_segments[index].capC,
                                                   QP_Model->hmf2Profile);
            if (QP_Model->fof2Profile > 0.0) {
               QP_Model->fof2Profile = sqrt (QP_Model->fof2Profile);
            } else {
               QP_Model->fof2Profile = 0.0;
            }
         } else if ((hmProfile < MAXIMUM_HME_RADIAL) && (hmProfile > MINIMUM_HME_RADIAL)) {
            QP_Model->hmeProfile = hmProfile;
            QP_Model->foeProfile = QPS_Solve_Fn2 (QP_Model->qps_segments[index].capA,
                                                   QP_Model->qps_segments[index].capB,
                                                   QP_Model->qps_segments[index].capC,
                                                   QP_Model->hmeProfile);
            if (QP_Model->foeProfile > 0.0) {
               QP_Model->foeProfile = sqrt (QP_Model->foeProfile);
            } else {
               QP_Model->foeProfile = 0.0;
            }
         }
      }
   }
   return (status);
}

/*
 *****************************************************************************
 *
 * Equation 2.64 (Mercer)
 *
 *****************************************************************************
 */

double Max_ApogeeHeight (double capB, double capC, double frequency)
{
   double recip_freq2 = 0.0;
   double rtmax       = 0.0;

   if (frequency != 0.0) {
      recip_freq2 = 1.0 / (frequency * frequency);
      rtmax       = (capB * recip_freq2) / (2.0 - 2.0 * capC * recip_freq2);
   }

   return (rtmax);
}

/*
 *****************************************************************************
 *
 *
 *
 *****************************************************************************
 */

double Max_Height4Distance (double groundRange)
{
   double vheight = radial_to_height (MEAN_RADIUS_EARTH / cos (theta_angle (groundRange)));

   return (vheight);
}

/*
 *****************************************************************************
 *
 *
 *
 *****************************************************************************
 */

double Max_Elevation4Homing (double groundRange, double hmProfile, double foProfile, 
                             double frequency)
{
   double theta = theta_angle (groundRange);
   double phi0  = phi0_angle (theta, hmProfile);
   double freqV = frequency * cos (phi0);
   double freqO = fvert_to_fob (phi0, foProfile);
   double elev  = -M_PI;

   if (freqV >= freqO) {
      elev  = M_PI / 2.0 - theta - phi0;
//      printf (" Computing Elevation for %lf as %lf\n",hmProfile, elev*180.0/M_PI);
   }

   return (elev);
}
