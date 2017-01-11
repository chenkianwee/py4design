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
import random

import pycitygml
import gmlparmpalette

class Parameterise(object):
    def __init__(self, citygmlfile):
        reader = pycitygml.Reader()
        reader.load_filepath(citygmlfile)
        self.citygml = reader
        self.parm_obj_dict_list = []
        self.nparameters = None
        
        self.buildings = self.citygml.get_buildings()
        self.landuses = self.citygml.get_landuses()
        self.stops = self.citygml.get_bus_stops()
        self.roads = self.citygml.get_roads()
        self.railways = self.citygml.get_railways()
        self.building_footprints = None
        
        self.buildings2landuses = None
        
    def add_bldg_flr_area_height_parm(self, bldg_class= None, bldg_function = None, bldg_usage = None, parm_definition = None, 
                                      range_definition = True):
        """specify the class, function and usage of the buildings this parameter will be applied to, if none are given, 
        this parameter will apply to all buildings"""

        parm = gmlparmpalette.BldgFlrAreaHeightParm()
        
        if parm_definition!=None:
            if range_definition == True:
                is_it_int = True
                for ele in parm_definition:
                    if type(ele) == float:
                        is_it_int = False
                        
                if is_it_int:        
                    parm.define_int_range(parm_definition[0],parm_definition[1],parm_definition[2])
                else:
                    n_p_define = len(parm_definition)
                    if n_p_define == 2:
                        parm.define_float_range(parm_definition[0],parm_definition[1])
                    if n_p_define == 3:
                        parm.define_float_range(parm_definition[0],parm_definition[1], parm_definition[2])
                        
            if range_definition == False:
                parm.set_parm_range(parm_definition)
            
            
        if bldg_class !=None:
            parm.apply_2_bldg_class(bldg_class)
        if bldg_function != None:
            parm.apply_2_bldg_function(bldg_function)
        if bldg_usage != None:
            parm.apply_2_bldg_usage(bldg_usage)
            
        bldg_parm_dict = {}
        bldg_parm_dict["parameter_object"] = parm
        self.parm_obj_dict_list.append(bldg_parm_dict)
        
    def add_bldg_orientation_parm(self, parm_definition, range_definition = True, bldg_class= None, 
                                  bldg_function = None, bldg_usage = None, clash_detection = True, boundary_detection = True):
        """specify the class, function and usage of the buildings this parameter will be applied to, if none are given, 
        this parameter will apply to all buildings
        
        parm definition can either be a [start, stop, step] or a list of the parameters"""

        parm = gmlparmpalette.BldgOrientationParm()
        
        if range_definition == True:
            is_it_int = True
            for ele in parm_definition:
                if type(ele) == float:
                    is_it_int = False
                    
            if is_it_int:        
                parm.define_int_range(parm_definition[0],parm_definition[1],parm_definition[2])
            else:
                n_p_define = len(parm_definition)
                if n_p_define == 2:
                    parm.define_float_range(parm_definition[0],parm_definition[1])
                if n_p_define == 3:
                    parm.define_float_range(parm_definition[0],parm_definition[1], parm_definition[2])
                    
        if range_definition == False:
            parm.set_parm_range(parm_definition)
            
        if bldg_class !=None:
            parm.apply_2_bldg_class(bldg_class)
        if bldg_function != None:
            parm.apply_2_bldg_function(bldg_function)
        if bldg_usage != None:
            parm.apply_2_bldg_usage(bldg_usage)
            
        if clash_detection == False:
            parm.set_clash_detection(clash_detection)
        if boundary_detection == False:
            parm.set_boundary_detection(boundary_detection)
    
        bldg_parm_dict = {}
        bldg_parm_dict["parameter_object"] = parm
        self.parm_obj_dict_list.append(bldg_parm_dict)
        
    def add_bldg_pos_parm(self, xdim = 10, ydim=10, bldg_class= None, bldg_function = None, bldg_usage = None, 
                          clash_detection = True, boundary_detection = True):
        
        parm = gmlparmpalette.BldgPositionParm()
        parm.set_xdim_ydim(xdim, ydim)
        
        if bldg_class !=None:
            parm.apply_2_bldg_class(bldg_class)
        if bldg_function != None:
            parm.apply_2_bldg_function(bldg_function)
        if bldg_usage != None:
            parm.apply_2_bldg_usage(bldg_usage)
            
        if clash_detection == False:
            parm.set_clash_detection(clash_detection)
        if boundary_detection == False:
            parm.set_boundary_detection(boundary_detection)
            
        bldg_parm_dict = {}
        bldg_parm_dict["parameter_object"] = parm
        self.parm_obj_dict_list.append(bldg_parm_dict)
        
    def add_parm(self, parm_obj):
        bldg_parm_dict = {}
        bldg_parm_dict["parameter_object"] = parm_obj
        self.parm_obj_dict_list.append(bldg_parm_dict)
        
    def define_nparameters(self):
        parm_obj_dict_list = self.parm_obj_dict_list
        citygml_reader = self.citygml
        total_nparms = 0
        for parm_obj_dict in parm_obj_dict_list:
            parm_obj = parm_obj_dict["parameter_object"]
            nparms = parm_obj.define_nparameters(citygml_reader)
            parm_obj_dict["parameter_count"] = (total_nparms, total_nparms+nparms )
            total_nparms += nparms
            
        self.nparameters = total_nparms
        
    def generate_random_parameters(self):
        if self.nparameters == None:
            self.define_nparameters()
        parameters = []
        for _ in range(self.nparameters):
            random.seed()
            parameters.append(random.random())
        return parameters
        
    def generate_design_variant(self, parameters, dv_citygml_filepath):
        if self.nparameters == None:
            self.define_nparameters()
        parm_obj_dict_list = self.parm_obj_dict_list
        citygml_reader = self.citygml
        for parm_obj_dict in parm_obj_dict_list:
            parm_obj = parm_obj_dict["parameter_object"]
            parm_cnt = parm_obj_dict["parameter_count"]
            parm_object_parms = parameters[parm_cnt[0]:parm_cnt[1]]
            citygml_reader = parm_obj.execute(citygml_reader, parm_object_parms)
            
        citygml_writer = pycitygml.Writer()
        citygml_writer.citymodelnode = citygml_reader.citymodelnode
        citygml_writer.write(dv_citygml_filepath)
#===================================================================================================================================================