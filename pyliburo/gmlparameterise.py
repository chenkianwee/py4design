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

class Parameterise(object):
    def __init__(self, citygmlfile):
        reader = pycitygml.Reader()
        reader.load_filepath(citygmlfile)
        self.citygml = reader
        self.parm_obj_dict_list = []
        self.nparameters = None        
        
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
            print parm_obj
            citygml_reader = parm_obj.execute(citygml_reader, parm_object_parms)
            
        citygml_writer = pycitygml.Writer()
        citygml_writer.citymodelnode = citygml_reader.citymodelnode
        citygml_writer.write(dv_citygml_filepath)
#===================================================================================================================================================