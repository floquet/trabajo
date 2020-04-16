#!/bin/bash
source activate alfa
export PYTHONPATH="$PWD:$PWD/Shared/GridGeneration:$PYTHONPATH"

export DIR_MODELS_REF_DAT="$PWD/Shared/IRITestCoef/"       # tell python IRI to use Test Coefficients

case $OSTYPE in
"linux-gnu")
    export LD_LIBRARY_PATH="$PWD/Shared/IonoPyIface/lib:$PWD/IonoModelEngine/Fit/lib:$PWD/IonoModelEngine/IRTAM/lib:$LD_LIBRARY_PATH"
;;
"darwin"*)
    export DYLD_LIBRARY_PATH="$PWD/Shared/IonoPyIface/lib:$PWD/IonoModelEngine/Fit/lib:$PWD/IonoModelEngine/IRTAM/lib:$DYLD_LIBRARY_PATH"
    # Necessray to avoid the error message about duplicates of OpenMP libraries.
    export KMP_DUPLICATE_LIB_OK=TRUE
esac
