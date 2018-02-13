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
import calculate
import modify

from OCCUtils import face, Construct, Common
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid, BRepBuilderAPI_MakeWire
from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.gp import gp_Pnt, gp_Vec, gp_Lin, gp_Circ, gp_Ax1, gp_Ax2, gp_Dir, gp_Ax3
from OCC.ShapeAnalysis import ShapeAnalysis_FreeBounds
from OCC.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Section
from OCC.TopTools import TopTools_HSequenceOfShape, Handle_TopTools_HSequenceOfShape
from OCC.GeomAPI import GeomAPI_PointsToBSpline
from OCC.TColgp import TColgp_Array1OfPnt
from OCC.BRep import BRep_Builder, BRep_Tool
from OCC.TopoDS import TopoDS_Shell, TopoDS_Shape
from OCC.BRepMesh import BRepMesh_IncrementalMesh
from OCC.TopLoc import TopLoc_Location

#========================================================================================================
#NUMERIC & TEXT INPUTS
#========================================================================================================
def make_rectangle(xdim, ydim):
    """
    This function constructs an OCCface rectangle from the rectangle's breath and height.
 
    Parameters
    ----------
    xdim : float
        Breath of the rectangle.
        
    ydim : ydim
        Height of the rectangle.
        
    Returns
    -------
    rectangle : OCCface
        An OCCface rectangle constructed from the breath and height.
    """
    point_list = [((xdim/2.0)*-1, ydim/2.0, 0), (xdim/2.0, ydim/2.0, 0), (xdim/2.0, (ydim/2.0)*-1, 0), ((xdim/2.0)*-1, (ydim/2.0)*-1, 0)]
    face = make_polygon(point_list)
    return face

def make_box(length, width, height):
    """
    This function constructs a box based on the length, width and height.
 
    Parameters
    ----------
    length : float
        Length of box
        
    width : float
        Width of box
        
    height : float
        Height of box.
        
    Returns
    -------
    box : OCCsolid
        OCCsolid box constructed based on the length, width and height.
    """
    box = fetch.topo2topotype(BRepPrimAPI_MakeBox(length,width,height).Shape())
    return box

def make_brep_text(text_string, font_size):
    """
    This function constructs a OCCcompound 3D text from a string.
 
    Parameters
    ----------
    text_string : str
        The string to be converted.
        
    font_size : int
        The font size.
 
    Returns
    -------
    3D text : OCCcompound
        An OCCcompound of the 3D text.
    """
    from OCC.Addons import text_to_brep, Font_FA_Bold
    brepstr = text_to_brep(text_string, "Arial", Font_FA_Bold, font_size, True)
    return brepstr

#========================================================================================================
#POINT INPUTS
#========================================================================================================    
def make_vertex(pypt):
    """
    This function constructs an OCCvertex.
 
    Parameters
    ----------
    pypt : tuple of floats
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
 
    Returns
    -------
    vertex : OCCvertex
        An OCCvertex constructed from the point
    """
    gppt = make_gppnt(pypt)
    vert = Construct.make_vertex(gppt)
    return vert

def make_plane_w_dir(centre_pypt, normal_pydir):
    """
    This function constructs a OCCface plane from a centre pt and the normal direction of the plane.
 
    Parameters
    ----------
    centre_pypt : tuple of floats
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    normal_pydir : tuple of floats
        A pydir is a tuple that documents the xyz vector of a dir e.g. (x,y,z)
        
    Returns
    -------
    plane : OCCface
        An OCCface constructed from the point and direction
    """
    plane_face = Construct.make_plane(center=gp_Pnt(centre_pypt[0],centre_pypt[1],centre_pypt[2]), 
                         vec_normal = gp_Vec(normal_pydir[0], normal_pydir[1], normal_pydir[2]))
    return plane_face

def make_circle(centre_pypt, normal_pydir, radius):
    """
    This function constructs an OCCedge circle based on the centre point, the orientation direction and the radius.
 
    Parameters
    ----------
    centre_pypt : tuple of floats
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    normal_pydir : tuple of floats
        A pydir is a tuple that documents the xyz vector of a dir e.g. (x,y,z)
        
    radius : float
        Radius of the circle.
        
    Returns
    -------
    circle : OCCedge
        An OCCedge circle.
    """    
    if radius <1:
        circle = gp_Circ(gp_Ax2(gp_Pnt(centre_pypt[0], centre_pypt[1], centre_pypt[2]), gp_Dir(normal_pydir[0], normal_pydir[1], normal_pydir[2])), 1)
        circle_edge = BRepBuilderAPI_MakeEdge(circle, 0, circle.Length())
        circle_edge = fetch.topo2topotype(modify.scale(circle_edge, radius, centre_pypt))
        
    else:
        circle = gp_Circ(gp_Ax2(gp_Pnt(centre_pypt[0], centre_pypt[1], centre_pypt[2]), gp_Dir(normal_pydir[0], normal_pydir[1], normal_pydir[2])), radius)
        circle_edge = BRepBuilderAPI_MakeEdge(circle, 0, circle.Length())
    
    return circle_edge.Edge()

def make_polygon_circle(centre_pypt, normal_pydir, radius, division = 10):
    """
    This function constructs an polygon circle based on the centre point, the orientation direction and the radius.
 
    Parameters
    ----------
    centre_pypt : tuple of floats
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    normal_pydir : tuple of floats
        A pydir is a tuple that documents the xyz vector of a dir e.g. (x,y,z)
        
    radius : float
        Radius of the circle.
        
    distance : float, optional
        The smallest distance between two points from the edges, Default = 0.01. 
        The further the distance the less precise is the resultant faces.
        
    Returns
    -------
    circle : OCCedge
        An OCCedge circle.
    """
    if radius <1:
        ref_c = make_circle(centre_pypt, normal_pydir, 1)
        lb, ub = fetch.edge_domain(ref_c)
        domain = ub - lb
        interval = domain/float(division)
        pt_list = []
        for i in range(division):
            parm = i*interval
            pt = calculate.edgeparameter2pt(parm, ref_c)
            pt_list.append(pt)
            
        poly_c = make_polygon(pt_list)
        circle = fetch.topo2topotype(modify.scale(poly_c, radius, centre_pypt))
        return circle
    else:
        circle = make_circle(centre_pypt, normal_pydir, radius)
        lb, ub = fetch.edge_domain(circle)
        domain = ub - lb
        interval = domain/float(division)
        pt_list = []
        for i in range(division):
            parm = i*interval
            pt = calculate.edgeparameter2pt(parm, circle)
            pt_list.append(pt)
            
        poly_c = make_polygon(pt_list)
        return poly_c
    
def make_edge(pypt1, pypt2):
    """
    This function constructs an OCCedge from two points.
 
    Parameters
    ----------
    pypt1 : tuple of floats
        The starting pt of the edge. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    pypt2 : tuple of floats
        The last pt of the edge. A pydir is a tuple that documents the xyz vector of a dir e.g. (x,y,z)
        
    Returns
    -------
    edge : OCCedge
        An OCCedge constructed from the two points
    """
    gp_point1 = gp_Pnt(pypt1[0], pypt1[1], pypt1[2])
    gp_point2 = gp_Pnt(pypt2[0], pypt2[1], pypt2[2])
        
    make_edge = BRepBuilderAPI_MakeEdge(gp_point1, gp_point2)
    return make_edge.Edge()

def make_vector(pypt1,pypt2):
    """
    This function create a OCCvector from two points.
 
    Parameters
    ----------
    pypt1 : tuple of floats
        The starting pt of the vector. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    pypt2 : tuple of floats
        The last pt of the vector. A pydir is a tuple that documents the xyz vector of a dir e.g. (x,y,z)
    
    Returns
    -------
    vector : OCCvector(gp_Vec)
        The OCCvector(gp_Vec).
    """
    gp_pt1 = gp_Pnt(pypt1[0],pypt1[1],pypt1[2])
    gp_pt2 = gp_Pnt(pypt2[0],pypt2[1],pypt2[2])
    gp_vec = gp_Vec(gp_pt1, gp_pt2)
    return gp_vec

def make_gp_ax3(pypt, pydir):  
    """
    This function constructs a OCC coordinate system (gp_ax3) with a point and direction.
 
    Parameters
    ----------
    pypt : tuple of floats
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    pydir : tuple of floats
        A pydir is a tuple that documents the xyz vector of a dir e.g. (x,y,z)
        
    Returns
    -------
    coordinate system : OCC coordinate (gp_ax3)
        An OCC coordinate system (gp_ax3) constructed from the point and direction.
    """
    gp_ax3 = gp_Ax3(gp_Pnt(pypt[0], pypt[1], pypt[2]), gp_Dir(pydir[0], pydir[1], pydir[2]))
    return gp_ax3

def make_gppnt(pypt):
    """
    This function constructs a OCC point (gp_pnt) with a point.
 
    Parameters
    ----------
    pypt : tuple of floats
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    Returns
    -------
    OCC point : OCC point (gp_pnt)
        An OCC point (gp_pnt) constructed from the point.
    """
    return gp_Pnt(pypt[0], pypt[1], pypt[2])
    
    
def make_line(pypt, pydir):
    """
    This function constructs a OCC line (gp_lin) with a point and direction.
 
    Parameters
    ----------
    pypt : tuple of floats
        The starting point of the line. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    pydir : tuple of floats
        The direction of the line. A pydir is a tuple that documents the xyz vector of a dir e.g. (x,y,z)
        
    Returns
    -------
    line : OCC line (gp_lin)
        An OCC line (gp_lin) constructed from the point and direction.
    """
    occ_line = gp_Lin(gp_Ax1(gp_Pnt(pypt[0], pypt[1], pypt[2]), gp_Dir(pydir[0], pydir[1], pydir[2])))
    return occ_line

def make_occvertex_list(pyptlist):
    """
    This function constructs a list of OCCvertices.
 
    Parameters
    ----------
    pyptlist : a list of tuples
        List of points to be converted. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    Returns
    -------
    list of points : list of OCCvertices.
        A list of OCCvertices converted from the list of points.
    """
    vertlist = []
    for pypt in pyptlist:
        vert = make_vertex(pypt)
        vertlist.append(vert)
    return vertlist

def make_gppnt_list(pyptlist):
    """
    This function constructs a list of OCC points (gp_pnt).
 
    Parameters
    ----------
    pyptlist : a list of tuples
        List of points to be converted. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    Returns
    -------
    list of OCC points : list of OCC points (gp_pnt)
        A list of OCC points (gp_pnt) converted from the list of points.
    """
    gpptlist = []
    for pypt in pyptlist:
        gpptlist.append(make_gppnt(pypt))
    return gpptlist

def make_polygon(pyptlist):
    """
    This function constructs a OCCface polygon from a list of points.
 
    Parameters
    ----------
    pyptlist : a list of tuples
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
 
    Returns
    -------
    polygon : OCCface
        An OCCface constructed from the list of points
    """
    array = []
    for pt in pyptlist:
        array.append(gp_Pnt(pt[0],pt[1],pt[2]))

    poly = BRepBuilderAPI_MakePolygon()
    map(poly.Add, array)
    poly.Build()
    poly.Close()
    
    wire = poly.Wire()
    occface = BRepBuilderAPI_MakeFace(wire)
    return occface.Face()
    
    
def make_bspline_edge(pyptlist, mindegree=3, maxdegree = 8):
    """
    This function constructs an bspline OCCedge from a list of points.
 
    Parameters
    ----------
    pyptlist : a list of tuples
        List of points for constructing the edge. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    mindegree : int, optional
        The minimun degree of the bspline curve. Default = 3.
        
    maxdegree : int, optional
        The maximum degree of the bspline curve. Default = 8. 
        
    Returns
    -------
    edge : OCCedge
        An OCCedge constructed from the list of points
    """
    array = TColgp_Array1OfPnt(1, len(pyptlist))
    pcnt = 1
    for pypt in pyptlist:
        gppt = make_gppnt(pypt)
        array.SetValue(pcnt, gppt)
        pcnt+=1
    bcurve =GeomAPI_PointsToBSpline(array,mindegree,maxdegree).Curve()
    curve_edge = BRepBuilderAPI_MakeEdge(bcurve)
    return curve_edge.Edge()
    
def make_bspline_edge_interpolate(pyptlist, is_closed):
    """
    This function constructs an bspline OCCedge from a list of points.
 
    Parameters
    ----------
    pyptlist : a list of tuples
        List of points for constructing the edge. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    is_closed : bool
        True or False whether the edge constructed should be opened or closed.
        
    Returns
    -------
    edge : OCCedge
        An OCCedge constructed from the list of points. The edge is opened or closed as specified.
    """
    gpptlist = make_gppnt_list(pyptlist)
    bcurve = Common.interpolate_points_to_spline_no_tangency(gpptlist, closed=is_closed)
    curve_edge = BRepBuilderAPI_MakeEdge(bcurve)
    return curve_edge.Edge()
    
def make_wire(pyptlist):
    """
    This function constructs an OCCwire from a list of points.For a closed wire, the last point needs to be the same as the first point.
 
    Parameters
    ----------
    pyptlist : a list of tuples
        List of points for constructing the wire. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z),
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    Returns
    -------
    wire : OCCwire
        An OCCwire constructed from the list of points.
    """
    array = []
    for pt in pyptlist:
        array.append(gp_Pnt(pt[0],pt[1],pt[2]))

    poly = BRepBuilderAPI_MakePolygon()
    map(poly.Add, array)
    poly.Build()
    wire = poly.Wire()
    return wire

def circles_frm_pyptlist(pyptlist, radius):
    """
    This function constructs a list of OCCedge circles based on the list of centre points and the radius.
 
    Parameters
    ----------
    pyptlist : a list of tuples
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    radius : float
        Radius of the circles.
        
    Returns
    -------
    list of circles : list of OCCedge
        List of  OCCedge circles.
    """
    circlelist = []
    gpptlist = make_gppnt_list(pyptlist)
    for gppt in gpptlist:
        circle = make_circle((gppt.X(),gppt.Y(),gppt.Z()), (0,0,1), radius)
        circlelist.append(circle)
    return circlelist
    
def delaunay3d(pyptlist, tolerance = 1e-06):
    """
    This function constructs a mesh (list of triangle OCCfaces) from a list of points. Currently only works for two dimensional xy points.
 
    Parameters
    ----------
    pyptlist : a list of tuples
        The list of points to be triangulated. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    tolerance : float, optional
        The minimal surface area of each triangulated face, Default = 1e-06.. Any faces smaller than the tolerance will be deleted.
 
    Returns
    -------
    list of face : list of OCCfaces
        A list of meshed OCCfaces (triangles) constructed from the meshing.
    """
    import numpy as np
    from scipy.spatial import Delaunay
    pyptlistx = []
    pyptlisty = []
    pyptlistz = []
    
    for pypt in pyptlist:
        pyptlistx.append(pypt[0])
        pyptlisty.append(pypt[1])
        pyptlistz.append(pypt[2])
        
    # u, v are parameterisation variables
    u = np.array(pyptlistx) 
    v = np.array(pyptlisty) 
    
    x = u
    y = v
    z = np.array(pyptlistz)
    
    # Triangulate parameter space to determine the triangles
    tri = Delaunay(np.array([u,v]).T)
    
    occtriangles = []
    xyz = np.array([x,y,z]).T
    for verts in tri.simplices:
        pt1 = list(xyz[verts[0]])
        pt2 = list(xyz[verts[1]])
        pt3 = list(xyz[verts[2]])
        occtriangle = make_polygon([pt1,pt2,pt3])
        tri_area = calculate.face_area(occtriangle)
        if tri_area > tolerance:
            occtriangles.append(occtriangle)
    return occtriangles

def convex_hull3d(pyptlist, return_area_volume = False ):
    """
    This function constructs a convex hull (list of triangle OCCfaces) from a list of points. The points cannot be coplanar.
 
    Parameters
    ----------
    pyptlist : a list of tuples
        The list of points to be triangulated. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    return_area_volume : bool, optional
        If set to True, will only return the area and volume of the hull and not the faces, default = False
 
    Returns
    -------
    list of face : list of OCCfaces
        A list of meshed OCCfaces (triangles) constructed from the hull. Return faces only when return_area_volume == False.
    
    hull area : float
        Area of hull. Return area only when return_area_volume == True.
        
    hull volume : float
        Volume of hull. Return volume only when return_area_volume == True.
    """
    import numpy as np
    from scipy.spatial import ConvexHull
    points = np.array(pyptlist)
    hull = ConvexHull(points)
    if return_area_volume:
        hull_area = hull.area
        hull_volume = hull.volume
        return hull_area, hull_volume
    else:
        face_list = []
        for simplex in hull.simplices:
            pt1 = list(points[simplex[0]])
            pt2 = list(points[simplex[1]])
            pt3 = list(points[simplex[2]])
            face = make_polygon([pt1,pt2,pt3])
            face_list.append(face)
        
        return face_list

def convex_hull2d(pyptlist):
    """
    This function constructs a 2d convex hull (list of triangle OCCfaces) from a list of points. Only work on 2d xy points.
 
    Parameters
    ----------
    pyptlist : a list of tuples
        The list of points to be triangulated. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
 
    Returns
    -------
    face : OCCface
        A OCCface polygon constructed from the hull. Return faces only when return_area == False.
        
    """
    import numpy as np
    from scipy.spatial import ConvexHull
    pyptlist2d = []
    occvert_list = []
    for pypt in pyptlist:
        pypt2d = (pypt[0],pypt[1])
        occvert = make_vertex(pypt)
        occvert_list.append(occvert)
        pyptlist2d.append(pypt2d)
        
    cmpd = make_compound(occvert_list)
    centre_pt = calculate.get_centre_bbox(cmpd)
    
    points = np.array(pyptlist2d)
    hull = ConvexHull(points)

    verts = hull.vertices
    hull_pt_list = []
    for v in verts:
        pt = pyptlist[v]
        pt2 = (pt[0],pt[1], centre_pt[2])
        hull_pt_list.append(pt2)
    face = make_polygon(hull_pt_list)
    
    return face
    
#========================================================================================================
#EDGE INPUTS
#========================================================================================================
def extrude_edge(occedge, pydir, magnitude):
    """
    This function creates an extruded OCCface from an OCCedge.
 
    Parameters
    ----------
    occedge : OCCedge
        The OCCedge to be extruded.
        
    pydir : tuple of floats
        The direction of the extrusion. A pydir is a tuple that documents the xyz vector of a dir e.g. (x,y,z)
    
    magnitude : float
        The magnitude of the extrusion.
        
    Returns
    -------
    face : OCCface
        An OCCface constructed from the extrusion.
    """
    edge_midpt = calculate.edge_midpt(occedge)
    location_pt = modify.move_pt(edge_midpt, pydir, magnitude)
    edge2 = fetch.topo2topotype(modify.move(edge_midpt, location_pt, occedge))
    edge_wire = make_wire_frm_edges([occedge])
    edge_wire2 = make_wire_frm_edges([edge2])
    edgeface = make_loft_with_wires([edge_wire,edge_wire2])
    facelist = fetch.topo_explorer(edgeface, "face")
    return facelist[0]

def make_wire_frm_edges(occedge_list):
    """
    This function constructs an OCCwire from a list of OCCedges.
 
    Parameters
    ----------
    occedge_list : a list of OCCedges
        List of OCCedge for constructing the wire.
        
    Returns
    -------
    wire : OCCwire
        An OCCwire constructed from the list of OCCedge.
    """
    wire = Construct.make_wire(occedge_list)
    return wire

def faces_frm_loose_edges(occedge_list):
    """
    This function creates a list of OCCfaces from a list of OCCedges. The edges need to be able to form a close face. 
    It does not work with a group of open edges.
 
    Parameters
    ----------
    occedge_list : list of OCCedges
        The list of OCCedges for creating the list of OCCfaces. 
        
    Returns
    -------
    list of faces : list of OCCfaces
        A list of OCCfaces constructed from the list of OCCedges.
    """
    edges = TopTools_HSequenceOfShape()
    edges_handle = Handle_TopTools_HSequenceOfShape(edges)
    
    wires = TopTools_HSequenceOfShape()
    wires_handle = Handle_TopTools_HSequenceOfShape(wires)
    
    # The edges are copied to the sequence
    for edge in occedge_list: edges.Append(edge)
                
    # A wire is formed by connecting the edges
    ShapeAnalysis_FreeBounds.ConnectEdgesToWires(edges_handle, 1e-05, False, wires_handle)
    wires = wires_handle.GetObject()
        
    # From each wire a face is created
    face_list = []
    for i in range(wires.Length()):
        wire_shape = wires.Value(i+1)
        wire_shape = modify.fix_shape(wire_shape)
        wire = fetch.topo2topotype(wire_shape)            
        #visualise([edges], ['BLUE'])
        occface = BRepBuilderAPI_MakeFace(wire).Face()
        
        if not occface.IsNull():
            f_occface = modify.fix_face(occface)
            face_list.append(f_occface)
    return face_list

def faces_frm_loose_edges2(occedge_list, roundndigit = 6, distance = 0.1):
    """
    This function creates a list of OCCfaces from a list of OCCedges. The edges need to be able to form a close face. 
    It does not work with a group of open edges. wire_frm_loose_edges2 are for more complex geometries.
 
    Parameters
    ----------
    occedge_list : list of OCCedges
        The list of OCCedges for creating the list of OCCfaces.
    
    roundndigit : int, optional
        The number of decimal places of the xyz of the points, Default = 6. The higher the number the more precise are the points.
        Depending on the precision of the points, it will decide whether the edges are connected.
        
    distance : float, optional
        The smallest distance between two points from the edges, Default = 0.01. 
        The further the distance the less precise is the resultant faces.
        
    Returns
    -------
    list of faces : list of OCCfaces
        A list of OCCfaces constructed from the list of OCCedges.
    """
    edges = TopTools_HSequenceOfShape()
    edges_handle = Handle_TopTools_HSequenceOfShape(edges)
    
    wires = TopTools_HSequenceOfShape()
    wires_handle = Handle_TopTools_HSequenceOfShape(wires)
    
    # The edges are copied to the sequence
    for edge in occedge_list: edges.Append(edge)
                
    # A wire is formed by connecting the edges
    ShapeAnalysis_FreeBounds.ConnectEdgesToWires(edges_handle, 1e-05, False, wires_handle)
    wires = wires_handle.GetObject()
        
    # From each wire a face is created
    face_list = []
    for i in range(wires.Length()):
        wire_shape = wires.Value(i+1)
        wire = fetch.topo2topotype(wire_shape)
        #occface = BRepBuilderAPI_MakeFace(wire).Face()
        #occface = modify.fix_face(occface)
        #fixed_wire = modify.fix_closed_wire(wire, occface, tolerance = 1e-06)
        pyptlist = fetch.points_frm_wire(wire)
        pyptlist = modify.rmv_duplicated_pts(pyptlist, roundndigit = roundndigit)
        pyptlist = modify.rmv_duplicated_pts_by_distance(pyptlist, distance = distance)
        npts = len(pyptlist)
        if npts >=3:
            occface = make_polygon(pyptlist)
            if not occface.IsNull():
                face_list.append(occface)
                
    diff_list = []
    cnt =0
    for occface in face_list:
        face_list2 = face_list[:]
        del face_list2[cnt]
        extrude_list = []
        for face2 in face_list2:
            midpt = calculate.face_midpt(face2)
            loc_pt = modify.move_pt(midpt, (0,0,-1),0.3)
            #move the face down
            m_occface = modify.move(midpt, loc_pt, face2)
            m_occface = fetch.topo2topotype(m_occface)
            #extrude the face
            extrude_solid = extrude(m_occface, (0,0,1), 0.6)
            extrude_list.append(extrude_solid)
            
        cmpd = make_compound(extrude_list)
        diff_cmpd = boolean_difference(occface, cmpd)
        diff_face_list = fetch.topo_explorer(diff_cmpd, "face")
        #diff_face_list = simple_mesh(diff_cmpd)
        if diff_face_list:
            diff_list.extend(diff_face_list)
        cnt+=1
                        
    return diff_list
    
def arrange_edges_2_wires(occedge_list, isclosed = False):
    """
    This function creates a list of OCCwires from a list of OCCedges. The edges does not need to form a close face. 
 
    Parameters
    ----------
    occedge_list : list of OCCedges
        The list of OCCedges for creating the list of OCCwires.
    
    isclosed : bool, optional
        True or False, is the resultant wires suppose to be closed or opened.
        
    Returns
    -------
    list of wires : list of OCCwires
        A list of OCCwires constructed from the list of OCCedges.
    """
    from OCC.TopoDS import topods 
    from OCC.TopExp import topexp
    from OCC.BRep import BRep_Tool
    from OCC.ShapeAnalysis import ShapeAnalysis_WireOrder
    from OCC.BRepBuilderAPI import BRepBuilderAPI_WireDone, BRepBuilderAPI_EmptyWire, BRepBuilderAPI_DisconnectedWire, BRepBuilderAPI_NonManifoldWire
    
    wb_errdict={BRepBuilderAPI_WireDone:"No error", BRepBuilderAPI_EmptyWire:"Empty wire", BRepBuilderAPI_DisconnectedWire:"disconnected wire",
    BRepBuilderAPI_NonManifoldWire:"non-manifold wire"}
    
    sawo_statusdict={0:"all edges are direct and in sequence",
    1:"all edges are direct but some are not in sequence",
    2:"unresolved gaps remain",
    -1:"some edges are reversed, but no gaps remain",
    -2:"some edges are reversed and some gaps remain",
    -10:"failure on reorder"}
    
    mode3d = True
    tolerance = 1e-06
    SAWO = ShapeAnalysis_WireOrder(mode3d, tolerance) #precision.PConfusion()
    
    for edge in occedge_list:
        V1 = topexp.FirstVertex(topods.Edge(edge))
        V2 = topexp.LastVertex(topods.Edge(edge))
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
        SAWO.SetChains(tolerance)
        wirelist = []
        #print "Number of chains: ", SAWO.NbChains()
        
        for i in range(SAWO.NbChains()):
            wirebuilder = BRepBuilderAPI_MakeWire()
            estart, eend = SAWO.Chain(i+1)
            #print "Number of edges in chain", i, ": ", eend - estart + 1
            if (eend - estart + 1)==0:
                continue
            for j in range(estart, eend+1):
                idx = abs(SAWO.Ordered(j)) # wirebuilder = s_addToWireBuilder(wirebuilder, edgelist[idx-1])
                edge2w = occedge_list[idx-1]
                wirebuilder.Add(edge2w)
                if wirebuilder is None:
                    raise RuntimeError, " build wire: Error adding edge number " + str(j+1) + " to Wire number " + str(i)
                    err = wirebuilder.Error()
                    if err != BRepBuilderAPI_WireDone:
                        raise RuntimeError, "Overlay2D: build wire: Error adding edge number " + str(j+1) + " to Wire number " + str(i) +": \n" + wb_errdict[err]
                        try:
                            wirebuilder.Build()
                            aWire = wirebuilder.Wire()
                            wirelist.append(aWire)
                        except Exception, err:
                            raise RuntimeError, "Overlay2D: build wire: Creation of Wire number " + str(i) + " from edge(s) failed. \n" + str(err)
            
            print wirebuilder
            wirebuilder.Build()
            aWire = wirebuilder.Wire()
            wirelist.append(aWire)
            
    return wirelist
    
#========================================================================================================
#WIRE INPUTS
#========================================================================================================
def make_loft_with_wires(occwire_list):
    """
    This function lofts a list of OCCwires.
 
    Parameters
    ----------
    occwire_list : a list of OCCwires
        List of OCCwires for the loft.
        
    Returns
    -------
    shape : OCCshape
        An OCCshape constructed from lofting the list of OCCwires.
    """
    loft = Construct.make_loft(occwire_list, ruled = False)
    return loft

def make_face_frm_wire(occwire):
    """
    This function creates an OCCface from an OCCwire.
 
    Parameters
    ----------
    occwire : OCCwire
        The OCCwire for creating the OCCface. 
        
    Returns
    -------
    face : OCCface
        An OCCface constructed from the OCCwire.
    """
    occface = BRepBuilderAPI_MakeFace(occwire).Face()
    if not occface.IsNull():    
        return occface
    
#========================================================================================================
#FACE INPUTS
#========================================================================================================
def make_offset(occface, offset_value):
    """
    This function offsets an OCCface.
 
    Parameters
    ----------
    occface : OCCface
        OCCface to be offset
        
    offset_value : float
        The offset value. A negative value will offset the circle inwards, while a positive value will offset it outwards.
    
    Returns
    -------
    offset face : OCCface
        The offsetted OCCface.
    """
    o_wire = Construct.make_offset(occface, offset_value)
    o_face = BRepBuilderAPI_MakeFace(o_wire)
    return o_face.Face()
    
def make_offset_face2wire(occface, offset_value):
    """
    This function offsets an OCCface and return the wire instead of the face.
 
    Parameters
    ----------
    occface : OCCface
        OCCface to be offset
        
    offset_value : float
        The offset value. A negative value will offset the circle inwards, while a positive value will offset it outwards.
    
    Returns
    -------
    offset wire : OCCwire
        The offsetted OCCwire.
    """
    o_wire = Construct.make_offset(occface, offset_value)
    return fetch.topo2topotype(o_wire)

def grid_face(occface, udim, vdim):
    """
    This function creates a list of OCCfaces grids from an OCCface. The OCCface must be planar.
 
    Parameters
    ----------
    occface : OCCface
        The OCCface to be gridded.
        
    udim : int
        The number of rows of the grid.
    
    vdim : int
        The number of columns of the grid.
        
    Returns
    -------
    grids : list of OCCfaces
        A list of OCCfaces constructed from the gridding.
    """
    #returns a series of polygons 
    pt_list = []
    face_list = []
    fc = face.Face(occface)
    umin, umax, vmin, vmax = fc.domain()
    u_div = int(math.ceil((umax-umin)/udim))
    v_div = int(math.ceil((vmax-vmin)/vdim))
    for ucnt in range(u_div+1):
        for vcnt in range(v_div+1):
            u = umin + (ucnt*udim)
            v = vmin + (vcnt*vdim)
            occpt = fc.parameter_to_point(u,v)
            pt = [occpt.X(),occpt.Y(),occpt.Z()]
            pt_list.append(pt)

    for pucnt in range(u_div):
        for pvcnt in range(v_div):
            pcnt = pucnt*(v_div+1) + pvcnt
            #print pcnt
            pt1 = pt_list[pcnt]
            pt2 = pt_list[pcnt+v_div+1]
            pt3 = pt_list[pcnt+v_div+2]
            pt4 = pt_list[pcnt+1]
            occface1 = make_polygon([pt1, pt2, pt3, pt4])
            face_list.append(occface1)
       
    #intersect the grids and the face so that those grids that are not in the face will be erase
    
    intersection_list = []
    for f in face_list:
        intersection = BRepAlgoAPI_Common(f, occface).Shape()
        compound = fetch.topo2topotype(intersection)
        inter_face_list = fetch.topo_explorer(compound, "face")
        if inter_face_list:
            for inter_face in inter_face_list:
                intersection_list.append(inter_face)

    return intersection_list
    
def extrude(occface, pydir, magnitude):
    """
    This function creates an extruded OCCsolid from an OCCface.
 
    Parameters
    ----------
    occface : OCCface
        The OCCface to be extruded.
        
    pydir : tuple of floats
        The direction of the extrusion. A pydir is a tuple that documents the xyz vector of a dir e.g. (x,y,z)
    
    magnitude : float
        The magnitude of the extrusion.
        
    Returns
    -------
    list of shell : list of OCCshells
        An OCCsolid constructed from the extrusion.
    """
    orig_pt = calculate.face_midpt(occface)
    dest_pt = modify.move_pt(orig_pt, pydir, magnitude)
    wire_list =  fetch.topo_explorer(occface,"wire")
    nwire = len(wire_list)
    if nwire > 1:
        #clockwise = hole
        #anticlockwise = face
        hole_solid_list = []
        face_extrude_list = []
        face_nrml = calculate.face_normal(occface)
        
        for wire in wire_list:
            #first check if there are holes and which wire are holes
            pyptlist = fetch.points_frm_wire(wire)
            is_anticlockwise = calculate.is_anticlockwise(pyptlist, face_nrml)
            #create face from the wires
            wire_face = make_face_frm_wire(wire)
            
            moved_face = modify.move(orig_pt,dest_pt, wire_face)
            moved_face = fetch.topo2topotype(moved_face)
            #create solid from the faces
            loft = make_loft([wire_face, moved_face])
            face_list = fetch.topo_explorer(loft, "face")
            face_list.append(wire_face)
            face_list.append(moved_face)
            
            shell = sew_faces(face_list)[0]
            solid = make_solid(shell)
            solid = modify.fix_close_solid(solid)
            
            if not is_anticlockwise:
                hole_solid_list.append(solid)
            else:
                face_extrude_list.append(solid)
                
        extrude_cmpd = make_compound(face_extrude_list)
        hole_cmpd = make_compound(hole_solid_list)
        diff_cmpd = boolean_difference(extrude_cmpd, hole_cmpd)
        solid_list = fetch.topo_explorer(diff_cmpd, "solid")
        return solid_list[0]
    else:
        moved_face = modify.move(orig_pt,dest_pt, occface)
        loft = make_loft([occface, moved_face])
        face_list = fetch.topo_explorer(loft, "face")
        face_list.append(occface)
        face_list.append(moved_face)
        shell = sew_faces(face_list)[0]
        solid = make_solid(shell)
        solid = modify.fix_close_solid(solid)
        return solid
    
def merge_faces(occface_list, tolerance = 1e-06 ):
    """
    This function creates a list of merged OCCfaces from a list of OCCfaces. The function loops through the OCCfaces to search for all possible
    connected faces and merged them into a single face.
 
    Parameters
    ----------
    occface_list : a list of OCCfaces
        List of OCCfaces that will be looped through in search of all possible connected faces.
        
    tolerance : float, optional
        The minimal tolerance to decide if two faces are connected, Default = 1e-06.
        
    Returns
    -------
    list of face : list of OCCfaces
        A list of merged OCCfaces constructed from the list of OCCfaces.
    """
    sew = BRepBuilderAPI_Sewing(tolerance)
    for shp in occface_list:
        if isinstance(shp, list):
            for i in shp:
                sew.Add(i)
        else:
            sew.Add(shp)
            
    sew.Perform()
    nfreeedge = sew.NbFreeEdges()
    free_edges = []
    for fe_cnt in range(nfreeedge):
        free_edges.append(sew.FreeEdge(fe_cnt+1))
    face_list = faces_frm_loose_edges(free_edges)
    return face_list

def make_loft(occface_list, rule_face = True, tolerance = 1e-06):
    """
    This function lofts a list of OCCfaces.
 
    Parameters
    ----------
    occface_list : a list of OCCfaces
        List of OCCfaces for the loft.
        
    rule_face : bool, optional
        True or False, Default = True. Specify if the loft is a ruled face.
    
    tolerance : float, optional
        Specify the tolerance of the loft, Default = 1e-06.
        
    Returns
    -------
    shape : OCCshape
        An OCCshape constructed from lofting the list of OCCfaces.
    """
    #get the wires from the face_list
    wire_list = []
    for f in occface_list:
        wires = fetch.wires_frm_face(f)
        wire_list.extend(wires)
        
    loft = Construct.make_loft(wire_list, ruled = rule_face, tolerance = tolerance )
    return loft
    
def make_shell(occface_list):
    """
    This function creates an OCCshell from a list of OCCfaces. The OCCfaces in the shell might not be connected. 
    For creating an OCCshell that is definitely connected please use sew_faces function.
 
    Parameters
    ----------
    occface_list : a list of OCCfaces
        List of OCCfaces for the shell.
        
    Returns
    -------
    shell : OCCshell
        An OCCshell constructed from the list of OCCfaces.
    """
    builder = BRep_Builder()
    shell = TopoDS_Shell()
    builder.MakeShell(shell)
    for occface in occface_list:
        builder.Add(shell, occface)
        
    return shell
    
def sew_faces(occface_list, tolerance = 1e-06):
    """
    This function creates a list of OCCshells from a list of OCCfaces. The function loops through the OCCfaces to search for all possible
    shells that can be created from the faces.
 
    Parameters
    ----------
    occface_list : a list of OCCfaces
        List of OCCfaces that will be looped through in search of all possible shells.
        
    tolerance : float, optional
        Specify the tolerance of the sewing, Default = 1e-06.
        
    Returns
    -------
    list of shell : list of OCCshells
        A list of OCCshells constructed from the list of OCCfaces.
    """
    #make shell
    sewing = BRepBuilderAPI_Sewing()
    sewing.SetTolerance(tolerance)
    for f in occface_list:
        sewing.Add(f)
        
    sewing.Perform()
    sewing_shape = fetch.topo2topotype(sewing.SewedShape())
    shell_list = fetch.topo_explorer(sewing_shape, "shell")
    return shell_list
    
def make_occfaces_frm_pypolygons(pypolygon_list):
    """
    This function creates a list of OCCfaces from a list of polygons.
 
    Parameters
    ----------
    pypolygon_list : a 2d list of tuples
        List of polygon for constructing the list of faces. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z). 
        A pypolygon is a list of pypt that forms a polygon e.g. [(x1,y1,z1), (x2,y2,z2), ...].
        A pypolygon_list is a 2d list of tuples e.g. [[(x11,y11,z11), (x12,y12,z12), ...], [(x21,y21,z21), (x22,y22,z22), ...], ...]
                
    Returns
    -------
    list of faces : list of OCCfaces
        A list of OCCfaces constructed from the list of pypolygons.
    """
    face_list = []
    for polygon_pts in pypolygon_list:
        face = make_polygon(polygon_pts)
        face_list.append(face)
    return face_list
    
def make_occsolid_frm_pypolygons(pypolygon_list):
    """
    This function creates a OCCsolid from a list of connected polygons.
 
    Parameters
    ----------
    pypolygon_list : a 2d list of tuples
        List of connected polygon for constructing the OCCsolid. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z). 
        A pypolygon is a list of pypt that forms a polygon e.g. [(x1,y1,z1), (x2,y2,z2), ...].
        A pypolygon_list is a 2d list of tuples e.g. [[(x11,y11,z11), (x12,y12,z12), ...], [(x21,y21,z21), (x22,y22,z22), ...], ...]
                
    Returns
    -------
    solid : OCCsolid
        An OCCsolid constructed from the list of pypolygons.
    """
    face_list = make_occfaces_frm_pypolygons(pypolygon_list)
    #make shell
    shell_list = sew_faces(face_list)
    shell = shell_list[0]
    shell = modify.fix_shell_orientation(shell)
    
    solid = make_solid(shell)
    solid = modify.fix_close_solid(solid)
    return solid
    
#========================================================================================================
#SHELL INPUTS
#========================================================================================================
def make_solid(occshell):
    """
    This function creates a OCCsolid from a OCCshell.
 
    Parameters
    ----------
    occshell : OCCshell
        A closed OCCshell to be converted into OCCsolid.
                
    Returns
    -------
    solid : OCCsolid
        An OCCsolid constructed from the closed OCCshell.
    """
    ms = BRepBuilderAPI_MakeSolid()
    ms.Add(occshell)
    return ms.Solid()
    
def make_solid_from_shell_list(occshell_list):
    """
    This function creates a OCCsolid from a list of connected OCCshell.
 
    Parameters
    ----------
    occshell_list : list of OCCshells
        A list of connected closed OCCshell to be converted into OCCsolid.
                
    Returns
    -------
    solid : OCCsolid
        An OCCsolid constructed from the list of connected closed OCCshell.
    """
    ms = BRepBuilderAPI_MakeSolid()
    for occ_shell in occshell_list:
        ms.Add(occ_shell)
    return ms.Solid()
    
#========================================================================================================
#TOPOLOGY INPUTS
#========================================================================================================
def make_compound(occtopo_list):
    """
    This function creates a OCCcompound from a list of OCCtopologies.
 
    Parameters
    ----------
    occtopo_list : list of OCCtopology
        A list of OCCtopologies to be converted into OCCcompound. 
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
                
    Returns
    -------
    compound : OCCcompound
        An OCCcompound constructed from the list of OCCtopologies.
    """
    return Construct.compound(occtopo_list)

def boolean_common(occtopology1, occtopology2):
    """
    This function creates an OCCcompound from intersecting the two OCCtopologies.
 
    Parameters
    ----------
    occtopology1 : OCCtopology
        The OCCtopology to be intersected. 
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    occtopology2 : OCCtopology
        The OCCtopology to be intersected.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    Returns
    -------
    compound : OCCcompound
        An OCCcompound constructed from the intersection.
    """
    intersection = BRepAlgoAPI_Common(occtopology1, occtopology2).Shape()
    compound = fetch.topo2topotype(intersection)
    return compound
    
def boolean_fuse(occtopology1, occtopology2):
    """
    This function creates an OCCcompound from fusing the two OCCtopologies.
 
    Parameters
    ----------
    occtopology1 : OCCtopology
        The OCCtopology to be fused. 
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    occtopology2 : OCCtopology
        The OCCtopology to be fused.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    Returns
    -------
    compound : OCCcompound
        An OCCcompound constructed from the fusion.
    """
    fused = Construct.boolean_fuse(occtopology1, occtopology2)
    compound = fetch.topo2topotype(fused)
    return compound

def boolean_difference(occstopology2cutfrm, cutting_occtopology):
    """
    This function creates an OCCcompound from cutting the two OCCtopologies.
 
    Parameters
    ----------
    occstopology2cutfrm : OCCtopology
        The OCCtopology to be cut. 
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    cutting_occtopology : OCCtopology
        The cutting OCCtopology.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    Returns
    -------
    compound : OCCcompound
        An OCCcompound constructed from the cutting.
    """
    difference = Construct.boolean_cut(occstopology2cutfrm, cutting_occtopology)
    compound = fetch.topo2topotype(difference)
    return compound

def boolean_section(section_occface, occtopology2cut, roundndigit = 6, distance = 0.1):
    """
    This function creates an OCCcompound from cutting the OCCtopology with an OCCface.
 
    Parameters
    ----------
    section_occface : OCCface
        The OCCface for cutting the OCCtopology. 
        
    occtopology2cut : OCCtopology
        The OCCtopology to be cut.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
    
    roundndigit : int, optional
        The number of decimal places of the xyz of the points, Default = 6. The higher the number the more precise are the points.
        Depending on the precision of the points, it will decide whether the edges are connected.
        
    distance : float, optional
        The smallest distance between two points from the edges, Default = 0.01. 
        The further the distance the less precise is the resultant faces.
        
    Returns
    -------
    compound : OCCcompound
        An OCCcompound constructed from the cutting. The OCCcompound is a collection of OCCfaces
    """
    section = BRepAlgoAPI_Section(section_occface, occtopology2cut).Shape()
    edges = fetch.topo_explorer(section, "edge")
    face_list = faces_frm_loose_edges2(edges, roundndigit = roundndigit, distance = distance)
    compound = make_compound(face_list)
    #visualise([[compound]], ["BLUE"])
    return compound
    
def simple_mesh(occtopology, mesh_incremental_float = 0.8):
    """
    This function creates a mesh (list of triangle OCCfaces) of the OCCtopology.
 
    Parameters
    ----------
    occtopology : OCCtopology
        The OCCtopology to be meshed.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    mesh_incremental_float : float, optional
        Default = 0.8.
        
    Returns
    -------
    list of face : list of OCCfaces
        A list of meshed OCCfaces (triangles) constructed from the meshing.
    """
    #TODO: figure out why is it that some surfaces do not work
    occtopology = TopoDS_Shape(occtopology)
    bt = BRep_Tool()
    BRepMesh_IncrementalMesh(occtopology, mesh_incremental_float)
    occshape_face_list = fetch.topo_explorer(occtopology, "face")
    occface_list = []
    for occshape_face in occshape_face_list:
        location = TopLoc_Location()
        #occshape_face = modify.fix_face(occshape_face)
        facing = bt.Triangulation(occshape_face, location).GetObject()
        if facing:
            tab = facing.Nodes()
            tri = facing.Triangles()
            for i in range(1, facing.NbTriangles()+1):
                trian = tri.Value(i)
                index1, index2, index3 = trian.Get()
                #print index1, index2, index3
                pypt1 = modify.occpt_2_pypt(tab.Value(index1))
                pypt2 = modify.occpt_2_pypt(tab.Value(index2))
                pypt3 = modify.occpt_2_pypt(tab.Value(index3))
                #print pypt1, pypt2, pypt3
                occface = make_polygon([pypt1, pypt2, pypt3])
                occface_list.append(occface)
    return occface_list