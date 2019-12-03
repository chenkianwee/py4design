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
from . import calculate
from . import modify

from .OCCUtils import Topology
from .OCCUtils import edge

from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_COMPOUND, TopAbs_COMPSOLID, TopAbs_SOLID, TopAbs_SHELL, TopAbs_FACE, TopAbs_WIRE, TopAbs_EDGE, TopAbs_VERTEX, TopAbs_REVERSED
from OCC.Core.TopoDS import topods_Compound, topods_CompSolid, topods_Solid, topods_Shell, topods_Face, topods_Wire, topods_Edge, topods_Vertex
from OCC.Core.Geom import Handle_Geom_BSplineCurve_Create, Geom_BSplineCurve
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_HCurve

#========================================================================================================
#EDGE INPUTS
#========================================================================================================
def points_frm_edge(occedge):
    """
    This function fetches a list of points from the OCCedge. The list of points consist of the starting and ending point of the edge.
 
    Parameters
    ----------
    occedge : OCCedge
        The OCCedge to be examined.
        
    Returns
    -------
    list of points : pyptlist
        The list of points extracted from the OCCedge.
    """
    vertex_list = list(Topology.Topo(occedge).vertices())
    point_list = modify.occvertex_list_2_occpt_list(vertex_list)
    pyptlist = modify.occpt_list_2_pyptlist(point_list)
    return pyptlist
    
def is_edge_bspline(occedge):
    """
    This function checks if an OCCedge contains a bspline curve.
 
    Parameters
    ----------
    occedge : OCCedge
        The OCCedge to be examined.
        
    Returns
    -------
    True or False : bool
        True or False if the edge contains a bspline curve.
    """

    #GeomAbs_Line 	        0
    #GeomAbs_Circle 	        1
    #GeomAbs_Ellipse         2	
    #GeomAbs_Hyperbola       3 	
    #GeomAbs_Parabola        4	
    #GeomAbs_BezierCurve     5	
    #GeomAbs_BSplineCurve    6	
    #GeomAbs_OtherCurve      7

    adaptor = BRepAdaptor_Curve(occedge)
    ctype = adaptor.GetType()
    if ctype == 6:
        return True
    else:
        return False

def is_edge_line(occedge):
    """
    This function checks if an OCCedge contains a line.
 
    Parameters
    ----------
    occedge : OCCedge
        The OCCedge to be examined.
        
    Returns
    -------
    True or False : bool
        True or False if the edge contains a line.
    """
    adaptor = BRepAdaptor_Curve(occedge)
    
    #GeomAbs_Line 	        0
    #GeomAbs_Circle 	        1
    #GeomAbs_Ellipse         2	
    #GeomAbs_Hyperbola       3 	
    #GeomAbs_Parabola        4	
    #GeomAbs_BezierCurve     5	
    #GeomAbs_BSplineCurve    6	
    #GeomAbs_OtherCurve      7

    ctype = adaptor.GetType()
    if ctype == 0:
        return True
    else:
        return False

    
def poles_from_bsplinecurve_edge(occedge):
    """
    This function fetches the poles of a bspline OCCedge.
 
    Parameters
    ----------
    occedge : OCCedge
        The OCCedge to be examined. The OCCedge needs to contain a bspline curve
        
    Returns
    -------
    List of poles : pyptlist
        List of poles of the bspline curve
    """
    adaptor = BRepAdaptor_Curve(occedge)
    adaptor_handle = BRepAdaptor_HCurve(adaptor)
    bspline = adaptor.BSpline()
    #handle_bspline = Handle_Geom_BSplineCurve_Create()
    #bspline = Geom_BSplineCurve(adaptor.Curve())
    #print(bspline)
    #bspline = handle_bspline.DownCast(adaptor.Curve().Curve()).GetObject()
    npoles =  bspline.NbPoles()
    polelist = []
    for np in range(npoles):
        pole = bspline.Pole(np+1)
        pypole = (pole.X(), pole.Y(), pole.Z())
        polelist.append(pypole)
        
    if topods_Edge(occedge).Orientation() == TopAbs_REVERSED:
        polelist.reverse()

    return polelist

def edge_domain(occedge):
    """
    This function fetches the domain of an OCCedge.
 
    Parameters
    ----------
    occedge : OCCedge
        The OCCedge to be examined.
        
    Returns
    -------
    lower bound: float
        The lower bound of the OCCedge domain
    upper bound: float
        The upper bound of the OCCedge domain
    """
    occutil_edge = edge.Edge(occedge)
    lbound, ubound = occutil_edge.domain()
    return lbound, ubound

#========================================================================================================
#WIRE INPUTS
#========================================================================================================
def points_frm_wire(occwire):
    """
    This function fetches a list of points from the OCCwire. The wire is constructed based on the list of points.
    TODO: WHEN DEALING WITH OPEN WIRE IT WILL NOT RETURN THE LAST VERTEX
 
    Parameters
    ----------
    occwire : OCCwire
        The OCCwire to be examined.
        
    Returns
    -------
    list of points : pyptlist
        The list of points extracted from the OCCwire.
    """
    verts = list(Topology.WireExplorer(occwire).ordered_vertices())
    point_list = modify.occvertex_list_2_occpt_list(verts)
    pyptlist = modify.occpt_list_2_pyptlist(point_list)
    return pyptlist

def edges_frm_wire(occwire):
    """
    This function fetches a list of OCCedges from the OCCwire. The wire is constructed based on the list of edges.
 
    Parameters
    ----------
    occwire : OCCwire
        The OCCwire to be examined.
        
    Returns
    -------
    list of edges : list of OCCedges
        The list of OCCedges extracted from the OCCwire.
    """
    edge_list = Topology.WireExplorer(occwire).ordered_edges()
    return list(edge_list)

#========================================================================================================
#FACE INPUTS
#========================================================================================================
def points_frm_occface(occface):
    """
    This function fetches a list of points from the OCCface. The face is constructed based on the list of points.
 
    Parameters
    ----------
    occface : OCCface
        The OCCface to be examined.
        
    Returns
    -------
    list of points : pyptlist
        The list of points extracted from the OCCface.
    """
    wire_list = wires_frm_face(occface)
    pt_list = []
    for wire in wire_list:
        pypts = points_frm_wire(wire)
        pt_list.extend(pypts)
    
    normal = calculate.face_normal(occface)
    anticlockwise = calculate.is_anticlockwise(pt_list, normal)
    if anticlockwise:
        pt_list.reverse()
        return pt_list
    else:
        return pt_list

def wires_frm_face(occface):
    """
    This function fetches a list of OCCwires from the OCCface. The face is constructed based on the list of wires.
 
    Parameters
    ----------
    occface : OCCface
        The OCCface to be examined.
        
    Returns
    -------
    list of wires : list of OCCwires
        The list of OCCwires extracted from the OCCface.
    """
    wire_list =  Topology.Topo(occface).wires()
    return list(wire_list)

def is_face_null(occface):
    """
    This function checks if the OCCface is null. Null means it is a degenerated face.
 
    Parameters
    ----------
    occface : OCCface
        The OCCface to be examined.
        
    Returns
    -------
    True or False : bool
        If True OCCface is null, if False OCCface is not null.
    """
    return occface.IsNull()
    
#========================================================================================================
#SHELL INPUTS
#========================================================================================================
def faces_frm_shell(occshell):
    """
    This function fetches a list of OCCfaces from the OCCshell. The shell is constructed based on the list of faces.
 
    Parameters
    ----------
    occshell : OCCshell
        The OCCshell to be examined.
        
    Returns
    -------
    list of faces : list of OCCfaces
        The list of OCCfaces extracted from the OCCshell.
    """
    face_list = Topology.Topo(occshell).faces()
    return list(face_list) 

#========================================================================================================
#SOLID INPUTS
#========================================================================================================
def faces_frm_solid(occsolid):
    """
    This function fetches a list of OCCfaces from the OCCsolid. The solid is constructed based on the list of faces.
 
    Parameters
    ----------
    occsolid : OCCsolid
        The OCCsolid to be examined.
        
    Returns
    -------
    list of faces : list of OCCfaces
        The list of OCCfaces extracted from the OCCsolid.
    """
    face_list = []
    shell_list = shells_frm_solid(occsolid)
    for shell in shell_list:
        faces = faces_frm_shell(shell)
        face_list.extend(faces)
    return face_list
        
def shells_frm_solid(occsolid):
    """
    This function fetches a list of OCCshells from the OCCsolid. The solid is constructed based on the list of shells.
 
    Parameters
    ----------
    occsolid : OCCsolid
        The OCCsolid to be examined.
        
    Returns
    -------
    list of shells : list of OCCshells
        The list of OCCshells extracted from the OCCsolid.
    """
    shell_list = Topology.Topo(occsolid).shells()
    return list(shell_list)

def points_frm_solid(occsolid):
    """
    This function fetches a list of points from the OCCsolid.
 
    Parameters
    ----------
    occsolid : OCCsolid
        The OCCsolid to be examined.
        
    Returns
    -------
    list of points : pyptlist
        The list of points extracted from the OCCsolid.
    """
    verts = list(Topology.Topo(occsolid).vertices())
    ptlist = modify.occvertex_list_2_occpt_list(verts)
    pyptlist = modify.occpt_list_2_pyptlist(ptlist)        
    return pyptlist

def solids_frm_compsolid(occcompsolid):
    """
    This function fetches a list of OCCsolids from the OCCcompsolid.
 
    Parameters
    ----------
    occcompsolid : OCCcompsolid
        The OCCcompsolid to be examined.
        
    Returns
    -------
    list of solids : list of OCCsolids
        The list of OCCsolids extracted from the occcompsolid.
    """
    solid_list = Topology.Topo(occcompsolid).solids()
    return list(solid_list)

#========================================================================================================
#COMPOUND INPUTS
#========================================================================================================
def topos_frm_compound(occcompound):
    """
    This function extracts all the topologies in the OCCcompound.
 
    Parameters
    ----------
    occcompound : OCCcompound
        The OCCcompound to be examined.
        
    Returns
    -------
    dictionary of topologies : dictionary of OCCtopologies
        The dictionary of OCCtopologies extracted from the occcompound. Specify the topology as keywords to obtain each topology list.
        e.g. dictionary of topologies["face"] to extract the list of OCCfaces in the OCCcompound.
    """
    topo_list = {}
    
    #find all the compsolids
    compsolid_list = topo_explorer(occcompound, "compsolid")
    topo_list["compsolid"] = compsolid_list

    #find all the solids
    solid_list = topo_explorer(occcompound, "solid")
    topo_list["solid"] = solid_list

    #find all the shells
    shell_list = topo_explorer(occcompound, "shell")
    topo_list["shell"] = shell_list

    #find all the faces
    face_list = topo_explorer(occcompound, "face")
    topo_list["face"] = face_list

    #find all the wires
    wire_list = topo_explorer(occcompound, "wire")
    topo_list["wire"] = wire_list

    #find all the edges
    edge_list = topo_explorer(occcompound, "edge")
    topo_list["edge"] = edge_list

    #find all the vertices
    vertex_list = topo_explorer(occcompound, "vertex")
    topo_list["vertex"] = vertex_list
    
    return topo_list

def is_compound_null(occ_compound):
    """
    This function checks if the OCCcompound is null. Null means its empty.
 
    Parameters
    ----------
    occcompound : OCCcompound
        The OCCcompound to be examined.
        
    Returns
    -------
    True or False : bool
        If True the compound is null, if False compound is not null.
    """
    
    isnull = True
    
    #find all the compsolids
    compsolid_list = topo_explorer(occ_compound, "compsolid")
    if compsolid_list:
        isnull = False

    #find all the solids
    solid_list = topo_explorer(occ_compound, "solid")
    if solid_list:
        isnull = False

    #find all the shells
    shell_list = topo_explorer(occ_compound, "shell")
    if shell_list:
        isnull = False

    #find all the faces
    face_list = topo_explorer(occ_compound, "face")
    if face_list:
        isnull = False

    #find all the wires
    wire_list = topo_explorer(occ_compound, "wire")
    if wire_list:
        isnull =False

    #find all the edges
    edge_list = topo_explorer(occ_compound, "edge")
    if edge_list:
        isnull= False

    #find all the vertices
    vertex_list = topo_explorer(occ_compound, "vertex")
    if vertex_list:
        isnull = False
    
    return isnull

#========================================================================================================
#TOPOLOGY INPUTS
#========================================================================================================    
def get_topotype(occtopology_or_topo_str):
    """
    This function fetches the OCCtopology class object based on the specified OCCtopology or a string describing the topology. e.g. "face".
 
    Parameters
    ----------
    occtopology_or_topo_str : OCCtopology or a string describing the topology. 
        The strings can be e.g. "compound", "compsolid", "solid", "shell", "face", "wire", "edge", "vertex". 
        
    Returns
    -------
    topology class : OCCtopology class (TopABS_xx)
        The OCCtopology class based on the specified inputs.
    """
    if isinstance(occtopology_or_topo_str, str):
        if occtopology_or_topo_str == "compound":
            return TopAbs_COMPOUND
        if occtopology_or_topo_str == "compsolid":
            return TopAbs_COMPSOLID
        if occtopology_or_topo_str == "solid":
            return TopAbs_SOLID
        if occtopology_or_topo_str == "shell":
            return TopAbs_SHELL
        if occtopology_or_topo_str == "face":
            return TopAbs_FACE
        if occtopology_or_topo_str == "wire":
            return TopAbs_WIRE
        if occtopology_or_topo_str == "edge":
            return TopAbs_EDGE
        if occtopology_or_topo_str == "vertex":
            return TopAbs_VERTEX
    else:        
        return occtopology_or_topo_str.ShapeType()
    
def topo2topotype(occtopology):
    """
    This function converts the original OCCtopology of the given topology. e.g. an OCCcompound that is originally an OCCface etc.
 
    Parameters
    ----------
    occtopology : OCCtopology 
        The OCCtopology to be converted. 
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    Returns
    -------
    original topology : OCCtopology
        The original OCCtopology of the input.
    """
    shapetype = occtopology.ShapeType()
    if shapetype == TopAbs_COMPOUND:#compound
        orig_topo = topods_Compound(occtopology)
    if shapetype == TopAbs_COMPSOLID:#compsolid
        orig_topo = topods_CompSolid(occtopology)
    if shapetype == TopAbs_SOLID:#solid
        orig_topo = topods_Solid(occtopology)
    if shapetype == TopAbs_SHELL:#shell
        orig_topo = topods_Shell(occtopology)
    if shapetype == TopAbs_FACE:#face
        orig_topo = topods_Face(occtopology)
    if shapetype == TopAbs_WIRE:#wire
        orig_topo = topods_Wire(occtopology)
    if shapetype == TopAbs_EDGE:#edge
        orig_topo = topods_Edge(occtopology)
    if shapetype == TopAbs_VERTEX:#vertex
        orig_topo = topods_Vertex(occtopology)
    return orig_topo

def topo_explorer(occtopo2explore, topotype2find):
    """
    This function explores and fetches the specified topological type from the given OCCtopology.
    e.g. find a list of OCCfaces in an OCCcompound.
 
    Parameters
    ----------
    occtopo2explore : OCCtopology 
        The OCCtopology to be explored.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    topotype2find : str 
        The string describing the topology to find. 
        The strings can be e.g. "compound", "compsolid", "solid", "shell", "face", "wire", "edge", "vertex". 
        
    Returns
    -------
    list of topology : list of OCCtopology
        The list of OCCtopology found in the specified OCCtopology.
    """
    geom_list = []
    if topotype2find == "compound":
        shapetype2find_topABS = TopAbs_COMPOUND
    if topotype2find == "compsolid":
        shapetype2find_topABS = TopAbs_COMPSOLID
    if topotype2find == "solid":
        shapetype2find_topABS = TopAbs_SOLID
    if topotype2find == "shell":
        shapetype2find_topABS = TopAbs_SHELL
    if topotype2find == "face":
        shapetype2find_topABS = TopAbs_FACE
    if topotype2find == "wire":
        shapetype2find_topABS = TopAbs_WIRE
    if topotype2find == "edge":
        shapetype2find_topABS = TopAbs_EDGE
    if topotype2find == "vertex":
        shapetype2find_topABS = TopAbs_VERTEX
        
    ex = TopExp_Explorer(occtopo2explore, shapetype2find_topABS)
    while ex.More():
        if shapetype2find_topABS == 0:
            geom = topods_Compound(ex.Current())
        if shapetype2find_topABS == 1:
            geom = topods_CompSolid(ex.Current())
        if shapetype2find_topABS == 2:
            geom = topods_Solid(ex.Current())
        if shapetype2find_topABS == 3:
            geom = topods_Shell(ex.Current())
        if shapetype2find_topABS == 4:
            geom = topods_Face(ex.Current())
        if shapetype2find_topABS == 5:
            geom = topods_Wire(ex.Current())
        if shapetype2find_topABS == 6:
            geom = topods_Edge(ex.Current())
        if shapetype2find_topABS == 7:
            geom = topods_Vertex(ex.Current())
        geom_list.append(geom)
        ex.Next()
    return geom_list