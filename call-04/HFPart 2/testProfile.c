#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <math.h>

#include "hfpart_constants.h"
#include "QPSegment.h"
#include "QPS_Model.h"

int main (int argc, char **argv)
{

   double h_prof[55] = {
      60,  70,  80,  90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220,
     230, 240, 250, 260, 270, 280, 290, 300, 310, 320, 330, 340, 350, 360, 370, 380, 390,
     400, 410, 420, 430, 440, 450, 460, 470, 480, 490, 500, 510, 520, 530, 540, 550, 560,
     570, 580, 590, 600
     };

/* Test case using Ne / m3  */
 
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

   int edp_pts = 55;

   struct qps_model_profile_t QPModel;

   QPS_Model_Profile (h_prof, ne_prof, edp_pts, ELECTRON_DENSITY_M3, &QPModel);

   QPS_Model_SegmentList (h_prof, ne_prof, edp_pts, &QPModel, VERBOSE_LEVEL2);

}
