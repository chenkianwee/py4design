# ==================================================================================================
#
#    Copyright (c) 2016, Chen Kian Wee (chenkianwee@gmail.com)
#
#    This file is part of py4design
#
#    py4design is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    py4design is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with py4design.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================
import math

import fetch
import construct
import modify

from OCCUtils import face, Common, Construct, Topology, edge

from OCC import BRepFeat 
from OCC.gp import gp_Pnt, gp_Vec, gp_Lin, gp_Ax1, gp_Dir, gp_Trsf
from OCC.TopAbs import TopAbs_IN, TopAbs_REVERSED 
from OCC.BRepClass3d import BRepClass3d_SolidClassifier
from OCC.GProp import GProp_GProps
from OCC.BRepGProp import brepgprop_VolumeProperties
from OCC.BRepCheck import BRepCheck_Wire, BRepCheck_Shell, BRepCheck_NoError
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.BRep import BRep_Tool
from OCC.IntCurvesFace import IntCurvesFace_ShapeIntersector
from OCC.BRepExtrema import BRepExtrema_DistShapeShape
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeEdge

#========================================================================================================
#POINT INPUTS
#======================================================================================================== 
def point_in_face(pypt, occface, tolerance = 1e-04):
    """
    This function checks if a point is inside an OCCface.
 
    Parameters
    ----------
    pypt : tuple of floats
        Check if this point is inside the OCCface. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    occface : OCCface
        Check if the point is inside this OCCface.
        
    tolerance : float, optional
        The minimum distance between the point and the face to determine if the point is inside the face.
        Default = 1e-04.

    Returns
    -------
    True or False : bool
        If True means the point is in the face, if False the point is not in the face.
    """
    vertex = construct.make_vertex(pypt)
    min_dist = minimum_distance(vertex, occface)
    if min_dist < tolerance:
        isinside = True
    else:
        isinside = False
    #isinside = BOPInt_Context().IsValidPointForFace(gp_pt, occ_face,tol )
    return isinside

def point_in_solid(pypt, occsolid):
    """
    This function checks if a point is inside an OCCsolid.
 
    Parameters
    ----------
    pypt : tuple of floats
        Check if this point is inside the OCCsolid. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    occsolid : OCCsolid
        Check if the point is inside this OCCsolid.

    Returns
    -------
    True, False, None : True, False, None
        If True means the point is in the solid, if False the point is not in the solid, if None means the point is on the solid.
    """
    gp_pnt = gp_Pnt(pypt[0], pypt[1], pypt[2] )
    if Common.point_in_solid(occsolid, gp_pnt)[0]:
        return True 
    elif Common.point_in_solid(occsolid, gp_pnt)[0] == None:
        return None #means its on the solid
    else: 
        return False
    
def project_point_on_infedge(pypt, occedge):
    """
    This function projects a point towards the OCCedge. The edge is treated as a vector and it stretched through infinity.  
 
    Parameters
    ----------
    pypt : tuple of floats
        The point to be projected. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    occedge : OCCedge
        The edge to be projected on.

    Returns
    -------
    Projected point : pypt
        The projected point on the edge.
    """
    gp_pt = gp_Pnt(pypt[0], pypt[1], pypt[2])
    occutil_edge = edge.Edge(occedge)
    u, projpt = occutil_edge.project_vertex(gp_pt)
    proj_pypt = modify.occpt_2_pypt(projpt)
    return proj_pypt

def project_point_on_faceplane(pypt, occface):
    """
    This function projects a point towards the OCCface. The face is treated as a plane and it stretched through infinity.  
 
    Parameters
    ----------
    pypt : tuple of floats
        The point to be projected. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    occface : OCCface
        The face to be projected on.

    Returns
    -------
    Projected point : pypt
        The projected point on the face.
    """
    gp_pt = gp_Pnt(pypt[0], pypt[1], pypt[2])
    fc = face.Face(occface)
    uv, projected_pt = fc.project_vertex(gp_pt)
    proj_pypt = modify.occpt_2_pypt(projected_pt)
    return proj_pypt
    
def angle_bw_2_vecs_w_ref(pyvec1, pyvec2, ref_pyvec):
    """
    This function measures the angle between two vectors regards to a reference vector. 
    The reference vector must be perpendicular to both the vectors. The angle is measured in counter-clockwise direction.
 
    Parameters
    ----------
    pyvec1 : tuple of floats
        The first vector to be measured.  A pyvec is a tuple that documents the xyz direction of a vector e.g. (x,y,z)
    
    pyvec2 : tuple of floats
        The second vector to be measured.  A pyvec is a tuple that documents the xyz direction of a vector e.g. (x,y,z)
        
    ref_pyvec : tuple of floats
        The reference vector must be perpendicular to pyvec1 and pyvec2. 
         A pyvec is a tuple that documents the xyz direction of a vector e.g. (x,y,z)

    Returns
    -------
    angle : float
        The measured angle between pyvec1 and pyvec2 regards to ref_pyvec, the angle is measured in counter-clockwise direction.
    """
    vec1 = gp_Vec(pyvec1[0], pyvec1[1], pyvec1[2])
    vec2 = gp_Vec(pyvec2[0], pyvec2[1], pyvec2[2])
    ref_vec = gp_Vec(ref_pyvec[0], ref_pyvec[1], ref_pyvec[2])
    radangle = vec1.AngleWithRef(vec2, ref_vec)
    angle = radangle * (180.0/math.pi)
    if angle <0:
        angle = 360+angle
    #the angle is measured in counter-clockwise direction
    return angle

def angle_bw_2_vecs(pyvec1, pyvec2):
    """
    This function measures the angle between two vectors. 
 
    Parameters
    ----------
    pyvec1 : tuple of floats
        The first vector to be measured. A pyvec is a tuple that documents the xyz direction of a vector e.g. (x,y,z)
    
    pyvec2 : tuple of floats
        The second vector to be measured. A pyvec is a tuple that documents the xyz direction of a vector e.g. (x,y,z)
        
    Returns
    -------
    angle : float
        The measured angle between pyvec1 and pyvec2.
    """
    vec1 = gp_Vec(pyvec1[0], pyvec1[1], pyvec1[2])
    vec2 = gp_Vec(pyvec2[0], pyvec2[1], pyvec2[2])
    radangle = vec1.Angle(vec2)
    angle = radangle * (180.0/math.pi)
    return angle
    
def distance_between_2_pts(pypt1, pypt2):
    """
    This function measures the distance between two points. 
 
    Parameters
    ----------
    pypt1 : tuple of floats
        The first point to be measured. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
    
    pypt2 : tuple of floats
        The second point to be measured. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)

    Returns
    -------
    angle : float
        The measured distance between pypt1 and pypt2.
    """
    gp_pnt1 = gp_Pnt(pypt1[0], pypt1[1], pypt1[2])
    gp_pnt2 = gp_Pnt(pypt2[0], pypt2[1], pypt2[2])
    distance = gp_pnt1.Distance(gp_pnt2)
    return distance

def is_anticlockwise(pyptlist, ref_pyvec):
    """
    This function checks if the list of points are arranged anticlockwise in regards to the ref_pyvec. 
    The ref_pyvec must be perpendicular to the points.
 
    Parameters
    ----------
    pyptlist : a list of tuples
        The list of points to be checked. List of points to be converted. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
    
    ref_pyvec : tuple of floats
        The reference vector must be perpendicular to the list of points. 
        A pyvec is a tuple that documents the xyz direction of a vector e.g. (x,y,z)
        
    Returns
    -------
    True or False : bool
        If True the list of points are arranged in anticlockwise manner, if False they are not.
    """
    total = [0,0,0]    
    npts = len(pyptlist)
    for i in range(npts):
        pt1 = pyptlist[i]
        if i == npts-1:
            pt2 = pyptlist[0]
        else:
            pt2 = pyptlist[i+1]
            
        #cross the two pts
        vec1 = gp_Vec(pt1[0],pt1[1],pt1[2])
        vec2 = gp_Vec(pt2[0],pt2[1],pt2[2])
        prod = vec1.Crossed(vec2)
        total[0] += prod.X()
        total[1] += prod.Y()
        total[2] += prod.Z()
        
    gp_total = gp_Vec(total[0],total[1],total[2])
    gp_ref_vec = gp_Vec(ref_pyvec[0],ref_pyvec[1],ref_pyvec[2])
    result  = gp_total.Dot(gp_ref_vec)
    if result < 0:
        return False 
    else:
        return True

#========================================================================================================
#EDGE INPUTS
#======================================================================================================== 
def edge_midpt(occedge):
    """
    This function calcuates the midpoint of an OCCedge.
 
    Parameters
    ----------
    occedge : OCCedge
        The edge to be analysed.
        
    Returns
    -------
    midpoint : pypt
        The midpoint of the edge.
    """
    occutil_edge = edge.Edge(occedge)
    mid_parm, midpt = occutil_edge.mid_point()
    return (midpt.X(), midpt.Y(), midpt.Z())

def project_edge_on_face(occedge, occface):
    """
    This function projects an OCCedge towards the OCCface. #TODO: figure out if it is a faceplane or just the face. 
 
    Parameters
    ----------
    occedge : OCCedge
        The edge to be projected.
        
    occface : OCCface
        The face to be projected on.

    Returns
    -------
    Projected edge : OCCedge
        The projected edge on the face.
    """
    
    fc = face.Face(occface)
    projected_curve = fc.project_curve(occedge)
    curve_edge = BRepBuilderAPI_MakeEdge(projected_curve)
    return curve_edge.Edge()

def intersect_edge_with_edge(occedge1, occedge2, tolerance = 1e-06):
    """
    This function intersects two OCCedges and obtain a list of intersection points.
 
    Parameters
    ----------
    occedge1 : OCCedge
        The first edge to be intersected.
        
    occedge2 : OCCedge
        The second edge to be intersected.
        
    tolerance : float, optional
        The minimum distance between the two edges to determine if the edges are intersecting, Default = 1e-06.

    Returns
    -------
    list of intersection points : pyptlist
        The list of points where the two edges intersect.
    """
    interpyptlist = []
    dss = BRepExtrema_DistShapeShape(occedge1, occedge2)
    dss.SetDeflection(tolerance)
    dss.Perform()
    min_dist = dss.Value()
    if min_dist < tolerance:
        npts = dss.NbSolution()
        for i in range(npts):
            gppt = dss.PointOnShape1(i+1)
            pypt = (gppt.X(), gppt.Y(), gppt.Z())
            interpyptlist.append(pypt)
            
    return interpyptlist

def edge_common_vertex(occedge1, occedge2):
    """
    This function checks if two OCCedges have common vertices.
 
    Parameters
    ----------
    occedge1 : OCCedge
        The first edge to be analysed.
        
    occedge2 : OCCedge
        The second edge to be analysed.

    Returns
    -------
    list of common points : pyptlist
        The list of common points between the two edges.
    """
    pyptlist_all = []
    edgepyptlist1 = fetch.points_from_edge(occedge1)
    edgepyptlist2 = fetch.points_from_edge(occedge2)
    pyptlist_all.extend(edgepyptlist1)
    pyptlist_all.extend(edgepyptlist2)

    seen = set()
    uniq = []
    common = []
    for pypt in pyptlist_all:
        if pypt not in seen:
            uniq.append(pypt)
            seen.add(pypt)
        else:
            common.append(pypt)

    if not common:
        return ()
    else:
        return common

def intersect_edge_with_face(occedge, occface, tolerance = 1e-02):
    """
    This function intersects an OCCedge with an OCCface and obtain a list of intersection points.
 
    Parameters
    ----------
    occedge : OCCedge
        The edge to be intersected.
        
    occface : OCCface
        The face to be intersected.
        
    tolerance : float, optional
        The minimum distance between the edge and face to determine if the they are intersecting, Default = 1e-02.

    Returns
    -------
    list of intersection points : pyptlist
        The list of points where the two topologies intersect.
    """
    occutil_edge = edge.Edge(occedge)
    interptlist = occutil_edge.Intersect.intersect(occface, tolerance)
    return interptlist

def pt2edgeparameter(pypt, occedge):
    """
    This function calculates the parameter of the OCCedge from the given point. The length of the edge can be calculated by specifying
    two parameters in the edgelength function.
 
    Parameters
    ----------
    pypt : tuple of floats
        The point on the OCCedge to be converted to the parameter. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z).
        
    occedge : OCCedge
        The edge to be analysed.

    Returns
    -------
    parameter : float
        The parameter of the point on the OCCedge.
    """
    occutil_edge = edge.Edge(occedge)
    gppt = construct.make_gppnt(pypt)
    parameter, nearest_gppt = occutil_edge.project_vertex(gppt)
    return parameter

def edgeparameter2pt(parameter, occedge):
    """
    This function calculates the point on the OCCedge from the given parameter.
 
    Parameters
    ----------
    parameter : float
        The parameter of the OCCedge.
        
    occedge : OCCedge
        The edge to be analysed.

    Returns
    -------
    point on edge : pypt
        The point on the edge based on the parameter.
    """
    occutil_edge = edge.Edge(occedge)
    gppt = occutil_edge.parameter_to_point(parameter)
    return (gppt.X(),gppt.Y(), gppt.Z())
    
def edgelength(lbound, ubound, occedge):
    """
    This function calculates the length of the OCCedge between the lower and upper bound.
 
    Parameters
    ----------
    lbound : float
        The lower bound of the OCCedge.
        
    ubound : float
        The upper bound of the OCCedge.
        
    occedge : OCCedge
        The edge to be analysed.

    Returns
    -------
    length : float
        The length of the edge between the upper and lower bound.
    """
    occutil_edge = edge.Edge(occedge)
    length = occutil_edge.length(lbound, ubound)
    return length
    
def are_same_edges(occedge1, occedge2):
    """
    This function checks if the two OCCedges are the same.
 
    Parameters
    ----------
    occedge1 : OCCedge
        The first edge to be analysed.
        
    occedge2 : OCCedge
        The second edge to be analysed.

    Returns
    -------
    True or False : bool
        If True the two edges are the same, if False the two edges are not the same.
    """
    edgepyptlist1 = fetch.points_frm_edge(occedge1)
    edgepyptlist2 = fetch.points_frm_edge(occedge2)
    if edgepyptlist1 == edgepyptlist2:
        return True
    else:
        edgepyptlist1.reverse()
        if edgepyptlist1 == edgepyptlist2:
            return True 
        else:
            return False 
            
def sort_edges_into_order(occedge_list, isclosed = False):
    """
    This function creates a list of ordered OCCedges from a list of loose OCCedges. The edges does not need to form a close face. 
 
    Parameters
    ----------
    occedge_list : list of OCCedges
        The list of OCCedges to be sorted.
    
    isclosed : bool, optional
        True or False, is the resultant wires suppose to be closed or opened, Default = False.
        
    Returns
    -------
    list of sorted edges : list of OCCedges
        A list of ordered OCCedges.
    """
    from OCC.TopoDS import topods 
    from OCC.TopExp import topexp
    from OCC.BRep import BRep_Tool
    from OCC.ShapeAnalysis import ShapeAnalysis_WireOrder
    from OCC.Precision import precision
    
    sawo_statusdict={0:"all edges are direct and in sequence",
    1:"all edges are direct but some are not in sequence",
    2:"unresolved gaps remain",
    -1:"some edges are reversed, but no gaps remain",
    -2:"some edges are reversed and some gaps remain",
    -10:"failure on reorder"}
    
    mode3d = True
    SAWO = ShapeAnalysis_WireOrder(mode3d, precision.PConfusion())
    
    for occedge in occedge_list:
        V1 = topexp.FirstVertex(topods.Edge(occedge))
        V2 = topexp.LastVertex(topods.Edge(occedge))
        pnt1 = BRep_Tool().Pnt(V1)
        pnt2 = BRep_Tool().Pnt(V2)
        SAWO.Add(pnt1.XYZ(), pnt2.XYZ())
        SAWO.SetKeepLoopsMode(True)
        
    SAWO.Perform(isclosed)
    #print "SAWO.Status()", SAWO.Status()
    if not SAWO.IsDone():
        raise RuntimeError, "build wire: Unable to reorder edges: \n" + sawo_statusdict[SAWO.Status()]
    else:
        if SAWO.Status() not in [0, -1]:
            pass # not critical, wirebuilder will handle this
        SAWO.SetChains(precision.PConfusion())
        sorted_edge2dlist = []
        #print "Number of chains: ", SAWO.NbChains()
        for i in range(SAWO.NbChains()):
            sorted_edges = []
            estart, eend = SAWO.Chain(i+1)
            #print "Number of edges in chain", i, ": ", eend - estart + 1
            if (eend - estart + 1)==0:
                continue
            for j in range(estart, eend+1):
                idx = abs(SAWO.Ordered(j))
                edge2w = occedge_list[idx-1]
                if SAWO.Ordered(j) <0:
                    edge2w.Reverse()
                sorted_edges.append(edge2w)
                
            sorted_edge2dlist.append(sorted_edges)
            
    return sorted_edge2dlist
    
def identify_open_close_wires_frm_loose_edges(occedge_list):
    """
    This function rearranged the list of OCCedges and categorise them into two lists of open and closed OCCwires.
 
    Parameters
    ----------
    occedge_list : list of OCCedges
        The list of OCCedges to be sorted.
     
    Returns
    -------
    list of closed wires : list of OCCwires
        A list of closed OCCwires from the loose OCCedges.
    
    list of opened wires : list of OCCwires
        A list of opened OCCwires from the loose OCCedges.
    """
    open_wires = []
    close_wires = []
    occedgelist2 = occedge_list[:]
    cur_edge = occedgelist2[0]
    cur_wire = [cur_edge]
    if len(occedge_list) == 1:
        open_wires.append(occedge_list)
    else:
        while len(occedge_list)>0:
            
            occedgelist2.remove(cur_edge)
            noccedgelist2 = len(occedgelist2)
            
            if noccedgelist2 == 0:
                open_wires.append(cur_wire)
                for rmvedge in cur_wire:
                    occedge_list.remove(rmvedge)
            
            ecnt = 0
            for occedge in occedgelist2:
                #make sure the 2 edges are not the same edge
                if are_same_edges(cur_edge, occedge):
                    occedge_list.remove(occedge)
                elif edge_common_vertex(cur_edge, occedge):
                    cur_wire.append(occedge)
                    cur_edge = occedge
                    #needs to check if this edge connects to any other previous edges
                    ncur_wire = len(cur_wire)
                    if ncur_wire>=3:
                        cur_wire_cntlist = range(ncur_wire+1)
                        #start counting from the back -2,-3 ...
                        #do not include -0
                        cur_wire_cntlist.remove(0)
                        #do not include -1, the last edge is 
                        #the same edge as occedge
                        cur_wire_cntlist.remove(1)
                        #do not include -2, the second last edge will 
                        #definitely share a common vertex
                        cur_wire_cntlist.remove(2)
                        for cwcnt in cur_wire_cntlist:
                            negcnt = cwcnt*-1
                            prev_edge = cur_wire[negcnt]
                            #if it is common with previous edge means its a close wire
                            if edge_common_vertex(occedge, prev_edge):
                                close_cur_wire = cur_wire[negcnt:]
                                close_wires.append(close_cur_wire)
                                #remove all the edges in cur_wire from occedgelist
                                for rmvedge in close_cur_wire:
                                    occedge_list.remove(rmvedge)
                                    
                                if len(occedge_list) > 0:
                                    occedgelist2 = occedge_list[:]
                                    cur_edge = occedgelist2[0]
                                    cur_wire = [cur_edge]
                                break
                        break
                                
                    else:
                        break 
                    
                #if you have loop through the whole edge list and still did not 
                #find any edge that share a common edge, it means this is the 
                # last edge of an open wire
                elif ecnt == noccedgelist2-1:
                    open_wires.append(cur_wire)
                    #remove all the edge in cur_wire from occedgelist
                    for rmvedge in cur_wire:
                        occedge_list.remove(rmvedge)
                        
                    if len(occedge_list) > 0:
                        occedgelist2 = occedge_list[:]
                        cur_edge = occedge
                        cur_wire = [cur_edge]
                    break
                    
                ecnt+=1
            
    return close_wires, open_wires
#========================================================================================================
#WIRE INPUTS
#======================================================================================================== 
def is_wire_closed(occwire):
    """
    This function checks if an OCCwire is closed.
 
    Parameters
    ----------
    occwire : OCCwire
        The OCCwire to be checked.
        
    Returns
    -------
    True or False : bool
        If True wire is closed, if False wire is opened.
    """
    wire_checker = BRepCheck_Wire(occwire)
    is_closed = wire_checker.Closed()
    if is_closed == BRepCheck_NoError:
        return True 
    else:
        return False 
    
def wirelength(occwire):
    """
    This function measures the length of the OCCwire.
 
    Parameters
    ----------
    occwire : OCCwire
        The OCCwire to be measured.
        
    Returns
    -------
    length of wire : float
        The lenght of the wire.
    """
    edgelist = fetch.edges_frm_wire(occwire)
    wire_length = 0
    for occedge in edgelist:
        dmin, dmax = fetch.edge_domain(occedge)
        wire_length = wire_length + edgelength(dmin, dmax, occedge)
    return wire_length
    
#========================================================================================================
#FACE INPUTS
#======================================================================================================== 
def face_normal(occface):
    """
    This function calculates the normal of the OCCface.
 
    Parameters
    ----------
    occface : OCCface
        The OCCface to be analysed.
        
    Returns
    -------
    face normal : pydirection
        The normal of the face. A pydir is a tuple that documents the xyz vector of a dir e.g. (x,y,z)
    """
    fc = face.Face(occface)
    centre_uv,centre_pt = fc.mid_point()
    normal_dir = fc.DiffGeom.normal(centre_uv[0],centre_uv[1])
    if occface.Orientation() == TopAbs_REVERSED:
        normal_dir = normal_dir.Reversed()
        
    normal = (normal_dir.X(), normal_dir.Y(), normal_dir.Z())
    return normal

def face_area(occface):
    """
    This function calculates the area of the OCCface.
 
    Parameters
    ----------
    occface : OCCface
        The OCCface to be analysed.
        
    Returns
    -------
    face area : float
        The area of the face.
    """
    surface_area = Common.GpropsFromShape(occface).surface()
    return surface_area.Mass()

def face_midpt(occface):
    """
    This function calculates the mid point of the OCCface.
 
    Parameters
    ----------
    occface : OCCface
        The OCCface to be analysed.
        
    Returns
    -------
    face mid point : pypt
        The mid point of the face.
    """
    fc = face.Face(occface)
    centre_uv,gpcentre_pt = fc.mid_point()
    centre_pt = (gpcentre_pt.X(), gpcentre_pt.Y(), gpcentre_pt.Z())
    return centre_pt
    
def is_face_planar(occface, tolerance = 1e-06):
    """
    This function calculates if the OCCface is planar.
 
    Parameters
    ----------
    occface : OCCface
        The OCCface to be analysed.
        
    tolerance : float, optional
        The precision for checking the planarity, Default = 1e-06.
        
    Returns
    -------
    True or False : bool
        If True face is planar, if False face is not planar.
    """
    fc = face.Face(occface)
    return fc.is_planar(tol = tolerance)

def face_is_inside(occface, boundary_occface):
    """
    This function calculates if OCCface is inside boundary OCCface.
 
    Parameters
    ----------
    occface : OCCface
        The OCCface to be analysed.
        
    boundary_occface : OCCface
        Check if occface is inside the boundary_occface.
        
    Returns
    -------
    True or False : bool
        If True face is inside boundary face, if False face is not inside boundary face.
    """
    return BRepFeat.brepfeat_IsInside(occface, boundary_occface)
    
def project_face_on_faceplane(occface2projon, occface2proj):
    """
    This function projects the OCCface onto another OCCface plane. The plane stretches through infinity.
 
    Parameters
    ----------
    occface2projon : OCCface
        The OCCface to be projected on.
        
    occface2proj : OCCface
        The OCCface to be projected.
        
    Returns
    -------
    list of points : pyptlist
        The list of projected points.
    """
    
    wire_list =  list(Topology.Topo(occface2proj).wires())
    occpt_list = []
    for wire in wire_list:
        occpts = Topology.WireExplorer(wire).ordered_vertices()
        occpt_list.extend(occpts)
    proj_ptlist = []
    for occpt in occpt_list:
        occ_pnt = BRep_Tool.Pnt(occpt)
        pypt = (occ_pnt.X(), occ_pnt.Y(), occ_pnt.Z())
        projected_pt = project_point_on_faceplane(pypt, occface2projon)
        proj_ptlist.append(projected_pt)
        
    return proj_ptlist

def srf_nrml_facing_solid_inward(occface, occsolid):
    """
    This function checks if the OCCface is facing the inside of the OCCsolid.
 
    Parameters
    ----------
    occface : OCCface
        The OCCface to be checked.
        
    occsolid : OCCsolid
        The OCCsolid.
        
    Returns
    -------
    True or False : bool
        If True the face is facing the inside of the solid, if False the face is not facing inwards.
    """
    #move the face in the direction of the normal
    #first offset the face so that vert will be within the solid 
    o_wire = Construct.make_offset(occface, 0.0001)
    o_face = BRepBuilderAPI_MakeFace(o_wire).Face()
    
    wire_list =  list(Topology.Topo(o_face).wires())
    occpt_list = []
    for wire in wire_list:
        occpts = Topology.WireExplorer(wire).ordered_vertices()
        occpt_list.extend(occpts)
        
        
    pt = BRep_Tool.Pnt(occpt_list[0]) #a point that is on the edge of the face 
    normal = face_normal(occface)
    
    gp_direction2move = gp_Vec(normal[0], normal[1], normal[2])
    gp_moved_pt = pt.Translated(gp_direction2move.Multiplied(0.001))
    mv_pt = (gp_moved_pt.X(), gp_moved_pt.Y(), gp_moved_pt.Z())
    
    in_solid = point_in_solid(occsolid, mv_pt)
    
    if in_solid:
        return True
    else:
        return False
    
def are_same_faces(occface1, occface2):
    """
    This function checks if the two OCCfaces are the same.
 
    Parameters
    ----------
    occface1 : OCCface
        The first OCCface to be checked.
        
    occface2 : OCCface
        The second OCCface to be checked.
        
    Returns
    -------
    True or False : bool
        If True the faces are the same, if False the faces are not the same.
    """
    pyptlist1 = fetch.points_frm_occface(occface1)
    pyptlist2 = fetch.points_frm_occface(occface2)
    pyptlist1.sort()
    pyptlist2.sort()
    if pyptlist1 == pyptlist2:
        return True
    else:
        return False

def face_normal_as_edges(occface_list, normal_magnitude = 1):
    """
    This function calculates the normals of the list of OCCfaces and construct a list of OCCedges from it.
 
    Parameters
    ----------
    occface_list : list of OCCfaces
        The list of OCCfaces to be analysed.
        
    normal_magnitude : float, optional
        The length of the normal OCCedges, Default = 1.
        
    Returns
    -------
    list of normals : list of OCCedges
        List of OCCedges.
    """
    nrml_list = []
    for occcface in occface_list:
        nrml = face_normal(occcface)
        midpt = face_midpt(occcface)
        for_edge_pt = modify.move_pt(midpt, nrml, normal_magnitude)
        nrml_edge = construct.make_edge(midpt, for_edge_pt)
        nrml_list.append(nrml_edge)
    return nrml_list

def grp_faces_acc2normals(occface_list):
    """
    This function groups the list of OCCfaces according to their normals.
 
    Parameters
    ----------
    occface_list : list of OCCfaces
        The list of OCCfaces to be analysed.
        
    Returns
    -------
    dictionary of faces according to their normals : dictionary of OCCfaces
        The normals are the keys of the dictionary. e.g. to obtain all the OCCfaces that have normals (0,0,1), dictionar[ (0,0,1)]
    """
    normal_face_dict = {}
    for occface in occface_list:
        n = face_normal(occface)
        n = (round(n[0],6), round(n[1],6), round(n[2],6))
        keys = normal_face_dict.keys()
        if n not in keys:
            normal_face_dict[n] = [occface]
        elif n in keys:
            normal_face_dict[n].append(occface)
            
    return normal_face_dict

#========================================================================================================
#SHELL INPUTS
#======================================================================================================== 
def is_shell_closed(occshell):
    """
    This function calculates if the OCCshell is closed.
 
    Parameters
    ----------
    occshell : OCCshell
        The OCCshell to be analysed.
        
    Returns
    -------
    True or False : bool
        If True OCCshell is closed, if False OCCshell is not closed.
    """
    shell_checker = BRepCheck_Shell(occshell)
    is_closed = shell_checker.Closed()
    if is_closed == BRepCheck_NoError:
        return True 
    else:
        return False 
#========================================================================================================
#SOLID INPUTS
#======================================================================================================== 
def solid_volume(occsolid):
    """
    This function calculates the volume of the OCCsolid.
 
    Parameters
    ----------
    occsolid : OCCsolid
        The OCCsolid to be analysed.
        
    Returns
    -------
    volume : float
        The volume of the solid.
    """
    props = GProp_GProps()
    brepgprop_VolumeProperties(occsolid, props)
    volume = props.Mass()
    return volume

def check_solid_inward(occsolid):
    """
    This function checks if all the OCCfaces of the OCCsolids is facing inwards.
 
    Parameters
    ----------
    occsolid : OCCsolid
        The OCCsolid to be analysed.
        
    Returns
    -------
    True or False : bool
        If True OCCsolid is facing inwards, if False OCCsolid is not facing inwards.
    """
    classify = BRepClass3d_SolidClassifier()
    classify.Load(occsolid)
    classify.PerformInfinitePoint(0.001)
    state = classify.State()
    if state == TopAbs_IN:
        return True 
    else:
        return False 
#========================================================================================================
#TOPOLOGY INPUTS
#======================================================================================================== 
def get_bounding_box(occtopology):
    """
    This function calculates the bounding box of the OCCtopology.
 
    Parameters
    ----------
    occtopology : OCCtopology
        The OCCtopology to be analysed.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    Returns
    -------
    xmin : float
        Minimum X-coordinate
        
    ymin : float
        Minimum Y-coordinate
        
    zmin : float
        Minimum Z-coordinate
        
    xmax : float
        Maximum X-coordinate
        
    ymax : float
        Maximum Y-coordinate
        
    zmax : float
        Maximum Z-coordinate
    """
    return Common.get_boundingbox(occtopology)
    
def get_centre_bbox(occtopology):
    """
    This function calculates the centre of the bounding box of the OCCtopology.
 
    Parameters
    ----------
    occtopology : OCCtopology
        The OCCtopology to be analysed.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    Returns
    -------
    centre point : pypt
        The centre point of the OCCtopology's bounding box.
    """
    occ_midpt = Common.center_boundingbox(occtopology)
    return (occ_midpt.X(), occ_midpt.Y(), occ_midpt.Z())
    
def minimum_distance(occtopology1, occtopology2):
    """
    This function calculates the minimum distance between the two OCCtopologies.
 
    Parameters
    ----------
    occtopology1 : OCCtopology
        The OCCtopology to be analysed.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    occtopology2 : OCCtopology
        The OCCtopology to be analysed.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    Returns
    -------
    minimum distance : float
        The minimum distance between the two topologies.
    """
    min_dist, min_dist_shp1, min_dist_shp2 = Common.minimum_distance(occtopology1, occtopology2)
    return min_dist

def project_shape_on_shape(occtopo_proj, occtopo_projon, tolerance = 1e-06):
    """
    This function project the occtopoproj (OCCtopology) onto the occtopoprojon (OCCtopology), and returns the list of projected points.
 
    Parameters
    ----------
    occtopo_proj : OCCtopology
        The OCCtopology to to project.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    occtopo_projon : OCCtopology
        The OCCtopology to be projected on.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    tolerance : float, optional
        The precision of the projection, Default = 1e-06.
        
    Returns
    -------
    list of projected points : pyptlist
        The list of projected points.
    """

    interpyptlist = []
    dss = BRepExtrema_DistShapeShape(occtopo_proj, occtopo_projon)
    dss.SetDeflection(tolerance)
    dss.Perform()
    min_dist = dss.Value()
    npts = dss.NbSolution()
    for i in range(npts):
        gppt = dss.PointOnShape2(i+1)
        pypt = (gppt.X(), gppt.Y(), gppt.Z())
        interpyptlist.append(pypt)
            
    return interpyptlist

def intersect_shape_with_ptdir(occtopology, pypt, pydir):
    """
    This function projects a point in a direction and calculates the at which point does the point intersects the OCCtopology.
 
    Parameters
    ----------
    occtopology : OCCtopology
        The OCCtopology to be projected on.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    pypt : tuple of floats
        The point to be projected. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    pydir : tuple of floats
        The direction of the point to be projected. A pydir is a tuple that documents the xyz vector of a dir e.g. (x,y,z)
        
    Returns
    -------
    intersection point : pypt
        The point in which the projected point intersect the OCCtopology. If None means there is no intersection.
    
    intersection face : OCCface
        The OCCface in which the projected point hits. If None means there is no intersection.
    """
    occ_line = gp_Lin(gp_Ax1(gp_Pnt(pypt[0], pypt[1], pypt[2]), gp_Dir(pydir[0], pydir[1], pydir[2])))
    shape_inter = IntCurvesFace_ShapeIntersector()
    shape_inter.Load(occtopology, 1e-6)
    shape_inter.PerformNearest(occ_line, 0.0, float("+inf"))
    if shape_inter.IsDone():
        npts = shape_inter.NbPnt()
        if npts !=0:
            return modify.occpt_2_pypt(shape_inter.Pnt(1)), shape_inter.Face(1)
        else:
            return None, None 
    else:
        return None, None 
#========================================================================================================
#OTHER INPUTS
#======================================================================================================== 
def cs_transformation(occ_gpax3_1, occ_gpax3_2):
    """
    This function maps a OCC coordinate system (occ_gpax3) to another OCC coordinate system (occ_gpax3).
 
    Parameters
    ----------
    occ_gpax3_1 : gp_Ax3
        The coordinate system to be mapped.
        
    occ_gpax3_2 : gp_Ax3
        The coordinate system to be mapped onto.
        
    Returns
    -------
    transformation : gp_Trsf
        The transformation for the mapping.
    """
    aTrsf = gp_Trsf()
    aTrsf.SetTransformation(occ_gpax3_1,occ_gpax3_2)
    return aTrsf