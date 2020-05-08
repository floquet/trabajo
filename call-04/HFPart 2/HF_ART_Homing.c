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
 *     20 March 2020
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

int POET_Homing_First (struct ray_trace_def_t *RT_Path, double frequency,
                       double radialBottom, int propagationType, int *numberTraces,
                       double *elevArray, double *rangeArray,
                       struct qps_model_profile_t *QP_Model, int verbose);

int POET_Homing_Middle (struct ray_trace_def_t *RT_Path, double frequency,
                       double radialBottom, int propagationType, int *numberTraces,
                       double rangeHoming, double *elevArray, double *rangeArray,
                       struct qps_model_profile_t *QP_Model, int verbose);

int POET_Homing_Check (struct ray_trace_def_t *RT_Path, double frequency,
                       double radialBottom, double elevTest, int *numberTraces, 
                       struct qps_model_profile_t *QP_Model, int verbose);

int POET_Homing_IntPos (struct ray_trace_def_t *RT_Path, double frequency,
                       double radialBottom, int propagationType, int *numberTraces,
                       double rangeHoming, double *elevArray, double *rangeArray,
                       struct qps_model_profile_t *QP_Model, int verbose);

int POET_Homing_FitPos (struct ray_trace_def_t *RT_Path, double frequency,
                       double radialBottom, int propagationType, int *numberTraces,
                       double rangeHoming, double *elevArray, double *rangeArray,
                       struct qps_model_profile_t *QP_Model, int verbose);

double POET_Homing_GroupDelay (struct ray_trace_def_t *RT_Path, int compLevel);

double POET_Homing_Spread (struct ray_trace_def_t *RT_Path);

int POET_Homing_CloseOut (struct ray_trace_def_t *RT_Path, double rangeHoming,
                        int numberTraces, double *elevArray, double *rangeArray,
                        double *coeffArray, char *labelString, int verbose);

/*
 *****************************************************************************
 *
 *
 *
 *****************************************************************************
 */

int POET_Homing_Check (struct ray_trace_def_t *RT_Path, double frequency,
                       double radialBottom, double elevTest, int *numberTraces, 
                       struct qps_model_profile_t *QP_Model, int verbose)
{

   memset (RT_Path, 0, sizeof (struct ray_trace_def_t));
   (*numberTraces)++;
   RayTracePath (RT_Path, frequency, elevTest, radialBottom, QP_Model, verbose);

   return (RT_Path->rayTraceFlag);
}

/*
 *****************************************************************************
 *
 *
 *
 *****************************************************************************
 */

int POET_Homing_First (struct ray_trace_def_t *RT_Path, double frequency,
                       double radialBottom, int propagationType, int *numberTraces,
                       double *elevArray, double *rangeArray,
                       struct qps_model_profile_t *QP_Model, int verbose)
{
   int    status     = SUCCESS_ART_HOMING;
   double deltaElev  = 0.0;
   double deg2rad    = M_PI / 180.0;

/*
 * Need to move to the mid-point and re-do the first point recheck since
 *    the initial estimate exits the ionosphere.
 */
   if (POET_Homing_Check (RT_Path, frequency, radialBottom, elevArray[0], 
                          numberTraces, QP_Model, verbose) == EXIT_IONOSPHERE) {
      elevArray[0]  = (elevArray[0] + elevArray[1]) / 2.0;
      rangeArray[0] = 0.0;
      deltaElev     = elevArray[0] - elevArray[2];
      elevArray[1]  = elevArray[0] - deltaElev / 2.0;
      elevArray[2]  = elevArray[0] - deltaElev;
      if (verbose == VERBOSE_LEVEL2) {
         printf (" Reset back to Elev0: %.1lf Due to Exit Elev1: %lf DeltaElev: %lf\n",
                   elevArray[0]/deg2rad, elevArray[1]/deg2rad, deltaElev/deg2rad);
      }
      RT_Path->rayTraceFlag = EXIT_IONOSPHERE;
      status = EXIT_IONOSPHERE;
/*
 * Check the new starting point to see it will be below the original estimate
 *    if the point is not below it indicates a return to the beginning during
 *    the search for the other two points and having an penetration condition.
 */

   } else {
      status = RT_Path->rayTraceFlag;

      if (propagationType == FLAYER_RAY_PROP) {
         if (RT_Path->apogeeHeight < MAXIMUM_HME_HEIGHT) {
            if (verbose != VERBOSE_LEVEL0) {
               printf(" Looking for F-Layer Propagation and found E-Layer\n");
               printf (" Widen the search criteria by Factor of 2.0\n");
            }
            elevArray[0] *= 2.0;
            deltaElev     = elevArray[0] - elevArray[2];
            elevArray[1]  = elevArray[0] - deltaElev / 2.0;
         } else {
            rangeArray[0] = RT_Path->rangeMax;
            if (verbose == VERBOSE_LEVEL2) {
               printf (" Loading %lf Range %lf as FIRST F-Layer(%lf)\n",
                       elevArray[0]/deg2rad,rangeArray[0],RT_Path->apogeeHeight);
            }
            if (rangeArray[2] != 0.0) {
               if (elevArray[0] > elevArray[2] && rangeArray[0] > rangeArray[2]) {
                  if (verbose != VERBOSE_LEVEL0) {
                     printf (" WARNING:  Case of not finding Homing before leading edge range\n");
                  }
                  status = HOMING_NO_PROPAGATION;
               }
            }
         }
      } else if (propagationType == ELAYER_RAY_PROP) {
         if (RT_Path->apogeeHeight > MAXIMUM_HME_HEIGHT) {
            if (verbose != VERBOSE_LEVEL0) {
               printf (" Jumped to F-Layer on E-Layer initial search\n");
               printf (" Lower the search criteria by bisection of first and middle\n");
            }
            deltaElev     = elevArray[0] - elevArray[2];
            elevArray[0]  = elevArray[0] - deltaElev / 4.0;
            deltaElev     = elevArray[0] - elevArray[2];
            elevArray[1]  = elevArray[0] - deltaElev / 2.0;

         } else {
             rangeArray[0] = RT_Path->rangeMax;
             if (verbose != VERBOSE_LEVEL0) {
                printf (" Loading %lf Range %lf as FIRST E-Layer(%lf)\n",
                        elevArray[0]/deg2rad,rangeArray[0],RT_Path->apogeeHeight);
             }
         }
      } else {
         rangeArray[0] = RT_Path->rangeMax;
         if (verbose != VERBOSE_LEVEL0) {
            printf (" Loading %lf Range %lf as FIRST ?-Layer(%lf)\n",
                    elevArray[0]/deg2rad,rangeArray[0],RT_Path->apogeeHeight);
         }
      }
   }

   return (status);
}

/*
 *****************************************************************************
 *
 * This method can generate two solutions for the homing range provided.
 *    The potential for a low and high ray path exists based on the distance 
 *    and the E-Layer density.  The need to examine the E-Layer possible
 *    propagation will determine the return value and status flag.
 *
 *****************************************************************************
 */

int RayTraceHoming (struct ray_trace_def_t *RT_Path, double frequency,
                    double radialBottom, double rangeHoming, 
                    int skipElayer, int *propagationType, 
                    struct qps_model_profile_t *QP_Model, int verbose)
{
   int    status        = SUCCESS_ART_SEGMENT;
   int    notConverged  = 1;
   int    searchAgain   = 0;
   int    searchCode    = HOMING_LOADFIRST;
   int    numberTraces  = 0;

   double deg2rad       = M_PI / 180.0;
/*
 * Compute 0 degree Elevation radial distance to compare against E-Layer height 
 */
   double maxVHeight    = height_to_radial (Max_Height4Distance (rangeHoming)); 

   double hmf2          = 0.0;
   double elevMax       = 0.0;
   double elevMin       = 0.0;
   double deltaElev     = 0.0;
   double profileMUF    = 0.0;

   double elevTest      = 0.0;
   double elevArray[3]  = {0.0, 0.0, 0.0};
   double rangeArray[3] = {0.0, 0.0, 0.0};
   double coeffArray[3] = {0.0, 0.0, 0.0};

/* 
 * The first step requires a revised QP model definition based on the lower 
 *    F2 boundary to obtain an estimated elevation.  The initial elevation is 
 *    used to construct the QP Model definitions of reflection heights at the 
 *    E, F layer.
 */
   elevTest = rangeHt_to_elev (rangeHoming, MINIMUM_HMF_HEIGHT);

   status   = Build_RayTrace_Coeff (QP_Model, elevTest, frequency);
   if (status != SUCCESS_QPS_SEGMENT) {
      fprintf (stderr, " RayTraceHoming: FAILURE on return from Build_RayTrace_Coeff\n");
      return (status);
   }
   hmf2     = radial_to_height (QP_Model->hmf2Profile);

   if (verbose != VERBOSE_LEVEL0) {
      printf ("*** Homing Frequency: %4.1lf Range: %.1lf\n",
                                   frequency, rangeHoming);
      printf ("       QPS Profile hme: %.1lf hmf2: %.1lf Horizon: %.1lf\n",
                                    radial_to_height (QP_Model->hmeProfile), 
                                    radial_to_height (QP_Model->hmf2Profile), 
                                    radial_to_height (maxVHeight));
   }

   if (skipElayer == SKIP_ELAYER) {
      elevMax = Max_Elevation4Homing (rangeHoming, radial_to_height (QP_Model->hmf2Profile), 
                                      QP_Model->fof2Profile, frequency);
      if (verbose != VERBOSE_LEVEL0) {
         printf ("       F Layer Reflection hmf2: %.1lf Horizon: %.1lf fof2: %.3lf El: %.2lf\n",
                 QP_Model->hmf2Profile, maxVHeight, QP_Model->fof2Profile, elevMax/deg2rad);
      }
      *propagationType = FLAYER_RAY_PROP;
      profileMUF = fp_to_MUF(QP_Model->fof2Profile, elevMax);
      if (profileMUF < frequency) {
         printf ("--- Homing MUF Limit  (steps %2d) %6.1lf Freq: %4.1lf MUF: %4.1lf\n",
                                  numberTraces, rangeHoming, frequency, profileMUF);
         RT_Path->rayTraceFlag = MUF_FREQUENCY_LIMIT;
         return (SUCCESS_ART_HOMING);
      }

   } else if (QP_Model->hmeProfile >= maxVHeight) {
      elevMax = Max_Elevation4Homing (rangeHoming, radial_to_height (QP_Model->hmeProfile),
                                      QP_Model->foeProfile, frequency);
      printf ("        E Layer Reflection hme: %.1lf Horizon: %.1lf foe: %.3lf El: %.2lf\n",
                    QP_Model->hmeProfile, maxVHeight, QP_Model->foeProfile, elevMax/deg2rad);
      if (elevMax < 0.0) { 
         printf ("     E-Layer not possible given heights\n");
         printf ("     Check F layer reflection? %lf %lf %lf\n",
                              QP_Model->hmf2Profile, maxVHeight, QP_Model->fof2Profile);
         elevMax = Max_Elevation4Homing (rangeHoming, radial_to_height 
                             (QP_Model->hmf2Profile), QP_Model->fof2Profile, frequency);
         *propagationType = FLAYER_RAY_PROP;
      } else {
         *propagationType = ELAYER_RAY_PROP;
      }

   } else {
      printf (" Checking for a F-Layer with no E %lf %lf %lf\n",
                              QP_Model->hmf2Profile, maxVHeight, QP_Model->fof2Profile);
      elevMax = Max_Elevation4Homing (rangeHoming, radial_to_height
                             (QP_Model->hmf2Profile), QP_Model->fof2Profile, frequency);
      *propagationType = FLAYER_RAY_PROP;
   }


   if (elevMax > 0.0) {
      if (elevMax < 10.0 * deg2rad) {
//         printf (" Probable long range or e/f1 mode %lf\n",elevMax / deg2rad);
         elevMax *= 1.5;  
      } else {
         elevMax *= 1.05;  // add 5% to the elevation to make it work down from the guess
      }
   } else {
      printf (" WARNING: RayTraceHoming: Failed Max Elevation < 0.0 Frequency %.1lf Range: %.1lf\n",
                          frequency, rangeHoming);
      elevMax = 2.0 * deg2rad;  // set to 2.0 degrees to force 
   } 

//   printf (" Starting Elevation -- %lf\n",elevMax / deg2rad);

   deltaElev    = (elevMax - elevMin);
   elevArray[0] =  elevMax;
   elevArray[2] =  elevMin;
   elevArray[1] =  (elevMax + elevMin) / 2.0;

   while (notConverged) {
/*
 * Load the first point in the sequence of search to find the elevation 
 *    producing the lower range distance with the other two points 
 *    producing a larger range distance.
 */
      if (searchCode == HOMING_LOADFIRST) {

         status = POET_Homing_First (RT_Path, frequency, radialBottom, (*propagationType),
                                &numberTraces, elevArray, rangeArray, QP_Model,
                                VERBOSE_LEVEL0);
         if (status == EXIT_IONOSPHERE) {
            if (elevMax < elevArray[0]) {

               printf ("--- Homing Exit Iono  (steps %2d) %6.1lf Freq: %4.1lf\n",
                                  numberTraces, rangeHoming, frequency);
               RT_Path->rayTraceFlag = EXIT_IONOSPHERE;
               return (EXIT_IONOSPHERE);
            }
         } else if (status == HOMING_NO_PROPAGATION) {

            printf ("--- Homing No Prop    (steps %2d) %6.1lf Freq: %4.1lf\n",
                                  numberTraces, rangeHoming, frequency);
            RT_Path->rayTraceFlag = NO_PROPAGATE_HOMING;
            return (SUCCESS_ART_HOMING);
         } else {

            if (fabs(rangeHoming - RT_Path->rangeMax) < HOMING_TOLERANCE) {
               status = POET_Homing_IntPos (RT_Path, frequency, radialBottom, (*propagationType),
                                            &numberTraces, rangeHoming, elevArray, rangeArray, 
                                            QP_Model, verbose);
               return (status);
            } else {
               if (rangeArray[0] != 0.0) {
                  searchCode = HOMING_LOADMIDDLE;
//               } else {
//                  printf (" Case of reset on search\n");
               }
            }
         }

      } else {
         if (searchCode == HOMING_LOADMIDDLE) {
            if (rangeArray[0] > rangeHoming) {
/*
 * First is beyond the Homing range, which indicates the elevation needs to be higher;
 */
//               printf (" First Guess is after the Homing Range\n");
               elevArray[2]  = elevArray[0];
               rangeArray[2] = rangeArray[0];
               elevArray[0]  = elevArray[0] * 1.1;  // 10% bump 
               rangeArray[0] = 0.0;
               elevArray[1]  = (elevArray[0] + elevArray[2]) / 2.0;
               searchCode = HOMING_LOADFIRST;

            } else {
/*
 * First is before the Homing range, which indicates the elevation needs to be lower.
 */
//               printf (" First guess is before the Homing Range; check middle\n");
               searchCode = POET_Homing_Middle (RT_Path, frequency, radialBottom, (*propagationType),
                                &numberTraces, rangeHoming, elevArray, rangeArray, QP_Model,
                                VERBOSE_LEVEL0);

               if (searchCode == HOMING_COMPLETE_CLOSE) {
                  status = POET_Homing_CloseOut (RT_Path, rangeHoming, numberTraces,
                                   elevArray, rangeArray, (double *)(NULL), "2nd", verbose);
                  return (SUCCESS_ART_HOMING);

               } else if (searchCode == HOMING_LOADMIDDLE) {

                  if (POET_Homing_Check (RT_Path, frequency, radialBottom, elevArray[1],
                          &numberTraces, QP_Model, VERBOSE_LEVEL0) == EXIT_IONOSPHERE) {
                     printf (" FAILURE: This condition should never exists!\n");
                     return (FAILURE_ART_HOMING);
                  } else {
                     if (RT_Path->apogeeHeight > MAXIMUM_HME_HEIGHT) {  
                        rangeArray[1] = RT_Path->rangeMax;
                     } else {
                        printf (" Middle moved into E layer (%lf)\n", RT_Path->rangeMax);
                        rangeArray[1] = 0.0;
                     }
                  }
               } else {
                  printf (" Condition not coded %d\n",searchCode);
               }
            }

         } else {
/*
 * What should this case be!
 */
            fprintf (stderr," FATAL ERROR: What is this case (%d)\n", searchCode);
            return (FAILURE_ART_HOMING);
         } 
      }

//      printf (" Elev-0 = %lf Range-0 = %lf\n",elevArray[0]/deg2rad, rangeArray[0]);
//      printf (" Elev-1 = %lf Range-1 = %lf\n",elevArray[1]/deg2rad, rangeArray[1]);
//      printf (" Elev-2 = %lf Range-2 = %lf\n",elevArray[2]/deg2rad, rangeArray[2]);

      if (numberTraces > MAX_HOMING_TRACES) {
         printf ("--- Homing NoConverge (steps %2d) %6.1lf Freq: %4.1lf MUF: %4.1lf\n",
                           numberTraces, rangeHoming, frequency, profileMUF);
         RT_Path->rayTraceFlag = NO_CONVERGE_HOMING;
         return (FAILURE_ART_HOMING);
      }
      if (rangeArray[1] != 0.0) {
         if (rangeArray[2] != 0.0) {

            status = POET_Homing_FitPos (RT_Path, frequency, radialBottom, (*propagationType),
                                         &numberTraces, rangeHoming, elevArray, rangeArray,
                                         QP_Model, verbose);
            if (!(status == HOMING_LOADMIDDLE)) {
               notConverged = 0;
            } 
         }
      }
   };

   return (status);
}

/*
 *****************************************************************************
 *
 *
 *
 *****************************************************************************
 */

int POET_Homing_Middle (struct ray_trace_def_t *RT_Path, double frequency,
                       double radialBottom, int propagationType, int *numberTraces,
                       double rangeHoming, double *elevArray, double *rangeArray,
                       struct qps_model_profile_t *QP_Model, int verbose)
{
   int    status     = SUCCESS_ART_HOMING;

   double deltaElev  = 0.0;
   double deg2rad    = M_PI / 180.0;

   if (POET_Homing_Check (RT_Path, frequency, radialBottom, elevArray[1],
                          numberTraces, QP_Model, verbose) == EXIT_IONOSPHERE) {
      printf (" FAILED: Should not happen if the first point didnt exit\n");
      return (FAILURE_ART_HOMING);
   } else {

      if (fabs (RT_Path->rangeMax - rangeHoming) <= HOMING_TOLERANCE) {
//         printf (" This is close enough %lf %lf\n", RT_Path->rangeMax, rangeHoming);
         rangeArray[1] = RT_Path->rangeMax;
         status = HOMING_COMPLETE_CLOSE;
      } else {
//         printf (" Middle is: %lf with apogee: %lf\n", RT_Path->rangeMax,RT_Path->apogeeHeight);

         if (RT_Path->apogeeHeight > MAXIMUM_HME_HEIGHT) {
            if (RT_Path->rangeMax < rangeHoming) {
//               printf (" This Middle is now the higher elevation\n");
               elevArray[0]  = elevArray[1];
               rangeArray[0] = RT_Path->rangeMax;
               elevArray[1] = (elevArray[0] + elevArray[2]) / 2.0;
            } else {
//               printf (" This Middle is now the lower elevation\n");
               elevArray[2]  = elevArray[1];
               rangeArray[2] = RT_Path->rangeMax;
               elevArray[1]  = (elevArray[0] + elevArray[2]) / 2.0;
               rangeArray[1] = 0.0;
            }
            status = HOMING_LOADMIDDLE;
         } else {
            if (verbose != VERBOSE_LEVEL0) {
               printf (" Entered E-Layer propagation range\n");
               printf (" Moving middle toward upper by fraction and calling lower\n");
            }
            elevArray[2]  = elevArray[1] - 0.1 * deg2rad;
            rangeArray[2] = 0.0;
            elevArray[1]  = (elevArray[0] + elevArray[2]) / 2.0;
            rangeArray[1] = 0.0;
            status = HOMING_LOADMIDDLE;
         }
      }
   }

   return (status);
}

/*
 *****************************************************************************
 *
 *
 *
 *****************************************************************************
 */

int POET_Homing_IntPos (struct ray_trace_def_t *RT_Path, double frequency,
                        double radialBottom, int propagationType, int *numberTraces,
                        double rangeHoming, double *elevArray, double *rangeArray,
                        struct qps_model_profile_t *QP_Model, int verbose)
{
   int    status     = SUCCESS_ART_HOMING;
   double elevTest   = 0.0;
   double deg2rad    = M_PI / 180.0;

   if (rangeArray[1] == 0.0) {
      elevArray[1] = elevArray[0] - 0.1 * deg2rad;

      if (POET_Homing_Check (RT_Path, frequency, radialBottom, elevArray[1],
                          numberTraces, QP_Model, VERBOSE_LEVEL0) == EXIT_IONOSPHERE) {
         printf (" FAILURE: This condition should never exists!\n");
         return (FAILURE_ART_HOMING);
      } else {
         rangeArray[1] = RT_Path->rangeMax;
         RT_Path->dEldRange = (elevArray[0] - elevArray[1]) / (rangeArray[0] - rangeArray[1]);
         elevTest = elevArray[1] + RT_Path->dEldRange * (rangeHoming - rangeArray[1]);

         if (fabs(rangeHoming - RT_Path->rangeMax) > HOMING_TOLERANCE) {
            if (verbose == VERBOSE_LEVEL2) {
               printf (" broke the tolerance dEldRange = %lf %lf\n",
                                     RT_Path->dEldRange, RT_Path->dEldRange/deg2rad);
               printf (" elevTest: %lf new %lf\n",elevTest, elevTest/deg2rad);
            }
            if (POET_Homing_Check (RT_Path, frequency, radialBottom, elevTest,
                               numberTraces, QP_Model, VERBOSE_LEVEL0) == EXIT_IONOSPHERE) {
               printf (" WARNING: This condition should never exists!\n");
               printf (" Lost the earlier solution\n");
               return (FAILURE_ART_HOMING);
            } else {
//               printf (" New set of values %lf\n",RT_Path->rangeMax);
               rangeArray[1] = RT_Path->rangeMax;
               elevArray[1]  = elevTest;
            }
         }
      }
   }

   status = POET_Homing_CloseOut (RT_Path, rangeHoming, *numberTraces,
                          elevArray, rangeArray, (double *)(NULL), "1st", verbose);

   return (SUCCESS_ART_HOMING);

}

/*
 *****************************************************************************
 *
 *
 *
 *****************************************************************************
 */

int POET_Homing_FitPos (struct ray_trace_def_t *RT_Path, double frequency,
                       double radialBottom, int propagationType, int *numberTraces,
                       double rangeHoming, double *elevArray, double *rangeArray,
                       struct qps_model_profile_t *QP_Model, int verbose)
{
   int    status     = SUCCESS_ART_SEGMENT;
   double elevTest   = 0.0;
   double deg2rad    = M_PI / 180.0;

   double coeffArray[3] = {0.0, 0.0, 0.0};


//   printf (" Should have a set of three to work with\n");

   if (elevArray[0] - elevArray[2] < 4.0 * deg2rad) {
//    printf (" Spread should be good for fit.\n");

      Parabolic_Fit (rangeArray, elevArray, 3, coeffArray);
//    printf (" CoeffL %lf %lf %lf\n",coeffArray[0], coeffArray[1],coeffArray[2]);

      elevTest = coeffArray[2] * rangeHoming * rangeHoming +
                 coeffArray[1] * rangeHoming +
                 coeffArray[0];
//    printf (" Guess Elev %lf\n",elevTest/deg2rad);

      if (POET_Homing_Check (RT_Path, frequency, radialBottom, elevTest,
                            numberTraces, QP_Model, VERBOSE_LEVEL0) == EXIT_IONOSPHERE) {
         printf (" FAILURE: Should not happen if the first point didnt exit\n");
         status = FAILURE_ART_HOMING;
      } else {

         status = POET_Homing_CloseOut (RT_Path, rangeHoming, *numberTraces,
                                   elevArray, rangeArray, coeffArray, "Fit", verbose);
         status = HOMING_COMPLETE_CLOSE;
      }
   } else {
//    printf (" Try to bisect upper or lower region to get spread down\n");
      if (rangeArray[1] < rangeHoming) {
//       printf (" Middle is a better upper elevation\n");
         elevArray[0]  = elevArray[1];
         rangeArray[0] = rangeArray[1];
         elevArray[1]  = (elevArray[0] + elevArray[2]) / 2.0;
         rangeArray[1] = 0.0;
         status = HOMING_LOADMIDDLE;
      } else {
//       printf (" Middle is a better lower elevation\n");
         elevArray[2]  = elevArray[1];
         rangeArray[2] = rangeArray[1];
         elevArray[1]  = (elevArray[0] + elevArray[2]) / 2.0;
         rangeArray[1] = 0.0;
         status = HOMING_LOADMIDDLE;
      }
   }

   return (status);
}
 
/*
 *-----------------------------------------------------------------------------
 *
 *
 *
 *-----------------------------------------------------------------------------
 */

double POET_Homing_GroupDelay (struct ray_trace_def_t *RT_Path, int compLevel)
{
   int index = 0;

   double lenValue  = 0.0;
   double rangeSq   = RT_Path->rangeMax * RT_Path->rangeMax;
   double heightSq  = RT_Path->apogeeHeight * RT_Path->apogeeHeight;
   double quadValue = rangeSq + 16.0 * heightSq;
/*
 * Simple method of two point for parabolic definition of length.
 */

   if (compLevel == GROUP_DELAY_SIMPLE) {
      lenValue = 0.5 * sqrt (quadValue) + (rangeSq / (8.0 * RT_Path->apogeeHeight)) *
               log ((4.0 * RT_Path->apogeeHeight + sqrt (quadValue)) / RT_Path->rangeMax);
   }

   return (lenValue);
}

/*
 *-----------------------------------------------------------------------------
 *
 *
 *
 *-----------------------------------------------------------------------------
 */

double POET_Homing_Spread (struct ray_trace_def_t *RT_Path) 
{
   double deg2rad     = M_PI / 180.0;

   double deltaRange  = 0.0;
   double effectRange = 0.0;
   double spreadLoss  = 0.0;

   if (RT_Path->dEldRange != 0.0) {
/*
 * Note to reader: delta_Elevation/delta_GroundRange is negative since the elevation 
 *    increases and the ground range will decrease.  Below has a negative applied to the
 *    elevation increment selected of 0.1 degrees
 */
      deltaRange = (-0.1 * deg2rad) / RT_Path->dEldRange; // Use 0.1 degree elevation
   }
/*
 * Define the new center for the ray projection based on the delta elevation
 *    Approach obtained from AFCAP Python.
 */
   effectRange = MEAN_RADIUS_EARTH * (sin (2.0 * theta_angle (RT_Path->rangeMax + deltaRange)) + 
                                      sin (2.0 * theta_angle (RT_Path->rangeMax - deltaRange))) / 2.0;

   spreadLoss = deltaRange * (0.1 * deg2rad) * effectRange;

   return (spreadLoss);
}

/*
 *-----------------------------------------------------------------------------
 *
 *
 *
 *-----------------------------------------------------------------------------
 */

int POET_Homing_CloseOut (struct ray_trace_def_t *RT_Path, double rangeHoming, 
                          int numberTraces, double *elevArray, double *rangeArray, 
                          double *coeffArray, char *labelString, int verbose)
{
   int status = SUCCESS_ART_HOMING;

   double deg2rad = M_PI / 180.0;

   if (strncmp(labelString, "Fit", 3) == 0) {
/*
 * Direct solution from the ground range fit
 */
      RT_Path->dEldRange    = (2.0 * coeffArray[2] * rangeHoming + coeffArray[1]);
   } else {
/*
 * Solution from delta ground range steps.
 */
      RT_Path->dEldRange = (elevArray[0] - elevArray[1]) / (rangeArray[0] - rangeArray[1]);
   }
   RT_Path->groupPath    = POET_Homing_GroupDelay (RT_Path, GROUP_DELAY_SIMPLE);
   RT_Path->spreadLoss   = POET_Homing_Spread (RT_Path);
   RT_Path->numTraceRuns = numberTraces;

   if (fabs(rangeHoming - RT_Path->rangeMax) > HOMING_TOLERANCE) {
      printf (" WARNING: Wrong elevation or an improbable distance\n");
   }

   printf ("--- Homing Result %s (steps %2d) %6.1lf %6.1lf %4.1lf ",
                   labelString, numberTraces, rangeHoming, RT_Path->rangeMax,
                   fabs(rangeHoming - RT_Path->rangeMax));
   printf ("Freq: %4.1lf El: %4.1lf ", RT_Path->frequency, RT_Path->beta0/deg2rad);
   printf ("Apogee: %5.1lf P': %6.1lf Sl: %5.1lf\n", RT_Path->apogeeHeight,
                                      RT_Path->groupPath, RT_Path->spreadLoss);

   return (status);

}

