# ==================================================================================================
#
#    Copyright (c) 2016, Chen Kian Wee (chenkianwee@gmail.com)
#
#    This file is part of py4design
#
#    py4design is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    py4design is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with py4design.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================
import abc
from . import py3dmodel

class BaseAnalysisRule(object):
    """
    The base class for developing new analysis rule for analysing topologies in massing model. For more information please refer to 
    Chen, Kian Wee, Patrick Janssen, and Leslie Norford. 2017. Automatic Generation of Semantic 3D City Models from Conceptual Massing Models. 
    In Future Trajectories of Computation in Design, Proceedings of the 17th International Conference on Computer Aided Architectural Design Futures, pp 84 to 100. Istanbul, Turkey.
    """
    
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractproperty
    def for_topo_type(self):
        """The topological type the rule apply to: there are 7 topologies, vertex, edge, wire, face, shell, solid, compsolid, compound."""
        return 
        
    @abc.abstractproperty
    def dict_key(self):
        """The key to the value that will be added to the ShapeAttributes class instance, the value must be a True or False (bool)."""
        return 
        
    @abc.abstractmethod
    def execute(self, occshape_dict_list):
        """ The definition of the analysis rule and the method executes the analysis rule """
        return             
#========================================================================================
class IsShellClosed(BaseAnalysisRule):   
    """An implementation of the BaseAnalysisRule class for checking if the shell in the massing models are closed."""
    @property
    def for_topo_type(self):
        """The rule applies to the shell topology."""
        return py3dmodel.fetch.get_topotype("shell")
        
    @property
    def dict_key(self):
        """The attribute name of rule result: "is_shell_closed"."""
        return "is_shell_closed"
        
    def execute(self, occshape_attribs_obj_list):
        """
        This function executes the rule to check if all the shells in the massing model are closed. Shells that are not closed will have an attribute "is_shell_closed": False, shells that 
        are closed will have an attribute "is_shell_closed": True.
        
        Parameters
        ----------
        occshape_attribs_obj_list : list of ShapeAttributes objects
            The geometeries of the massing model to be checked.
        
        Returns
        -------        
        checked occshape_attribs_obj_list : list of ShapeAttributes objects
            List of checked geometries with the appended attributes.
        """
        nshp = len(occshape_attribs_obj_list)
        
        for shpcnt in range(nshp):
            occshp_attribs_obj = occshape_attribs_obj_list[shpcnt]
            occshp = occshp_attribs_obj.shape
            shptype = py3dmodel.fetch.get_topotype(occshp)
            if shptype == self.for_topo_type:
                is_closed = py3dmodel.calculate.is_shell_closed(occshp)
                if is_closed:
                    occshp_attribs_obj.set_analysis_rule_item(self.dict_key, True)
                else:
                    occshp_attribs_obj.set_analysis_rule_item(self.dict_key, False)
                
        return occshape_attribs_obj_list
        
class IsShellInBoundary(BaseAnalysisRule):
    """An implementation of the BaseAnalysisRule class for checking if the shell is in the boundary of another shell."""
    @property
    def for_topo_type(self):
        """The rule applies to the shell topology."""
        return py3dmodel.fetch.get_topotype("shell")
        
    @property
    def dict_key(self):
        """The attribute name of rule result: "is_shell_in_boundary"."""
        return "is_shell_in_boundary"
        
        
    def execute(self, occshape_attribs_obj_list):
        """
        This function executes the rule to check if all the shells in the massing model are in the boundary of another shell. Shells that are in the boundary of another shell  will have an 
        attribute "is_shell_in_boundary": True, shells that are not will have an attribute "is_shell_in_boundary": False.
        
        Parameters
        ----------
        occshape_attribs_obj_list : list of ShapeAttributes objects
            The geometeries of the massing model to be checked.
        
        Returns
        -------        
        checked occshape_attribs_obj_list : list of ShapeAttributes objects
            List of checked geometries with the appended attributes.
        """
        nshp = len(occshape_attribs_obj_list)
        #get all the geometries from the dictionary 
        occshape_flatten_list = []
        for occshape_attrib in occshape_attribs_obj_list:
            shptype = py3dmodel.fetch.get_topotype(occshape_attrib.shape)
            if shptype == py3dmodel.fetch.get_topotype("shell"):
                occshape_flatten_list.append(occshape_attrib.get_value("flatten_shell_face"))

        for shpcnt in range(nshp):
            is_in_boundary = []
            occshp_attribs_obj = occshape_attribs_obj_list[shpcnt]
            occshp = occshp_attribs_obj.shape
            shptype = py3dmodel.fetch.get_topotype(occshp)
            if shptype == self.for_topo_type:
                cur_boundary = occshp_attribs_obj.get_value("flatten_shell_face") #py3dmodel.modify.flatten_shell_z_value(occshp)
                for shpcnt2 in range(nshp):
                    if shpcnt2 != shpcnt:
                        nxt_occshp_dict_obj = occshape_attribs_obj_list[shpcnt2]
                        nxt_occshp = nxt_occshp_dict_obj.shape
                        nxt_shptype = py3dmodel.fetch.get_topotype(nxt_occshp)
                        if nxt_shptype == self.for_topo_type:
                            nxt_boundary = nxt_occshp_dict_obj.get_value("flatten_shell_face") #py3dmodel.modify.flatten_shell_z_value(nxt_occshp)
                            #check if cur_shell is inside nxt_shell
                            is_inside_nxt_boundary = py3dmodel.calculate.face_is_inside(cur_boundary,nxt_boundary)
                            if is_inside_nxt_boundary:
                                is_in_boundary.append(nxt_occshp)
                
            if len(is_in_boundary)>0:
                occshp_attribs_obj.set_analysis_rule_item(self.dict_key, True)
            else:
                occshp_attribs_obj.set_analysis_rule_item(self.dict_key, False)

        return occshape_attribs_obj_list
        
class ShellBoundaryContains(BaseAnalysisRule):
    """An implementation of the BaseAnalysisRule class for checking if the shell contains another shell."""
    @property
    def for_topo_type(self):
        """The rule applies to the shell topology."""
        return py3dmodel.fetch.get_topotype("shell")
        
    @property
    def dict_key(self):
        """The attribute name of rule result: "shell_boundary_contains"."""
        return "shell_boundary_contains"
        
        
    def execute(self, occshape_attribs_obj_list):
        """
        This function executes the rule to check if all the shells in the massing model contain another shell. Shells that contain another shell will have an 
        attribute "shell_boundary_contains": True, shells that does not contain another shell will have an attribute "shell_boundary_contains": False.
        
        Parameters
        ----------
        occshape_attribs_obj_list : list of ShapeAttributes objects
            The geometeries of the massing model to be checked.
        
        Returns
        -------        
        checked occshape_attribs_obj_list : list of ShapeAttributes objects
            List of checked geometries with the appended attributes.
        """
        nshp = len(occshape_attribs_obj_list)
        
        for shpcnt in range(nshp):
            boundary_contains = []
            occshp_attribs_obj = occshape_attribs_obj_list[shpcnt]
            occshp = occshp_attribs_obj.shape
            shptype = py3dmodel.fetch.get_topotype(occshp)
            if shptype == self.for_topo_type:
                cur_boundary = occshp_attribs_obj.get_value("flatten_shell_face") #py3dmodel.modify.flatten_shell_z_value(occshp)
                for shpcnt2 in range(nshp):
                    if shpcnt2 != shpcnt:
                        nxt_occshp_dict_obj = occshape_attribs_obj_list[shpcnt2]
                        nxt_occshp = nxt_occshp_dict_obj.shape
                        nxt_shptype = py3dmodel.fetch.get_topotype(nxt_occshp)
                        if nxt_shptype == self.for_topo_type:
                            nxt_boundary = nxt_occshp_dict_obj.get_value("flatten_shell_face") #py3dmodel.modify.flatten_shell_z_value(nxt_occshp)
                            #check if cur_shell is inside nxt_shell
                            contains_nxt_boundary = py3dmodel.calculate.face_is_inside(nxt_boundary,cur_boundary)
                            if contains_nxt_boundary:
                                boundary_contains.append(nxt_occshp)
                        
            if len(boundary_contains)>0:
                occshp_attribs_obj.set_analysis_rule_item(self.dict_key, True)
            else:
                occshp_attribs_obj.set_analysis_rule_item(self.dict_key, False)
                
        return occshape_attribs_obj_list

class IsEdgeInBoundary(BaseAnalysisRule):
    """An implementation of the BaseAnalysisRule class for checking if the edge is in the boundary of a shell."""       
    @property
    def for_topo_type(self):
        """The rule applies to the edge topology."""
        return py3dmodel.fetch.get_topotype("edge")
        
    @property
    def dict_key(self):
        """The attribute name of rule result: "is_edge_in_boundary"."""
        return "is_edge_in_boundary"
        
    def execute(self,occshape_attribs_obj_list):
        """
        This function executes the rule to check if all the edges in the massing model are in the boundary of another shell. Edges that are in the boundary of another shell will have an 
        attribute "is_edge_in_boundary": True, edges that are not will have an attribute "is_edge_in_boundary": False.
        
        Parameters
        ----------
        occshape_attribs_obj_list : list of ShapeAttributes objects
            The geometeries of the massing model to be checked.
        
        Returns
        -------        
        checked occshape_attribs_obj_list : list of ShapeAttributes objects
            List of checked geometries with the appended attributes.
        """
        nshp = len(occshape_attribs_obj_list)
        occshape_list = []
        for occshape_attrib in occshape_attribs_obj_list:
            occ_shp = occshape_attrib.shape
            if py3dmodel.fetch.get_topotype(occ_shp) == py3dmodel.fetch.get_topotype("shell"):
                occshape_list.append(occshape_attrib.shape)
            
        for shpcnt in range(nshp):
            #is_in_boundary = []
            occshp_attribs_obj = occshape_attribs_obj_list[shpcnt]
            occshp = occshp_attribs_obj.shape
            shptype = py3dmodel.fetch.get_topotype(occshp)
            if shptype == self.for_topo_type:
                occshape_list2 = occshape_list[:]
                other_cmpd = py3dmodel.construct.make_compound(occshape_list2)
                min_dist = py3dmodel.calculate.minimum_distance(occshp,other_cmpd)
                if min_dist < 0.0001:
                    occshp_attribs_obj.set_analysis_rule_item(self.dict_key, True)
                else:
                    occshp_attribs_obj.set_analysis_rule_item(self.dict_key, False)
        return occshape_attribs_obj_list
#========================================================================================
class IsShellTallerThan(BaseAnalysisRule):
    """An implementation of the BaseAnalysisRule class for checking if the edge is in the boundary of a shell."""       
    
    def __init__(self, height_threshold):
        """Initialises the class"""
        self.height_threshold = height_threshold
        
    @property
    def for_topo_type(self):
        """The rule applies to the shell topology."""
        return py3dmodel.fetch.get_topotype("shell")
        
    @property
    def dict_key(self):
        """The attribute name of rule result: "is_height_taller_than"."""
        return "is_height_taller_than"
        
    def execute(self,occshape_attribs_obj_list):
        """
        This function executes the rule to check if the shell in the massing model are taller than a certain height 
        , shell is taller than the height, the attribute "is_height_taller_than": True, else an attribute "is_height_taller_than": False.
        
        Parameters
        ----------
        occshape_attribs_obj_list : list of ShapeAttributes objects
            The geometeries of the massing model to be checked.
        
        Returns
        -------        
        checked occshape_attribs_obj_list : list of ShapeAttributes objects
            List of checked geometries with the appended attributes.
        """
        height_threshold = self.height_threshold
        nshp = len(occshape_attribs_obj_list)
        occshape_list = []
        for occshape_attrib in occshape_attribs_obj_list:
            occ_shp = occshape_attrib.shape
            if py3dmodel.fetch.get_topotype(occ_shp) == py3dmodel.fetch.get_topotype("shell"):
                occshape_list.append(occshape_attrib.shape)
            
        for shpcnt in range(nshp):
            #is_in_boundary = []
            occshp_attribs_obj = occshape_attribs_obj_list[shpcnt]
            occshp = occshp_attribs_obj.shape
            shptype = py3dmodel.fetch.get_topotype(occshp)
            
                
            if shptype == self.for_topo_type:
                xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(occshp)
                height = zmax-zmin
                if height > height_threshold:
                    occshp_attribs_obj.set_analysis_rule_item(self.dict_key, True)
                else:
                    occshp_attribs_obj.set_analysis_rule_item(self.dict_key, False)
        return occshape_attribs_obj_list