/*
 ***********************************************************************
 *
 * $Id: spline.c,v 1.1.1.1 2011/05/23 20:12:03 bdrummon Exp $
 *
 ***********************************************************************
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <limits.h>

#include <math.h>
#include "spline.h"
/*
 *******
 *
 * Coded from Mathematical Elements for Computer Graphics, 
 *                David F. Rogers & J. Alan Adams.
 * 
 *
 * Nelson Bonito Radex Inc October 2003
 *
 *******
 */

int Relaxed_Spline2D (double *xpoints, double *ypoints, int numb_pnts,
                      double *coef)
{
   int index;
   double *coef_ptr;
   static int last_memset = 0;
   static struct spline_element_t *RSpline2d = 
                                     (struct spline_element_t *)(NULL);

   int SplineEndPoint2D (int init_mode, int end_mode,
                      struct spline_element_t *RSpline2d, int numb_pnts);
   int SplineGauss2D (struct spline_element_t *RSpline2d, int numb_pnts);
   int SplineCoeff2D (struct spline_element_t *RSpline2d, int numb_pnts);

/*
 * Save the memory from previous allocations to prevent the needless
 *    tasking of the memory allocation process (risky if done wrong)
 */

   if (last_memset != numb_pnts) {
      if (last_memset) {
         free (RSpline2d);
         }
      last_memset = numb_pnts;
      RSpline2d = (struct spline_element_t *)
                  (malloc (sizeof (struct spline_element_t) * numb_pnts));
      }
   
   for (index = 0; index < numb_pnts; index++) {
/* 
 * Load input data into local structure for processing.
 */
      RSpline2d[index].xdata = xpoints[index];
      RSpline2d[index].ydata = ypoints[index];
      }

/*
 * Generate chord lengths and elements in the B, U and M matrices
 *    which depend upon the specified end conditions
 */

   SplineEndPoint2D (RELAXED, RELAXED, RSpline2d,  numb_pnts);

   SplineGauss2D (RSpline2d, numb_pnts);

   SplineCoeff2D (RSpline2d, numb_pnts);

   coef_ptr = coef;
   for (index = 0; index < numb_pnts - 1; index++) {
      *coef_ptr       = RSpline2d[index].xdata;
      *(coef_ptr + 1) = RSpline2d[index].ydata;
      coef_ptr += 2;
      *coef_ptr       = RSpline2d[index].tanvector[0];
      *(coef_ptr + 1) = RSpline2d[index].tanvector[1];
      coef_ptr += 2;
      *coef_ptr       = RSpline2d[index].pdotvector[0];
      *(coef_ptr + 1) = RSpline2d[index].pdotvector[1];
      coef_ptr += 2;
      *coef_ptr       = RSpline2d[index].p2dotvector[0];
      *(coef_ptr + 1) = RSpline2d[index].p2dotvector[1];
      coef_ptr += 2;
      *coef_ptr       = RSpline2d[index].cordlen;
      *(coef_ptr + 1) = RSpline2d[index].delta_x;
      *(coef_ptr + 2) = RSpline2d[index].delta_y;
      coef_ptr += 3;
      }
/*
   for (index = 0; index < numb_pnts; index++) {
      printf (" X = %.3lf Y = %.3lf Cord = %.3lf U = %.3lf  %.3lf %.3lf\n",
          RSpline2d[index].xdata, RSpline2d[index].ydata,
          RSpline2d[index].cordlen, 
          RSpline2d[index].tanvector[0],
          RSpline2d[index].tanvector[1], RSpline2d[index].tanvector[2]);
      }
 */
}

/*
 *******
 *
 *
 * Nelson Bonito Radex Inc October 2003
 *
 *******
 */

int Relaxed_SplineXY (double *xpoints, double *ypoints, int numb_pnts,
                      double *coef)
{
   int index;
   double *coef_ptr;
   static int last_memset = 0;
   static struct spline_element_t *RSplineXY =
                                     (struct spline_element_t *)(NULL);

   int SplineEndPointXY (int init_mode, int end_mode,
                      struct spline_element_t *RSplineXY, int numb_pnts);
   int SplineGaussXY (struct spline_element_t *RSplineXY, int numb_pnts);
   int SplineCoeffXY (struct spline_element_t *RSplineXY, int numb_pnts);

/*
 * Save the memory from previous allocations to prevent the needless
 *    tasking of the memory allocation process (risky if done wrong)
 */

   if (last_memset != numb_pnts) {
      if (last_memset) {
         free (RSplineXY);
         }
      last_memset = numb_pnts;
      RSplineXY = (struct spline_element_t *)
                  (malloc (sizeof (struct spline_element_t) * numb_pnts));
      }

   for (index = 0; index < numb_pnts; index++) {
/*
 * Load input data into local structure for processing.
 */
      RSplineXY[index].xdata = xpoints[index];
      RSplineXY[index].ydata = ypoints[index];
      }
/*
 * Generate chord lengths and elements in the B, U and M matrices
 *    which depend upon the specified end conditions
 */

   SplineEndPointXY (RELAXED, RELAXED, RSplineXY,  numb_pnts);

   SplineGaussXY (RSplineXY, numb_pnts);

   SplineCoeffXY (RSplineXY, numb_pnts);

   coef_ptr = coef;
   for (index = 0; index < numb_pnts - 1; index++) {
      *coef_ptr       = RSplineXY[index].xdata;
      *(coef_ptr + 1) = RSplineXY[index].ydata;
      *(coef_ptr + 2) = RSplineXY[index].tanvector[1];
      *(coef_ptr + 3) = RSplineXY[index].pdotvector[1];
      *(coef_ptr + 4) = RSplineXY[index].p2dotvector[1];
      *(coef_ptr + 5) = RSplineXY[index].cordlen;
      *(coef_ptr + 6) = RSplineXY[index].delta_x;
      coef_ptr += 7;
      }
}

/*
 *******
 *
 *
 * Nelson Bonito Radex Inc October 2003
 *
 *******
 */

int SplineEndPoint2D (int init_mode, int end_mode, 
                      struct spline_element_t *RSpline2d, int numb_pnts)
{
   int index;
   int end_pnt;
   double xdata, ydata, cord;
   struct spline_element_t *RSpline2d_ptr;

   int SplineSetEndConds (int first_last, int mode,
                       struct spline_element_t *RorC_Spline);

/*
 * Set up first row of M matrix for initial condition
 *    M matrix is represented as a tri-diagonal with index 0 = a[N],
 *    index 1 = b[N], and 2 = c[N]. The need for index 3 is to address
 *    the Gauss Elimination method used to solve for a normal diagonal
 */

   SplineSetEndConds (FIRST_POINT, init_mode, &RSpline2d[0]);

/*
 * Set up last row of M matrix for end condition
 */

   end_pnt = numb_pnts - 1;
   SplineSetEndConds (LAST_POINT, end_mode, &RSpline2d[end_pnt]);

/*
 * Determine the cord length between xy pairs.
 */

   for (index = 0; index < end_pnt; index++) {
      RSpline2d[index].delta_x = 
                 xdata = RSpline2d[index + 1].xdata - RSpline2d[index].xdata;
      RSpline2d[index].delta_y = 
                 ydata = RSpline2d[index + 1].ydata - RSpline2d[index].ydata;
      cord = (xdata * xdata + ydata * ydata);
      RSpline2d[index].cordlen = (cord == 0) ? 0.0 : sqrt(cord);
      }
/*
 * Set B for the relaxed initial (x, y components) Eq. 5.38
 */
   RSpline2d[0].bdata[2] = 0.0;
   if (init_mode == RELAXED) {
      cord = (3.0 / (2.0 * RSpline2d[0].cordlen));
      RSpline2d[0].bdata[0] = cord *
                              (RSpline2d[1].xdata - RSpline2d[0].xdata);
      RSpline2d[0].bdata[1] = cord *
                              (RSpline2d[1].ydata - RSpline2d[0].ydata);
      }
   else {
/*
 * Set B to U (tangent) for clamped initial (x, y components) 
 */
      RSpline2d[0].bdata[0] = RSpline2d[0].tanvector[0];
      RSpline2d[0].bdata[1] = RSpline2d[0].tanvector[1];
      }

/*
 * Set B for the relaxed end (x, y components) Eq. 5.39
 */
   RSpline2d[end_pnt].bdata[2] = 0.0;  
   if (end_mode == RELAXED) {
      cord = (6.0 / RSpline2d[end_pnt - 1].cordlen);
      RSpline2d[end_pnt].bdata[0] = cord *
                    (RSpline2d[end_pnt].xdata - RSpline2d[end_pnt - 1].xdata);
      RSpline2d[end_pnt].bdata[1] = cord *
                    (RSpline2d[end_pnt].ydata - RSpline2d[end_pnt - 1].ydata);
      }
   else {
/*
 * Set B to U (tangent) for clamped end (x, y components) 
 */
      RSpline2d[end_pnt].bdata[0] = RSpline2d[end_pnt].tanvector[0];
      RSpline2d[end_pnt].bdata[1] = RSpline2d[end_pnt].tanvector[1];
      }

}
/*
 *******
 *
 *
 * Nelson Bonito Radex Inc October 2003
 *
 *******
 */

int SplineEndPointXY (int init_mode, int end_mode,
                      struct spline_element_t *RSplineXY, int numb_pnts)
{
   int index;
   int end_pnt;
   double xdata, ydata, cord;
   struct spline_element_t *RSplineXY_ptr;

   int SplineSetEndConds (int first_last, int mode,
                       struct spline_element_t *RorC_Spline);

/*
 * Set up first row of M matrix for initial condition
 *    M matrix is represented as a tri-diagonal with index 0 = a[N],
 *    index 1 = b[N], and 2 = c[N]. The need for index 3 is to address
 *    the Gauss Elimination method used to solve for a normal diagonal
 */

   SplineSetEndConds (FIRST_POINT, init_mode, &RSplineXY[0]);

/*
 * Set up last row of M matrix for end condition
 */
   end_pnt = numb_pnts - 1;
   SplineSetEndConds (LAST_POINT, end_mode, &RSplineXY[end_pnt]);

/*
 * Determine the cord length between xy pairs.
 */
   for (index = 0; index < end_pnt; index++) {
      RSplineXY[index].delta_x =
                 xdata = RSplineXY[index + 1].xdata - RSplineXY[index].xdata;
      RSplineXY[index].delta_y =
                 ydata = RSplineXY[index + 1].ydata - RSplineXY[index].ydata;
      cord = (xdata * xdata + ydata * ydata);
      RSplineXY[index].cordlen = (cord == 0) ? 0.0 : sqrt(cord);
      }
/*
 * Set B for the relaxed initial (x, y components) Eq. 5.38
 */
   if (init_mode == RELAXED) {
      cord = (3.0 / (2.0 * RSplineXY[0].cordlen));
      RSplineXY[0].bdata[1] = cord *
                              (RSplineXY[1].ydata - RSplineXY[0].ydata);

      }
   else {
/*
 * Set B to U (tangent) for clamped initial (x, y components)
 */
      RSplineXY[0].bdata[1] = RSplineXY[0].tanvector[1];
      }
/*
 * Set B for the relaxed end (x, y components) Eq. 5.39
 */
   if (end_mode == RELAXED) {
      cord = (6.0 / RSplineXY[end_pnt - 1].cordlen);
      RSplineXY[end_pnt].bdata[1] = cord *
                    (RSplineXY[end_pnt].ydata - RSplineXY[end_pnt - 1].ydata);
      }
   else {
/*
 * Set B to U (tangent) for clamped end (x, y components)
 */
      RSplineXY[end_pnt].bdata[1] = RSplineXY[end_pnt].tanvector[1];
      }
}

/*
 *******
 *
 *
 * Nelson Bonito Radex Inc October 2003
 *
 *******
 */

int SplineSetEndConds (int first_last, int mode, 
                       struct spline_element_t *RorC_Spline)
{

   RorC_Spline->ndata[3] = 0.0;

   if (mode == RELAXED) {
      if (first_last == 1) {
         RorC_Spline->ndata[0] = 0.0;
         RorC_Spline->ndata[1] = 1.0;
         RorC_Spline->ndata[2] = 0.5;
         }
      else {
         RorC_Spline->ndata[0] = 2.0;
         RorC_Spline->ndata[1] = 4.0;
         RorC_Spline->ndata[2] = 0.0;
         }
      }
   else if (mode == CLAMPED) {
      RorC_Spline->ndata[0] = 0.0;
      RorC_Spline->ndata[1] = 1.0;
      RorC_Spline->ndata[2] = 0.0;
      }
   else {
      printf ("Invalid End Data Point mode\n");
      exit(1);
      }

   return (0);
}
/*
 *******
 *
 *
 * Nelson Bonito Radex Inc October 2003
 *
 *******
 */

int SplineGaussXY (struct spline_element_t *RSplineXY, int numb_pnts)
{
   int index, indexm1;
   int kindex, kindexp1;
   double diag;
   int end_pnt;

   end_pnt = numb_pnts - 1;

   for (index = 1; index < end_pnt; index++) {
      indexm1 = index - 1;
/*
 * Create non-zero values for internal rows of M-matrix also need
 *    to set the outside tri-daigonal (index 3).
 */
      RSplineXY[index].ndata[0] = RSplineXY[index].cordlen;
      RSplineXY[index].ndata[1] = 2.0 *
                   (RSplineXY[index].cordlen + RSplineXY[indexm1].cordlen);
      RSplineXY[index].ndata[2] = RSplineXY[indexm1].cordlen;
      RSplineXY[index].ndata[3] = 0.0;
/*
 * Create rows 2 through n-1 of B-matrix Eq 5.26
 */
      RSplineXY[index].bdata[1] = (3.0 *
                 ((RSplineXY[indexm1].cordlen * RSplineXY[indexm1].cordlen) *
                  (RSplineXY[index + 1].ydata - RSplineXY[index].ydata) +
                  (RSplineXY[index].cordlen   * RSplineXY[index].cordlen) *
                  (RSplineXY[index].ydata     - RSplineXY[indexm1].ydata))) /
                  (RSplineXY[index].cordlen   * RSplineXY[indexm1].cordlen);
      }
/*
 * The following is the Guassian elimination process
 */
   for (index = 1; index < numb_pnts; index++) {
      indexm1 = index - 1;
/*
 * Normalize diagonal to previous right hand component
 */
      if (RSplineXY[index].ndata[0] != 0.0) {
         diag = RSplineXY[indexm1].ndata[1] / RSplineXY[index].ndata[0];
/*
 * Reduce by scaling and subtraction of the previous right hand component
 *    the goal is to get a[N] = 0 and b[N] = 1 with c[n] scaled to match
 */
         for (kindex = 0; kindex < 3; kindex++) {
            RSplineXY[index].ndata[kindex] = diag *
                                     RSplineXY[index].ndata[kindex] -
                                     RSplineXY[indexm1].ndata[kindex + 1];
            }
         RSplineXY[index].bdata[1] =diag * RSplineXY[index].bdata[1] -
                                           RSplineXY[indexm1].bdata[1];
/*
 * Normalize to get b[N] = 1 and the B matrix equivalent
 */
         diag = RSplineXY[index].ndata[1];
         for (kindex = 0; kindex < 3; kindex++) {
            RSplineXY[index].ndata[kindex] =
                                        RSplineXY[index].ndata[kindex] / diag;
            }
         RSplineXY[index].bdata[1] = RSplineXY[index].bdata[1] / diag;
         }

      }
/*
 * Since this is a Gauss Elimination the backward subtraction will need
 *    to start with the last point. Since the backward look would have
 *    tried to introduce a previous answer, the need to do the last
 *    separate from the loop.
 */

   RSplineXY[end_pnt].tanvector[1] = RSplineXY[end_pnt].bdata[1] /
                                     RSplineXY[end_pnt].ndata[1];

   for (index = 1; index < numb_pnts; index++) {
      RSplineXY[end_pnt - index].tanvector[1] =
                               (RSplineXY[end_pnt - index].bdata[1] -
                                RSplineXY[end_pnt - index].ndata[2] *
                                RSplineXY[end_pnt - index + 1].tanvector[1]) /
                                RSplineXY[end_pnt - index].ndata[1];
      }
}

/*
 *******
 *
 *
 * Nelson Bonito Radex Inc October 2003
 *
 *******
 */

int SplineGauss2D (struct spline_element_t *RSpline2d, int numb_pnts)
{
   int index, indexm1;
   int kindex, kindexp1;
   double diag;
   int end_pnt;

   end_pnt = numb_pnts - 1;

   for (index = 1; index < end_pnt; index++) {
      indexm1 = index - 1;
/*
 * Create non-zero values for internal rows of M-matrix also need
 *    to set the outside tri-daigonal (index 3).
 */
      RSpline2d[index].ndata[0] = RSpline2d[index].cordlen;
      RSpline2d[index].ndata[1] = 2.0 *
                   (RSpline2d[index].cordlen + RSpline2d[indexm1].cordlen);
      RSpline2d[index].ndata[2] = RSpline2d[indexm1].cordlen;
      RSpline2d[index].ndata[3] = 0.0;
/*
 * Create rows 2 through n-1 of B-matrix Eq 5.26
 */
      RSpline2d[index].bdata[0] = (3.0 * 
                 ((RSpline2d[indexm1].cordlen * RSpline2d[indexm1].cordlen) * 
                  (RSpline2d[index + 1].xdata - RSpline2d[index].xdata) +
                  (RSpline2d[index].cordlen * RSpline2d[index].cordlen) *
                  (RSpline2d[index].xdata - RSpline2d[indexm1].xdata))) /
                  (RSpline2d[index].cordlen * RSpline2d[indexm1].cordlen);

     RSpline2d[index].bdata[1] = (3.0 * 
                 ((RSpline2d[indexm1].cordlen * RSpline2d[indexm1].cordlen) * 
                  (RSpline2d[index + 1].ydata - RSpline2d[index].ydata) +
                  (RSpline2d[index].cordlen * RSpline2d[index].cordlen) *
                  (RSpline2d[index].ydata - RSpline2d[indexm1].ydata))) /
                  (RSpline2d[index].cordlen * RSpline2d[indexm1].cordlen);

      RSpline2d[index].bdata[2] = 0.0;
      }

/*
 * The following is the Guassian elimination process 
 */

   for (index = 1; index < numb_pnts; index++) {
      indexm1 = index - 1;
/*
 * Normalize diagonal to previous right hand component
 */
      if (RSpline2d[index].ndata[0] != 0.0) {
         diag = RSpline2d[indexm1].ndata[1] / RSpline2d[index].ndata[0];
/*
 * Reduce by scaling and subtraction of the previous right hand component
 *    the goal is to get a[N] = 0 and b[N] = 1 with c[n] scaled to match
 */
         for (kindex = 0; kindex < 3; kindex++) {
            RSpline2d[index].ndata[kindex] = diag *
                                     RSpline2d[index].ndata[kindex] -
                                     RSpline2d[indexm1].ndata[kindex + 1];

            RSpline2d[index].bdata[kindex] = diag *
                                     RSpline2d[index].bdata[kindex] -
                                     RSpline2d[indexm1].bdata[kindex];
            }
/*
 * Normalize to get b[N] = 1 and the B matrix equivalent 
 */
         diag = RSpline2d[index].ndata[1];
         for (kindex = 0; kindex < 3; kindex++) {
            RSpline2d[index].ndata[kindex] = 
                                        RSpline2d[index].ndata[kindex] / diag;
            RSpline2d[index].bdata[kindex] = 
                                        RSpline2d[index].bdata[kindex] / diag;
            }
         }
      }
/*
 * Since this is a Gauss Elimination the backward subtraction will need
 *    to start with the last point. Since the backward look would have
 *    tried to introduce a previous answer, the need to do the last 
 *    separate from the loop.
 */
   RSpline2d[end_pnt].tanvector[0] = RSpline2d[end_pnt].bdata[0] /
                                     RSpline2d[end_pnt].ndata[1];
   RSpline2d[end_pnt].tanvector[1] = RSpline2d[end_pnt].bdata[1] /
                                     RSpline2d[end_pnt].ndata[1];
   RSpline2d[end_pnt].tanvector[2] = RSpline2d[end_pnt].bdata[2] /
                                     RSpline2d[end_pnt].ndata[1];

   for (index = 1; index < numb_pnts; index++) {
      RSpline2d[end_pnt - index].tanvector[0] = 
                               (RSpline2d[end_pnt - index].bdata[0] -
                                RSpline2d[end_pnt - index].ndata[2] *
                                RSpline2d[end_pnt - index + 1].tanvector[0]) /
                                RSpline2d[end_pnt - index].ndata[1];
      RSpline2d[end_pnt - index].tanvector[1] = 
                               (RSpline2d[end_pnt - index].bdata[1] -
                                RSpline2d[end_pnt - index].ndata[2] *
                                RSpline2d[end_pnt - index + 1].tanvector[1]) /
                                RSpline2d[end_pnt - index].ndata[1];
      RSpline2d[end_pnt - index].tanvector[2] = 
                               (RSpline2d[end_pnt - index].bdata[2] -
                                RSpline2d[end_pnt - index].ndata[2] *
                                RSpline2d[end_pnt - index + 1].tanvector[2]) /
                                RSpline2d[end_pnt - index].ndata[1];
      }
}

/*
 *******
 *
 *
 * Nelson Bonito Radex Inc October 2003
 *
 *******
 */

int SplineCoeff2D (struct spline_element_t *RSpline2d, int numb_pnts)
{
   int index, indexp1;
   double l2temp, ltemp;

   for (index = 0; index < numb_pnts - 1; index++) {
      indexp1 = index + 1;
      l2temp  = RSpline2d[index].cordlen * RSpline2d[index].cordlen;
      ltemp   = 1.0 / RSpline2d[index].cordlen;

      RSpline2d[index].pdotvector[0] = (3.0 / l2temp) * 
                (RSpline2d[indexp1].xdata  - RSpline2d[index].xdata) -
                 ltemp  *  (RSpline2d[indexp1].tanvector[0] + 
                        2.0 * RSpline2d[index].tanvector[0]);

      RSpline2d[index].pdotvector[1] = (3.0 / l2temp) *
                (RSpline2d[indexp1].ydata  - RSpline2d[index].ydata) -
                 ltemp  *  (RSpline2d[indexp1].tanvector[1] + 
                        2.0 * RSpline2d[index].tanvector[1]);

      l2temp = l2temp * RSpline2d[index].cordlen;
      ltemp   = 1.0 / (RSpline2d[index].cordlen * RSpline2d[index].cordlen);

      RSpline2d[index].p2dotvector[0] = (-2.0 / l2temp) * 
                 (RSpline2d[indexp1].xdata  - RSpline2d[index].xdata) +
                  ltemp * (RSpline2d[indexp1].tanvector[0] +
                             RSpline2d[index].tanvector[0]);

      RSpline2d[index].p2dotvector[1] = (-2.0 / l2temp) * 
                 (RSpline2d[indexp1].ydata  - RSpline2d[index].ydata) +
                  ltemp * (RSpline2d[indexp1].tanvector[1] +
                             RSpline2d[index].tanvector[1]);
      }
}

/*
 *******
 *
 *
 * Nelson Bonito Radex Inc October 2003
 *
 *******
 */

int SplineCoeffXY (struct spline_element_t *RSplineXY, int numb_pnts)
{
   int index, indexp1;
   double l2temp, ltemp;

   for (index = 0; index < numb_pnts - 1; index++) {
      indexp1 = index + 1;
      l2temp  = RSplineXY[index].cordlen * RSplineXY[index].cordlen;
      ltemp   = 1.0 / RSplineXY[index].cordlen;

      RSplineXY[index].pdotvector[1] = (3.0 / l2temp) *
                (RSplineXY[indexp1].ydata  - RSplineXY[index].ydata) -
                 ltemp  *  (RSplineXY[indexp1].tanvector[1] +
                        2.0 * RSplineXY[index].tanvector[1]);

      l2temp = l2temp * RSplineXY[index].cordlen;
      ltemp   = 1.0 / (RSplineXY[index].cordlen * RSplineXY[index].cordlen);

      RSplineXY[index].p2dotvector[1] = (-2.0 / l2temp) *
                 (RSplineXY[indexp1].ydata  - RSplineXY[index].ydata) +
                  ltemp * (RSplineXY[indexp1].tanvector[1] +
                             RSplineXY[index].tanvector[1]);
      }
}

/*
 *******
 *
 *
 * Nelson Bonito Radex Inc October 2003
 *
 *******
 */

int Solve_Spline2D (double delta, double *coef, double *xres, double *yres)
{
   double delta2, delta3;

   delta2 = delta * delta;
   delta3 = delta2 * delta;
/*
 * Coef Roadmap 
 *     0,1 = original - x,y
 *     2,3 = tangent vector - x,y
 *     4,5 = P-dot at original - x,y
 *     6,7 = P-2dot at original - x,y
 *     8   = cordlength to next point. 
 *     9,10= delta to next point - x,y
 */
   *xres = coef[0] + coef[2] * delta + coef[4] * delta2 + coef[6] * delta3;
   *yres = coef[1] + coef[3] * delta + coef[5] * delta2 + coef[7] * delta3;

}
/*
 *******
 *
 *
 * Nelson Bonito Radex Inc October 2003
 *
 *******
 */

int Solve_SplineXY (double xpoint, double *coef, double *yres)
{
   double delta, delta2, delta3;

/*
 * Coef Roadmap
 *     0 = original - x
 *     1 = original - y
 *     2 = tangent at original - y
 *     3 = P-dot at original - y
 *     4 = P-2dot at original - y
 *     5 = cordlength to next point.
 *     6 = delta to next point - x
 */

   delta = ((xpoint - coef[0])/ coef[6]) * coef[5];

   delta2 = delta * delta;
   delta3 = delta2 * delta;

   *yres = coef[1] + coef[2] * delta + coef[3] * delta2 + coef[4] * delta3;

}
