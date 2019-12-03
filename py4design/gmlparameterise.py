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
import random
from . import pycitygml

class Parameterise(object):
    """
    An object that extracts all the neccessary information from CityGML model and parameterise it.For more information please refer to 
    Chen, Kian Wee, Patrick Janssen, and Leslie Norford. 2017. Automatic Parameterisation of Semantic 3D City Models for Urban Design Optimisation. 
    In Future Trajectories of Computation in Design, Proceedings of the 17th International Conference on Computer Aided Architectural Design Futures, pp 84 to 100. Istanbul, Turkey.
    
    Attributes
    ----------    
    citygml : pycitygml.Reader class instance
        The reader to read the CityGML.
    
    parm_obj_dict_list : list of dictionaries
        Each dictionary has keys {"parameter_object", "parameter_count"}. The parameter_object contains a BaseParm class instance for parameterising the model, and the parameter count is a 
        tuple of ints that specify the index of the parameters used for generating a design alternative.
            
    nparameters : int
        The number of parameters for the model.
    """
    def __init__(self, citygmlfile):
        """Initialises the class"""
        reader = pycitygml.Reader()
        reader.load_filepath(citygmlfile)
        self.citygml = reader
        self.parm_obj_dict_list = []
        self.nparameters = None        
        
    def add_parm(self, parm_obj):
        """
        This function adds BaseParm object for the parameterisation.
        
        Parameters
        ----------
        parm_obj : BaseParm class instance
            The BaseParm for parameterising the model.
        """
        bldg_parm_dict = {}
        bldg_parm_dict["parameter_object"] = parm_obj
        self.parm_obj_dict_list.append(bldg_parm_dict)
        
    def define_nparameters(self):
        """ 
        The function determines the total parameters for the model.
        """
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
        """ 
        The function generates a list of random parameters.
        
        Returns
        -------        
        parameter list : list of int/floats
            List of normalised parameters.
        """
        if self.nparameters == None:
            self.define_nparameters()
        parameters = []
        for _ in range(self.nparameters):
            random.seed()
            parameters.append(random.random())
        return parameters
        
    def generate_design_variant(self, parameters, dv_citygml_filepath):
        """ 
        This function defines generates a design alternative based on all the appended parameter objects.
        
        Parameters
        ----------        
        parameters : list of ints/floats
            The normalised parameters to be mapped to the real parameters defined, the parameters will be used to generate a design alternative.
        
        dv_citygml_filepath : str
            The file path of the CityGML file to write the generated design alternative.
        """
        if self.nparameters == None:
            self.define_nparameters()
        parm_obj_dict_list = self.parm_obj_dict_list
        citygml_reader = self.citygml
        for parm_obj_dict in parm_obj_dict_list:
            parm_obj = parm_obj_dict["parameter_object"]
            parm_cnt = parm_obj_dict["parameter_count"]
            parm_object_parms = parameters[parm_cnt[0]:parm_cnt[1]]
            print(parm_obj)
            citygml_reader = parm_obj.execute(citygml_reader, parm_object_parms)
            
        citygml_writer = pycitygml.Writer()
        citygml_writer.citymodel_node = citygml_reader.citymodel_node
        citygml_writer.write(dv_citygml_filepath)
#===================================================================================================================================================