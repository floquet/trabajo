#
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#

SYSTEM_TYPE := $(shell uname)

include Make.flags.$(SYSTEM_TYPE)

INCDIRS = -I ./

LIBS = -lm

SRC = \
	generalUtils.c \
	HF_RayTrace.c \
	QPS_Model.c \
	HF_ART_Homing.c \
	spline.c \
	QPSegment.c

OBJ = $(SRC:.c=.o)

all:	testProfile testRayPath testHoming testPOETbox

testProfile:	testProfile.o $(OBJ)
	$(CC) -o testProfile testProfile.o $(OBJ) $(LIBS)

testRayPath:	testRayPath.o $(OBJ)
	$(CC) -o testRayPath testRayPath.o $(OBJ) $(LIBS)

testHoming:	testHoming.o $(OBJ)
	$(CC) -o testHoming testHoming.o $(OBJ) $(LIBS)

testPOETbox:	testPOETbox.o $(OBJ)
	$(CC) -o testPOETbox testPOETbox.o $(OBJ) $(LIBS)

clean:

install:

#
## rules for compilation
#
.c.a:
	$(CC) $(CFLAGS) $(INCDIRS) -c `pwd`/$<
.c.o:
	$(CC) $(CFLAGS) $(INCDIRS) -c `pwd`/$<
