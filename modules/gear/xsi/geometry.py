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

## @package gear.xsi.geometry
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
from gear.xsi import xsi, c, XSIFactory, dynDispatch
import gear.xsi.utils as uti


##########################################################
# SUBCOMPONENT
##########################################################
# getSymSubComponent =====================================
## get the symmetrical suncomponent indices.
# @param indexes List of Integer - List of subcomponent index to mirror.
# @param subcomponentType String - Type of subcomponent. (pntSubComponent, polySubComponent or edgeSubComponent)
# @param mesh Geometry - The owner mesh.
# @return List of Integer - The list of symmetrical indices.
def getSymSubComponent(indexes, subcomponentType, mesh):

     symmetryMap = uti.getSymmetryMap(mesh)
     if not symmetryMap:
          return False

     symmetryArray = symmetryMap.Elements.Array[0]
     symIndexes = []

     geometry = dynDispatch(mesh.ActivePrimitive.Geometry)

     # Point Cluster ---------------------------
     if subcomponentType == "pntSubComponent":
          for pointIndex in indexes:
                symIndexes.append(symmetryArray[pointIndex])

     # Polygon Cluster -------------------------
     elif subcomponentType == "polySubComponent":

          for polyIndex in indexes:

                # Get Symmetrical Polygon Points
                symPoints = []
                for vertex in geometry.Polygons(polyIndex).Vertices:
                     symPoints.append(symmetryArray[vertex.Index])

                # Get symmetrical Polygons (Get too much polygons, we filter them right after)
                aSymPolygons = []
                for pointIndex in symPoints:
                     for polygon in geometry.Vertices(pointIndex).NeighborPolygons(1):
                          if polygon.Index not in aSymPolygons:
                                aSymPolygons.append(polygon.Index)

                # Find the good one (the one which all points belongs to the symmetrical array)
                for polyIndex in aSymPolygons:
                     polygon = geometry.Polygons(polyIndex)

                     b = True
                     for vertex in polygon.Vertices:
                          if vertex.Index not in symPoints:
                                b = False
                                break

                     if b:
                          symIndexes.append(polyIndex)

     # Edge Cluster ----------------------------
     elif subcomponentType == "edgeSubComponent":

          for edgeIndex in indexes:

                # Get Edge Points
                symPoints = []
                for vertex in geometry.Edges(edgeIndex).Vertices:
                     symPoints.append(symmetryArray[vertex.Index])

                # Get symmetrical Edges (Get too much edges, we filter them right after)
                aSymEdges = []
                for pointIndex in symPoints:
                     for edge in geometry.Vertices(pointIndex).NeighborEdges(1):
                          if edge.Index not in aSymEdges:
                                aSymEdges.append(edge.Index)

                # Find the good one (the one which all points belongs to the symmetrical array)
                for edgeIndex in aSymEdges:
                     edge = geometry.Edges(edgeIndex)

                     b = True
                     for vertex in edge.Vertices:
                          if vertex.Index not in symPoints:
                                b = False
                                break

                     if b:
                          symIndexes.append(edgeIndex)

     return symIndexes

# ========================================================
##
# @param cls CLuster
# @return Cluster
def mirrorCluster(cls):

    mesh = cls.Parent3DObject
    mirror_component = getSymSubComponent(cls.Elements, cls.Type+"SubComponent", mesh)

    mirror_cls = mesh.ActivePrimitive.Geometry.AddCluster(cls.Type, uti.convertRLName(cls.Name), mirror_component)

    return mirror_cls

##########################################################
# CONSTRUCTION HISTORY
##########################################################
# ========================================================
def isFrozen(obj):
    if obj.ActivePrimitive.NestedObjects.Count <= 5:
        return True
    else:
        return False

# getOperatorFromStack ===================================
## Return an operator of given type from the deformer stack of given geometry
# @param obj Geometry - The geometry to check.
# @param opType String - The type of the operator to find.
# @param firstOnly Boolean - Only return first matching operator.
# @return An operator if firstOnly is true, a collection of operator if it's false, False if there is no such operator.
def getOperatorFromStack(obj, opType, firstOnly=True):

     operators = XSIFactory.CreateObject("XSI.Collection")

     for nested in obj.ActivePrimitive.NestedObjects:
          if nested.IsClassOf(c.siOperatorID):
                if nested.Type == opType:
                     if firstOnly:
                          return nested
                     else:
                          operators.Add(nested)

     if operators.Count:
          return operators

     return False
##########################################################
# POLYMESH
##########################################################
# ========================================================
##
# @param objects List of Polymesh
# @return Operator - The merge operator
def getStars(obj, count, equalOrSuperior=False):

    stars = []

    for vertex in obj.ActivePrimitive.Geometry.Vertices:

        if equalOrSuperior:
            if vertex.NeighborEdges().Count >= count:
                stars.append(vertex.Index)
        else:
            if vertex.NeighborEdges().Count == count:
                stars.append(vertex.Index)

    return stars

# ========================================================
##
# @param objects List of Polymesh
# @return Operator - The merge operator
def mergeWithClusters(objects):

    # Apply Merge Operator -------------------------------
    merge_op = xsi.ApplyGenOp("MeshMerge", "", objects, 3, c.siPersistentOperation, c.siKeepGenOpInputs, None)(0)
    merged_mesh = merge_op.OutputPorts(0).Target2.Parent

    # Merge Clusters -------------------------------------
    # Init subcomponent count
    point_count = 0
    face_count = 0
    edge_count = 0
    sample_count = 0

    # Loop on objects to recreate the clusters
    for i, obj in enumerate(objects):

        # Add last object subcomponent count to total
        if i > 0:
            last_geo = objects[i-1].ActivePrimitive.Geometry

            point_count += last_geo.Vertices.Count
            face_count += last_geo.Polygons.Count
            edge_count += last_geo.Edges.Count
            sample_count += last_geo.Samples.Count

        # Cycle on clusters to be recreate
        for cls in obj.ActivePrimitive.Geometry.Clusters:

            cls_type = cls.Type

            if cls_type == "poly":
                sub_count = face_count
            elif cls_type == "pnt":
                sub_count = point_count
            elif cls_type == "edge":
                sub_count = edge_count
            elif cls_type == "sample":
                sub_count = sample_count
            else:
                continue

            # Offset Cluster Elements Indexes
            cls_indexes = []
            for i in cls.Elements:
                cls_indexes.append(i+sub_count)

            # Create the cluster
            merged_mesh.ActivePrimitive.Geometry.AddCluster(cls_type, obj.Name +"_"+ cls.Name, cls_indexes)

    return merge_op

# ========================================================
##
# @param obj Polymesh
# @return List of Polymesh
def splitPolygonIsland(obj):

    geometry = obj.ActivePrimitive.Geometry
    polygons_indexes = range(geometry.Polygons.Count)

    islands = []
    while polygons_indexes:

        depth = 1
        old_count = 0

        while True:

            polygon = geometry.Polygons(polygons_indexes[0])

            neighbors = polygon.NeighborPolygons(depth)

            if neighbors.Count == old_count:
                island_indexes = [poly.Index for poly in neighbors]
                island_indexes.append(polygon.Index)
                for i in island_indexes:
                    polygons_indexes.remove(i)
                break

            depth += 1
            old_count = neighbors.Count

        # Extract Polygons
        isle = xsi.ExtractFromComponents("ExtractPolygonsOp", obj.FullName+".poly"+str(island_indexes), obj.Name+"_island", None, c.siPersistentOperation, c.siKeepGenOpInputs)(0)(0)
        islands.append(isle)

    return islands
