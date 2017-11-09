# ==================================================================================================
#    Copyright (c) 2016, Chen Kian Wee (chenkianwee@gmail.com)
#
#    This file is part of pyliburo
#
#    pyliburo is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    pyliburo is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Pyliburo.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================
import fetch
import calculate
import construct
import modify

from OCCUtils import Construct, Common

from OCC.BRepBuilderAPI import BRepBuilderAPI_Transform, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_GTransform
from OCC.gp import gp_Pnt, gp_Vec, gp_Ax1, gp_Ax3, gp_Dir, gp_DZ, gp_Trsf, gp_GTrsf, gp_Mat
from OCC.ShapeFix import ShapeFix_Shell, ShapeFix_Solid, ShapeFix_Wire, ShapeFix_Face
from OCC.BRepLib import breplib
from OCC.Geom import Geom_TrimmedCurve
from OCC.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_CompCurve, BRepAdaptor_HCompCurve
from OCC.GeomConvert import geomconvert_CurveToBSplineCurve
from OCC.BRep import BRep_Tool

#========================================================================================================
#POINT INPUTS
#======================================================================================================== 
def occpt_2_pypt(occpt):
    """
    This function constructs a point (pypt) from an OCC point (gp_pnt).
 
    Parameters
    ----------
    occpt : OCC point (gp_pnt)
        OCC point (gp_pnt) to be converted to a pypt.
        
    Returns
    -------
    point : pypt
        A pypt constructed from the OCC point (gp_pnt).
    """
    pypt = (occpt.X(), occpt.Y(), occpt.Z())
    return pypt

def occpt_list_2_pyptlist(occpt_list):
    """
    This function constructs a list of points (pyptlist) from a list of OCC points (gp_pnt).
 
    Parameters
    ----------
    occpt_list : list of OCC points (gp_pnt)
        list of OCC points (gp_pnt) to be converted to a pyptlist.
        
    Returns
    -------
    list of points : pyptlist
        A pyptlist constructed from the list of OCC points (gp_pnt).
    """
    pyptlist = []
    for occpt in occpt_list:
        pypt = occpt_2_pypt(occpt)
        pyptlist.append(pypt)
    return pyptlist

def occvertex_2_occpt(occvertex):
    """
    This function constructs an OCC point (gp_pnt) from an OCCvertex.
 
    Parameters
    ----------
    occvertex : OCCvertex
        OCCvertex to be converted to a OCC point (gp_pnt).
        
    Returns
    -------
    point : OCC point (gp_pnt)
        An OCC point constructed from the OCCvertex.
    """
    occ_pnt = BRep_Tool.Pnt(occvertex)
    return occ_pnt

def occvertex_list_2_occpt_list(occvertex_list):
    """
    This function constructs a list of OCC points (gp_pnt) from a list of OCCvertices.
 
    Parameters
    ----------
    occvertex_list : list of OCCvertices
        List of OCCvertices to be converted to a list of OCC points (gp_pnt).
        
    Returns
    -------
    list of points : list of OCC points (gp_pnt)
        A list of OCC points (gp_pnt) constructed from the list of OCCvertices.
    """
    point_list = []
    for vert in occvertex_list:
        point_list.append(BRep_Tool.Pnt(vert))
    return point_list

def gpvec_2_pyvec(gpvec):
    """
    This function construct a pyvec from a OCC vector (gp_vec).
 
    Parameters
    ----------
    gpvec : gp_vec
        OCCvector to be converted.
        
    Returns
    -------
    normalised vector : pyvec
        Tuple of floats.  A pyvec is a tuple that documents the xyz vector of a dir e.g. (x,y,z).
       
    """
    return (gpvec.X(), gpvec.Y(), gpvec.Z())

def normalise_vec(gpvec):
    """
    This function normalises a OCC vector (gp_vec).
 
    Parameters
    ----------
    gpvec : gp_vec
        OCCvector to be normalised.
        
    Returns
    -------
    normalised vector : pyvec
        Tuple of floats.  A pyvec is a tuple that documents the xyz vector of a dir e.g. (x,y,z).
       
    """
    ngpvec = gpvec.Normalized()
    return (ngpvec.X(), ngpvec.Y(), ngpvec.Z())

def reverse_vector(pyvec):
    """
    This function reverses a vector.
 
    Parameters
    ----------
    pyvec : tuple of floats
        A pyvec is a tuple that documents the xyz vector of a dir e.g. (x,y,z).
        
    Returns
    -------
    reversed vector : pyvec
        Tuple of floats.  A pyvec is a tuple that documents the xyz vector of a dir e.g. (x,y,z).
    """
    gp_rev_vec = gp_Vec(pyvec[0], pyvec[1], pyvec[2]).Reversed()
    rev_vec = (gp_rev_vec.X(), gp_rev_vec.Y(), gp_rev_vec.Z())
    return rev_vec

def move_pt(orig_pypt, pydir2move, magnitude):
    """
    This function moves a point.
 
    Parameters
    ----------
    orig_pypt : tuple of floats
        The original point to be moved. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    pydir2move : tuple of floats
        The direction to move the point. A pydir is a tuple that documents the xyz vector of a dir e.g. (x,y,z).
        
    magnitude : float
        The distance of the move.
        
    Returns
    -------
    moved point : pypt
        The moved point.
    """
    gp_orig_pt = gp_Pnt(orig_pypt[0], orig_pypt[1],orig_pypt[2])
    gp_direction2move = gp_Vec(pydir2move[0], pydir2move[1], pydir2move[2])
    gp_moved_pt = gp_orig_pt.Translated(gp_direction2move.Multiplied(magnitude))
    moved_pt = (gp_moved_pt.X(), gp_moved_pt.Y(), gp_moved_pt.Z())
    return moved_pt

def round_pypt(pypt, roundndigit):
    """
    This function rounds a point according to the roundndigit input.
 
    Parameters
    ----------
    pypt : tuple of floats
        The point to be rounded. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z).
        
    roundndigit : int
        The number of decimal place the points will be rounded to.
        
    Returns
    -------
    rounded point : pypt
        The rounded point.
    """
    rounded_pypt = (round(pypt[0],roundndigit), round(pypt[1],roundndigit), round(pypt[2],roundndigit))
    return rounded_pypt

def round_pyptlist(pyptlist, roundndigit):
    """
    This function rounds a list of points according to the roundndigit input.
 
    Parameters
    ----------
    pyptlist : a list of tuples
        List of points to be rounded. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    roundndigit : int
        The number of decimal place the points will be rounded to.
        
    Returns
    -------
    list of rounded points : pyptlist
        The list of rounded points.
    """    
    rounded_pyptlist = []
    for pypt in pyptlist:
        rounded_pypt = round_pypt(pypt, roundndigit)
        rounded_pyptlist.append(rounded_pypt)
    return rounded_pyptlist

def rmv_duplicated_pts_by_distance(pyptlist, distance = 1e-06):
    """
    This function fuses all the points within a certain distance.
 
    Parameters
    ----------
    pyptlist : a list of tuples
        List of points to be fused. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    distance : float, optional
        The minimal distance between two points, default = 1e-06. Any points closer than this distance will be fused.
        
    Returns
    -------
    list of fused points : pyptlist
        The list of fused points.
    """
    vert_list = construct.make_occvertex_list(pyptlist)
    occpt_list = occvertex_list_2_occpt_list(vert_list)
    
    filtered_pt_list = Common.filter_points_by_distance(occpt_list, distance = distance)
    f_pyptlist = occpt_list_2_pyptlist(filtered_pt_list)

    return f_pyptlist

def rmv_duplicated_pts(pyptlist, roundndigit = None):
    """
    This function removes duplicated points.
 
    Parameters
    ----------
    pyptlist : a list of tuples
        List of points to be analysed. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    roundndigit : int, optional
        The number of decimal place the points will be rounded to. Default= None
        
    Returns
    -------
    list of fused points : pyptlist
        The list of fused points.
    """    
    if roundndigit == None:
        u_pyptlist = []
        for pypt in pyptlist:
            if pypt not in u_pyptlist:
                u_pyptlist.append(pypt)
                
        return u_pyptlist
        
    else:
        round_pyptlist = []
        for pypt in pyptlist:
            round_pypt = (round(pypt[0],roundndigit), round(pypt[1],roundndigit), round(pypt[2],roundndigit))
            if round_pypt not in round_pyptlist:
                round_pyptlist.append(round_pypt)
            
    return round_pyptlist
    
#========================================================================================================
#EDGE INPUTS
#======================================================================================================== 
def rmv_duplicated_edges(occedge_list):
    """
    This function removes duplicated OCCedges.
 
    Parameters
    ----------
    occedge_list : a list of OCCedges
        The list of OCCedges to be analysed.
        
    Returns
    -------
    list of non-duplicated edges : list of OCCedges
        The list of non-duplicated OCCedges.
    """  
    fcnt = 0
    same_edge_list = []
    non_dup_edges = []
    for occedge in occedge_list:
        same_index = [fcnt]
        for fcnt2 in range(len(occedge_list)):
            if fcnt2 != fcnt:
                is_same = calculate.are_same_edges(occedge, occedge_list[fcnt2])
                if is_same:
                    same_index.append(fcnt2)

        same_index.sort()
        if same_index not in same_edge_list:
            same_edge_list.append(same_index)                        
        fcnt +=1
        
    for indexes in same_edge_list:
        unique_f = occedge_list[indexes[0]]
        non_dup_edges.append(unique_f)
    return non_dup_edges

def trimedge(lbound, ubound, occedge):
    """
    This function trims the OCCedge according to the specified lower and upper bound.
 
    Parameters
    ----------
    lbound : float
        The lower bound of the OCCedge.
        
    ubound : float
        The upper bound of the OCCedge.
        
    occedge : OCCedge
        The edge to be trimmed.

    Returns
    -------
    trimmed edge : OCCedge
        The trimmed OCCedge.
    """
    adaptor = BRepAdaptor_Curve(occedge)
    tr = Geom_TrimmedCurve(adaptor.Curve().Curve(), lbound, ubound)
    tr.SetTrim(lbound, ubound)
    bspline_handle = geomconvert_CurveToBSplineCurve(tr.GetHandle())
    tr_edge = BRepBuilderAPI_MakeEdge(bspline_handle)
    
    return tr_edge.Edge()

def flatten_edge_z_value(occedge, z=0):
    """
    This function flattens the Z-dimension of the OCCedge.
 
    Parameters
    ----------        
    occedge : OCCedge
        The edge to be flatten.
        
    z : float, optional
        The Z-value to flatten to. Default = 0.

    Returns
    -------
    flatten edge : OCCedge
        The flatten OCCedge.
    """
    pyptlist = fetch.points_frm_edge(occedge)
    pyptlist_2d = []
    for pypt in pyptlist:
        pypt2d = (pypt[0],pypt[1],z)
        pyptlist_2d.append(pypt2d)
    flatten_edge = construct.make_edge(pyptlist_2d[0],pyptlist_2d[1])
    return flatten_edge

#========================================================================================================
#WIRE INPUTS
#======================================================================================================== 
def fix_closed_wire(occwire,occface, tolerance = 1e-06):
    """
    This function will try to closed an open wire.
 
    Parameters
    ----------        
    occwire : OCCwire
        The OCCwire to be fixed.
        
    occface : OCCface
        The reference OCCface used for closing the OCCwire.
        
    tolerance : float, optional
        The precision for the fix, Default = 1e-06. 

    Returns
    -------
    fixed wire : OCCwire
        The fixed OCCwire.
    """
    shapefix = ShapeFix_Wire(occwire, occface, tolerance)
    shapefix.FixClosed()
    shapefix.FixSmall(True)
    shapefix.FixDegenerated()
    shapefix.FixSelfIntersection()
    shapefix.FixReorder()
    shapefix.Perform()
    fix_wire = shapefix.Wire()
    return fix_wire

def trim_wire(occwire, pypt1, pypt2, is_periodic=False):
    """
    This function trims the wire.
 
    Parameters
    ----------        
    occwire : OCCwire
        The OCCwire to be fixed.
        
    pypt1 : tuple of floats
        The starting point of the trim. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    pypt2 : tuple of floats
        The ending point of the trim. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    is_periodic : bool, optional
        Indicates if the wire is open or close, True for close, False for open, Default = False.

    Returns
    -------
    trimmed wire : OCCwire
        The trimmed OCCwire.
    """
    gppnt1 = construct.make_gppnt(pypt1)
    gppnt2 = construct.make_gppnt(pypt2)
    trimmed = Construct.trim_wire(occwire, gppnt1, gppnt2, periodic= is_periodic )
    return trimmed

def wire_2_bsplinecurve_edge(occwire):
    """
    This function covnerts an OCCwire to a bspline OCCedge.
 
    Parameters
    ----------        
    occwire : OCCwire
        The OCCwire to be converted.

    Returns
    -------
    converted bspline edge : OCCedge
        The converted OCCedge.
    """
    adaptor = BRepAdaptor_CompCurve(occwire)
    hadap = BRepAdaptor_HCompCurve(adaptor)
    from OCC.Approx import Approx_Curve3d
    from OCC.GeomAbs import GeomAbs_C2
    approx = Approx_Curve3d(hadap.GetHandle(), 1e-06, GeomAbs_C2 , 10000, 12)
    bspline_handle = approx.Curve()
    occedge = BRepBuilderAPI_MakeEdge(bspline_handle)
    return occedge.Edge()

def resample_wire(occwire):
    """
    This function resamples an OCCwire uniformly.
 
    Parameters
    ----------        
    occwire : OCCwire
        The OCCwire to be resampled.

    Returns
    -------
    resampled wire : OCCwire
        The resampled OCCwire.
    """
    resample_curve = Common.resample_curve_with_uniform_deflection(occwire)
    return resample_curve
#========================================================================================================
#FACE INPUTS
#======================================================================================================== 
def reverse_face(occface):
    """
    This function reverse an OCCface orientation.
 
    Parameters
    ----------        
    occface : OCCface
        The OCCface to be reversed.

    Returns
    -------
    reversed face : OCCface
        The reverse OCCface.
    """
    occ_face_r = fetch.topo2topotype(occface.Reversed())
    return occ_face_r

def fix_face(occ_face):
    """
    This function fixes an OCCface.
 
    Parameters
    ----------        
    occface : OCCface
        The OCCface to be fixed.

    Returns
    -------
    fixed face : OCCface
        The fixed OCCface.
    """
    fix = ShapeFix_Face(occ_face)
    #fix.FixMissingSeam()
    fix.FixOrientation()
    fix.Perform()
    return fix.Face()

def rmv_duplicated_faces(occface_list):
    """
    This function removes duplicated faces from a list of OCCfaces.
 
    Parameters
    ----------        
    occface_list : list of OCCfaces
        The list of OCCfaces to be analysed.

    Returns
    -------
    non-duplicated list of faces : list of OCCfaces
        The list of non-duplicated OCCfaces.
    """
    fcnt = 0
    same_face_list = []
    non_dup_faces = []
    for occface in occface_list:
        same_index = [fcnt]
        for fcnt2 in range(len(occface_list)):
            if fcnt2 != fcnt:
                is_same = calculate.are_same_faces(occface, occface_list[fcnt2])
                if is_same:
                    print is_same
                    same_index.append(fcnt2)
                    
        same_index.sort()
        if same_index not in same_face_list:
            same_face_list.append(same_index)                       
        fcnt +=1
        
    for indexes in same_face_list:
        unique_f = occface_list[indexes[0]]
        non_dup_faces.append(unique_f)
    return non_dup_faces

def flatten_face_z_value(occface, z=0):
    """
    This function flatten the OCCface to the Z-value specified.
 
    Parameters
    ----------        
    occface : OCCface
        The OCCface to be flatten.
        
    z : float, optional
        The Z-value to flatten to. Default = 0.

    Returns
    -------
    flatten face : OCCface
        The flatten OCCface.
    """
    pyptlist = fetch.points_frm_occface(occface)
    pyptlist_2d = []
    for pypt in pyptlist:
        pypt2d = (pypt[0],pypt[1],z)
        pyptlist_2d.append(pypt2d)
    
    flatten_face = construct.make_polygon(pyptlist_2d)
    return flatten_face
#========================================================================================================
#SHELL INPUTS
#======================================================================================================== 
def fix_shell_orientation(occshell):
    """
    This function fixes the OCCshell orientation. The fix will orientate all the OCCfaces in the shell towards the same direction.
 
    Parameters
    ----------        
    occshell : OCCshell
        The OCCshell to be fixed.
        
    Returns
    -------
    fixed shell : OCCshell
        The fixed OCCshell.
    """
    shapefix = ShapeFix_Shell(occshell)
    shapefix.FixFaceOrientation(occshell)
    shapefix.Perform()
    fix_shell = shapefix.Shell()
    return fix_shell

def flatten_shell_z_value(occshell, z=0):
    """
    This function flatten the OCCshell to the Z-value specified.
 
    Parameters
    ----------        
    occshell : OCCshell
        The OCCshell to be flattened.
        
    z : float, optional
        The Z-value to flatten to. Default = 0.

    Returns
    -------
    flatten shell : OCCshell
        The flatten OCCshell.
    """
    face_list = fetch.faces_frm_solid(occshell)
    xmin,ymin,zmin,xmax,ymax,zmax = calculate.get_bounding_box(occshell)
    boundary_pyptlist = [[xmin,ymin,zmin], [xmax,ymin,zmin], [xmax,ymax,zmin], [xmin,ymax,zmin]]
    boundary_face = construct.make_polygon(boundary_pyptlist)
    b_mid_pt = calculate.face_midpt(boundary_face)
    
    #flatten_shell = fetch.topo2topotype(uniform_scale(occshell, 1, 1, 0, b_mid_pt))
    
    face_list = construct.simple_mesh(occshell)
    f_face_list = []
    for occface in face_list:
        f_face = flatten_face_z_value(occface, z=zmin)
        f_face_list.append(f_face)
        
    face_list = f_face_list
    flatten_shell = construct.make_compound(face_list)
    nfaces = len(face_list)
    merged_faces = construct.merge_faces(face_list)
    dest_pt = [b_mid_pt[0], b_mid_pt[1], z]    
    #depending on how complicated is the shell we decide which is the best way to flatten it 
    #1.) if it is an open shell and when everything is flatten it fits nicely as a flat surface 
    if len(merged_faces) == 1:
        m_area = calculate.face_area(merged_faces[0])
        if m_area > 1e-06:
            flatten_face = fetch.topo2topotype(move(b_mid_pt, dest_pt,merged_faces[0]))
            return flatten_face
       
    #2.) if it is a complex shell with less than 500 faces we fused and create a single surface
    if nfaces < 50:
        try:
            fused_shape = None
            fcnt = 0
            for face in face_list:
                face_area = calculate.face_area(face)
                if not face_area < 0.001:
                    if fcnt == 0:
                        fused_shape = face 
                    else:
                        #construct.visualise([[fused_shape], [face]], ['WHITE', 'RED'])
                        fused_shape = construct.boolean_fuse(fused_shape, face)
                    fcnt+=1
                    
            if fused_shape!=None:
                fused_face_list = fetch.topo_explorer(fused_shape, "face")
                merged_faces = construct.merge_faces(fused_face_list)
                if len(merged_faces) == 1:
                    flatten_face = fetch.topo2topotype(move(b_mid_pt, dest_pt,merged_faces[0]))
                    return flatten_face
                else:
                    flatten_vertex = fetch.topo_explorer(flatten_shell,"vertex")
                    flatten_pts = modify.occvertex_list_2_occpt_list(flatten_vertex)
                    flatten_pypts = modify.occpt_list_2_pyptlist(flatten_pts)
                    
                    dface_list = construct.delaunay3d(flatten_pypts)
                    merged_faces = construct.merge_faces(dface_list)
                    if len(merged_faces) == 1:
                        flatten_face = fetch.topo2topotype(move(b_mid_pt, dest_pt,merged_faces[0]))
                        return flatten_face
                    else:
                        #construct.visualise([[occshell]],["WHITE"])
                        return None
        except RuntimeError:
            flatten_vertex = fetch.topo_explorer(flatten_shell,"vertex")
            flatten_pts = modify.occvertex_list_2_occpt_list(flatten_vertex)
            flatten_pypts = modify.occpt_list_2_pyptlist(flatten_pts)
            dface_list = construct.delaunay3d(flatten_pypts)
            merged_faces = construct.merge_faces(dface_list)
            if len(merged_faces) == 1:
                flatten_face = fetch.topo2topotype(move(b_mid_pt, dest_pt,merged_faces[0]))
                return flatten_face
            else:
                #construct.visualise([[occshell]],["WHITE"])
                return None
    
    #3.) if it is a complex shell with more than 500 faces we get the vertexes and create a triangulated srf with delaunay 
        #and merge all the faces to make a single surface
    if nfaces >=50:
        flatten_vertex = fetch.topo_explorer(flatten_shell,"vertex")
        flatten_pts = modify.occvertex_list_2_occpt_list(flatten_vertex)
        flatten_pypts = modify.occpt_list_2_pyptlist(flatten_pts)
        #flatten_pypts = rmv_duplicated_pts_by_distance(flatten_pypts, tolerance = 1e-04)
        dface_list = construct.delaunay3d(flatten_pypts)
        merged_faces = construct.merge_faces(dface_list)
        if len(merged_faces) == 1:
            flatten_face = fetch.topo2topotype(move(b_mid_pt, dest_pt,merged_faces[0]))
            return flatten_face
        else:
            #construct.visualise([[occshell]],["WHITE"])
            return None
        
def simplify_shell(occshell, tolerance = 1e-06):
    """
    This function simplifies the OCCshell by merging all the coincidental OCCfaces in the shell into a single OCCface. 
 
    Parameters
    ----------        
    occshell : OCCshell
        The OCCshell to be simplified.
        
    tolerance : float, optional
        The precision of the simplification, Default = 1e-06.

    Returns
    -------
    simplified shell : OCCshell
        The simplified OCCshell.
    """
    #this will merge any coincidental faces into a single surfaces to simplify the geometry
    fshell = fix_shell_orientation(occshell)
    #get all the faces from the shell and arrange them according to their normals
    sfaces = fetch.topo_explorer(fshell,"face")
    nf_dict = calculate.grp_faces_acc2normals(sfaces)
    merged_fullfacelist = []
    #merge all the faces thats share edges into 1 face     
    for snfaces in nf_dict.values():
        connected_face_shell_list = construct.sew_faces(snfaces, tolerance=tolerance)
        if connected_face_shell_list:
            for shell in connected_face_shell_list:
                shell_faces = fetch.topo_explorer(shell, "face")    
                merged_facelist = construct.merge_faces(shell_faces,tolerance=tolerance)
                if merged_facelist:
                    merged_fullfacelist.extend(merged_facelist)
                else:
                    merged_fullfacelist.extend(shell_faces)
        else:
            merged_fullfacelist.extend(snfaces)
            
    nmerged_face = len(merged_fullfacelist)

    if len(merged_fullfacelist) >1:
        fshell2 = construct.sew_faces(merged_fullfacelist, tolerance=tolerance)
        fshell2 = fix_shell_orientation(fshell2[0])
        nfshell2_face = len(fetch.topo_explorer(fshell2, "face"))
        if nfshell2_face!= nmerged_face:
            return occshell        
    else:
        #if there is only one face it means its an open shell
        fshell2 = construct.make_shell(merged_fullfacelist)

    return fshell2

#========================================================================================================
#SOLID INPUTS
#======================================================================================================== 
def fix_close_solid(occsolid):
    """
    This function fixes an OCCsolid by making sure all the OCCfaces in the solid have an outward orientation. 
 
    Parameters
    ----------        
    occsolid : OCCsolid
        The OCCsolid to be fixed.

    Returns
    -------
    fixed solid : OCCsolid
        The fixed OCCsolid. If None it means the solid is not fixed.
    """
    shape_fix = ShapeFix_Solid(occsolid)
    shape_fix.Perform()
    fix_solid = shape_fix.Solid()
    fix_solid_list = fetch.topo_explorer(fix_solid, "solid")
    if not fix_solid_list:
        return None
    else:
        fix_solid = fix_solid_list[0]
        breplib.OrientClosedSolid(fix_solid)
        return fix_solid
    
#========================================================================================================
#TOPOLOGY INPUTS
#======================================================================================================== 
def move(orig_pypt, location_pypt, occtopology):
    """
    This function moves an OCCtopology from the orig_pypt to the location_pypt.
 
    Parameters
    ----------        
    orig_pypt : tuple of floats
        The OCCtopology will move in reference to this point.
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    location_pypt : tuple of floats
        The destination of where the OCCtopology will be moved in relation to the orig_pypt.
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    occtopology : OCCtopology
        The OCCtopology to be moved.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 

    Returns
    -------
    moved topology : OCCtopology (OCCshape)
        The moved OCCtopology.
    """
    gp_ax31 = gp_Ax3(gp_Pnt(orig_pypt[0], orig_pypt[1], orig_pypt[2]), gp_DZ())
    gp_ax32 = gp_Ax3(gp_Pnt(location_pypt[0], location_pypt[1], location_pypt[2]), gp_DZ())
    aTrsf = gp_Trsf()
    aTrsf.SetTransformation(gp_ax32,gp_ax31)
    trsf_brep = BRepBuilderAPI_Transform(aTrsf)
    trsf_brep.Perform(occtopology, True)
    trsf_shp = trsf_brep.Shape()
    return trsf_shp
    
def map_cs(occgp_ax3_1, occgp_ax3_2, occtopology):
    """
    This function maps an OCCtopology from one OCC coordinate sytem to another.
 
    Parameters
    ----------        
    occgp_ax3_1 : gp_ax3
        The original OCC coordinate system, OCC coordinate system can be created using construct.make_gp_ax3 function.
        
    occgp_ax3_2 : gp_ax3
       The destination OCC coordinate system, OCC coordinate system can be created using construct.make_gp_ax3 function.
        
    occtopology : OCCtopology
        The OCCtopology to be mapped.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 

    Returns
    -------
    mapped topology : OCCtopology (OCCshape)
        The mapped OCCtopology.
    """
    a_trsf = calculate.cs_transformation(occgp_ax3_1, occgp_ax3_2)
    trsf_shp = BRepBuilderAPI_Transform(occtopology, a_trsf).Shape()
    return trsf_shp
    
def rotate(occtopology, rot_pypt, pyaxis, degree):
    """
    This function rotates an OCCtopology based on the rotation point, an axis and the rotation degree.
 
    Parameters
    ----------        
    occtopology : OCCtopology
        The OCCtopology to be rotated.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    rot_pypt : tuple of floats
        The OCCtopology will rotate in reference to this point.
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    pyaxis : tuple of floats
        The OCCtopology will rotate along this axis.
        A pyaxis is a tuple that documents the xyz of a direction e.g. (x,y,z)
        
    degree : float
       The degree of rotation.
        
    Returns
    -------
    rotated topology : OCCtopology (OCCshape)
        The rotated OCCtopology.
    """
    
    from math import radians
    gp_ax3 = gp_Ax1(gp_Pnt(rot_pypt[0], rot_pypt[1], rot_pypt[2]), gp_Dir(pyaxis[0], pyaxis[1], pyaxis[2]))
    aTrsf = gp_Trsf()
    aTrsf.SetRotation(gp_ax3, radians(degree))
    rot_brep = BRepBuilderAPI_Transform(aTrsf)
    rot_brep.Perform(occtopology, True)
    rot_shape = rot_brep.Shape()
    return rot_shape
    
def uniform_scale(occtopology, tx, ty, tz, ref_pypt):
    """
    This function uniformly scales an OCCtopology based on the reference point and tx,ty,tz factors.
 
    Parameters
    ----------        
    occtopology : OCCtopology
        The OCCtopology to be scaled.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    tx : float
        The scale factor in the X-axis.
        
    ty : float
        The scale factor in the Y-axis.
        
    tz : float
        The scale factor in the Z-axis.
       
    ref_pypt : tuple of floats
        The OCCtopology will scale in reference to this point.
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    Returns
    -------
    scaled topology : OCCtopology (OCCshape)
        The scaled OCCtopology.
    """
    moved_shape = move(ref_pypt, (0,0,0),occtopology)
    xform = gp_GTrsf()
    xform.SetVectorialPart(gp_Mat(
      tx, 0, 0,
      0, ty, 0,
      0, 0, tz,
    ))
    
    brep = BRepBuilderAPI_GTransform(xform)
    brep.Perform(moved_shape, True)
    trsfshape = brep.Shape()
    move_back_shp = move((0,0,0), ref_pypt,trsfshape)
    return move_back_shp

def scale(occtopology, scale_factor, ref_pypt):
    """
    This function uniformly scales an OCCtopology based on the reference point and the scale factor.
 
    Parameters
    ----------        
    occtopology : OCCtopology
        The OCCtopology to be scaled.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    scale_factor : float
        The scale factor.
       
    ref_pypt : tuple of floats
        The OCCtopology will scale in reference to this point.
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
        
    Returns
    -------
    scaled topology : OCCtopology (OCCshape)
        The scaled OCCtopology.
    """
    xform = gp_Trsf()
    gp_pnt = construct.make_gppnt(ref_pypt)
    xform.SetScale(gp_pnt, scale_factor)
    brep = BRepBuilderAPI_Transform(xform)
    brep.Perform(occtopology, True)
    trsfshape = brep.Shape()
    return trsfshape


def fix_shape(occtopology):
    """
    This function fixes an OCCtopology.
 
    Parameters
    ----------        
    occtopology : OCCtopology
        The OCCtopology to be fixed.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    Returns
    -------
    fixed topology : OCCtopology (OCCshape)
        The fixed OCCtopology.
    """
    fixed_shape = Construct.fix_shape(occtopology)
    return fixed_shape