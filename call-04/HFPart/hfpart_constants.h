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

#ifndef _HFPART_CONSTANTS_H_

#define VERBOSE_LEVEL0                0
#define VERBOSE_LEVEL1                1
#define VERBOSE_LEVEL2                2

#define HZ_TO_MHZ                     1.0E-6
#define PLASMA_FREQUENCY_TO_NE        1.24E10
#define NE_M3_TO_PLASMA_FREQUENCY     8.978659167     // Constant for m-cubed to Hz
#define NE_CM3_TO_PLASMA_FREQUENCY    0.008978659167  // Constant for cm-cubed to Hz
#define OPTIMUM_WORK_FREQ_PERCENT     0.85
#define INDEX_REFRACTION_PLASMA      80.616

#define MEAN_RADIUS_EARTH          6370.000
#define MINIMUM_HMF_HEIGHT          200.000
#define MINIMUM_HMF_RADIAL         6570.000           // 200 km height 
#define MINIMUM_HME_HEIGHT           90.000
#define MINIMUM_HME_RADIAL         6460.000           //  90 km height
#define MAXIMUM_HME_HEIGHT          110.000
#define MAXIMUM_HME_RADIAL         6480.000           // 110 km height

double height_to_radial (double profHeight);

double radial_to_height (double profRadial);

float  indexRefraction  (float rayFreq, float density);

double gamma_angle      (double elevation, double radial_height);

double phi0_angle       (double theta, double height);

double theta_angle      (double rangeDistance);

double fvert_to_fob     (double phi0, double freqVert);

double fob_to_fvert     (double phi0, double freqOblique);

double beta_to_range    (double beta, double radial_height);

double rangeHt_to_elev  (double range, double height);

float  OWF_for_MUF      (float freqMUF);

float  elevation_MUF    (float freqMUF, float freqCritical);

float  fp_to_MUF        (float criticalFreq, float rayElev);

double fp_to_Ne         (double plasmaFreq);

double Ne_to_fp         (double density);

double Ne_cm3_to_fp     (double density);

#endif
