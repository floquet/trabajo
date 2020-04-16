#include <iostream>
#include <stdio.h>
#include <string.h>
#include "saoreadc.h"

using namespace std;

extern "C"
{
    void getprofile(double *pfreq, double *pheight, double *paramiri, const char *filename)
    {
        getprofile_(pfreq, pheight, paramiri,filename);
    }
}


