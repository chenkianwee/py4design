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

import py3dmodel
import threedmodel
from collada import *

'''
script to automatically convert a collada file into citygml file
the script is tested with a collada file exported from sketchup
'''

def daesrfs2occsrfs(daefacelist):
    occfacelist = []
    for face in daefacelist:
        pyptlist = face.vertices.tolist()
        occface = py3dmodel.construct.make_polygon(pyptlist)
        occfacelist.append(occface)
        
    return occfacelist
                    
def daeedges2occedges(daeedgelist):
    occedgelist = []
    for edge in daeedgelist:
        pyptlist = edge.vertices.tolist()
        occedge = py3dmodel.construct.make_edge(pyptlist[0], pyptlist[1])
        occedgelist.append(occedge)
            
    return occedgelist

def identify_city_objects(geomlist):
    '''
    identify the various city objects, terrain, landuse, roads and buildings
    '''
    #faces_frm_edges = py3dmodel.construct.wire_frm_loose_edges(occedgelist)
    building_solidlist = []
    plots_shelllist = []
    terrain_shelllist = []
    terrain_dictlist = []
    roads_edgelist =[]
    
    sslist = []
    edge2dlist = []    
    for geom_d in geomlist:
        if "solidorshell" in geom_d.keys():
            solidorshell = geom_d["solidorshell"]
            xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(solidorshell)
            boundary_pyptlist = [[xmin,ymin,0], [xmax,ymin,0], [xmax,ymax,0], [xmin,ymax,0]]
            boundary_face = py3dmodel.construct.make_polygon(boundary_pyptlist)
            geom_d["boundary"] = boundary_face
            sslist.append(geom_d)
        else:
            edge2dlist.append(geom_d)
    
    nss = len(sslist)
    nsscntlist = range(nss)
    for nsscnt in nsscntlist:
        cur_boundary = sslist[nsscnt] 
        nsscntlist2 = nsscntlist[:]
        nsscntlist2.remove(nsscnt)
        faces_inside = []
        for nsscnt2 in nsscntlist2:
            cur_boundary2 = sslist[nsscnt2]
            is_inside = py3dmodel.calculate.face_is_inside(cur_boundary2["boundary"], cur_boundary["boundary"])
            if is_inside:
                cur_boundary_area = py3dmodel.calculate.face_area(cur_boundary["boundary"])
                cur_boundary_area2 = py3dmodel.calculate.face_area(cur_boundary2["boundary"])
                if cur_boundary_area == cur_boundary_area2:
                    difference = py3dmodel.construct.boolean_difference(cur_boundary["boundary"], cur_boundary2["boundary"])
                    if py3dmodel.fetch.is_compound_null(py3dmodel.fetch.shape2shapetype(difference)):
                        if "is_same_as" in cur_boundary.keys():
                            cur_boundary["is_same_as"].append(nsscnt2)
                        else:
                            cur_boundary["is_same_as"] = [nsscnt2]
                    else:
                        faces_inside.append(nsscnt2)
                        if "is_inside" in cur_boundary2.keys():
                            cur_boundary2["is_inside_indices"].append(nsscnt)
                        else:
                            cur_boundary2["is_inside_indices"] = [nsscnt]
                else:
                    faces_inside.append(nsscnt2)
                    if "is_inside" in cur_boundary2.keys():
                        cur_boundary2["is_inside_indices"].append(nsscnt)
                    else:
                        cur_boundary2["is_inside_indices"] = [nsscnt]
                
        cur_boundary["contain_faces_indices"] = faces_inside
    
    #identify the various city objects base on the size and position of the geometry
    sscnt = 0
    for ss in sslist:
        keys = ss.keys()
        print keys
        ncontainface = len(ss["contain_faces_indices"])
        #if the geom only contain faces and is not inside any other faces
        if ncontainface > 0 and "is_inside_indices" not in keys: 
            #do not append repeeat geometries
            if "is_same_as" in keys:
                samecntlist = ss["is_same_as"]
                samecntlist.append(sscnt)
                min_index = samecntlist.index(min(samecntlist))
                if min_index == len(samecntlist)-1:
                    terrain_shelllist.append(ss["solidorshell"])
                    terrain_dictlist.append(ss)
            else:
                terrain_shelllist.append(ss["solidorshell"])
                terrain_dictlist.append(ss)
                
        #if the geom is inside other geom and do not contain anything it is a building 
        if ncontainface == 0 and "is_inside_indices" in keys:
            building_solidlist.append((ss["solidorshell"]))
            
        sscnt+=1
    
    for ts in terrain_dictlist:
        meshcnt = ts["meshcnt"]
        #for edge_d in edge2dlist:
            
            
    displaylist = []
    #displaylist.append(ssdict["solidorshell"])
    displaylist.extend(terrain_shelllist)
    displaylist.extend(building_solidlist)
    return displaylist

def convert(collada_file):
    dae = Collada(collada_file)
    meshs = list(dae.scene.objects('geometry'))
    displaylist = []    
    
    geomlist = []
    meshcnt = 0
    for mesh in meshs:
        prim2dlist = list(mesh.primitives())
        for primlist in prim2dlist:     
            print primlist
            if primlist:
                geom_dict = {}
                geom_dict["meshcnt"] = meshcnt
                if type(primlist) == triangleset.BoundTriangleSet or type(primlist) == polylist.BoundPolylist:
                    #need to check if the triangleset is a close solid 
                    occfacelist = daesrfs2occsrfs(primlist)
                    occshell = py3dmodel.construct.make_shell_frm_faces(occfacelist)[0]
                    shell_closed = py3dmodel.calculate.is_shell_closed(occshell)
                    if shell_closed:#solids are possibly building massings
                        merged_fullfacelist = []
                        #group the faces according to their normals
                        occfacelist = py3dmodel.fetch.faces_frm_shell(occshell)
                        nf_dict = py3dmodel.calculate.grp_faces_acc2normals(occfacelist)
                        #merge all the faces thats share edges into 1 face
                        for faces in nf_dict.values():
                            merged_facelist = py3dmodel.construct.merge_faces(faces)
                            merged_fullfacelist.extend(merged_facelist)
                        shell = py3dmodel.construct.make_shell_frm_faces(merged_fullfacelist)[0]
                        solid = py3dmodel.construct.make_solid(shell)
                        geom_dict["solidorshell"] = solid
                            
                    elif not shell_closed: #open shells are possibly terrains and plots
                        geom_dict["solidorshell"] = occshell

                elif type(primlist) == lineset.BoundLineSet: 
                    occedgelist = daeedges2occedges(primlist)
                    geom_dict["edgelist"] = occedgelist
                    
                geomlist.append(geom_dict)
                
        meshcnt +=1
    #first find which of the open shell is a terrain
    faces_frm_edges = identify_city_objects(geomlist)
    displaylist.extend(faces_frm_edges)
    #terrain_shelllist.append(faces_frm_edges)
    
    return displaylist