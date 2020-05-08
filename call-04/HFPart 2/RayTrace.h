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

#ifndef _RAYTRACE_H_

#define SUCCESS_ART_SEGMENT    0
#define FAILURE_ART_SEGMENT   -1

#define SUCCESS_ART_HOMING     0
#define FAILURE_ART_HOMING    -2

#define SEGMENT_LOWER_BOUNDARY 0
#define SEGMENT_UPPER_BOUNDARY 1

#define HOMING_COMPLETE_CLOSE  9 
#define HOMING_FIT_RESULTS    10
#define HOMING_LOADFIRST      12
#define HOMING_LOADMIDDLE     13
#define HOMING_LOADLAST       14
#define HOMING_RELOADFIRST    15
#define HOMING_NO_PROPAGATION 16

#define UPLEG_RAYTRACE        17
#define DOWNLEG_RAYTRACE     -17

#define APOGEE_SEARCH         18
#define APOGEE_DETECTED       19
#define APOGEE_SEGMENT        20

#define ELAYER_RAY_PROP       21
#define FLAYER_RAY_PROP       22
#define LOW_RAY_PROP          23
#define HIGH_RAY_PROP         24

#define EXIT_IONOSPHERE       25
#define MUF_FREQUENCY_LIMIT   26
#define NO_CONVERGE_HOMING    27
#define NO_PROPAGATE_HOMING   28

#define SKIP_ELAYER           29
#define NEXT_PROPLAYER        30

#define GROUP_DELAY_FULL      31
#define GROUP_DELAY_FIT       32
#define GROUP_DELAY_SIMPLE    33

#define HOMING_TOLERANCE      10.0
#define MAX_HOMING_TRACES     15

/*
 * Caution with this since it should be greater than the number of QPS 
 *    Segments, since segments are the points used to define the ray path points
 */
#define MAX_RT_POINTS        100  

struct ray_path_def_t {
   double range;
   double height;
   double gammaSegment;
   double rangeUiMLi;
};

struct ray_trace_def_t {
   double frequency;        // Transmit frequency
   double beta0;            // Equivalent to launched elevation 
   double gammaBottom;      // Angle at bottom of ionosphere
   double radialBottom;     // Radial distance to the ionosphere bottom
   double rangeBottom;      // Range to the ionosphere bottom
   double apogeeRange;      // Radial distance to the ray path apogee
   double apogeeHeight;     // Height to the ray path apogee
   double rangeMax;         // Total ground range distance for ray path
   double dEldRange;        // Change in Elevation with respect to Ground Range
   double groupPath;        // Simple estimate of the ray path length
   double spreadLoss;       // Simple estimate for the ray projection at receiver
   int    numPoints;        // Number of points in the ray path
   int    rayTraceFlag;     // Flag (see above) for ray propagation
   int    numTraceRuns;     // Counter of number of ray traces calls performed
   struct ray_path_def_t rayPoints[MAX_RT_POINTS];
};


int    Solve_BoundaryIntegral (struct qps_definition_t *QPS_Segment, 
                            double lowerBound, double upperBound, double rayRadial,
                            double *integralUpper, double *integralLower,
                            int apogeeFlag);

int    Solve_Apogee_Upper  (double italC, double denom_quad, double *integralValue);

int    Boundary_NegC       (double italA, double italB, double italC, double denom_quad,
                            double rValue, double *integralValue);

int    Boundary_PosC       (double italA, double italB, double italC, double denom_quad,
                            double rValue, double xValue, int boundaryFlag,
                            double *integralValue, double *partialLogValue);

double Ray_ApogeeRadial    (struct qps_definition_t *QPS_Segment);

double GrndRangeTraveled   (double beta, double radialBase, double integralUiMLi);

int    RayTrace_UpLeg_Portion (struct qps_model_profile_t *QPModel,
                            struct ray_trace_def_t     *RT_Path,
                            double gammaBottom, double radialBottom, 
                            double rangeBottom, double *strtRadial,
                            int *rayDirection, double *integralUiMLi, double *rangeIono);

int    RayTrace_DownLeg_Portion (struct qps_model_profile_t *QPModel,
                            struct ray_trace_def_t     *RT_Path,
                            double gammaBottom, double radialBottom,
                            double rangeBottom, double *strtRadial,
                            int *rayDirection, double *integralUiMLi, double *rangeIono);

int    Output_RayTrace_Result (struct ray_trace_def_t *RT_Path, int verbose);

int    RayTracePath        (struct ray_trace_def_t *RT_Path, double frequency,
                            double elevation, double radialBottom,
                            struct qps_model_profile_t *QP_Model, int verbose);

int    RayTraceHoming      (struct ray_trace_def_t *RT_Path, double frequency,
                            double radialBottom, double rangeHoming, 
                            int skipElayer, int *propagationType,
                            struct qps_model_profile_t *QP_Model, int verbose);

int    Parabolic_Fit       (double *xValues, double *yValues, int nptsFit, double *coeff);

#endif
