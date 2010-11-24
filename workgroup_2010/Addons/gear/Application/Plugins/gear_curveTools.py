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

## @package gear_curveTools.py
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
import gear

from gear.xsi import xsi, c, dynDispatch

import gear.xsi.primitive as pri
import gear.xsi.curve as cur

##########################################################
# XSI LOAD / UNLOAD PLUGIN
##########################################################
# ========================================================
def XSILoadPlugin(in_reg):

    in_reg.Author = "Jeremie Passerin"
    in_reg.Name = "gear_curveTools"
    in_reg.Email = "geerem@hotmail.com"
    in_reg.URL = "http://www.jeremiepasserin.com"
    in_reg.Major = 1
    in_reg.Minor = 0

    # Commands
    in_reg.RegisterCommand("gear_CurveResampler","gear_CurveResampler")

    in_reg.RegisterCommand("gear_DrawCnsCurve_Linear","gear_DrawCnsCurve_Linear")
    in_reg.RegisterCommand("gear_DrawCnsCurve_Cubic","gear_DrawCnsCurve_Cubic")

    in_reg.RegisterCommand("gear_MergeCurves","gear_MergeCurves")
    in_reg.RegisterCommand("gear_SplitCurves","gear_SplitCurves")

    # Operators
    in_reg.RegisterOperator("gear_CurveResamplerOp")

    return True

# ========================================================
def XSIUnloadPlugin(in_reg):
    strPluginName = in_reg.Name
    gear.log(str(strPluginName) + str(" has been unloaded."), c.siVerbose)
    return True

##########################################################
# CURVE RESAMPLER
##########################################################
# Define =================================================
def gear_CurveResamplerOp_Define(ctxt):

    op = ctxt.Source
    op.AlwaysEvaluate = False
    op.Debug = 0

    pdef = XSIFactory.CreateParamDef("Start", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "",0,0,100,0,100)
    op.AddParameter(pdef)
    pdef = XSIFactory.CreateParamDef("End", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "",100,0,100,0,100)
    op.AddParameter(pdef)

    return True

# Update =================================================
def gear_CurveResamplerOp_Update(ctxt):

    # Inputs
    curve_geo = ctxt.GetInputValue(0, 0, 0).Geometry
    nurbscrv = curve_geo.Curves(0)

    start = ctxt.GetParameterValue("Start")
    end = ctxt.GetParameterValue("End")

    point_count = curve_geo.Points.Count

    # Process
    positions = []

    for i in range(point_count):

        step = (end - start) / (point_count-1.0)
        perc = start + (i*step)

        pos = nurbscrv.EvaluatePositionFromPercentage(perc)[0]
        positions.append(pos.X)
        positions.append(pos.Y)
        positions.append(pos.Z)

    # Output
    Out = ctxt.OutputTarget
    Out.Geometry.Points.PositionArray = positions

# Execute ================================================
def gear_CurveResampler_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    for curve in xsi.Selection:

        if curve.Type not in ["crvlist"]:
            gear.log("Invalid selection", gear.sev_warning)
            continue

        if curve.ActivePrimitive.Geometry.Curves.Count > 1:
            gear.log("Curve Resampler works only with single curve", gear.sev_warning)
            continue

        # Apply Operator
        op = cur.applyCurveResamplerOp(curve)

    xsi.InspectObj(op)

##########################################################
# DRAW CONSTRAINED CURVE LINEAR
##########################################################
# Execute ================================================
def gear_DrawCnsCurve_Linear_Execute():

    if xsi.Selection.Count < 2:
        gear.log("Select enough centers", gear.sev_error)
        return

    cur.addCnsCurve(xsi.ActiveSceneRoot, "crvCns", xsi.Selection, False, 1)

##########################################################
# DRAW CONSTRAINED CURVE CUBIC
##########################################################
# Execute ================================================
def gear_DrawCnsCurve_Cubic_Execute():

    if xsi.Selection.Count < 2:
        gear.log("Select enough centers", gear.sev_error)
        return

    cur.addCnsCurve(xsi.ActiveSceneRoot, "crvCns", xsi.Selection, False, 3)

##########################################################
# MERGE CURVES
##########################################################
# Execute ================================================
def gear_MergeCurves_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    curves = [curve for curve in xsi.Selection if curve.Type in ["crvlist"]]
    if not curves:
        gear.log("Invalid selection", gear.sev_error)
        return

    cur.mergeCurves(curves)

##########################################################
# SPLIT CURVES
##########################################################
# Execute ================================================
def gear_SplitCurves_Execute():

    if not xsi.Selection.Count:
        gear.log("No selection", gear.sev_error)
        return

    for curve in xsi.Selection:

        if curve.Type not in ["crvlist"]:
            gear.log("Invalid selection", gear.sev_warning)
            continue

        cur.splitCurve(curve)
