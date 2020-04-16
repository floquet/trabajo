#ifndef saoread_h
#define saoread_h

#define EXPORT

extern "C"
{
    EXPORT void getprofile_(double* pfreq, double* pheight,double* paramiri,const char* filename);

    void getprofile(double* pfreq, double* pheight,double* paramiri,const char* filename);

}

#endif
