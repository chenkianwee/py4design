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
import abc
import py3dmodel

class BaseAnalysisRule(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractproperty
    def forshapetype(self):
        """the shapetype the rule apply to: there are 6 shapetype, vertex, edge, face, shell, solid, compsolid, compound"""
        return 
        
    @abc.abstractproperty
    def dict_key(self):
        """the key to the value that will be added to the geometry dictionary, 
        the value to must always be a true or false (bool) """
        return 
        
    @abc.abstractmethod
    def execute(self, occshape_dict_list):
        """ the analysis rule is defined 
        and the method executes the analysis rule """
        return             
#========================================================================================
class IsShellClosed(BaseAnalysisRule):        
    @property
    def forshapetype(self):
        return py3dmodel.fetch.get_shapetype("shell")
        
    @property
    def dict_key(self):
        return "is_shell_closed"
        
    def execute(self, occshape_attribs_obj_list):
        nshp = len(occshape_attribs_obj_list)
        
        for shpcnt in range(nshp):
            occshp_attribs_obj = occshape_attribs_obj_list[shpcnt]
            occshp = occshp_attribs_obj.shape
            shptype = py3dmodel.fetch.get_shapetype(occshp)
            if shptype == self.forshapetype:
                is_closed = py3dmodel.calculate.is_shell_closed(occshp)
                if is_closed:
                    occshp_attribs_obj.set_analysis_rule_item(self.dict_key, True)
                else:
                    occshp_attribs_obj.set_analysis_rule_item(self.dict_key, False)
                
        return occshape_attribs_obj_list
        
class IsShellInBoundary(BaseAnalysisRule):
    @property
    def forshapetype(self):
        return py3dmodel.fetch.get_shapetype("shell")
        
    @property
    def dict_key(self):
        return "is_shell_in_boundary"
        
    def make_2dboundingface(self,occshape):
        xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(occshape)
        boundary_pyptlist = [[xmin,ymin,0], [xmax,ymin,0], [xmax,ymax,0], [xmin,ymax,0]]
        boundary_face = py3dmodel.construct.make_polygon(boundary_pyptlist)
        return boundary_face
        
    def execute(self, occshape_attribs_obj_list):
        nshp = len(occshape_attribs_obj_list)
        
        for shpcnt in range(nshp):
            is_in_boundary = []
            occshp_attribs_obj = occshape_attribs_obj_list[shpcnt]
            occshp = occshp_attribs_obj.shape
            shptype = py3dmodel.fetch.get_shapetype(occshp)
            if shptype == self.forshapetype:
                cur_boundary = self.make_2dboundingface(occshp)
                for shpcnt2 in range(nshp):
                    if shpcnt2 != shpcnt:
                        nxt_occshp_dict_obj = occshape_attribs_obj_list[shpcnt2]
                        nxt_occshp = nxt_occshp_dict_obj.shape
                        nxt_shptype = py3dmodel.fetch.get_shapetype(nxt_occshp)
                        if nxt_shptype == self.forshapetype:
                            nxt_boundary = self.make_2dboundingface(nxt_occshp)
                            #check if cur_shell is inside nxt_shell
                            is_inside_nxt_boundary = py3dmodel.calculate.face_is_inside(cur_boundary,nxt_boundary)
                            if is_inside_nxt_boundary:
                                is_in_boundary.append(nxt_occshp)
                        
            if len(is_in_boundary)>0:
                occshp_attribs_obj.set_analysis_rule_item(self.dict_key, True)
            else:
                occshp_attribs_obj.set_analysis_rule_item(self.dict_key, False)

        return occshape_attribs_obj_list
        
class ShellboundaryContains(BaseAnalysisRule):        
    @property
    def forshapetype(self):
        return py3dmodel.fetch.get_shapetype("shell")
        
    @property
    def dict_key(self):
        return "shell_boundary_contains"
        
    def make_2dboundingface(self,occshape):
        xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(occshape)
        boundary_pyptlist = [[xmin,ymin,0], [xmax,ymin,0], [xmax,ymax,0], [xmin,ymax,0]]
        boundary_face = py3dmodel.construct.make_polygon(boundary_pyptlist)
        return boundary_face
        
    def execute(self, occshape_attribs_obj_list):
        nshp = len(occshape_attribs_obj_list)
        
        for shpcnt in range(nshp):
            boundary_contains = []
            occshp_attribs_obj = occshape_attribs_obj_list[shpcnt]
            occshp = occshp_attribs_obj.shape
            shptype = py3dmodel.fetch.get_shapetype(occshp)
            if shptype == self.forshapetype:
                cur_boundary = self.make_2dboundingface(occshp)
                for shpcnt2 in range(nshp):
                    if shpcnt2 != shpcnt:
                        nxt_occshp_dict_obj = occshape_attribs_obj_list[shpcnt2]
                        nxt_occshp = nxt_occshp_dict_obj.shape
                        nxt_shptype = py3dmodel.fetch.get_shapetype(nxt_occshp)
                        if nxt_shptype == self.forshapetype:
                            nxt_boundary = self.make_2dboundingface(nxt_occshp)
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
    @property
    def forshapetype(self):
        return py3dmodel.fetch.get_shapetype("edge")
        
    @property
    def dict_key(self):
        return "is_edge_in_boundary"
        
    def execute(self,occshape_attribs_obj_list):
        nshp = len(occshape_attribs_obj_list)
        for shpcnt in range(nshp):
            is_in_boundary = []
            occshp_attribs_obj = occshape_attribs_obj_list[shpcnt]
            occshp = occshp_attribs_obj.shape
            shptype = py3dmodel.fetch.get_shapetype(occshp)
            if shptype == self.forshapetype:
                for shpcnt2 in range(nshp):
                    nxt_occshp_dict_obj = occshape_attribs_obj_list[shpcnt2]
                    nxt_occshp = nxt_occshp_dict_obj.shape
                    nxt_shptype = py3dmodel.fetch.get_shapetype(nxt_occshp)
                    if nxt_shptype == py3dmodel.fetch.get_shapetype("shell"):
                        min_dist = py3dmodel.calculate.minimum_distance(occshp,nxt_occshp)
                        if min_dist < 0.0001:
                            is_in_boundary.append(nxt_occshp)
                            
            if len(is_in_boundary)>0:
                occshp_attribs_obj.set_analysis_rule_item(self.dict_key, True)
            else:
                occshp_attribs_obj.set_analysis_rule_item(self.dict_key, False)
            
        return occshape_attribs_obj_list
#========================================================================================