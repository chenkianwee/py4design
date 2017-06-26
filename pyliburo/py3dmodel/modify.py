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
#    along with Dexen.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================
from OCCUtils import Construct, Common
from OCC.BRepBuilderAPI import BRepBuilderAPI_Transform, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_GTransform
from OCC.gp import gp_Pnt, gp_Vec, gp_Ax1, gp_Ax3, gp_Dir, gp_DZ, gp_Trsf, gp_GTrsf, gp_Mat
from OCC.ShapeFix import ShapeFix_Shell, ShapeFix_Solid, ShapeFix_Wire, ShapeFix_Face
from OCC.BRepLib import breplib
from OCC.Geom import Geom_TrimmedCurve
from OCC.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_CompCurve, BRepAdaptor_HCompCurve
from OCC.GeomConvert import geomconvert_CurveToBSplineCurve

import fetch
import calculate
import construct

def move(orig_pt, location_pt, occshape):
    gp_ax31 = gp_Ax3(gp_Pnt(orig_pt[0], orig_pt[1], orig_pt[2]), gp_DZ())
    gp_ax32 = gp_Ax3(gp_Pnt(location_pt[0], location_pt[1], location_pt[2]), gp_DZ())
    aTrsf = gp_Trsf()
    aTrsf.SetTransformation(gp_ax32,gp_ax31)
    trsf_brep = BRepBuilderAPI_Transform(aTrsf)
    trsf_brep.Perform(occshape, True)
    trsf_shp = trsf_brep.Shape()
    return trsf_shp
    
def map_cs(occgp_ax3_1, occgp_ax3_2, occshape):
    a_trsf = calculate.cs_transformation(occgp_ax3_1, occgp_ax3_2)
    trsf_shp = BRepBuilderAPI_Transform(occshape, a_trsf).Shape()
    return trsf_shp
    
def normalise_vec(gpvec):
    ngpvec = gpvec.Normalized()
    return (ngpvec.X(), ngpvec.Y(), ngpvec.Z())
    
def rotate(occshape, rot_pt, axis, degree):
    from math import radians
    gp_ax3 = gp_Ax1(gp_Pnt(rot_pt[0], rot_pt[1], rot_pt[2]), gp_Dir(axis[0], axis[1], axis[2]))
    aTrsf = gp_Trsf()
    aTrsf.SetRotation(gp_ax3, radians(degree))
    rot_brep = BRepBuilderAPI_Transform(aTrsf)
    rot_brep.Perform(occshape, True)
    rot_shape = rot_brep.Shape()
    return rot_shape
    
def move_pt(orig_pt, direction2move, magnitude):
    gp_orig_pt = gp_Pnt(orig_pt[0], orig_pt[1],orig_pt[2])
    gp_direction2move = gp_Vec(direction2move[0], direction2move[1], direction2move[2])
    gp_moved_pt = gp_orig_pt.Translated(gp_direction2move.Multiplied(magnitude))
    moved_pt = (gp_moved_pt.X(), gp_moved_pt.Y(), gp_moved_pt.Z())
    return moved_pt
    
def uniform_scale(occshape, tx, ty, tz, ref_pypt):
    moved_shape = move(ref_pypt, (0,0,0),occshape)
    occshape.ShapeType()
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

def scale(occshape, scale_factor, ref_pypt):
    xform = gp_Trsf()
    gp_pnt = construct.make_gppnt(ref_pypt)
    xform.SetScale(gp_pnt, scale_factor)
    brep = BRepBuilderAPI_Transform(xform)
    brep.Perform(occshape, True)
    trsfshape = brep.Shape()
    return trsfshape

def reverse_vector(vec):
    gp_rev_vec = gp_Vec(vec[0], vec[1], vec[2]).Reversed()
    rev_vec = (gp_rev_vec.X(), gp_rev_vec.Y(), gp_rev_vec.Z())
    return rev_vec
    
def reverse_face(occ_face):
    #reverse the face
    occ_face_r = fetch.shape2shapetype(occ_face.Reversed())
    return occ_face_r
    
def fix_shell_orientation(occshell):
    shapefix = ShapeFix_Shell(occshell)
    shapefix.FixFaceOrientation(occshell)
    shapefix.Perform()
    fix_shell = shapefix.Shell()
    return fix_shell
    
def fix_close_solid(occsolid):
    shape_fix = ShapeFix_Solid(occsolid)
    shape_fix.Perform()
    fix_solid = shape_fix.Solid()
    fix_solid_list = fetch.geom_explorer(fix_solid, "solid")
    if not fix_solid_list:
        return None
    else:
        fix_solid = fix_solid_list[0]
        breplib.OrientClosedSolid(fix_solid)
        return fix_solid
    
def fix_closed_wire(occwire,occface, tolerance = 1e-06):
    shapefix = ShapeFix_Wire(occwire, occface, tolerance)
    shapefix.FixClosed()
    shapefix.FixSmall(True)
    shapefix.FixDegenerated()
    shapefix.FixSelfIntersection()
    shapefix.FixReorder()
    shapefix.Perform()
    fix_wire = shapefix.Wire()
    return fix_wire

def fix_shape(occ_shape):
    fixed_shape = Construct.fix_shape(occ_shape)
    return fixed_shape
    
def fix_face(occ_face):
    fix = ShapeFix_Face(occ_face)
    #fix.FixMissingSeam()
    fix.FixOrientation()
    fix.Perform()
    return fix.Face()
    
def rmv_duplicated_faces(occfacelist):
    fcnt = 0
    same_face_list = []
    non_dup_faces = []
    for occface in occfacelist:
        same_index = [fcnt]
        for fcnt2 in range(len(occfacelist)):
            if fcnt2 != fcnt:
                is_same = calculate.are_same_faces(occface, occfacelist[fcnt2])
                if is_same:
                    print is_same
                    same_index.append(fcnt2)
                    
        same_index.sort()
        if same_index not in same_face_list:
            same_face_list.append(same_index)                       
        fcnt +=1
        
    for indexes in same_face_list:
        unique_f = occfacelist[indexes[0]]
        non_dup_faces.append(unique_f)
    return non_dup_faces
    
def rmv_duplicated_edges(occedgelist):
    fcnt = 0
    same_edge_list = []
    non_dup_edges = []
    for occedge in occedgelist:
        same_index = [fcnt]
        for fcnt2 in range(len(occedgelist)):
            if fcnt2 != fcnt:
                is_same = calculate.are_same_edges(occedge, occedgelist[fcnt2])
                if is_same:
                    same_index.append(fcnt2)

        same_index.sort()
        if same_index not in same_edge_list:
            same_edge_list.append(same_index)                        
        fcnt +=1
        
    for indexes in same_edge_list:
        unique_f = occedgelist[indexes[0]]
        non_dup_edges.append(unique_f)
    return non_dup_edges
    
def rmv_duplicated_pts_by_distance(pyptlist, distance = 1e-06):
    '''
    fuse all pts in the list within a certain distance
    '''
    vert_list = fetch.pyptlist2vertlist(pyptlist)
    occpt_list = fetch.vertex_list_2_point_list(vert_list)
    
    filtered_pt_list = Common.filter_points_by_distance(occpt_list, distance = distance)
    f_pyptlist = fetch.occptlist2pyptlist(filtered_pt_list)
    '''
    npyptlist = len(pyptlist)
    total_ptlist = []
    for ptcnt in range(npyptlist):
        ptlist = []
        ptlist.append(ptcnt)
        for ptcnt2 in range(npyptlist):
            if ptcnt != ptcnt2:
                ptdist = calculate.distance_between_2_pts(pyptlist[ptcnt], pyptlist[ptcnt2])
                if ptdist <= distance:
                    ptlist.append(ptcnt2)
                    
        #ptlist.sort()
        if ptlist not in total_ptlist:
            total_ptlist.append(ptlist)
            
    upyptlist = []
    for upt in total_ptlist:
        upyptlist.append(pyptlist[upt[0]])
    return upyptlist
    '''
    return f_pyptlist
    
def rmv_duplicated_pts(pyptlist, roundndigit = None):
    '''
    fuse all pts in the list within a certain tolerance
    '''
    
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
   
def round_pypt(pypt, roundndigit):
    rounded_pypt = (round(pypt[0],roundndigit), round(pypt[1],roundndigit), round(pypt[2],roundndigit))
    return rounded_pypt
    
def round_pyptlist(pyptlist, roundndigit):
    rounded_pyptlist = []
    for pypt in pyptlist:
        rounded_pypt = round_pypt(pypt, roundndigit)
        rounded_pyptlist.append(rounded_pypt)
    return rounded_pyptlist
    
def trimedge(lbound, ubound, occedge):
    '''
    lbound: lower bound of the parameterise edge
    type: float
    
    ubound: upper bound of the parameterise edge
    type: float
    
    occedge: the edge to be trimmed
    type: occedge
    '''
    adaptor = BRepAdaptor_Curve(occedge)
    #print adaptor.Trim(adaptor.FirstParameter(), adaptor.LastParameter(), adaptor.Tolerance()).GetObject().NbPoles().Curve()
    tr = Geom_TrimmedCurve(adaptor.Curve().Curve(), lbound, ubound)
    tr.SetTrim(lbound, ubound)
    bspline_handle = geomconvert_CurveToBSplineCurve(tr.GetHandle())
    #print tr.GetHandle()
    tr_edge = BRepBuilderAPI_MakeEdge(bspline_handle)
    #occutil_edge = edge.Edge(occedge)
    #trimedge = occutil_edge.trim(lbound, ubound)
    
    return tr_edge.Edge()
    
def trim_wire(occ_wire, shapeLimit1, shapeLimit2, is_periodic=False):
    '''
    occwire: wire to be trimmed
    type: occwire
    
    shapeLimit1: the 1st point where to cut the wire
    type: tuple, e.g. (0,1,2.5)
    
    shapeLimit1: the 2nd point where to cut the wire
    type: tuple, e.g. (0,1,2.5)
    
    is_periodic: indicate if the wire is open or close, true for close, false for open
    type: bool, e.g. True or False
    '''
    
    trimmed = Construct.trim_wire(occ_wire, shapeLimit1, shapeLimit2, periodic= is_periodic )
    return trimmed
    
def wire_2_bsplinecurve_edge(occwire):
    '''
    occwire: wire to be converted
    type: occwire
    '''
    adaptor = BRepAdaptor_CompCurve(occwire)
    hadap = BRepAdaptor_HCompCurve(adaptor)
    from OCC.Approx import Approx_Curve3d
    from OCC.GeomAbs import GeomAbs_C0, GeomAbs_C0, GeomAbs_C2, GeomAbs_C3
    approx = Approx_Curve3d(hadap.GetHandle(), 1e-06, GeomAbs_C2 , 10000, 12)
    bspline_handle = approx.Curve()
    occedge = BRepBuilderAPI_MakeEdge(bspline_handle)
    return occedge.Edge()

def resample_wire(occwire):
    resample_curve = Common.resample_curve_with_uniform_deflection(occwire)
    print resample_curve
    
def flatten_face_z_value(occface, z=0):
    pyptlist = fetch.pyptlist_frm_occface(occface)
    pyptlist_2d = []
    for pypt in pyptlist:
        pypt2d = (pypt[0],pypt[1],z)
        pyptlist_2d.append(pypt2d)
    
    flatten_face = construct.make_polygon(pyptlist_2d)
    return flatten_face
        
def flatten_edge_z_value(occedge, z=0):
    occptlist = fetch.points_from_edge(occedge)        
    pyptlist = fetch.occptlist2pyptlist(occptlist)
    pyptlist_2d = []
    for pypt in pyptlist:
        pypt2d = (pypt[0],pypt[1],z)
        pyptlist_2d.append(pypt2d)
    flatten_edge = construct.make_edge(pyptlist_2d[0],pyptlist_2d[1])
    return flatten_edge
    
def flatten_shell_z_value(occshell, z=0):
    face_list = fetch.faces_frm_solid(occshell)
    xmin,ymin,zmin,xmax,ymax,zmax = calculate.get_bounding_box(occshell)
    boundary_pyptlist = [[xmin,ymin,zmin], [xmax,ymin,zmin], [xmax,ymax,zmin], [xmin,ymax,zmin]]
    boundary_face = construct.make_polygon(boundary_pyptlist)
    b_mid_pt = calculate.face_midpt(boundary_face)
    
    #flatten_shell = fetch.shape2shapetype(uniform_scale(occshell, 1, 1, 0, b_mid_pt))
    
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
        flatten_face = fetch.shape2shapetype(move(b_mid_pt, dest_pt,merged_faces[0]))
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
                fused_face_list = fetch.geom_explorer(fused_shape, "face")
                merged_faces = construct.merge_faces(fused_face_list)
                if len(merged_faces) == 1:
                    flatten_face = fetch.shape2shapetype(move(b_mid_pt, dest_pt,merged_faces[0]))
                    return flatten_face
                else:
                    flatten_vertex = fetch.geom_explorer(flatten_shell,"vertex")
                    flatten_pts = fetch.vertex_list_2_point_list(flatten_vertex)
                    flatten_pypts = fetch.occptlist2pyptlist(flatten_pts)
                    
                    dface_list = construct.delaunay3d(flatten_pypts)
                    merged_faces = construct.merge_faces(dface_list)
                    if len(merged_faces) == 1:
                        flatten_face = fetch.shape2shapetype(move(b_mid_pt, dest_pt,merged_faces[0]))
                        return flatten_face
                    else:
                        #construct.visualise([[occshell]],["WHITE"])
                        return None
        except RuntimeError:
            flatten_vertex = fetch.geom_explorer(flatten_shell,"vertex")
            flatten_pts = fetch.vertex_list_2_point_list(flatten_vertex)
            flatten_pypts = fetch.occptlist2pyptlist(flatten_pts)
            dface_list = construct.delaunay3d(flatten_pypts)
            merged_faces = construct.merge_faces(dface_list)
            if len(merged_faces) == 1:
                flatten_face = fetch.shape2shapetype(move(b_mid_pt, dest_pt,merged_faces[0]))
                return flatten_face
            else:
                #construct.visualise([[occshell]],["WHITE"])
                return None
    
    #3.) if it is a complex shell with more than 500 faces we get the vertexes and create a triangulated srf with delaunay 
        #and merge all the faces to make a single surface
    if nfaces >=50:
        flatten_vertex = fetch.geom_explorer(flatten_shell,"vertex")
        flatten_pts = fetch.vertex_list_2_point_list(flatten_vertex)
        flatten_pypts = fetch.occptlist2pyptlist(flatten_pts)
        #flatten_pypts = rmv_duplicated_pts_by_distance(flatten_pypts, tolerance = 1e-04)
        dface_list = construct.delaunay3d(flatten_pypts)
        merged_faces = construct.merge_faces(dface_list)
        if len(merged_faces) == 1:
            flatten_face = fetch.shape2shapetype(move(b_mid_pt, dest_pt,merged_faces[0]))
            return flatten_face
        else:
            #construct.visualise([[occshell]],["WHITE"])
            return None
    
    
def simplify_shell(occshell, tolerance = 1e-06):
    #this will merge any coincidental faces into a single surfaces to simplify the geometry
    fshell = fix_shell_orientation(occshell)
    #get all the faces from the shell and arrange them according to their normals
    sfaces = fetch.geom_explorer(fshell,"face")
    nf_dict = calculate.grp_faces_acc2normals(sfaces)
    merged_fullfacelist = []
    #merge all the faces thats share edges into 1 face     
    for snfaces in nf_dict.values():
        connected_face_shell_list = construct.make_shell_frm_faces(snfaces, tolerance=tolerance)
        if connected_face_shell_list:
            for shell in connected_face_shell_list:
                shell_faces = fetch.geom_explorer(shell, "face")    
                merged_facelist = construct.merge_faces(shell_faces,tolerance=tolerance)
                if merged_facelist:
                    merged_fullfacelist.extend(merged_facelist)
                else:
                    merged_fullfacelist.extend(shell_faces)
        else:
            merged_fullfacelist.extend(snfaces)
            
    nmerged_face = len(merged_fullfacelist)

    if len(merged_fullfacelist) >1:
        fshell2 = construct.make_shell_frm_faces(merged_fullfacelist, tolerance=tolerance)
        fshell2 = fix_shell_orientation(fshell2[0])
        nfshell2_face = len(fetch.geom_explorer(fshell2, "face"))
        if nfshell2_face!= nmerged_face:
            return occshell        
    else:
        #if there is only one face it means its an open shell
        fshell2 = construct.make_shell(merged_fullfacelist)

    return fshell2
    