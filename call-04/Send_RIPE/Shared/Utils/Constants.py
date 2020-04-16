# Copyright (C) 2017 Systems & Technology Research, LLC.
# http://www.stresearch.com
#
# STR Proprietary Information
#
# US Government retains Unlimited Rights
# Non-Government Users – restricted usage as defined through
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

## @package Shared.Utils.Constants
#  Collection of constants

## The conversion factor between plasma frequency and electron density.
#  [electron density 1/cm^3] = [plasma frequency Hz^2] / pfsqToEdConv()
#
pfsqtoEd = 80.6163849431291e6

## The conversion factor from electron density to plasma frequency squared.
#  [plasma frequency Hz^2] = [electron density 1/cm^3] * edToPfsqConv()
#
edToPfsq = 80.6163849431291
