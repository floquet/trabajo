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

#ifndef _QPS_MODEL_H_

#define SUCCUSS_QPS_MODEL     0
#define FAILED_QPS_MODEL     -1

#define OPT_FIT_POINTS        4
#define PLASMA_FREQUENCY      0x0FED
#define ELECTRON_DENSITY      0x00ED
#define ELECTRON_DENSITY_CM3  0x0ED3
#define ELECTRON_DENSITY_M3   0x0ED6

int    QPS_Model_Profile     (double *profHeight, double *profValues, int num_pts, int dataType,
                              struct qps_model_profile_t *QPModel);

int    QPS_Model_SegmentList (double *profHeight, double *profValues, int num_pts, 
                              struct qps_model_profile_t *QPModel, int verbose);

int    Build_RayTrace_Coeff  (struct qps_model_profile_t *QP_Model, double elevation,
                              double frequency);

double Max_ApogeeHeight      (double capB, double capC, double frequency);

double Max_Height4Distance   (double groundRange);

double Max_Elevation4Homing  (double groundRange, double hmProfile, double foProfile,
                              double frequency);

#endif
