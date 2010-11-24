'''

    This file is part of GEAR.

    GEAR is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/lgpl.html>.

    Author:     Jeremie Passerin      geerem@hotmail.com
    Company:    Studio Nest (TM)
    Date:       2010 / 11 / 15

'''

## @package gear.xsi.weightmap
# @author Jeremie Passerin, Miquel Campos
#

##########################################################
# GLOBAL
##########################################################
from gear.xsi import xsi, c

##########################################################
# WEIGHTMAP
##########################################################
# ========================================================
## Return all the point index affected by the weightmap.
# @param wmap WeightMap
# @param threshold Double
# @return List of Integer - The list of index
def getWeightMapPoints(wmap, threshold=1E-6):

    cls = wmap.Parent
    aWmap = wmap.Elements.Array[0]
    clsElements = cls.Elements.Array

    points = [clsElements[x] for x, v in enumerate(aWmap) if v > threshold]
 
    return points

# ========================================================
## Reset the value of selected point in the weightmap.
# @param wmap WeightMap
# @param points List of Integer - Indexes of point to reset.
def resetWeightMapPoints(wmap, points):

    weights = wmap.Elements.Array[0]
    clsElements = wmap.Parent.Elements

    # Process
    for i in points:
       if clsElements.FindIndex(i) != -1:
           weights[clsID] = 0.0

    wmap.Elements.Array = weights