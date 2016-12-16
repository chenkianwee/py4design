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
import pycitygml
from collada import *

'''
script to automatically convert a collada file into citygml file
the script is tested with a collada file exported from sketchup
'''
def redraw_occ_shell_n_edge(occcompound):
    #redraw the surfaces so the domain are right
    #TODO: fix the scaling 
    recon_shelllist = []
    shells = py3dmodel.fetch.geom_explorer(occcompound, "shell")
    for shell in shells:
        faces = py3dmodel.fetch.geom_explorer(shell, "face")
        recon_faces = []
        for face in faces:
            pyptlist = py3dmodel.fetch.pyptlist_frm_occface(face)
            recon_face = py3dmodel.construct.make_polygon(pyptlist)
            recon_faces.append(recon_face)
        nrecon_faces = len(recon_faces)
        if nrecon_faces == 1:
            recon_shell = py3dmodel.construct.make_shell(recon_faces)
        if nrecon_faces > 1:
            recon_shell = py3dmodel.construct.make_shell_frm_faces(recon_faces)[0]
        recon_shelllist.append(recon_shell)
        
    #boolean the edges from the shell compound and edges compound and find the difference to get the network edges
    shell_compound = py3dmodel.construct.make_compound(shells)
    shell_edges = py3dmodel.fetch.geom_explorer(shell_compound, "edge")
    shell_edge_compound = py3dmodel.construct.make_compound(shell_edges)
    
    edges = py3dmodel.fetch.geom_explorer(occcompound, "edge")
    edge_compound = py3dmodel.construct.make_compound(edges)
    network_edge_compound = py3dmodel.construct.boolean_difference(edge_compound,shell_edge_compound) 
    
    nw_edges = py3dmodel.fetch.geom_explorer(network_edge_compound,"edge")
    recon_edgelist = []
    for edge in nw_edges:
        eptlist = py3dmodel.fetch.points_from_edge(edge)
        epyptlist = py3dmodel.fetch.occptlist2pyptlist(eptlist)
        recon_edgelist.append(py3dmodel.construct.make_edge(epyptlist[0], epyptlist[1]))
        
    recon_compoundlist = recon_shelllist + recon_edgelist
    recon_compound = py3dmodel.construct.make_compound(recon_compoundlist)
    return recon_compound
    
def simplify_shell(occshell):
    #this will merge any coincidental faces into a single surfaces to simplify the geometry
    fshell = py3dmodel.modify.fix_shell_orientation(occshell)
    #get all the faces from the shell and arrange them according to their normals
    sfaces = py3dmodel.fetch.geom_explorer(fshell,"face")
    nf_dict = py3dmodel.calculate.grp_faces_acc2normals(sfaces)
    merged_fullfacelist = []
    #merge all the faces thats share edges into 1 face
    for snfaces in nf_dict.values():
        merged_facelist = py3dmodel.construct.merge_faces(snfaces)
        merged_fullfacelist.extend(merged_facelist)
        
    if len(merged_fullfacelist) >1:
        simpleshell = py3dmodel.construct.make_shell_frm_faces(merged_fullfacelist)
        fshell2 = py3dmodel.modify.fix_shell_orientation(simpleshell[0])
        
    else:
        #if there is only one face it means its an open shell
        fshell2 = py3dmodel.construct.make_shell(merged_fullfacelist)
    return fshell2

def make_2dboundingface(occshape):
    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(occshape)
    boundary_pyptlist = [[xmin,ymin,0], [xmax,ymin,0], [xmax,ymax,0], [xmin,ymax,0]]
    boundary_face = py3dmodel.construct.make_polygon(boundary_pyptlist)
    return boundary_face
    
def identify_shell_attribs(occshelllist):
    nshells = len(occshelllist)
    shell_dictlist = []

    for shellcnt in range(nshells):
        shell_dict = {}
        is_in_boundary = []
        boundary_contains = []
        #first check if it is an open or close shell
        shell = occshelllist[shellcnt]
        shell_dict["shell"] = shell
        is_closed = py3dmodel.calculate.is_shell_closed(shell)
        if is_closed:
            shell_dict["is_closed"] = True
        else:
            shell_dict["is_closed"] = False
            
        cur_boundary = make_2dboundingface(shell)
        for shellcnt2 in range(nshells):
            if shellcnt2 != shellcnt:
                nxt_shell = occshelllist[shellcnt2]
                nxt_boundary = make_2dboundingface(nxt_shell)
                #check if cur_shell is inside nxt_shell
                is_inside_nxt_boundary = py3dmodel.calculate.face_is_inside(cur_boundary,nxt_boundary)
                if is_inside_nxt_boundary:
                    is_in_boundary.append(nxt_shell)
                    
                #check if cur_shell contains nxt_shell
                contains_nxt_boundary = py3dmodel.calculate.face_is_inside(nxt_boundary,cur_boundary)
                if contains_nxt_boundary:
                    boundary_contains.append(nxt_shell)
                    
        shell_dict["is_in_boundary"] = is_in_boundary
        shell_dict["boundary_contains"] = boundary_contains
        shell_dictlist.append(shell_dict)
    return shell_dictlist
    
def identify_edge_attribs(occedgelist, occshelllist):
    edge_dictlist = []
    for edge in occedgelist:
        edge_dict = {}
        is_in_boundary = []
        edge_dict["edge"] = edge
        for shell in occshelllist:
            min_dist = py3dmodel.calculate.minimum_distance(edge,shell)
            if min_dist < 0.0001:
                is_in_boundary.append(shell)
                
        edge_dict["is_in_boundary"] = is_in_boundary
        edge_dictlist.append(edge_dict)
    return edge_dictlist
    
def identify_open_close_shells(occshell_list):
    close_shell_list = []
    open_shell_list = []
    for shell in occshell_list:
        is_closed = py3dmodel.calculate.is_shell_closed(shell)
        if is_closed:
            close_shell_list.append(shell)
        else:
            open_shell_list.append(shell)
            
    return close_shell_list, open_shell_list
    
def sew_shells(occshell_list):
    close_shell_list, open_shell_list = identify_open_close_shells(occshell_list)
            
    open_shell_compound = py3dmodel.construct.make_compound(open_shell_list)
    open_shell_faces = py3dmodel.fetch.geom_explorer(open_shell_compound, "face")
    #sew all the open shell faces together to check if there are solids among the open shells
    recon_shell_list = py3dmodel.construct.make_shell_frm_faces(open_shell_faces)
    recon_close_shell_list, recon_open_shell_list = identify_open_close_shells(recon_shell_list)
    if recon_close_shell_list:
        recon_close_shell_compound = py3dmodel.construct.make_compound(recon_close_shell_list)
        #boolean difference the close shells from the open shells 
        difference = py3dmodel.construct.boolean_difference(open_shell_compound, recon_close_shell_compound)
        difference = py3dmodel.fetch.shape2shapetype(difference)
        open_shell_faces2 = py3dmodel.fetch.geom_explorer(difference, "face")
        open_shell_list2 = py3dmodel.construct.make_shell_frm_faces(open_shell_faces2)
        return close_shell_list + recon_close_shell_list + open_shell_list2
    else:
        return occshell_list
    
def read_collada(dae_filepath):
    '''
    the dae file must be modelled as such:
    close_shells = buildings
    open_shells = terrain & plots(land-use)
    edges = street network
    '''
    edgelist = []
    shelllist = []
    mesh = Collada(dae_filepath)
    unit = mesh.assetInfo.unitmeter or 1
    geoms = mesh.scene.objects('geometry')
    geoms = list(geoms)
    gcnt = 0
    for geom in geoms:   
        prim2dlist = list(geom.primitives())
        for primlist in prim2dlist: 
            spyptlist = []
            epyptlist = []
            faces = []
            edges = []
            if primlist:
                for prim in primlist:
                    if type(prim) == polylist.Polygon or type(prim) == triangleset.Triangle:
                        pyptlist = prim.vertices.tolist()
                        pyptlist.sort()
                        if pyptlist not in spyptlist:
                            spyptlist.append(pyptlist)
                            occpolygon = py3dmodel.construct.make_polygon(pyptlist)
                            if not py3dmodel.fetch.is_face_null(occpolygon):
                                faces.append(occpolygon)
                            gcnt +=1
                    elif type(prim) == lineset.Line:
                        pyptlist = prim.vertices.tolist()
                        pyptlist.sort()
                        if pyptlist not in epyptlist:
                            epyptlist.append(pyptlist)
                            occedge = py3dmodel.construct.make_edge(pyptlist[0], pyptlist[1])
                            edges.append(occedge)
                        gcnt +=1
                        
                if faces:
                    #remove all the duplicated faces
                    #non_dup_faces = py3dmodel.modify.rmv_duplicated_faces(faces)
                    n_unique_faces = len(faces)
                    if n_unique_faces == 1:
                        shell = py3dmodel.construct.make_shell(faces)
                        shelllist.append(shell)
                    if n_unique_faces >1:
                        shell = py3dmodel.construct.make_shell_frm_faces(faces)[0]
                        #this will merge any coincidental faces into a single surfaces to simplify the geometry
                        shell = simplify_shell(shell)
                        shelllist.append(shell)
                else:
                    edgelist.extend(edges)
    
    #find the midpt of all the geometry
    compoundlist = shelllist + edgelist
    compound = py3dmodel.construct.make_compound(compoundlist)
    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(compound)
    ref_pt = py3dmodel.calculate.get_centre_bbox(compound)
    ref_pt = (ref_pt[0],ref_pt[1],zmin)
    #make sure no duplicate edges 
    scaled_shape = py3dmodel.modify.uniform_scale(compound, unit, unit, unit,ref_pt)
    scaled_compound = py3dmodel.fetch.shape2shapetype(scaled_shape)
    recon_compound = redraw_occ_shell_n_edge(scaled_compound)

    return recon_compound
    
def identify_cityobj(occcompound):
    '''
    occcompound is obtain from the function read_collada(dae_filepath)
    '''
    cityobj_dict = {}
    building_list = []
    landuse_list = []
    terrain_list = []
    network_list = []
    
    #define the geometrical attributes between shells
    shells  = py3dmodel.fetch.geom_explorer(occcompound,"shell")
    sewed_shells = sew_shells(shells)
    shell_dict_list = identify_shell_attribs(sewed_shells)
    
    #boolean the edges from the shell compound and edges compound and find the difference to get the network edges
    shell_compound = py3dmodel.construct.make_compound(sewed_shells)
    shell_edges = py3dmodel.fetch.geom_explorer(shell_compound, "edge")
    shell_edge_compound = py3dmodel.construct.make_compound(shell_edges)
    
    edges = py3dmodel.fetch.geom_explorer(occcompound, "edge")
    edge_compound = py3dmodel.construct.make_compound(edges)
    network_edge_compound = py3dmodel.construct.boolean_difference(edge_compound,shell_edge_compound) 
    nw_edges = py3dmodel.fetch.geom_explorer(network_edge_compound,"edge")
    #define the geometrical attributes between edges and shells    
    edge_dict_list = identify_edge_attribs(nw_edges, sewed_shells)
    
    for shell_dict in shell_dict_list:
        shell = shell_dict["shell"]
        is_closed = shell_dict["is_closed"]
        is_in_boundary = shell_dict["is_in_boundary"]
        boundary_contains = shell_dict["boundary_contains"]
        if is_closed == True and len(is_in_boundary)>0 and len(boundary_contains) == 0:
            #conver the shell to a solid to make sure all the faces are facing the right orientation
            solid = py3dmodel.construct.make_solid(shell)
            fix_solid = py3dmodel.modify.fix_close_solid(solid)
            building_list.append(fix_solid)
        if is_closed == False and len(is_in_boundary)==0 and len(boundary_contains)> 0:
            terrain_list.append(shell)
        if is_closed == False and len(is_in_boundary)>0 and len(boundary_contains)> 0:
            landuse_list.append(shell)
    
    for edge_dict in edge_dict_list:
        edge = edge_dict["edge"]
        is_in_boundary = edge_dict["is_in_boundary"]
        if len(is_in_boundary) >0:
            network_list.append(edge)
            
    cityobj_dict["building"] = building_list
    cityobj_dict["landuse"] = landuse_list
    cityobj_dict["terrain"] = terrain_list
    cityobj_dict["network"] = network_list
    return cityobj_dict
    
def write_gml_srf_member(occface_list):
    gml_geometry_list = []
    for face in occface_list:
        pypt_list = py3dmodel.fetch.pyptlist_frm_occface(face)
        first_pt = pypt_list[0]
        pypt_list.append(first_pt)
        pypt_list.reverse()
        srf = pycitygml.gmlgeometry.SurfaceMember(pypt_list)
        gml_geometry_list.append(srf)
    return gml_geometry_list
    
def write_gml_triangle(occface_list):
    gml_geometry_list = []
    for face in occface_list:
        pypt_list = py3dmodel.fetch.pyptlist_frm_occface(face)
        n_pypt_list = len(pypt_list)
        if n_pypt_list>3:
            occtriangles = py3dmodel.construct.delaunay3d(pypt_list)
            for triangle in occtriangles:
                t_pypt_list = py3dmodel.fetch.pyptlist_frm_occface(triangle)
                t_pypt_list.reverse()
                gml_tri = pycitygml.gmlgeometry.Triangle(t_pypt_list)
                gml_geometry_list.append(gml_tri)
        else:
            pypt_list.reverse()
            gml_tri = pycitygml.gmlgeometry.Triangle(pypt_list)
            gml_geometry_list.append(gml_tri)
            
    return gml_geometry_list
    
def write_gml_linestring(occedge):
    gml_edge_list = []
    occpt_list = py3dmodel.fetch.points_from_edge(occedge)
    pypt_list = py3dmodel.fetch.occptlist2pyptlist(occpt_list)
    linestring = pycitygml.gmlgeometry.LineString(pypt_list)
    gml_edge_list.append(linestring)
    return gml_edge_list
    
def write_2_citygml(city_obj_dict, citygml_filepath):
    '''
    city_obj_dict is obtain from the function identify_cityobj(occcompound)
    '''
    citygml_writer = pycitygml.Writer()
    
    bldg_list = city_obj_dict["building"]
    landuse_list = city_obj_dict["landuse"]
    terrain_list =  city_obj_dict["terrain"]
    network_list =  city_obj_dict["network"]
    bcnt = 0
    for bldg in bldg_list:
        bldg_name = "bldg" + str(bcnt)
        bfaces = py3dmodel.fetch.geom_explorer(bldg, "face")
        gml_geometry_list = write_gml_srf_member(bfaces)
        citygml_writer.add_building("lod1",bldg_name, gml_geometry_list)
        bcnt+=1
        
    lcnt = 0
    for landuse in landuse_list:
        luse_name = "luse" + str(lcnt)
        lfaces =  py3dmodel.fetch.geom_explorer(landuse, "face")
        gml_geometry_list = write_gml_srf_member(lfaces)
        citygml_writer.add_landuse("lod1", luse_name, gml_geometry_list)
        lcnt +=1
        
    ncnt = 0
    for network in network_list:
        network_name = "network" + str(ncnt)
        gml_edge_list = write_gml_linestring(network)
        citygml_writer.add_transportation("Road","lod0",network_name,gml_edge_list)
        ncnt+=1
        
    tcnt = 0
    for terrain in terrain_list:
        tname = "terrain" + str(tcnt)
        tfaces =  py3dmodel.fetch.geom_explorer(terrain, "face")
        gml_triangle_list = write_gml_triangle(tfaces)
        citygml_writer.add_tin_relief("lod1",tname,gml_triangle_list)
        tcnt+=1
        
    citygml_writer.write(citygml_filepath)
    print "SUCCESSFUL CONVERT DAE2CITYGML"
    
def auto_convert_dae2gml(colladafile, citygml_filepath):
    dae_compound = read_collada(colladafile)
    city_obj_dict = identify_cityobj(dae_compound)
    write_2_citygml(city_obj_dict, citygml_filepath)
    return city_obj_dict
    

def convert(collada_file):
    #TODO: a function that will convert collada to citygml base on the visual scenes and library nodes (groups and layers)
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
