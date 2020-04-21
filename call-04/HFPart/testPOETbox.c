#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <math.h>

#include "hfpart_constants.h"
#include "QPSegment.h"
#include "QPS_Model.h"
#include "RayTrace.h"
#include "spline.h"

int RayTrace_Interpolate (struct ray_trace_def_t *RT_Path, int verbose);

int main (int argc, char **argv)
{
   int index = 0;
   int index2 = 0;

   double h_prof[55] = {
      60,  70,  80,  90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220,
     230, 240, 250, 260, 270, 280, 290, 300, 310, 320, 330, 340, 350, 360, 370, 380, 390,
     400, 410, 420, 430, 440, 450, 460, 470, 480, 490, 500, 510, 520, 530, 540, 550, 560,
     570, 580, 590, 600
     };

   double ne_prof[55] = {
    -1.0000E+00, 4.0832E+07, 3.3141E+08, 3.0278E+09, 1.3428E+10, 1.4140E+10, 1.0666E+10,
     1.0703E+10, 1.4163E+10, 1.7500E+10, 2.2089E+10, 2.8963E+10, 4.2184E+10, 7.1019E+10,
     1.0656E+11, 1.4410E+11, 1.7807E+11, 2.0393E+11, 2.1960E+11, 2.2585E+11, 2.2571E+11,
     2.2190E+11, 2.1520E+11, 2.0634E+11, 1.9598E+11, 1.8472E+11, 1.7304E+11, 1.6133E+11,
     1.4987E+11, 1.3885E+11, 1.2840E+11, 1.1860E+11, 1.0948E+11, 1.0105E+11, 9.3284E+10,
     8.6160E+10, 7.9638E+10, 7.3679E+10, 6.8239E+10, 6.3275E+10, 5.8747E+10, 5.4615E+10,
     5.0843E+10, 4.7398E+10, 4.4249E+10, 4.1367E+10, 3.8728E+10, 3.6308E+10, 3.4085E+10,
     3.2043E+10, 3.0163E+10, 2.8431E+10, 2.6833E+10, 2.5356E+10, 2.3990E+10
     };

   int  edp_pts = 55;

   float elevation = 0.0;
   float frequency = 5.0;

   double deg2rad = M_PI / 180.0;
   double rad2deg = 180.0 / M_PI;

   double radialBottom   = 0.0;
   double rangeHoming    = 0.0;
   double testElev       = 0.0;

   double tempValue;
   double radial_tmax    = 0.0;

   int    propagationType  = 0;

   struct qps_model_profile_t QPModel;
   struct ray_trace_def_t RT_Path;
/*
 * Generate the QPS Model segments based on the provided data.
 */
   QPS_Model_Profile (h_prof, ne_prof, edp_pts, ELECTRON_DENSITY_M3, &QPModel);

/*
 * Diagnostic listing of the segments and not necessary for operations
 */
   QPS_Model_SegmentList (h_prof, ne_prof, edp_pts, &QPModel, VERBOSE_LEVEL0);

/*
 * Bottom Boundary of the defined ionosphere (Need to be careful with using
 *    really low bottoms with no real ionosphere available.  Using the QPS 
 *    bottom segment might be sufficient.  Another point is the lower segment
 *    might be defined already above the E-layer.
 *    Eq 2 & 3
 */
   radialBottom = QPModel.qps_segments[QPModel.numb_segments - 1].rValueLower - 5.0;

   for (rangeHoming = 300.0; rangeHoming < 3000.0; rangeHoming+=100.0) {

      for (frequency = 5.0; frequency < 29.0; frequency += 0.2) {

         RayTraceHoming (&RT_Path, (double)(frequency), radialBottom,
                         rangeHoming, SKIP_ELAYER, 
                         &propagationType, &QPModel, VERBOSE_LEVEL0);
         if (RT_Path.rayTraceFlag == EXIT_IONOSPHERE) {
//            printf (" End of Frequency Series - EXIT\n");
            frequency = 30.0;
         } else if (RT_Path.rayTraceFlag == MUF_FREQUENCY_LIMIT) {
//            printf (" End of Frequency Series - MUF\n");
            frequency = 30.0;
         } else if (RT_Path.rayTraceFlag == NO_PROPAGATE_HOMING) {
            frequency = 30.0;
         } else {
//            Output_RayTrace_Result (&RT_Path, VERBOSE_LEVEL2);
            RayTrace_Interpolate (&RT_Path, VERBOSE_LEVEL2);
         }
      }
   }
}

int RayTrace_Interpolate (struct ray_trace_def_t *RT_Path, int verbose)
{
   int index = 0;
   double *xValues = (double *)(NULL);
   double *yValues = (double *)(NULL);
   double *coefValues = (double *)(NULL);
   double height = 0.0;
   double grdRange = 0.0;
   int index_coef = 0;

   int numb_pnts = (int)(RT_Path->rangeMax / 5.0) + 1;

   xValues = (double *)(malloc (sizeof (double) * RT_Path->numPoints));
   yValues = (double *)(malloc (sizeof (double) * RT_Path->numPoints));
   coefValues = (double *)(malloc (sizeof (double) * RT_Path->numPoints * 7));
   
   for (index = 0; index < RT_Path->numPoints; index++) {
      xValues[index] = RT_Path->rayPoints[index].range;
      yValues[index] = RT_Path->rayPoints[index].height;
   }

   Relaxed_SplineXY (xValues, yValues, RT_Path->numPoints, coefValues);

   if (RT_Path->rayTraceFlag == APOGEE_DETECTED) {
      printf ("*** Frequency: %4.1lf Elevation: %4.1lf MaxRange: %6.1lf Apogee: %5.1lf\n",
               RT_Path->frequency, RT_Path->beta0 * 180.0 / M_PI, RT_Path->rangeMax,
               RT_Path->apogeeHeight);

   } else {
      printf ("*** Frequency: %4.1lf Elevation: %4.1lf MaxRange: %6.1lf\n",
               RT_Path->frequency, RT_Path->beta0 * 180.0 / M_PI, RT_Path->rangeMax);
   }  

   printf (" Number of Trace Points: %d\n",numb_pnts);

   index_coef = 0;
   for (index = 0; index < numb_pnts - 1; index++) {
      grdRange = index * 5.0;
      if (grdRange > xValues[index_coef + 1] && index_coef < RT_Path->numPoints) {
         index_coef++;
      }

      Solve_SplineXY (grdRange, &coefValues[index_coef*7], &height);
      printf (" Range: %6.1lf Height: %5.1lf %4d\n", grdRange, height, index);
   }
   printf (" Range: %6.1lf Height: %5.1lf\n", xValues[RT_Path->numPoints - 1], 
                                      yValues[RT_Path->numPoints - 1]);

   free (xValues);
   free (yValues);
   free (coefValues);

   return (0);
}