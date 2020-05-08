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

#ifndef _QPS_SEGMENT_H_ 

#define SUCCESS_QPS_SEGMENT  0
#define FAILURE_QPS_SEGMENT -1
#define FAILURE_QPS_MODEL   -2

#define PASSED_RMS_TOL_TEST  0
#define FAILED_RMS_TEST     -9
#define FAILED_TOL_TEST    -19

#define MAX_MHZ_ERROR      0.1
#define PERCENT_FP_ERROR  0.05
#define MAX_QPS_SEGMENTS    50

struct qps_definition_t {
   double capA;
   double capB;
   double capC;

   double italA;
   double italB;
   double italC;
   double denom_quad;

   float  rValueLower;
   float  yValueLower;

   float  rValueUpper;
   float  yValueUpper;

   int    nFitPts;
};

struct qps_model_profile_t {
   float  latitude;
   float  elevation;
   double hmeProfile;
   double foeProfile;
   double hmf2Profile;
   double fof2Profile;
   int    numb_segments;
   struct qps_definition_t qps_segments[MAX_QPS_SEGMENTS];
};


int    QP_LSq_Segment   (double *rValues, double *yValues, int nFitPts, 
                         double rInitial, double yInitial, double dydr,
                         double *capA, double *capB, double *capC);

double QPS_Solve_Fn2    (double capA, double capB, double capC, double rValue);

double QPS_Solve_X      (double capA, double capB, double capC, double rValue);

double QPS_Gradient     (double *rValues, int nFitPts, double capA, double capB);

int    QPS_RTrace_Coef  (float frequency, float beta, float r0base,
                         double capA, double capB, double capC,
                         double *italA, double *italB, double *italC);

double QPS_RTrace_Quad  (double italA, double italB, double italC);

double QPS_Start_dydr   (double capA, double capB, double rValue);

double QPS_Start_yValue (double capA, double capB, double capC, double rValue);

int    QPS_Compare      (double *rValues, double *yValues, double *fpValues,
                         int nFitPts, double perError, double maxMHz, 
                         double capA, double capB, double capC);

#endif
