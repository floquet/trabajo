#!/bin/bash

# Choosing the compiler that avoids proprietary shared libraries.
case $OSTYPE in
"linux-gnu")
    FC=gfortran
;;
"darwin"*)
    FC=intelem
esac

f2py  -c igrf12grid.f90 igrf12.f  --fcompiler=${FC} -m igrf12 
f2py  -c pfProfileToEnGrid.f90 --fcompiler=${FC} -m PfProfileToEnGrid
