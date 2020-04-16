// Copyright (C) 2017 Systems & Technology Research, LLC.
// http://www.stresearch.com
//
// STR Proprietary Information
//
// US Government retains Unlimited Rights
// Non-Government Users – restricted usage as defined through
// licensing with STR or via arrangement with Government.
//
// In no event shall the initial developers or copyright holders be
// liable for any damages whatsoever, including - but not restricted
// to - lost revenue or profits or other direct, indirect, special,
// incidental or consequential damages, even if they have been
// advised of the possibility of such damages, except to the extent
// invariable law, if any, provides otherwise.
//
// The Software is provided AS IS with NO
// WARRANTY OF ANY KIND, INCLUDING THE WARRANTY OF DESIGN,
// MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

#ifndef iono_c_iface_h
#define iono_c_iface_h

#define EXPORT

extern "C"
{

///////////////////////////////////////////
////////// PYTHON TO C SIGNATURE //////////
///////////////////////////////////////////

  void igrfpharlap(float* glat,
                   float* glong,
                   float* dec_year,
                   float* height,
                   float* dipole_moment,
                   float* babs,
                   float* bnorth,
                   float* beast,
                   float* bdown,
                   float* dip,
                   float* dec,
                   float* dip_lat,
                   float* l_value,
                   int*   l_value_code);

//! @brief The iri call to FORTRAN, BC modifications
//! This is the IRI function that is modified by Dima
//!
//! @param[in]
//!
//! @param[out]
//!
  void iri2016bc(double* pfreq,
                 double* paramiri,
                 double* iy,
                 double* imd,
                 double* ihour,
                 double* xlat,
                 double* xlon,
                 double* xfoF2,
                 double* xhmF2,
                 double* xfoF1,
                 double* xfoE,
                 double* xB0,
                 double* xB1);

//! @brief The iri call to FORTRAN, PHARLAP modifications
//! This is the IRI function that is provided by Manuel
//!
//! @param[in]
//!
//! @param[out]
//!
  void iri2016pharlap(int*   jf,
                      int*   jmag,
                      float* glat,
                      float* glon,
                      int*   year,
                      int*   mmdd,
                      float* dhour,
                      float* heibeg,
                      float* heiend,
                      float* heistp,
                      float* outf,
                      float* oarr);

//! @brief The iri call to FORTRAN, PHARLAP modifications
//! This is the IRI function that is provided by Manuel
//!
//! @param[in] start_lat      - double - origin lat in decimal degrees
//! @param[in] start_long     - double - origin lon in decimal degrees
//! @param[in] start_height   - double - origin height in decimal km
//! @param[in] elevs          - double[] - initial elevation of rays in decimal degrees
//! @param[in] bearings       - double[] - initial bearing of rays in decimal degrees
//! @param[in] freqs          - double[] - carier frequency of the rays in MHz
//! @param[in] OX_mode        - int - {1 O mode, -1 X mode, 0 no field}
//! @param[in] nhops          - int - number of hops (??max??)
//! @param[in] step_size_min  - double - min step size sizes for ODE in KM
//! @param[in] step_size_max  - double - max step size sizes for ODE in KM
//! @param[in] tol            - double - tolerance for ODE
//! @param[in] ionosphere     - double[] -
//!
//! @param[out]
//!
  void raytrace3d(double* start_lat,
                  double* start_long,
                  double* start_height,
                  int*    num_rays,
                  double* elevs,
                  double* bearings,
                  double* freqs,
                  int*    OX_mode,
                  int*    nhops,
                  double* step_size_min,
                  double* step_size_max,
                  double* tol,
                  struct ionosphere_struct*   ionosphere,
                  struct geomag_field_struct* geomag_field,
                  double* ray_state_vec_in,
                  int*    return_ray_path_data,
                  int*    return_ray_state_vec,
                  double* ray_data,
                  double* ray_path_data,
                  int*    ray_label,
                  int*    nhops_attempted,
                  int*    npts_in_ray,
                  double* ray_state_vec_out,
                  double* elapsed_time);

////////////////////////////////////////////
////////// C TO FORTRAN SIGNATURE //////////
////////////////////////////////////////////


  EXPORT void igrf2016_calc_(float* glat,
                             float* glong,
                             float* dec_year,
                             float* height,
                             float* dipole_moment,
                             float* babs,
                             float* bnorth,
                             float* beast,
                             float* bdown,
                             float* dip,
                             float* dec,
                             float* dip_lat,
                             float* l_value,
                             int*   l_value_code);
        
// HNH: NOTE WE CANNOT HAVE IRIBC AND IRIPHARLAP AT THE SAME TIME
/*  EXPORT void iri2016bc_(double* pfreq,
                         double* paramiri,
                         double* iy,
                         double* imd,
                         double* ihour,
                         double* xlat,
                         double* xlon,
                         double* xfoF2,
                         double* xhmF2,
                         double* xfoF1,
                         double* xfoE,
                         double* xB0,
                         double* xB1); */

  EXPORT void iri2016_calc_(int*   jf,
                            int*   jmag,
                            float* glat,
                            float* glon,
                            int*   year,
                            int*   mmdd,
                            float* dhour,
                            float* heibeg,
                            float* heiend,
                            float* heistp,
                            float* outf,
                            float* oarr);

  EXPORT void raytrace_3d_(double* start_lat,
                           double* start_long,
                           double* start_height,
                           int*    num_rays,
                           double* elevs,
                           double* bearings,
                           double* freqs,
                           int*    OX_mode,
                           int*    nhops,
                           double* step_size_min,
                           double* step_size_max,
                           double* tol,
                           struct ionosphere_struct*   ionosphere,
                           struct geomag_field_struct* geomag_field,
                           double* ray_state_vec_in,
                           int*    return_ray_path_data,
                           int*    return_ray_state_vec,
                           double* ray_data,
                           double* ray_path_data,
                           int*    ray_label,
                           int*    nhops_attempted,
                           int*    npts_in_ray,
                           double* ray_state_vec_out,
                           double* elapsed_time);

} // extern C

#endif
