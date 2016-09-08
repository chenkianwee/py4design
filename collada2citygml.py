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

def identify_city_objects(meshlist):
    '''
    identify the various city objects, terrain, landuse, roads and buildings
    '''
    #faces_frm_edges = py3dmodel.construct.wire_frm_loose_edges(occedgelist)
    
    building_solidlist = []
    plots_shelllist = []
    terrain_shelllist = []
    roads_edgelist =[]
    
    biggest_boundary_area = 0    
    mesh_cnt = 0
    boundarylist = []
    for mesh_d in meshlist:
        if "solidorshell" in mesh_d.keys():
            boundary_d = {}
            solidorshell = mesh_d["solidorshell"]
            xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(solidorshell)
            boundary_pyptlist = [[xmin,ymin,0], [xmax,ymin,0], [xmax,ymax,0], [xmin,ymax,0]]
            boundary_face = py3dmodel.construct.make_polygon(boundary_pyptlist)
            boundary_d["boundary"] = boundary_face
            boundary_d["meshcnt"] = mesh_cnt
            boundarylist.append(boundary_d)
        mesh_cnt+=1
    
    nboundary = len(boundarylist)
    boundarycntlist = range(nboundary)
    for bcnt in boundarycntlist:
        cur_boundary = boundarylist[bcnt] 
        boundarycntlist2 = boundarycntlist[:]
        boundarycntlist2.remove(bcnt)
        faces_inside = []
        for bcnt2 in boundarycntlist2:
            cur_boundary2 = boundarylist[bcnt2]
            is_inside = py3dmodel.calculate.face_is_inside(cur_boundary2["boundary"], cur_boundary["boundary"])
            if is_inside:
                faces_inside.append(cur_boundary2)
                cur_boundary2["is_inside"] = cur_boundary
                
        cur_boundary["contain_faces"] = faces_inside
    
    return meshlist[boundarylist[0]["is_inside"]["meshcnt"]]["solidorshell"]
            
    #return faces_frm_edges

def convert(collada_file):
    dae = Collada(collada_file)
    meshs = list(dae.scene.objects('geometry'))
    displaylist = []    
    
    meshlist = []
    for mesh in meshs:
        prim2dlist = list(mesh.primitives())
        mesh_dictionary = {}
        for primlist in prim2dlist:     
            print primlist
            if primlist:
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
                        mesh_dictionary["solidorshell"] = solid

                        
                    elif not shell_closed: #open shells are possibly terrains and plots
                        mesh_dictionary["solidorshell"] = occshell

                elif type(primlist) == lineset.BoundLineSet: 
                    occedgelist = daeedges2occedges(primlist)
                    mesh_dictionary["edgelist"] = occedgelist
                    
        meshlist.append(mesh_dictionary)
             
    #first find which of the open shell is a terrain
    faces_frm_edges = identify_city_objects(meshlist)
    displaylist.append(faces_frm_edges)
    #terrain_shelllist.append(faces_frm_edges)
    
    return displaylist