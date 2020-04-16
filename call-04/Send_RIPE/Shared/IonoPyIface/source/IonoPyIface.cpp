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

#include <iostream>
#include "../../Pharlap_4.2.0/headers/iono_structures_3d.h"
#include "IonoPyIface.h"

extern "C"
{
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
                   int*   l_value_code)
  {
#ifdef DEBUG_IGRF
    std::cout << "IGRF C input:" << std::endl;
    std::cout << " glat=" << *glat << ", glong=" << *glong << ", dec_year=" << *dec_year;
    std::cout << ", height=" << *height << std::endl;
#endif

    igrf2016_calc_(glat,
                   glong,
                   dec_year,
                   height,
                   dipole_moment,
                   babs,
                   bnorth,
                   beast,
                   bdown,
                   dip,
                   dec,
                   dip_lat,
                   l_value,
                   l_value_code);

#ifdef DEBUG_IGRF
    std::cout << "IGRF C output:" << std::endl;
    std::cout << " dipole_moment=" << *dipole_moment << ", babs=" << *babs << ", bnorth=" << *bnorth << std::endl;
    std::cout << " beast=" << *beast << ", bdown=" << *bdown << ", dip=" << *dip << ", dec=" << *dec << ", dip_lat=" << *dip_lat << std::endl;
#endif
  }

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
                 double* xB1)
  {
//    HNH: We are not planning to use this right now. It is incompatible with PHARLAP's IRI only IRI can exist
//
//    std::cout << "In C Interface; Calling iri2016bc with the following values: " << std::endl;
//    std::cout << "  iy:" << *iy << " imd:" << *imd << " ihour:" << *ihour << std::endl;
//    std::cout << "  xlat:" << *xlat << " xlon:" << *xlon << std::endl;
//    std::cout << "  xfoF2:" << *xfoF2 << " xhmF2:" << *xhmF2 << " xfoF1:" << *xfoF1 << " xfoE:" << *xfoE << std::endl;
//    std::cout << "  xB0:" << *xB0 << " xB1:" << *xB1 << std::endl;
//
//    iri2016bc_(pfreq,
//               paramiri,
//               iy,
//               imd,
//               ihour,
//               xlat,
//               xlon,
//               xfoF2,
//               xhmF2,
//               xfoF1,
//               xfoE,
//               xB0,
//               xB1);
  } // iri2016bc 

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
                      float* oarr)
  {
#ifdef DEBUG_IRI
    std::cout << "IRI C input:" << std::endl;
    std::cout << " jmag=" << *jmag << ", glat=" << *glat << ", glon=" << *glon << std::endl;
    std::cout << " year=" << *year << ", mmdd=" << *mmdd << ", dhour=" << *dhour << std::endl;
    std::cout << " heibeg=" << *heibeg << ", heiend=" << *heiend << ", heistp=" << *heistp << std::endl;
    std::cout << " jf=";
    for (int jj = 0; jj < 50; ++jj)
    {
      std::cout << jf[jj] << ", ";
    }
    std::cout << std::endl;
#endif

    iri2016_calc_(jf,
                  jmag,
                  glat,
                  glon,
                  year,
                  mmdd,
                  dhour,
                  heibeg,
                  heiend,
                  heistp,
                  outf,
                  oarr);

#ifdef DEBUG_IRI
    std::cout << "IRI C output:" << std::endl;
    std::cout << " foF2=" << oarr[0] << ", hmF2=" << oarr[1] << ", foF1=" << oarr[2];
    std::cout << ", foE=" << oarr[4] << ", B0=" << oarr[9] << ", B1=" << oarr[34] << std::endl;
#endif
  } // iri2016_pharlap

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
                  double* elapsed_time)
  {
    // Set the structs
    //
    raytrace_3d_(start_lat,
                 start_long,
                 start_height,
                 num_rays,
                 elevs,
                 bearings,
                 freqs,
                 OX_mode,
                 nhops,
                 step_size_min,
                 step_size_max,
                 tol,
                 ionosphere,
                 geomag_field,
                 ray_state_vec_in,
                 return_ray_path_data,
                 return_ray_state_vec,
                 ray_data,
                 ray_path_data,
                 ray_label,
                 nhops_attempted,
                 npts_in_ray,
                 ray_state_vec_out,
                 elapsed_time);
  }

}
