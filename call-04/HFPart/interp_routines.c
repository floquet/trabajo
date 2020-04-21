#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <math.h>

#include <time.h>
#include "nc_ifm_proto.h"

#include "gaim_update_struct.h"
#include "gaim_update_proto.h"

#ifndef RTOD
#define RTOD            (180.0F/M_PI)
#endif

#define MAGNETIC_RADIUS  6371.0

#define METER_KM          0.001
#define MEAN_R_EARTH   6371.0

/*
 *******
 *
 *
 *
 *******
 */

int Interpolate_GAIM_Longitude (struct netcdf_data_t *gaim_data,
                                struct netcdf_data_t *ifm_data)
{
   int index;
   int index_alt, index_lat, index_lon;
   double *x_values, *y_values, *longitude_coef;
   double density_value;

   struct iono_profile_t *profile_ptr; 
/*
 * Assign necessary memory area for use in the Spline fitting of Longitude
 *    Using the wrap around for dealing with points crossing 0 longitude.
 */
   Initialize_CoordInterp (&x_values, &y_values, &longitude_coef,
                              gaim_data->longitudes, gaim_data->numb_lons, 1);

   x_values[0] = gaim_data->longitudes[gaim_data->numb_lons - 1] - 360.0;
   x_values[gaim_data->numb_lons + 1] = gaim_data->longitudes[0] + 360.0;
/*
 * By this point the grid is already re-populated with IFM based latitude 
 *    and longitude grid resolution reference.
 */
   for (index_alt = 0; index_alt < ifm_data->numb_alts; index_alt++) {
      for (index_lat = 0; index_lat < ifm_data->numb_lats; index_lat++) {
/*
 * Use a spline to compute the IFM longitude equivalent from the GAIM defined
 *    PQL to RLL longitude steps
 */
         for (index_lon = 0; index_lon < gaim_data->numb_lons; index_lon++) {
            profile_ptr = (gaim_data->grid_pnts[index_lat *
                                         gaim_data->numb_lons + index_lon]);
            y_values[index_lon + 1] = profile_ptr->edensity[index_alt];
            }

         profile_ptr = gaim_data->grid_pnts[index_lat * gaim_data->numb_lons +
                                               gaim_data->numb_lons - 1];
         y_values[0] = profile_ptr->edensity[index_alt];
         profile_ptr = gaim_data->grid_pnts[index_lat * gaim_data->numb_lons];
         y_values[gaim_data->numb_lons + 1] = profile_ptr->edensity[index_alt];

         Relaxed_SplineXY (&x_values[0], &y_values[0], gaim_data->numb_lons + 2,
                                                             longitude_coef);
/*
 * Need to populate the longitude index for the output IFM grid
 */
         for (index_lon = 0; index_lon < ifm_data->numb_lons; index_lon++) {
            profile_ptr = ifm_data->grid_pnts[index_lat *
                                         ifm_data->numb_lons + index_lon];
            if (ifm_data->longitudes[index_lon] < x_values[0]) {
               profile_ptr->edensity[index_alt] = 0.0;
               }
            else if (ifm_data->longitudes[index_lon] > 
                                       x_values[gaim_data->numb_lons + 1]) {
               profile_ptr->edensity[index_alt] = 0.0;
               }
            else {

               index = 0;
               while (index < gaim_data->numb_lons + 2) {
                  if (x_values[index+1] >= ifm_data->longitudes[index_lon] &&
                      x_values[index]   <= ifm_data->longitudes[index_lon]) {
                     break;
                     }
                  index++;
                  };
               Solve_SplineXY (ifm_data->longitudes[index_lon],
                                  &longitude_coef[index*7], &density_value);
               profile_ptr->edensity[index_alt] = density_value;
               }
            }
         }

      }
}

/*
 *******
 *
 *
 *
 *******
 */

int Interpolate_GAIM_Latitude (struct netcdf_data_t *gaim_data,
                               struct netcdf_data_t *interp_data)
{
   int index;
   int wrap_index;
   int index_alt, index_lat, index_lon;
   double *x_values, *y_values, *latitude_coef;
   float *latitudes;
   int num_ifm_lats;

   double density_value;
   struct iono_profile_t *profile_ptr;
/*
 * Assign necessary memory area for use in the Spline fitting of latitude
 *    assuming an extension of values to the poles. An average of the 
 *    cross pole value is used for the pole assignment.
 */
   latitudes = interp_data->latitudes;
   num_ifm_lats = interp_data->numb_lats;

   Initialize_CoordInterp (&x_values, &y_values, &latitude_coef,
                            gaim_data->latitudes, gaim_data->numb_lats, 1);
   x_values[0] = -90.0;
   x_values[gaim_data->numb_lats+1] = 90.0;

   for (index_lon = 0; index_lon < gaim_data->numb_lons; index_lon++) {
      for (index_alt = 0; index_alt < gaim_data->numb_alts; index_alt++) {
/*
 * Use a spline to compute the IFM latitude equivalent from the GAIM defined
 *    PQL to RLL latitude steps
 */
         for (index_lat = 0; index_lat < gaim_data->numb_lats; index_lat++) {
            profile_ptr = (gaim_data->grid_pnts[index_lat * 
                                         gaim_data->numb_lons + index_lon]);
            y_values[index_lat + 1] = profile_ptr->edensity[index_alt];
            }

         wrap_index = (index_lon + (int)(gaim_data->numb_lons / 2)) % 
                                          gaim_data->numb_lons;

         profile_ptr = gaim_data->grid_pnts[index_lon];
         y_values[0] = profile_ptr->edensity[index_alt];
/*
         profile_ptr = gaim_data->grid_pnts[wrap_index];
         y_values[0] += profile_ptr->edensity[index_alt];
         y_values[0] /= 2.0;
if (index_alt == 69) printf ("Wrap south %d fill: %e\n",wrap_index,y_values[0]);
*/

         profile_ptr = gaim_data->grid_pnts[(gaim_data->numb_lats - 1) * 
                                             gaim_data->numb_lons + index_lon];
         y_values[gaim_data->numb_lats+1] = profile_ptr->edensity[index_alt];
/*
         profile_ptr = gaim_data->grid_pnts[(gaim_data->numb_lats - 1) *
                                           gaim_data->numb_lons + wrap_index];
         y_values[gaim_data->numb_lats+1] += profile_ptr->edensity[index_alt];
         y_values[gaim_data->numb_lats+1] /= 2.0;
if (index_alt == 69) printf ("Wrap north %d fill: %e\n",wrap_index,y_values[gaim_data->numb_lats+1]);
 */
         Relaxed_SplineXY (&x_values[0], &y_values[0], 
                               gaim_data->numb_lats + 2, latitude_coef);

         for (index_lat = 0; index_lat < num_ifm_lats; index_lat++) {
            profile_ptr = interp_data->grid_pnts[index_lat *
                                           interp_data->numb_lons + index_lon];
            if (latitudes[index_lat] < x_values[0]) {
               profile_ptr->edensity[index_alt] = 0.0;
               }
            else if (latitudes[index_lat] > x_values[gaim_data->numb_lats+1]) {
               profile_ptr->edensity[index_alt] = 0.0;
               }
            else {
               index = 0;
               while (index < gaim_data->numb_lats+2) {
                  if (x_values[index+1] >= latitudes[index_lat] && 
                      x_values[index]   <= latitudes[index_lat]) {
                     break;
                     }
                  index++;
                  };

               Solve_SplineXY (latitudes[index_lat], 
                               &latitude_coef[index*7], &density_value);
               profile_ptr->edensity[index_alt] = density_value;

               }
            }
         }
      }

   Free_CoordInterp (&x_values, &y_values, &latitude_coef);
}

/*
 *******
 *
 *
 *
 *******
 */

int Interpolate_GAIM_Altitude (struct netcdf_data_t *gaim_data,
                                 float *alt_heights, int num_ifm_alts)
{
   int index;
   int index_alt, index_lat, index_lon;
   double *x_values, *y_values, *altitude_coef;

   double density_value;
   struct iono_profile_t *profile_ptr;
/*
 * Assign necessary memory area for use in the Spline fitting of altitude
 */
   Initialize_CoordInterp (&x_values, &y_values, &altitude_coef, 
                             gaim_data->altitudes, gaim_data->numb_alts, 0);

   for (index_lat = 0; index_lat < gaim_data->numb_lats; index_lat++) {
      for (index_lon = 0; index_lon < gaim_data->numb_lons; index_lon++) {

         profile_ptr = gaim_data->grid_pnts[index_lat * gaim_data->numb_lons +
                                                   index_lon];
/*
 * Use a spline to compute the IFM altitude equivalent from the GAIM defined 
 *    PQL to RLL altitude steps
 */
         for (index_alt = 0; index_alt < gaim_data->numb_alts; index_alt++) {
            y_values[index_alt] = profile_ptr->edensity[index_alt];
            }
         Relaxed_SplineXY (&x_values[0], &y_values[0], gaim_data->numb_alts,
                                                          altitude_coef);
         for (index_alt = 0; index_alt < num_ifm_alts; index_alt++) {
            if (alt_heights[index_alt] < x_values[0]) {
               profile_ptr->edensity[index_alt] = 0.0;
               }
            else if (alt_heights[index_alt] > 
                                      x_values[gaim_data->numb_alts-1]) {
               profile_ptr->edensity[index_alt] = 0.0;
               }
            else {
               index = 0;
               while (x_values[index+1] < alt_heights[index_alt] &&
                      index < gaim_data->numb_alts) {
                  index++;
                  };
/*
 * Replace original data point with the altitude interpolated value
 */
               Solve_SplineXY (alt_heights[index_alt], &altitude_coef[index*7], 
                                 &density_value);
               profile_ptr->edensity[index_alt] = density_value;
               }
            }

         }
      }

   gaim_data->numb_alts = num_ifm_alts;
   for (index_alt = 0; index_alt < num_ifm_alts; index_alt++) {
      gaim_data->altitudes[index_alt] = alt_heights[index_alt];
      }

   Free_CoordInterp (&x_values, &y_values, &altitude_coef);
}

/*
 *******
 *
 *
 *
 *******
 */

int Initialize_CoordInterp (double **x_values, double **y_values, 
                   double **coef_values, float *base_values, int numb_values,
                   int wrap_flag)
{
   int index;
   int num_pts;
   double *x_ptr;
/*
 * Provides the ability to build the spline memory for use and 
 *    buffering the first and last for use in the wrap or extending the 
 *    range outside of the data provide by one delta step.
 */
   num_pts = (wrap_flag) ? numb_values + 2 : numb_values;
   *x_values = (double *)(malloc (sizeof (double) * num_pts));
   *y_values = (double *)(malloc (sizeof (double) * num_pts));

/*
 *  Spline Coef are based on 7 = coef points and number of data points.
 */
   *coef_values = (double *)(malloc (sizeof (double) * num_pts * 7));

   x_ptr = *x_values;

   if (wrap_flag) {
      *x_ptr = base_values[0];
      x_ptr++;
      }

   for (index = 0; index < numb_values; index++) {
      *x_ptr = base_values[index];
/*
 *      printf (" %d %f %lf\n",index, base_values[index], *x_ptr);
 */
      x_ptr++;
      }

   if (wrap_flag) {
      *x_ptr = base_values[numb_values - 1];
      }
}
/*
 *******
 *
 *
 *
 *******
 */
int Free_CoordInterp (double **x_values, double **y_values, 
                                         double **altitude_coef)
{
   free (*x_values);
   free (*y_values);
   free (*altitude_coef);
}
