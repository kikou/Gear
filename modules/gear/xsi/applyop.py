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

## @package gear.xsi.applyop
# @author Jeremie Passerin
#
# @brief library to easily apply operators
# This is not a UI to create operator within xsi but make the scripting easier.

##########################################################
# GLOBAL
##########################################################
# Built-in
import os

# gear
import gear
from gear.xsi import xsi, c, XSIFactory

import gear.xsi.parameter as par

# Language global name
CPP = 0
JSCRIPT = 1
PYTHON = 2

# JScript operators path
JSOPPATH = os.path.join(os.path.dirname(__file__), "jsop")

##########################################################
# BUILT IN OPERATORS APPLY
##########################################################
# PathCns ================================================
## Apply a path constraint or curve constraint.
# @param obj X3DObject - Constrained object.
# @param curve Nurbcurve - Constraining Curve.
# @param cnsType Integer - 0 for Path Constraint ; 1 for Curve Constraint (Parametric).
# @param u Double - Position of the object on the curve (from 0 to 100 for path constraint, from 0 to 1 for Curve cns).
# @param tangent Boolean - Active tangent.
# @param upv X3DObject - Object that act as up vector.
# @param comp Boolean - Active constraint compensation.
# @return the newly created constraint.
def pathCns(obj, curve, cnsType=0, u=0, tangent=False, upv=None, comp=False):

    if cnsType == 0:
        cns = obj.Kinematics.AddConstraint("Path", curve, comp)
        cns.Parameters("perc").Value = u
    else:
        cns = obj.Kinematics.AddConstraint("Curve", curve, comp)
        cns.Parameters("posu").Value = u

    cns.Parameters("tangent").Value = tangent

    if upv:
        xsi.ApplyOp("UpVectorDefiner", cns.FullName+";"+upv.FullName, c.siUnspecified, c.siPersistentOperation, "", 0)
        cns.Parameters("upvct_active").Value = True

    return cns

# PoseCns ================================================
## Apply a pose constraint
# @param obj X3DObject - Constrained object.
# @param master X3DObject - Constraining Object.
# @param comp Boolean - Active constraint compensation.
# @param position - Boolean - Active position constraint.
# @param orientation - Boolean - Active orientation constraint.
# @param scaling - Boolean - Active scaling constraint.
# @return the newly created constraint.
def poseCns(obj, master, comp=False, position=True, orientation=True, scaling=True):

    cns = obj.Kinematics.AddConstraint("Pose", master, comp)

    cns.Parameters("cnspos").Value = position
    cns.Parameters("cnsori").Value = orientation
    cns.Parameters("cnsscl").Value = scaling

    return cns

# ========================================================
def dirCns(obj, master, upv=None, comp=False, axis="xy"):

    cns = obj.Kinematics.AddConstraint("Direction", master, comp)

    if upv is not None:
        xsi.ApplyOp("UpVectorDefiner", cns.FullName+";"+upv.FullName)
        cns.Parameters("upvct_active").Value = True

    if axis == "xy": a = [1,0,0,0,1,0]
    elif axis == "xz": a = [1,0,0,0,0,1]
    elif axis == "yx": a = [0,1,0,1,0,0]
    elif axis == "yz": a = [0,1,0,0,0,1]
    elif axis == "zx": a = [0,0,1,1,0,0]
    elif axis == "zy": a = [0,0,1,0,1,0]
    
    elif axis == "-xy": a = [-1,0,0,0,1,0]
    elif axis == "-xz": a = [-1,0,0,0,0,1]
    elif axis == "-yx": a = [0,-1,0,1,0,0]
    elif axis == "-yz": a = [0,-1,0,0,0,1]
    elif axis == "-zx": a = [0,0,-1,1,0,0]
    elif axis == "-zy": a = [0,0,-1,0,1,0]

    elif axis == "x-y": a = [1,0,0,0,-1,0]
    elif axis == "x-z": a = [1,0,0,0,0,-1]
    elif axis == "y-x": a = [0,1,0,-1,0,0]
    elif axis == "y-z": a = [0,1,0,0,0,-1]
    elif axis == "z-x": a = [0,0,1,-1,0,0]
    elif axis == "z-y": a = [0,0,1,0,-1,0]
    
    elif axis == "-x-y": a = [-1,0,0,0,-1,0]
    elif axis == "-x-z": a = [-1,0,0,0,0,-1]
    elif axis == "-y-x": a = [0,-1,0,-1,0,0]
    elif axis == "-y-z": a = [0,-1,0,0,0,-1]
    elif axis == "-z-x": a = [0,0,-1,-1,0,0]
    elif axis == "-z-y": a = [0,0,-1,0,-1,0]

    for i, name in enumerate(["dirx", "diry", "dirz", "upx", "upy", "upz"]):
        cns.Parameters(name).Value = a[i]

    return cns

# TwoPointCns ============================================
## Apply a pose constraint
# @param obj X3DObject - Constrained object.
# @param master0 X3DObject - First constraining Object.
# @param master1 X3DObject - Last constraining Object.
# @param comp Boolean - Active constraint compensation.
# @return the newly created constraint.
def twoPointsCns(obj, master0, master1, comp=False):

    masters = XSIFactory.CreateObject("XSI.Collection")
    masters.Add(master0)
    masters.Add(master1)

    cns = obj.Kinematics.AddConstraint("TwoPoints", masters, comp)

    return cns

# ClsCtrOp ===============================================
## Apply a cluster center operator
# @param obj Geometry - A Polymesh, NurbMesh or NurbCurve to be constrained.
# @param center X3DObject - Constraining Object.
# @param pointIndexes List of Integer - List of point index to constraint.
# @return the newly created operator.
def clsCtrOp(obj, center, pointIndexes):

    cluster = obj.ActivePrimitive.Geometry.AddCluster(c.siVertexCluster, "center_" + str(pointIndexes), pointIndexes)
    op = xsi.ApplyOp( "ClusterCenter", cluster.FullName+";"+center.FullName, 0, 0, None, 2)

    return op

# Spine Point At ========================================
## Apply a SpinePointAt operator
# @param cns Constraint - The constraint to apply the operator on (must be a curve, path or direction constraint)
# @param startobj X3DObject - Start Reference.
# @param endobj X3DObject -End Reference.
# @param blend Double - Blend influence value from 0 to 1.
# @return the newly created operator.
def spinePointAtOp(cns, startobj, endobj, blend=.5):

    if cns.Parameters("tangent"):
        cns.Parameters("tangent").Value = True

    cns.Parameters("upvct_active").Value = True

    # Get In/Outputs
    sPointAtX = cns.Parameters("pointatx").FullName
    sPointAtY = cns.Parameters("pointaty").FullName
    sPointAtZ = cns.Parameters("pointatz").FullName

    sA_W = startobj.Kinematics.Global.Parameters("quatw").FullName
    sA_X = startobj.Kinematics.Global.Parameters("quatx").FullName
    sA_Y = startobj.Kinematics.Global.Parameters("quaty").FullName
    sA_Z = startobj.Kinematics.Global.Parameters("quatz").FullName

    sB_W = endobj.Kinematics.Global.Parameters("quatw").FullName
    sB_X = endobj.Kinematics.Global.Parameters("quatx").FullName
    sB_Y = endobj.Kinematics.Global.Parameters("quaty").FullName
    sB_Z = endobj.Kinematics.Global.Parameters("quatz").FullName

    # Apply Op
    s = "["+sPointAtX+","+sPointAtY+","+sPointAtZ+";"+\
      sA_W+","+sA_X+","+sA_Y+","+sA_Z+";"+\
      sB_W+","+sB_X+","+sB_Y+","+sB_Z+"]"

    op = xsi.ApplyOperator("SpinePointAt", s)

    op.Parameters("slider").Value = blend

    return op

##########################################################
# SN CUSTOM OPERATOR
##########################################################
# ========================================================
## Apply a sn_xfspring_op operator
# @param out X3DObject - constrained Object.
# @param mode Integer - 0 Scaling, 1 Rotation, 2 Translation, 3 SR, 4 RT, 5 ST, 6 SRT
# @return the newly created operator.
def sn_xfspring_op(out, mode=2):

    # Create Operator
    op = XSIFactory.CreateObject("sn_xfspring_op")

    # Outputs
    op.AddOutputPort(out.Kinematics.Global)

    # Inputs
    op.AddInputPort(out.Parent3DObject.Kinematics.Global)

    # Set default values
    op.Parameters("mode").Value = mode

    # Connect
    op.Connect()

    par.addExpression(op.Parameters("fc"), "fc")

    return op

# ========================================================
## Apply a sn_rotspring_op operator
# @param out X3DObject -
# @return the newly created operator.
def sn_rotspring_op(out):

    # Create Operator
    op = XSIFactory.CreateObject("sn_rotspring_op")

    # Outputs
    op.AddOutputPort(out.Kinematics.Global)

    # Inputs
    op.AddInputPort(out.Parent3DObject.Kinematics.Global)

    # Connect
    op.Connect()

    par.addExpression(op.Parameters("fc"), "fc")

    return op

# sn_ik2bone_op ==========================================
## Apply a sn_ik2bone_op operator
# @param out List of X3DObject - The constrained outputs order must be respected (BoneA, BoneB,  Center, CenterN, Eff), set it to None if you don't want one of the output.
# @param root X3DObject - Object that will act as the root of the chain.
# @param eff X3DObject - Object that will act as the eff controler of the chain.
# @param upv X3DObject - Object that will act as the up vector of the chain.
# @param lengthA Double - Length of first bone.
# @param lengthB Double - Length of second bone.
# @param negate Boolean - Use with negative Scale.
# @return the newly created operator.
def sn_ik2bone_op(out=[], root=None, eff=None, upv=None, lengthA=5, lengthB=3, negate=False):

    # Create Operator
    op = XSIFactory.CreateObject("sn_ik2bone_op")

    # Outputs
    for i, s in enumerate(["OutBoneA", "OutBoneB", "OutCenterN", "OutEff"]):
        if len(out) > i and out[i] is not None:
            port = op.AddOutputPort(out[i].Kinematics.Global, s)

    # Inputs
    op.AddInputPort(root.Kinematics.Global)
    op.AddInputPort(eff.Kinematics.Global)
    op.AddInputPort(upv.Kinematics.Global)

    # Set default values
    op.Parameters("negate").Value = negate
    op.Parameters("lengthA").Value = lengthA
    op.Parameters("lengthB").Value = lengthB

    # Connect
    op.Connect()

    return op

# ========================================================
## Apply a sn_ikfk2bone_op operator
# @param out List of X3DObject - The constrained outputs order must be respected (BoneA, BoneB,  Center, CenterN, Eff), set it to None if you don't want one of the output.
# @param root X3DObject - Object that will act as the root of the chain.
# @param eff X3DObject - Object that will act as the eff controler of the chain.
# @param upv X3DObject - Object that will act as the up vector of the chain.
# @param fk0 X3DObject - Object that will act as the first fk controler of the chain.
# @param fk1 X3DObject - Object that will act as the second fk controler of the chain.
# @param fk2 X3DObject - Object that will act as the fk effector controler of the chain.
# @param lengthA Double - Length of first bone.
# @param lengthB Double - Length of second bone.
# @param negate Boolean - Use with negative Scale.
# @param blend Double - Default blend value (0 for full ik, 1 for full fk).
# @return the newly created operator.
def sn_ikfk2bone_op(out=[], root=None, eff=None, upv=None, fk0=None, fk1=None, fk2=None, lengthA=5, lengthB=3, negate=False, blend=0, lang=CPP):

    # -----------------------------------------------------
    if lang == CPP:
        # Create Operator
        op = XSIFactory.CreateObject("sn_ikfk2bone_op")

        # Outputs
        for i, s in enumerate(["OutBoneA", "OutBoneB", "OutCenterN", "OutEff"]):
            if len(out) > i and out[i] is not None:
                op.AddOutputPort(out[i].Kinematics.Global, s)

        # Inputs
        op.AddInputPort(root.Kinematics.Global)
        op.AddInputPort(eff.Kinematics.Global)
        op.AddInputPort(upv.Kinematics.Global)
        op.AddInputPort(fk0.Kinematics.Global)
        op.AddInputPort(fk1.Kinematics.Global)
        op.AddInputPort(fk2.Kinematics.Global)

    # -----------------------------------------------------
    elif lang == JSCRIPT:

        paramDefs = []
        paramDefs.append(XSIFactory.CreateParamDef("lengthA", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 3, 0, None, 0, 10))
        paramDefs.append(XSIFactory.CreateParamDef("lengthB", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 5, 0, None, 0, 10))
        paramDefs.append(XSIFactory.CreateParamDef("negate", c.siBool, 0, c.siPersistable|c.siAnimatable, "", "", False))
        paramDefs.append(XSIFactory.CreateParamDef("blend", c.siDouble, 0, c.siPersistable |c.siAnimatable, "", "", 0, 0, 1, 0, 1))
        paramDefs.append(XSIFactory.CreateParamDef("roll", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 0, -360, 360, -360, 360))
        paramDefs.append(XSIFactory.CreateParamDef("scaleA", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 1, 0, None, 0, 2))
        paramDefs.append(XSIFactory.CreateParamDef("scaleB", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 1, 0, None, 0, 2))
        paramDefs.append(XSIFactory.CreateParamDef("maxstretch", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 1, 1, None, 1, 2))
        paramDefs.append(XSIFactory.CreateParamDef("softness", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 0, 0, None, 0, 1))
        paramDefs.append(XSIFactory.CreateParamDef("slide", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 0.5, 0, 1, 0, 1))
        paramDefs.append(XSIFactory.CreateParamDef("reverse", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 0, 0, 1, 0, 1))

        outputPorts = [ (out[i].Kinematics.Global, name) for i, name in enumerate(["OutBoneA", "OutBoneB", "OutCenterN", "OutEff"]) if (len(out) > i and out[i] is not None) ]
        inputPorts = [ (obj.Kinematics.Global, "input_%s"%i) for i, obj in enumerate([root, eff, upv, fk0, fk1, fk2]) ]

        op = createJSOpFromFile("sn_ikfk2bone_op", os.path.join(JSOPPATH, "sn_ikfk2bone_op.js"), outputPorts, inputPorts, paramDefs)

    # -----------------------------------------------------
    # Set default values
    op.Parameters("negate").Value = negate
    op.Parameters("lengthA").Value = lengthA
    op.Parameters("lengthB").Value = lengthB
    op.Parameters("blend").Value = blend

    # Connect
    op.Connect()

    return op

# ========================================================
def sn_stretchChain_op(root, ik_ctl):

    op = XSIFactory.CreateObject("sn_stretchChain_op")

    op.Parameters("rest0").Value = root.Bones(0).Length.Value
    op.Parameters("rest1").Value = root.Bones(1).Length.Value
    op.Parameters("prefrot").Value = root.Bones(1).Properties("Kinematic Joint").Parameters("prefrotz").Value

    op.AddOutputPort(root.Effector.Kinematics.Global)
    op.AddOutputPort(root.Bones(0).Length)
    op.AddOutputPort(root.Bones(1).Length)
    op.AddOutputPort(root.Bones(1).Properties("Kinematic Joint").Parameters("prefrotz"))
    op.AddInputPort(root.Kinematics.Global)
    op.AddInputPort(ik_ctl.Kinematics.Global)

    op.Connect()


    return op

# ========================================================
def sn_stretchChainMulti_op(root, ik_ctl):

    op = XSIFactory.CreateObject("sn_stretchChainMulti_op")

    for bone in root.Bones:
        op.Parameters("restlength").Value += bone.Length.Value

    op.AddOutputPort(root.Effector.Kinematics.Global)
    op.AddOutputPort(root.Bones(0).Kinematics.Local.Parameters("sclx"))
    op.AddInputPort(root.Kinematics.Global)
    op.AddInputPort(ik_ctl.Kinematics.Global)

    op.Connect()

    return op

# ========================================================
## Apply a sn_interLocalOri_op operator
# @param out X3DObject - constrained Object.
# @param refA X3DObject -
# @param refB X3DObject -
# @param blend Double -
# @return the newly created operator.
def sn_interLocalOri_op(out, refA, refB, blend=0):

    # Create Operator
    op = XSIFactory.CreateObject("sn_interLocalOri_op")

    # Outputs
    for s in ["rotx", "roty", "rotz", "nrotx", "nroty", "nrotz"]:
        op.AddOutputPort(out.Parameters(s), s)

    # Inputs
    op.AddInputPort(refA.Kinematics.Global)
    op.AddInputPort(refB.Kinematics.Global)
    op.AddInputPort(out.Parent.Kinematics.Global)
    op.AddInputPort(refA.Parameters("rotx"))
    op.AddInputPort(refB.Parameters("rotx"))

    # Set default values
    op.Parameters("blend").Value = blend

    # Connect
    op.Connect()

    return op


# sn_splinekine_op ======================================
## Apply a sn_splinekine_op operator
# @param out X3DObject - constrained Object.
# @param ctrl List of X3DObject - Objects that will act as controler of the bezier curve.
# @param u Double - Position of the object on the bezier curve (from 0 to 1).
# @return the newly created operator.
def sn_splinekine_op(out, ctrl=[], u=.5):

    # Create Operator
    op = XSIFactory.CreateObject("sn_splinekine_op")

    # Outputs
    op.AddOutputPort(out.Kinematics.Global)

    # Inputs
    for obj in ctrl:
        op.AddInputPort(obj.Kinematics.Global)
    op.AddInputPort(ctrl[0].Parent.Kinematics.Global)

    # Set default values
    op.Parameters("count").Value = len(ctrl)
    op.Parameters("u").Value = u
    op.Parameters("resample").Value = True

    # Connect
    op.Connect()

    return op

# sn_rollsplinekine_op ==================================
## Apply a sn_rollsplinekine_op operator
# @param out X3DObject - constrained Object.
# @param ctrl List of X3DObject - Objects that will act as controler of the bezier curve. Objects must have a parent that will be used as an input for the operator.
# @param u Double - Position of the object on the bezier curve (from 0 to 1).
# @return the newly created operator.
def sn_rollsplinekine_op(out, ctrl=[], u=.5):

    # Create Operator
    op = XSIFactory.CreateObject("sn_rollsplinekine_op")

    # Outputs
    op.AddOutputPort(out.Kinematics.Global)

    # Inputs
    for obj in ctrl:
        op.AddInputPort(obj.Parent.Kinematics.Global)
        op.AddInputPort(obj.Kinematics.Local)
    op.AddInputPort(ctrl[0].Parent.Kinematics.Global)

    # Set default values
    op.Parameters("count").Value = len(ctrl)
    op.Parameters("u").Value = u
    op.Parameters("resample").Value = True

    # Connect
    op.Connect()

    return op

# sn_curveslide_op =====================================
## Apply a sn_curveslide_op operator
# @param crv NurbeCurve - In / Out curve.
# @return the newly created operator.
def sn_curveslide_op(crv):

    length = crv.ActivePrimitive.Geometry.Length

    # Create Operator
    op = XSIFactory.CreateObject("sn_curveslide_op")

    # IO
    op.AddIOPort(crv.ActivePrimitive)

    # Set default values
    op.Parameters("length").Value = length

    # Connect
    op.Connect()

    return op

# sn_curveslide2_op =====================================
## Apply a sn_curveslide2_op operator
# @param outcrv NurbeCurve - Out Curve.
# @param incrv NurbeCurve - In Curve.
# @param position Double - Default position value (from 0 to 1).
# @param maxstretch Double - Default maxstretch value (from 1 to infinite).
# @param maxsquash Double - Default maxsquash value (from 0 to 1).
# @param softness Double - Default softness value (from 0 to 1).
# @return the newly created operator.
def sn_curveslide2_op(outcrv, incrv, position=0, maxstretch=1, maxsquash=1, softness=0):

    inlength = incrv.ActivePrimitive.Geometry.Length

    # Create Operator
    op = XSIFactory.CreateObject("sn_curveslide2_op")

    # IO
    op.AddIOPort(outcrv.ActivePrimitive)
    op.AddInputPort(incrv.ActivePrimitive)

    # Set default values
    op.Parameters("mstlength").Value = inlength
    op.Parameters("slvlength").Value = inlength

    op.Parameters("position").Value = position
    op.Parameters("maxstretch").Value = maxstretch
    op.Parameters("maxsquash").Value = maxsquash
    op.Parameters("softness").Value = softness

    # Connect
    op.Connect()

    return op

# sn_curvelength_op =====================================
## Apply a sn_curvelength_op operator
# @param out Parameter - The output of the curve length value.
# @param crv NurbeCurve - In Curve.
# @return the newly created operator.
def sn_curvelength_op(out, crv):

    # Create Operator
    op = XSIFactory.CreateObject("sn_curvelength_op")

    # Output
    op.AddOutputPort(out)

    # Input
    op.AddInputPort(crv.ActivePrimitive)

    # Connect
    op.Connect()

    return op

# sn_squashstretch_op ===================================
## Apply a sn_squashstretch_op operator
# @param out X3DObject - Constrained object.
# @param u Double - Position of the object on the S&S curve.
# @param length Double - Rest Length of the S&S.
# @return the newly created operator.
def sn_squashstretch_op(out, u=.5, length=5):

    # Create Operator
    op = XSIFactory.CreateObject("sn_squashstretch_op")

    # Output
    op.AddOutputPort(out.Kinematics.Global)

    # Input
    op.AddInputPort(out.Parent.Kinematics.Global)

    # Set default values
    op.Parameters("driver").Value = length
    op.Parameters("u").Value = u*100
    op.Parameters("sq_max").Value = length
    op.Parameters("st_min").Value = length

    # Connect
    op.Connect()

    return op

# sn_squashstretch2_op ==================================
## Apply a sn_squashstretch2_op operator
# @param out X3DObject - Constrained object.
# @param sclref X3DObject - Global scaling reference object.
# @param length Double - Rest Length of the S&S.
# @param axis String - 'x' for scale all except x axis...
# @return the newly created operator.
def sn_squashstretch2_op(out, sclref, length=5, axis="x"):

    # Create Operator
    op = XSIFactory.CreateObject("sn_squashstretch2_op")

    # Output
    op.AddOutputPort(out.Kinematics.Global)

    # Input
    op.AddInputPort(out.Kinematics.Global)
    op.AddInputPort(sclref.Kinematics.Global)

    # Set default values
    op.Parameters("driver_ctr").Value = length
    op.Parameters("driver_max").Value = length * 2
    op.Parameters("axis").Value = "xyz".index(axis)

    # Connect
    op.Connect()

    return op


# sn_null2curve_op =====================================
## Apply a sn_null2curve_op operator
# @param out X3DObject - Constrained object.
# @param driver X3DObject - Driving object.
# @param upv X3DObject - Up Vector.
# @param crv0 NurbsCurve - Curve to constraint the object on.
# @param crv1 NurbsCurve - Curve Use as reference (if None, crv0 is used).
# @return the newly created operator.
def sn_null2curve_op(out, driver, upv, crv0, crv1=None):

    if crv1 is None:
        crv1 = crv0

    # Create Operator
    op = XSIFactory.CreateObject("sn_null2curve_op")

    # Output
    op.AddOutputPort(out.Kinematics.Global)

    # Input
    op.AddInputPort(driver.Kinematics.Global)
    op.AddInputPort(upv.Kinematics.Global)
    op.AddInputPort(crv0.ActivePrimitive)
    op.AddInputPort(crv1.ActivePrimitive)

    # Connect
    op.Connect()

    return op

# sn_null2surface_op =====================================
## Apply a sn_null2surface_op operator
# @param out X3DObject - Constrained object.
# @param driver X3DObject - Driving object.
# @param upv X3DObject - Up Vector.
# @param srf0 NurbsSurface - NurbsSurface to constraint the object on.
# @param srf1 NurbsSurface - NurbsSurface Use as reference (if None, srf0 is used).
# @return the newly created operator.
def sn_null2surface_op(out, driver, upv, srf0, srf1=None):

    if srf1 is None:
        srf1 = srf0

    # Create Operator
    op = XSIFactory.CreateObject("sn_null2surface_op")

    # Output
    op.AddOutputPort(out.Kinematics.Global)

    # Input
    op.AddInputPort(driver.Kinematics.Global)
    op.AddInputPort(upv.Kinematics.Global)
    op.AddInputPort(srf0.ActivePrimitive)
    op.AddInputPort(srf1.ActivePrimitive)
    op.AddInputPort(driver.Kinematics.Local)

    # Connect
    op.Connect()

    return op

# sn_null2surface_op =====================================
## Apply a sn_inverseRotorder_op operator
# @param out X3DObject - Constrained object.
# @param driver X3DObject - Driving object.
# @param upv X3DObject - Up Vector.
# @param srf0 NurbsSurface - NurbsSurface to constraint the object on.
# @param srf1 NurbsSurface - NurbsSurface Use as reference (if None, srf0 is used).
# @return the newly created operator.
def sn_inverseRotorder_op(out_obj, in_obj):

    # Create Operator
    op = XSIFactory.CreateObject("sn_inverseRotorder_op")

    # Output
    op.AddOutputPort(out_obj.Kinematics.Local.Parameters("rotorder"))

    # Input

    # Connect
    op.Connect()

    par.addExpression(op.Parameters("rotorder"), in_obj.Kinematics.Local.Parameters("rotorder").FullName)

    return op

# ========================================================
## Apply a sn_pointAt_op operator
# @param out_obj X3DObject - Constrained object.
# @param target X3DObject
# @param upv X3DObject
# @return the newly created operator.
def sn_pointAt_op(out_obj, target, upv):

    # -----------------------------------------------------
    # JSCRIPT
    paramDefs = []
    paramDefs.append(XSIFactory.CreateParamDef("offset", c.siDouble, 0, c.siPersistable|c.siAnimatable, "", "", 0, -180, 180, -90, 90))

    outputPorts = [ (out_obj.Kinematics.Global, "out") ]
    inputPorts = [ (out_obj.Kinematics.Global, "out"), (target.Kinematics.Global, "in_target"), (upv.Kinematics.Global, "in_upv") ]

    op = createJSOpFromFile("sn_pointAt_op", os.path.join(JSOPPATH, "sn_pointAt_op.js"), outputPorts, inputPorts, paramDefs)

    op.Connect()

    return op

##########################################################
# MISC
##########################################################
# ========================================================
def createJSOpFromFile(name, path, outputPorts, inputPorts, paramDefs=[]):

     if not os.path.exists(path):
          gear.log("Can't find : "+path, gear.sev_warning)
          return False

     file = open(path)
     code = file.read()

     op = XSIFactory.CreateScriptedOp(name, code, "JScript")

     for port, name in outputPorts:
          op.AddOutputPort(port, name)

     for port, name in inputPorts:
          op.AddInputPort(port, name)

     for pdef in paramDefs:
          op.AddParameter(pdef)

     return op
