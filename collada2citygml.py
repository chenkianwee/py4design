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
    
def edges3d22d(occedgelist):
    occedge2d_list = []
    for edge in occedgelist:
        occptlist = py3dmodel.fetch.points_from_edge(edge)
        pyptlist = py3dmodel.fetch.occptlist2pyptlist(occptlist)
        pyptlist2d = []
        for pypt in pyptlist:
            pypt2d = (pypt[0], pypt[1],0)
            pyptlist2d.append(pypt2d)
        occedge2d = py3dmodel.construct.make_edge(pyptlist2d[0], pyptlist2d[1])
        occedge2d_list.append(occedge2d)
    return occedge2d_list

def wire3d22d(occwire):
    pyptlist2d = []
    pyptlist = py3dmodel.fetch.occptlist2pyptlist(py3dmodel.fetch.points_frm_wire(occwire))
    
    for pypt in pyptlist:
        pypt2d = [pypt[0],pypt[1],0]
        pyptlist2d.append(pypt2d)
         
    pyptlist2d.append(pyptlist2d[0])
    occwire2d = py3dmodel.construct.make_wire(pyptlist2d)
    return occwire2d
    
def sphere2edge_pts(occedgelist, radius):
    circlelist = []
    for edge in occedgelist:
        occptlist = py3dmodel.fetch.points_from_edge(edge)
        pyptlist = py3dmodel.fetch.occptlist2pyptlist(occptlist)
        for pypt in pyptlist:
            occcircle = py3dmodel.construct.make_circle(pypt, (0,0,1), radius)
            circlelist.append(occcircle)
    return circlelist
    
def make_boundingface(occshape):
    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(occshape)
    boundary_pyptlist = [[xmin,ymin,0], [xmax,ymin,0], [xmax,ymax,0], [xmin,ymax,0]]
    boundary_face = py3dmodel.construct.make_polygon(boundary_pyptlist)
    return boundary_face
    
def consolidate_terrain_shelllist(terrain_shelllist):
    terrain_faces = []
    for shell in terrain_shelllist:
        terrain_faces.extend(py3dmodel.fetch.faces_frm_shell(shell))
        
    consolidated_terrain_shelllist = py3dmodel.construct.make_shell_frm_faces(terrain_faces)
    return consolidated_terrain_shelllist

def is_edge_touching_terrain(edgelist, terrain_shelllist):
    touchlist = []
    min_dislist = []
    for shell in terrain_shelllist:
        for edge in edgelist:
            min_dist = py3dmodel.calculate.minimum_distance(edge, shell)
            min_dislist.append(min_dist)
            if round(min_dist,6) == 0:
                touchlist.append(1)
                
    if len(touchlist) >= len(edgelist):
        return True
    else:
        return False
        
def identify_city_objects(geomlist):
    '''
    identify the various city objects, terrain, landuse, roads and buildings
    '''
    building_solidlist = []
    plot_wirelist = []
    plot_shelllist = []
    terrain_shelllist = []
    terrain_dictlist = []
    road_wirelist =[]
    b_display = []
    
    #======================================================================
    #SEPARATE THE GEOMETRIES INTO SOLIDORSHELL AND EDGES
    #======================================================================
    sslist = []
    edge2dlist = []    
    for geom_d in geomlist:
        if "solidorshell" in geom_d.keys():
            solidorshell = geom_d["solidorshell"]
            boundary_face = make_boundingface(solidorshell)
            geom_d["boundary"] = boundary_face
            sslist.append(geom_d)
        else:
            edge2dlist.append(geom_d)
    
    print "NEDGES", len(edge2dlist)
    #======================================================================
    #ESTABLISH THE RELATIONSHIP BETWEEN GEOMETRIES "IS_INSIDE"
    #======================================================================
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
    
    #==============================================================================
    #identify the various city objects base on the size and position of the geometry
    #==============================================================================
    sscnt = 0
    for ss in sslist:
        keys = ss.keys()
        ncontainface = len(ss["contain_faces_indices"])
        is_solid = ss["is_solid"]
        #if the geom is open shell only contain faces and is not inside any other faces it is definitely a terrain
        if not is_solid and ncontainface > 0 and "is_inside_indices" not in keys: 
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
                
        #if the geom is open shell may or may not contain faces and is inside other faces it is possibly a terrain
        if not is_solid:
            terrain_shelllist.append(ss["solidorshell"])
            terrain_dictlist.append(ss)
            
        #if the geom is inside other geom and do not contain anything it is a building 
        if ncontainface == 0 and "is_inside_indices" in keys:
            building_solidlist.append((ss["solidorshell"]))
            
        sscnt+=1
        
    terrain_shelllist = consolidate_terrain_shelllist(terrain_shelllist)
    
    for ts in terrain_dictlist:
        meshcnt = ts["meshcnt"]
        #search for edges that has the same meshcnt as the terrain geometries or it is touching the terrain
        for edge_d in edge2dlist:
            edgelist = edge_d["edgelist"]
            edge_meshcnt = edge_d["meshcnt"]
            is_edge_touch = is_edge_touching_terrain(edgelist, terrain_shelllist)
           
            #if edge is touching the terrain or have same meshcnt 
            if edge_meshcnt == meshcnt or is_edge_touch:
                
                if edgelist:
                    #rearrange the edges, edges that are open are roads, closed edges are plots
                    close_wire_edge2dlist, open_wire_edge2dlist = py3dmodel.calculate.identify_open_close_wires_frm_loose_edges(edgelist)
                    for open_wire_edgelist in open_wire_edge2dlist:
                        open_wire = py3dmodel.construct.make_wire_frm_edges(open_wire_edgelist)
                        road_wirelist.append(open_wire)
                    for close_wire_edgelist in close_wire_edge2dlist:
                        close_wire = py3dmodel.construct.make_wire_frm_edges(close_wire_edgelist)
                        wire_pts = py3dmodel.fetch.occptlist2pyptlist(py3dmodel.fetch.points_frm_wire(close_wire))
                        plot_wirelist.append(close_wire)
              
    print "NROAD", len(road_wirelist)
    for plot_wire in plot_wirelist:
        plot_face3d = py3dmodel.construct.make_face_frm_wire(plot_wire)
        plot_wire2d = wire3d22d(plot_wire)
        #check the area of the plot, if the area is the same as the terrain it cannot be the plot
        #this is to make sure the outer edges cannot be counted as a plot
        #get the area of the terrain
        this_is_a_plot = True
        for tshell in terrain_shelllist:
            pdifference = py3dmodel.construct.boolean_difference(tshell, plot_face3d )
            if py3dmodel.fetch.is_compound_null(py3dmodel.fetch.shape2shapetype(pdifference)):
                #print "I AM REMOVED FOR BEING THE TERRAIN"
                this_is_a_plot = False
                plot_wirelist.remove(plot_wire)
                break

        #need to check if the touches any of the roads 
        #only if it doesnt touch any roads it is a plot
        if this_is_a_plot:
            for road_wire in road_wirelist:
                #first flatten the road 
                #road_wire2d = wire3d22d(road_wire)
                min_dist = py3dmodel.calculate.minimum_distance(plot_wire2d, road_wire)
                if min_dist == 0: #means it is touching, this is not a plot and prob a roundabout 
                    #print "I AM REMOVED FOR BEING A ROAD"                    
                    this_is_a_plot = False
                    road_wirelist.append(plot_wire)
                    plot_wirelist.remove(plot_wire)
                    break
            
        if this_is_a_plot:     
            wire_pts = py3dmodel.fetch.occptlist2pyptlist(py3dmodel.fetch.points_frm_wire(plot_wire2d))
            #plot_face = py3dmodel.construct.make_polygon(wire_pts)
            plot_face2d = py3dmodel.construct.make_face_frm_wire(plot_wire2d)            
            origpt = wire_pts[0]
            locpt = py3dmodel.modify.move_pt(origpt, (0,0,-1),500000)
            plot_face_moved = py3dmodel.modify.move(origpt, locpt, plot_face2d)
            
            extrude_plot = py3dmodel.construct.extrude(plot_face_moved, (0,0,1), 1000000)
            for terrain in terrain_shelllist:
                common_compound =py3dmodel.fetch.shape2shapetype(py3dmodel.construct.boolean_common(extrude_plot, terrain))
                is_compound_null = py3dmodel.fetch.is_compound_null(common_compound)
                if not is_compound_null:
                    face_list = py3dmodel.fetch.geom_explorer(common_compound, "face")
                    if len(face_list) != 1:
                        plot_shell = py3dmodel.construct.make_shell_frm_faces(face_list)[0]
                        plot_shelllist.append(plot_shell)
                    else:
                        plot_shelllist.append(face_list[0])
        
    cityobject_dict = {"terrain":terrain_shelllist, "plot":plot_shelllist, 
    "building":building_solidlist, "road":road_wirelist}
    
    return cityobject_dict

def convert(collada_file):
    dae = Collada(collada_file)
    nodes = dae.scene.nodes
    
    #this loops thru the visual scene 
    #loop thru the library nodes
    for node in nodes:
        name = node.xmlnode.get('name')
        children_nodes = node.children
        if children_nodes:
            for node2 in children_nodes:
                name2 = node2.xmlnode.get('name')
                print 'name2', name2
                children_node2 = node2.children
                if children_node2:
                    if type(children_node2[0]) == scene.NodeNode:
                        print children_node2[0].children

    
    meshs = list(dae.scene.objects('geometry')) 
    geomlist = []
    meshcnt = 0
    for mesh in meshs:
        prim2dlist = list(mesh.primitives())
        for primlist in prim2dlist:     
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
                        geom_dict["is_solid"] = True
                            
                    elif not shell_closed: #open shells are possibly terrains and plots
                        geom_dict["solidorshell"] = occshell
                        geom_dict["is_solid"] = False

                elif type(primlist) == lineset.BoundLineSet: 
                    occedgelist = daeedges2occedges(primlist)
                    geom_dict["edgelist"] = occedgelist
                    
                geomlist.append(geom_dict)
                
        meshcnt +=1
        
    #first find which of the open shell is a terrain
    cityobject_dict = identify_city_objects(geomlist)
    
    return cityobject_dict