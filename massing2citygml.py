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
import shapeattributes
from collada import *

class Massing2Citygml(object):
    def __init__(self):
        self.occshp_attribs_obj_list = None
        self.template_rule_obj_list = []
        
    def read_collada(self,dae_filepath):
        '''
        the dae file must be modelled as such:
        close_shells = buildings
        open_shells = terrain & plots(land-use)
        edges = street network
        
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
                            shell = self.simplify_shell(shell)
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
        recon_compound = self.redraw_occ_shell_n_edge(scaled_compound)
        
        #define the geometrical attributes between shells
        shells  = py3dmodel.fetch.geom_explorer(recon_compound,"shell")
        sewed_shells = self.sew_shells(shells)
        
        shell_compound = py3dmodel.construct.make_compound(sewed_shells)
        shell_edges = py3dmodel.fetch.geom_explorer(shell_compound, "edge")
        shell_edge_compound = py3dmodel.construct.make_compound(shell_edges)
        
        edges = py3dmodel.fetch.geom_explorer(recon_compound, "edge")
        edge_compound = py3dmodel.construct.make_compound(edges)
        network_edge_compound = py3dmodel.construct.boolean_difference(edge_compound,shell_edge_compound)
        nw_edges = py3dmodel.fetch.geom_explorer(network_edge_compound,"edge")
        
        occshp_attribs_obj_list = []
        for sewed_shell in sewed_shells:
            occshp_attribs_obj = shapeattributes.ShapeAttributes()
            occshp_attribs_obj.set_shape(sewed_shell)
            occshp_attribs_obj_list.append(occshp_attribs_obj)
            
        for nw_edge in nw_edges:
            occshp_attribs_obj = shapeattributes.ShapeAttributes()
            occshp_attribs_obj.set_shape(nw_edge)
            occshp_attribs_obj_list.append(occshp_attribs_obj)
        
        self.occshp_attribs_obj_list = occshp_attribs_obj_list
        
    def simplify_shell(self, occshell):
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
            
    def redraw_occ_shell_n_edge(self, occcompound):
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
        
    def identify_open_close_shells(self, occshell_list):
        close_shell_list = []
        open_shell_list = []
        for shell in occshell_list:
            is_closed = py3dmodel.calculate.is_shell_closed(shell)
            if is_closed:
                close_shell_list.append(shell)
            else:
                open_shell_list.append(shell)
                
        return close_shell_list, open_shell_list
    
    def sew_shells(self, occshell_list):
        close_shell_list, open_shell_list = self.identify_open_close_shells(occshell_list)
                
        open_shell_compound = py3dmodel.construct.make_compound(open_shell_list)
        open_shell_faces = py3dmodel.fetch.geom_explorer(open_shell_compound, "face")
        #sew all the open shell faces together to check if there are solids among the open shells
        recon_shell_list = py3dmodel.construct.make_shell_frm_faces(open_shell_faces)
        recon_close_shell_list, recon_open_shell_list = self.identify_open_close_shells(recon_shell_list)
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
            
    def add_template_rule(self, template_rule_obj):
        self.template_rule_obj_list.append(template_rule_obj)
        
    def execute_analysis_rule(self):
        occshp_attribs_obj_list = self.occshp_attribs_obj_list
        template_rule_obj_list = self.template_rule_obj_list
        analysis_rule_obj_list = []
        for template_rule_obj in template_rule_obj_list:
            analysis_rule_obj_dict_list = template_rule_obj.analysis_rule_obj_dict_list
            for analysis_rule_obj_dict in analysis_rule_obj_dict_list:
                analysis_rule_obj = analysis_rule_obj_dict["analysis_rule_obj"]
                if analysis_rule_obj not in analysis_rule_obj_list:
                    analysis_rule_obj_list.append(analysis_rule_obj)
                    
        for analysis_rule_obj in analysis_rule_obj_list:
            occshp_attribs_obj_list = analysis_rule_obj.execute(occshp_attribs_obj_list)
            
        self.occshp_attribs_obj_list = occshp_attribs_obj_list
            
    def execute_template_rule(self, citygml_filepath):
        template_rule_obj_list = self.template_rule_obj_list
        occshape_attribs_obj_list = self.occshp_attribs_obj_list
        pycitygml_writer = pycitygml.Writer()
        for template_rule_obj in template_rule_obj_list:
            template_rule_obj.identify(occshape_attribs_obj_list, pycitygml_writer)
            
        pycitygml_writer.write(citygml_filepath)