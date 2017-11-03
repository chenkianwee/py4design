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
import gml3dmodel
import shapeattributes
import collada
from collada import polylist, triangleset, lineset

class Massing2Citygml(object):
    """
    An object that extracts all the neccessary information from a massing model and converts the geometries into CityGML objects with semantics, only works for LOD1 CityGML models.
    For more information please refer to Chen, Kian Wee, Patrick Janssen, and Leslie Norford. 2017. Automatic Generation of Semantic 3D City Models from Conceptual Massing Models. 
    In Future Trajectories of Computation in Design, Proceedings of the 17th International Conference on Computer Aided Architectural Design Futures, pp 84 to 100. Istanbul, Turkey.
    
    Attributes
    ----------    
    occshp_attribs_obj_list : list of ShapeAttributes objects
        The geometries are first converted to ShapeAttributes objects before into CityGML object. ShapeAttributes is an intermediate format.
    
    template_rule_obj_list : list of BaseTemplateRule class instances
        The template rules for converting the geometries.
    """
    def __init__(self):
        """Initialises the class"""
        self.occshp_attribs_obj_list = None
        self.template_rule_obj_list = []
        
    def read_collada(self,dae_filepath):
        """
        This function reads the Collada (.dae) file to be converted and convert the geometries to ShapeAttributes objects.
        
        Parameters
        ----------
        dae_filepath : str
            The file path of the Collada file to be converted.
        
        """
        #TODO: a function that will convert collada to citygml base on the visual scenes and library nodes (groups and layers)
        #dae = Collada(collada_file)
        #nodes = dae.scene.nodes
        
        #this loops thru the visual scene 
        #loop thru the library nodes
        #for node in nodes:
        #    name = node.xmlnode.get('name')
        #    children_nodes = node.children
        #    if children_nodes:
        #        for node2 in children_nodes:
        #            name2 = node2.xmlnode.get('name')
        #            print 'name2', name2
        #            children_node2 = node2.children
        #            if children_node2:
        #                if type(children_node2[0]) == scene.NodeNode:
        #                    print children_node2[0].children
        
        tolerance = 1e-04
        edgelist = []
        shelllist = []
        mesh = collada.Collada(dae_filepath)
        unit = mesh.assetInfo.unitmeter or 1
        geoms = mesh.scene.objects('geometry')
        geoms = list(geoms)
        gcnt = 0
        
        for geom in geoms:
            if gcnt >= 0: #and gcnt <= 45:
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
                                sorted_pyptlist = sorted(pyptlist)
                                
                                if sorted_pyptlist not in spyptlist:
                                    spyptlist.append(sorted_pyptlist)
                                    occpolygon = py3dmodel.construct.make_polygon(pyptlist)
                                    if not py3dmodel.fetch.is_face_null(occpolygon):
                                        faces.append(occpolygon)

                            elif type(prim) == lineset.Line:
                                pyptlist = prim.vertices.tolist()
                                pyptlist.sort()
                                if pyptlist not in epyptlist:
                                    epyptlist.append(pyptlist)
                                    occedge = py3dmodel.construct.make_edge(pyptlist[0], pyptlist[1])
                                    edges.append(occedge)
                                
                        if faces:
                            n_unique_faces = len(faces)
                            if n_unique_faces == 1:
                                shell = py3dmodel.construct.make_shell(faces)
                                shelllist.append(shell)
                            if n_unique_faces >1:
                                shell = py3dmodel.construct.sew_faces(faces, tolerance = tolerance)
                                if shell:
                                    shelllist.append(shell[0])
                        else:
                            edgelist.extend(edges)
            gcnt +=1
        
        cmpd_shell = py3dmodel.construct.make_compound(shelllist) 
        cmpd_edge = py3dmodel.construct.make_compound(edgelist)
        cmpd_list = [cmpd_shell, cmpd_edge]
        #find the midpt of all the geometry
        compound = py3dmodel.construct.make_compound(cmpd_list)
        
        xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(compound)
        #ref_pt = py3dmodel.calculate.get_centre_bbox(compound)
        #ref_pt = (ref_pt[0],ref_pt[1],zmin)
        ref_pt = (0,0,0)
        #scale all the geometries into metre
        #TO DO: THIS HAS A PROBLEM WHEN YOU HAVE TWO FILES WITH DIFF MIDPTS
        #scaled_shell_shape = py3dmodel.modify.uniform_scale(cmpd_shell, unit, unit, unit,ref_pt)
        #scaled_edge_shape = py3dmodel.modify.uniform_scale(cmpd_edge, unit, unit, unit,ref_pt)
        scaled_shell_shape = py3dmodel.modify.scale(cmpd_shell, unit,ref_pt)
        scaled_edge_shape = py3dmodel.modify.scale(cmpd_edge, unit,ref_pt)
        
        scaled_shell_compound = py3dmodel.fetch.topo2topotype(scaled_shell_shape)
        scaled_edge_compound = py3dmodel.fetch.topo2topotype(scaled_edge_shape)
        
        recon_shell_compound = gml3dmodel.redraw_occ_shell(scaled_shell_compound, tolerance)
        recon_edge_compound = gml3dmodel.redraw_occ_edge(scaled_edge_compound, tolerance)
        
        #sort and recompose the shells 
        shells  = py3dmodel.fetch.topo_explorer(recon_shell_compound,"shell")
        sewed_shells = gml3dmodel.reconstruct_open_close_shells(shells)
        
        nw_edges = py3dmodel.fetch.topo_explorer(recon_edge_compound,"edge")

        occshp_attribs_obj_list = []
        for sewed_shell in sewed_shells:
            occshp_attribs_obj = shapeattributes.ShapeAttributes()
            occshp_attribs_obj.set_shape(sewed_shell)
            occshp_attribs_obj_list.append(occshp_attribs_obj)
            
        for nw_edge in nw_edges:
            occshp_attribs_obj = shapeattributes.ShapeAttributes()
            occshp_attribs_obj.set_shape(nw_edge)
            occshp_attribs_obj_list.append(occshp_attribs_obj)

        print len(shells), len(sewed_shells)
        self.occshp_attribs_obj_list = occshp_attribs_obj_list

    def add_template_rule(self, template_rule_obj):
        """
        This function adds BaseTemplateRule objects to this class.
        
        Parameters
        ----------
        template_rule_obj : implementation of the BaseTemplateRule meta class
            The template rule used for converting the geometries to semantic models.
        """
        self.template_rule_obj_list.append(template_rule_obj)
        
    def execute_analysis_rule(self):
        """
        This function adds executes the analysis rules in the template rules and append the analysis results to the ShapeAttributes objects.
        """
        occshp_attribs_obj_list = self.occshp_attribs_obj_list
        template_rule_obj_list = self.template_rule_obj_list
        analysis_rule_obj_list = []
        
        for template_rule_obj in template_rule_obj_list:
            analysis_rule_obj_dict_list = template_rule_obj.analysis_rule_obj_dict_list
            for analysis_rule_obj_dict in analysis_rule_obj_dict_list:
                analysis_rule_obj = analysis_rule_obj_dict["analysis_rule_obj"]
                if analysis_rule_obj not in analysis_rule_obj_list:
                    analysis_rule_obj_list.append(analysis_rule_obj)
                    
        #calculate the flatten shell for the analysis rules
        #doing it once here saves time
        print  "GETTING FLATTEN SURFACE"
        for occshp_attribs_obj in occshp_attribs_obj_list:
            occshp = occshp_attribs_obj.shape
            shptype = py3dmodel.fetch.get_topotype(occshp)
            if shptype == py3dmodel.fetch.get_topotype("shell"):
                flatten_shell_face = py3dmodel.modify.flatten_shell_z_value(occshp)
                if not flatten_shell_face == None:
                    flat_pyptlist = py3dmodel.fetch.points_frm_occface(flatten_shell_face)
                    flatten_shell_face = py3dmodel.construct.make_polygon(flat_pyptlist)
                    occshp_attribs_obj.dictionary["flatten_shell_face"] = flatten_shell_face


        for analysis_rule_obj in analysis_rule_obj_list:
            print analysis_rule_obj
            occshp_attribs_obj_list = analysis_rule_obj.execute(occshp_attribs_obj_list)
            
        self.occshp_attribs_obj_list = occshp_attribs_obj_list
            
    def execute_template_rule(self, citygml_filepath):
        """
        This function executes the template rule and convert the geometry to semantic models.
        
        Parameters
        ----------
        citygml_filepath : str
            The file path of the resultant CityGML file.
        """
        template_rule_obj_list = self.template_rule_obj_list
        occshape_attribs_obj_list = self.occshp_attribs_obj_list
        pycitygml_writer = pycitygml.Writer()
        for template_rule_obj in template_rule_obj_list:
            print template_rule_obj
            template_rule_obj.identify(occshape_attribs_obj_list, pycitygml_writer)
            
        pycitygml_writer.write(citygml_filepath)