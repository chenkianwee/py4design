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
#    along with Pyliburo.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================
import abc
import py3dmodel
import gml3dmodel
import urbangeom

class BaseTemplateRule(object):
    """
    The base class for developing new template rule for analysing topologies in massing model. For more information please refer to 
    Chen, Kian Wee, Patrick Janssen, and Leslie Norford. 2017. Automatic Generation of Semantic 3D City Models from Conceptual Massing Models. 
    In Future Trajectories of Computation in Design, Proceedings of the 17th International Conference on Computer Aided Architectural Design Futures, pp 84 to 100. Istanbul, Turkey.
    """
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractproperty
    def for_topo_type(self):
        """The topological type the rule apply to: there are 7 topologies, vertex, edge, wire, face, shell, solid, compsolid, compound."""
        return 
    
    @abc.abstractmethod
    def get_analysis_rule_obj_dict_list(self):
        """This function gets all the BaseAnalysisRule objects appended to this template rule."""
        return 
        
    @abc.abstractmethod
    def add_analysis_rule(self, analysis_rule_obj, bool_condition):
        """
        This function adds BaseAnalysisRule object to this template rule and specify its bool condition for the analysis rule (either True or False).
        
        Parameters
        ----------
        analysis_rule_obj : implementation of the BaseAnalysisRule meta class
            The analysis rule and condition of the template rule.
        
        bool_condition : bool
            True or False.
        """
        analysis_rule_obj_dict = {}
        analysis_rule_obj_dict["analysis_rule_obj"] = analysis_rule_obj
        analysis_rule_obj_dict["condition"] = bool_condition
        return analysis_rule_obj_dict
        
    @abc.abstractmethod
    def identify(self, occshape_attribs_obj_list, pycitygml_writer):
        """
        This function executes the analysis rule and identify the city object based on the condition set. e.g. if a shell is closed and within anopther shell boundary, the shell is a building.
        
        Parameters
        ----------
        occshape_attribs_obj_list : list of ShapeAttributes objects
            The geometeries of the massing model to be identified.
            
        pycitygml_writer : pycitygml.Writer class instance
            The writer to write the identified city objects into CityGML.
        """      
        analysis_rule_obj_dict_list = self.get_analysis_rule_obj_dict_list()
        conditioned_list = []
        cnt = 0
        for occshape_attribs_obj in occshape_attribs_obj_list:
            occshp = occshape_attribs_obj.shape
            shptype = py3dmodel.fetch.get_topotype(occshp)
            if shptype == self.for_topo_type:
                conditioned_list.append(occshp)
                for analysis_rule_obj_dict in analysis_rule_obj_dict_list:
                    analysis_rule_obj = analysis_rule_obj_dict["analysis_rule_obj"] 
                    analysis_rule_key = analysis_rule_obj.dict_key
                    condition = analysis_rule_obj_dict["condition"]
                    analysis_attrib = occshape_attribs_obj.get_value(analysis_rule_key)
                    if analysis_attrib != condition:
                        conditioned_list.remove(occshp)
                        break
            cnt+=1
        return conditioned_list
        
#========================================================================================
class IdentifyBuildingMassings(BaseTemplateRule):
    """An implementation of the BaseTemplateRule class for identifying the massing of buildings (LOD1)."""
    def __init__(self):
        """Initialises the class"""
        self.analysis_rule_obj_dict_list = []
        
    @property
    def for_topo_type(self):
        """The rule applies to the shell topology."""
        return py3dmodel.fetch.get_topotype("shell")
        
    def get_analysis_rule_obj_dict_list(self):
        """This function gets all the BaseAnalysisRule objects appended to this template rule."""
        return self.analysis_rule_obj_dict_list
        
    def add_analysis_rule(self, analysis_rule_obj, bool_condition):
        """
        This function adds BaseAnalysisRule object to this template rule and specify its bool condition for the analysis rule (either True or False).
        
        Parameters
        ----------
        analysis_rule_obj : implementation of the BaseAnalysisRule meta class
            The analysis rule and condition of the template rule.
        
        bool_condition : bool
            True or False.
        """
        analysis_rule_obj_dict = super(IdentifyBuildingMassings, self).add_analysis_rule(analysis_rule_obj,bool_condition)
        self.analysis_rule_obj_dict_list.append(analysis_rule_obj_dict)
        
    def identify(self, occshape_attribs_obj_list, pycitygml_writer):
        """
        This function executes the analysis rule and identify the city object based on the condition set. e.g. if a shell is closed and within anopther shell boundary, the shell is a building.
        
        Parameters
        ----------
        occshape_attribs_obj_list : list of ShapeAttributes objects
            The geometeries of the massing model to be identified.
            
        pycitygml_writer : pycitygml.Writer class instance
            The writer to write the identified city objects into CityGML.
        """
        building_list = super(IdentifyBuildingMassings, self).identify(occshape_attribs_obj_list,pycitygml_writer)
        tolerance = 1e-04
        bcnt = 0
        for building in building_list:
            building = py3dmodel.modify.fix_shell_orientation(building)
            #first try to simplify the solid as much as possible
            mbuilding = py3dmodel.modify.simplify_shell(building, tolerance = tolerance)

            least_verts = 2
            while least_verts <3:
                least_verts = 3
                shell_faces = py3dmodel.fetch.geom_explorer(mbuilding, "face")
                #this is to try to remove any unwanted small area face 
                #this will only happens when the simplification do not work
                for face in shell_faces:
                    pyptlist= py3dmodel.fetch.pyptlist_frm_occface(face)
                    nverts = len(pyptlist)
                    if nverts <3:
                        shell_faces.remove(face)
                        least_verts = 2
                        continue
                    area = py3dmodel.calculate.face_area(face)
                    if area < 1e-03:
                        shell_faces.remove(face)
                        least_verts = 2
                        
                #reconstruct the shell with the remaining face
                mbuilding = py3dmodel.construct.make_shell_frm_faces(shell_faces,tolerance = tolerance)[0]
                mbuilding = py3dmodel.modify.fix_shell_orientation(mbuilding)
            
            is_shell_close = py3dmodel.calculate.is_shell_closed(mbuilding)
            is_shell_planar = urbangeom.is_shell_faces_planar(mbuilding)
            is_shell_simple = urbangeom.is_shell_simple(mbuilding)
            #if after removal of faces the shell is no longer close 
            #reconstruct the entire shell entirely by meshing the original geometry
            if is_shell_close == False or is_shell_planar == False or is_shell_simple == False :
                mesh_faces = py3dmodel.construct.simple_mesh(building)
                mbuilding = py3dmodel.construct.make_shell_frm_faces(mesh_faces,tolerance = tolerance)[0]
                mbuilding = py3dmodel.modify.fix_shell_orientation(mbuilding)
                mbuilding = py3dmodel.construct.make_solid(mbuilding)
                mbuilding = py3dmodel.modify.fix_close_solid(mbuilding)
            else:
                mbuilding = py3dmodel.construct.make_solid(mbuilding)
                mbuilding = py3dmodel.modify.fix_close_solid(mbuilding)

            bfaces = py3dmodel.fetch.geom_explorer(mbuilding, "face")
            gml_geometry_list = gml3dmodel.write_gml_srf_member(bfaces)
            bldg_name = "bldg" + str(bcnt)
            pycitygml_writer.add_building("lod1",bldg_name, gml_geometry_list)
            bcnt+=1
            
class IdentifyTerrainMassings(BaseTemplateRule):
    """An implementation of the BaseTemplateRule class for identifying the massing of terrains (LOD1)."""
    def __init__(self):
        self.analysis_rule_obj_dict_list = []
        
    @property
    def for_topo_type(self):
        """The rule applies to the shell topology."""
        return py3dmodel.fetch.get_topotype("shell")
        
    def get_analysis_rule_obj_dict_list(self):
        """This function gets all the BaseAnalysisRule objects appended to this template rule."""
        return self.analysis_rule_obj_dict_list
        
    def add_analysis_rule(self, analysis_rule_obj, bool_condition):
        """
        This function adds BaseAnalysisRule object to this template rule and specify its bool condition for the analysis rule (either True or False).
        
        Parameters
        ----------
        analysis_rule_obj : implementation of the BaseAnalysisRule meta class
            The analysis rule and condition of the template rule.
        
        bool_condition : bool
            True or False.
        """
        analysis_rule_obj_dict = super(IdentifyTerrainMassings, self).add_analysis_rule(analysis_rule_obj,bool_condition)
        self.analysis_rule_obj_dict_list.append(analysis_rule_obj_dict)
        
    def identify(self, occshape_attribs_obj_list, pycitygml_writer):
        """
        This function executes the analysis rule and identify the city object based on the condition set. e.g. if a shell is opened and not within anopther shell boundary, the shell is a terrain.
        
        Parameters
        ----------
        occshape_attribs_obj_list : list of ShapeAttributes objects
            The geometeries of the massing model to be identified.
            
        pycitygml_writer : pycitygml.Writer class instance
            The writer to write the identified city objects into CityGML.
        """
        terrain_list = super(IdentifyTerrainMassings, self).identify(occshape_attribs_obj_list,pycitygml_writer)
        tolerance = 1e-04
        tcnt = 0
        for terrain in terrain_list:
            xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(terrain)
            zrange = zmax-zmin
            if zrange <= tolerance:
                terrain = py3dmodel.modify.simplify_shell(terrain, tolerance = tolerance)
            
            tfaces =  py3dmodel.fetch.geom_explorer(terrain, "face")
            gml_triangle_list = gml3dmodel.write_gml_triangle(tfaces)
            tname = "terrain" + str(tcnt)
            pycitygml_writer.add_tin_relief("lod1",tname,gml_triangle_list)
            tcnt+=1
            
class IdentifyLandUseMassings(BaseTemplateRule):
    """An implementation of the BaseTemplateRule class for identifying the massing of landuse plots (LOD1)."""
    def __init__(self):
        self.analysis_rule_obj_dict_list = []
        
    @property
    def for_topo_type(self):
        """The rule applies to the shell topology."""
        return py3dmodel.fetch.get_topotype("shell")
        
    def get_analysis_rule_obj_dict_list(self):
        """This function gets all the BaseAnalysisRule objects appended to this template rule."""
        return self.analysis_rule_obj_dict_list
        
    def add_analysis_rule(self, analysis_rule_obj, bool_condition):
        """
        This function adds BaseAnalysisRule object to this template rule and specify its bool condition for the analysis rule (either True or False).
        
        Parameters
        ----------
        analysis_rule_obj : implementation of the BaseAnalysisRule meta class
            The analysis rule and condition of the template rule.
        
        bool_condition : bool
            True or False.
        """
        analysis_rule_obj_dict = super(IdentifyLandUseMassings, self).add_analysis_rule(analysis_rule_obj,bool_condition)
        self.analysis_rule_obj_dict_list.append(analysis_rule_obj_dict)
        
    def identify(self, occshape_attribs_obj_list, pycitygml_writer):
        """
        This function executes the analysis rule and identify the city object based on the condition set. e.g. if a shell is opened and within anopther shell boundary, the shell is a plot.
        
        Parameters
        ----------
        occshape_attribs_obj_list : list of ShapeAttributes objects
            The geometeries of the massing model to be identified.
            
        pycitygml_writer : pycitygml.Writer class instance
            The writer to write the identified city objects into CityGML.
        """
        landuse_list = super(IdentifyLandUseMassings, self).identify(occshape_attribs_obj_list,pycitygml_writer)
        tolerance = 1e-04
        lcnt = 0
        for landuse in landuse_list:
            xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(landuse)
            zrange = zmax-zmin
            if zrange <= tolerance:
                landuse = py3dmodel.modify.simplify_shell(landuse, tolerance = tolerance)
            else:
                mesh_faces = py3dmodel.construct.simple_mesh(landuse)
                landuse = py3dmodel.construct.make_shell_frm_faces(mesh_faces,tolerance = tolerance)[0]
                landuse = py3dmodel.modify.fix_shell_orientation(landuse)
                
            lfaces =  py3dmodel.fetch.geom_explorer(landuse, "face")
            gml_geometry_list = gml3dmodel.write_gml_srf_member(lfaces)
            luse_name = "luse" + str(lcnt)
            pycitygml_writer.add_landuse("lod1", luse_name, gml_geometry_list)
            lcnt +=1

class IdentifyRoadMassings(BaseTemplateRule):
    """An implementation of the BaseTemplateRule class for identifying the massing of landuse road network (LOD0)."""
    def __init__(self):
        self.analysis_rule_obj_dict_list = []
        
    @property
    def for_topo_type(self):
        """The rule applies to the edge topology."""
        return py3dmodel.fetch.get_topotype("edge")
        
    def get_analysis_rule_obj_dict_list(self):
        """This function gets all the BaseAnalysisRule objects appended to this template rule."""
        return self.analysis_rule_obj_dict_list
        
    def add_analysis_rule(self, analysis_rule_obj, bool_condition):
        """
        This function adds BaseAnalysisRule object to this template rule and specify its bool condition for the analysis rule (either True or False).
        
        Parameters
        ----------
        analysis_rule_obj : implementation of the BaseAnalysisRule meta class
            The analysis rule and condition of the template rule.
        
        bool_condition : bool
            True or False.
        """
        analysis_rule_obj_dict = super(IdentifyRoadMassings, self).add_analysis_rule(analysis_rule_obj,bool_condition)
        self.analysis_rule_obj_dict_list.append(analysis_rule_obj_dict)
        
    def identify(self, occshape_attribs_obj_list, pycitygml_writer):
        """
        This function executes the analysis rule and identify the city object based on the condition set. e.g. if an edge is within anopther shell boundary, the edge is a road.
        
        Parameters
        ----------
        occshape_attribs_obj_list : list of ShapeAttributes objects
            The geometeries of the massing model to be identified.
            
        pycitygml_writer : pycitygml.Writer class instance
            The writer to write the identified city objects into CityGML.
        """
        network_list = super(IdentifyRoadMassings, self).identify(occshape_attribs_obj_list,pycitygml_writer)
        ncnt = 0
        for network in network_list:
            network_name = "network" + str(ncnt)
            gml_edge_list = gml3dmodel.write_gml_linestring(network)
            pycitygml_writer.add_transportation("Road","lod0",network_name,gml_edge_list)
            ncnt+=1