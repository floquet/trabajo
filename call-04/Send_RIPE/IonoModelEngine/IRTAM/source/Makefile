# Copyright (C) 2017 Boston College
# http://bc.edu
#
# BC Proprietary Information
#
# US Government retains Unlimited Rights
# Non-Government Users � restricted usage as defined through
# licensing with STR or via arrangement with Government.
#
# In no event shall the initial developers or copyright holders be
# liable for any damages whatsoever, including - but not restricted
# to - lost revenue or profits or other direct, indirect, special,
# incidental or consequential damages, even if they have been
# advised of the possibility of such damages, except to the extent
# invariable law, if any, provides otherwise.
#
# The Software is provided AS IS with NO
# WARRANTY OF ANY KIND, INCLUDING THE WARRANTY OF DESIGN,
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

fortranfiles = ProcessIrtam.f
libflagsF = -Wno-dev -O3 -fPIC -shared -fdefault-real-8

mac:
	gfortran $(libflagsF) -o libirtam_mac.so $(fortranfiles)
lin:
	gfortran $(libflagsF) -o libirtam_lin.so $(fortranfiles)

