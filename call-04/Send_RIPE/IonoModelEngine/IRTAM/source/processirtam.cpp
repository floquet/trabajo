// Copyright (C) 2017 Boston College
// http://bc.edu
//
// BC Proprietary Information
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
#include <stdio.h>
#include <string.h>
#include "processirtam.h"

using namespace std;

extern "C" 
  {
    void processirtam(double *alati, double *along, double *xmodip, double *hourut, double *tov, double *param, double *param_local)
    {   
      // *param = 2;
      // cout << "xuj" << *alati << *along << *xmodip << *hourut << *tov << *param_local << *param;
      processirtam_(alati, along, xmodip, hourut, tov, param, param_local);
      // cout << *alati << *along << *xmodip << *hourut << *tov << *param_local << *param;

  }
}


