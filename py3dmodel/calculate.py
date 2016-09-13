# ==================================================================================================
#
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
import math
import fetch

from OCCUtils import face, Common, Construct, Topology, edge
from OCC import BRepFeat 
from OCC.gp import gp_Pnt, gp_Vec, gp_Lin, gp_Ax1, gp_Dir
from OCC.TopAbs import TopAbs_IN, TopAbs_REVERSED 
from OCC.BRepClass3d import BRepClass3d_SolidClassifier
from OCC.GProp import GProp_GProps
from OCC.BRepGProp import brepgprop_VolumeProperties
from OCC.BOPInt import BOPInt_Context
from OCC.BRepCheck import BRepCheck_Wire, BRepCheck_Shell, BRepCheck_NoError
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.BRep import BRep_Tool
from OCC.IntCurvesFace import IntCurvesFace_ShapeIntersector

def get_bounding_box(occ_shape):
    return Common.get_boundingbox(occ_shape)
    
def get_centre_bbox(occ_shape):
    occ_midpt = Common.center_boundingbox(occ_shape)
    return (occ_midpt.X(), occ_midpt.Y(), occ_midpt.Z())
    
def point_in_solid(occ_solid, pypt):
    gp_pnt = gp_Pnt(pypt[0], pypt[1], pypt[2] )
    if Common.point_in_solid(occ_solid, gp_pnt)[0]:
        return True 
    elif Common.point_in_solid(occ_solid, gp_pnt)[0] == None:
        return None #means its on the solid
    else: 
        return False
        
def minimum_distance(occ_shape1, occ_shape2):
    min_dist, min_dist_shp1, min_dist_shp2 = Common.minimum_distance(occ_shape1, occ_shape2)
    return min_dist
    
def face_normal(occface):
    fc = face.Face(occface)
    centre_uv,centre_pt = fc.mid_point()
    normal_dir = fc.DiffGeom.normal(centre_uv[0],centre_uv[1])
    if occface.Orientation() == TopAbs_REVERSED:
        normal_dir = normal_dir.Reversed()
        
    normal = (normal_dir.X(), normal_dir.Y(), normal_dir.Z())
    return normal
    
def face_midpt(occface):
    fc = face.Face(occface)
    centre_uv,gpcentre_pt = fc.mid_point()
    centre_pt = (gpcentre_pt.X(), gpcentre_pt.Y(), gpcentre_pt.Z())
    return centre_pt
    
def is_anticlockwise(pyptlist, pyref_vec):
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
    gp_ref_vec = gp_Vec(pyref_vec[0],pyref_vec[1],pyref_vec[2])
    result  = gp_total.Dot(gp_ref_vec)
    if result < 0:
        return False 
    else:
        return True
        
def face_area(occ_face):
    surface_area = Common.GpropsFromShape(occ_face).surface()
    return surface_area.Mass()
    
def solid_volume(occ_solid):
    props = GProp_GProps()
    brepgprop_VolumeProperties(occ_solid, props)
    volume = props.Mass()
    return volume
    
def face_is_inside(occ_face, occ_boundary_face):
    return BRepFeat.brepfeat_IsInside(occ_face, occ_boundary_face)

def point_in_face(pypt, occ_face, tol=0.0001):
    gp_pt = gp_Pnt(pypt[0], pypt[1], pypt[2])
    isinside = BOPInt_Context().IsValidPointForFace(gp_pt, occ_face,tol )
    return isinside
    
def check_solid_inward(occ_solid):
    classify = BRepClass3d_SolidClassifier()
    classify.Load(occ_solid)
    classify.PerformInfinitePoint(0.001)
    state = classify.State()
    if state == TopAbs_IN:
        return True 
    else:
        return False 
        
def is_wire_closed(occ_wire):
    wire_checker = BRepCheck_Wire(occ_wire)
    is_closed = wire_checker.Closed()
    if is_closed == BRepCheck_NoError:
        return True 
    else:
        return False 
     
def project_edge_on_face(occface, occ_edge):
    fc = face.Face(occface)
    projected_curve = fc.project_curve(occ_edge)
    return projected_curve
    
def project_point_on_faceplane(occface, pypt):
    gp_pt = gp_Pnt(pypt[0], pypt[1], pypt[2])
    fc = face.Face(occface)
    uv, projected_pt = fc.project_vertex(gp_pt)
    return projected_pt
    
def project_face_on_faceplane(occface2projon, occface2proj):
    wire_list =  list(Topology.Topo(occface2proj).wires())
    occpt_list = []
    for wire in wire_list:
        occpts = Topology.WireExplorer(wire).ordered_vertices()
        occpt_list.extend(occpts)
    proj_ptlist = []
    for occpt in occpt_list:
        occ_pnt = BRep_Tool.Pnt(occpt)
        pypt = (occ_pnt.X(), occ_pnt.Y(), occ_pnt.Z())
        projected_pt = project_point_on_faceplane(occface2projon, pypt)
        proj_ptlist.append(projected_pt)
        
    return proj_ptlist
    
def intersect_edge_with_face(occ_edge, occ_face):
    occutil_edge = edge.Edge(occ_edge)
    interptlist = occutil_edge.Intersect.intersect(occ_face, 1e-2)
    return interptlist
    
def project_point_on_infedge(occ_edge, pypt):
    gp_pt = gp_Pnt(pypt[0], pypt[1], pypt[2])
    occutil_edge = edge.Edge(occ_edge)
    u, projpt = occutil_edge.project_vertex(gp_pt)
    return projpt
    
def intersect_shape_with_ptdir(occ_shape, pypt, pydir):
    occ_line = gp_Lin(gp_Ax1(gp_Pnt(pypt[0], pypt[1], pypt[2]), gp_Dir(pydir[0], pydir[1], pydir[2])))
    shape_inter = IntCurvesFace_ShapeIntersector()
    shape_inter.Load(occ_shape, 1e-6)
    shape_inter.PerformNearest(occ_line, 0.0, float("+inf"))
    if shape_inter.IsDone():
        npts = shape_inter.NbPnt()
        if npts !=0:
            return shape_inter.Pnt(1), shape_inter.Face(1)
        else:
            return None, None 
    else:
        return None, None 
    
def srf_nrml_facing_solid_inward(occ_face, occ_solid):
    #move the face in the direction of the normal
    #first offset the face so that vert will be within the solid 
    o_wire = Construct.make_offset(occ_face, 0.0001)
    o_face = BRepBuilderAPI_MakeFace(o_wire).Face()
    
    wire_list =  list(Topology.Topo(o_face).wires())
    occpt_list = []
    for wire in wire_list:
        occpts = Topology.WireExplorer(wire).ordered_vertices()
        occpt_list.extend(occpts)
        
        
    pt = BRep_Tool.Pnt(occpt_list[0]) #a point that is on the edge of the face 
    normal = face_normal(occ_face)
    
    gp_direction2move = gp_Vec(normal[0], normal[1], normal[2])
    gp_moved_pt = pt.Translated(gp_direction2move.Multiplied(0.001))
    mv_pt = (gp_moved_pt.X(), gp_moved_pt.Y(), gp_moved_pt.Z())
    
    in_solid = point_in_solid(occ_solid, mv_pt)
    
    if in_solid:
        return True
    else:
        return False
        
def angle_bw_2_vecs(pyvec1, pyvec2):
    vec1 = gp_Vec(pyvec1[0], pyvec1[1], pyvec1[2])
    vec2 = gp_Vec(pyvec2[0], pyvec2[1], pyvec2[2])
    radangle = vec1.Angle(vec2)
    angle = radangle * (180.0/math.pi)
    return angle
    
def distance_between_2_pts(pypt1, pypt2):
    gp_pnt1 = gp_Pnt(pypt1[0], pypt1[1], pypt1[2])
    gp_pnt2 = gp_Pnt(pypt2[0], pypt2[1], pypt2[2])
    distance = gp_pnt1.Distance(gp_pnt2)
    return distance
    
def is_shell_closed(occshell):
    shell_checker = BRepCheck_Shell(occshell)
    is_closed = shell_checker.Closed()
    if is_closed == BRepCheck_NoError:
        return True 
    else:
        return False 
        
def grp_faces_acc2normals(occfacelist):
    normal_face_dict = {}
    for occface in occfacelist:
        n = face_normal(occface)
        n = (round(n[0],6), round(n[1],6), round(n[2],6))
        keys = normal_face_dict.keys()
        if n not in keys:
            normal_face_dict[n] = [occface]
        elif n in keys:
            normal_face_dict[n].append(occface)
            
    return normal_face_dict
    
def edge_common_vertex(occedge1, occedge2):
    pyptlist_all = []
    edgepyptlist1 = fetch.occptlist2pyptlist(fetch.points_from_edge(occedge1))
    edgepyptlist2 = fetch.occptlist2pyptlist(fetch.points_from_edge(occedge2))
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
        
def are_same_edges(occedge1, occedge2):
    edgepyptlist1 = fetch.occptlist2pyptlist(fetch.points_from_edge(occedge1))
    edgepyptlist2 = fetch.occptlist2pyptlist(fetch.points_from_edge(occedge2))
    if edgepyptlist1 == edgepyptlist2:
        return True
    else:
        edgepyptlist1.reverse()
        if edgepyptlist1 == edgepyptlist2:
            return True 
        else:
            return False 
    
def identify_open_close_wires_frm_loose_edges(occedgelist):
    open_wires = []
    close_wires = []
    occedgelist2 = occedgelist[:]
    cur_edge = occedgelist2[0]
    cur_wire = [cur_edge]
    
    while len(occedgelist)>0:
        print 'NOCCEDGELIST', len(occedgelist)
        occedgelist2.remove(cur_edge)
        noccedgelist2 = len(occedgelist2)
        print 'NOCCEDGELIST2', noccedgelist2
        
        if noccedgelist2 == 0:
            open_wires.append(cur_wire)
            for rmvedge in cur_wire:
                occedgelist.remove(rmvedge)
        
        ecnt = 0
        for occedge in occedgelist2:
            print 'ecnt', ecnt
            #make sure the 2 edges are not the same edge
            if are_same_edges(cur_edge, occedge):
                print "it is the same edge"
                occedgelist.remove(occedge)
            elif edge_common_vertex(cur_edge, occedge):
                print "I have the same points"
                cur_wire.append(occedge)
                cur_edge = occedge
                #needs to check if this edge connects to any other previous edges
                ncur_wire = len(cur_wire)
                print 'curwire', ncur_wire
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
                            print "I have the same point again"
                            close_cur_wire = cur_wire[negcnt:]
                            close_wires.append(close_cur_wire)
                            #remove all the edges in cur_wire from occedgelist
                            for rmvedge in close_cur_wire:
                                occedgelist.remove(rmvedge)
                                
                            occedgelist2 = occedgelist[:]
                            cur_edge = occedgelist2[0]
                            cur_wire = [cur_edge]
                            break

                    #cur_wire.append(occedge)
                    #cur_edge = occedge
                    break
                            
                else:
                    #cur_wire.append(occedge)
                    #cur_edge = occedge
                    break 
                
            #if you have loop through the whole edge list and still did not 
            #find any edge that share a common edge, it means this is the 
            # last edge of an open wire
            elif ecnt == noccedgelist2-1:
                print "I am at the last of the edges"
                open_wires.append(cur_wire)
                #remove all the edge in cur_wire from occedgelist
                for rmvedge in cur_wire:
                    occedgelist.remove(rmvedge)
                    
                occedgelist2 = occedgelist[:]
                cur_edge = occedge
                cur_wire = [cur_edge]
                break
                
            ecnt+=1
            
    print len(close_wires), len(open_wires)
    return close_wires, open_wires