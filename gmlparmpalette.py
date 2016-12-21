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

class BaseParm(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def define_nparameters(self, pycitygml_reader):
        """ the method determines how many parameters is required for 
        this urban design """
        return
        
    @abc.abstractmethod
    def execute(self,pycitygml_reader, parameters):
        """ the parameterisation process is defined 
        and the method executes the parameterisation process """
        return 
        
class BldgHeightParm(BaseParm):
    def __init__(self):
        self.bldg_class = None
        self.bldg_function = None
        self.bldg_usage = None
        self.parm_range = None
        
    def apply_2_bldg_class(self, bldg_class):
        self.bldg_class = bldg_class
        
    def apply_2_bldg_function(self, bldg_function):
        self.bldg_function = bldg_function
        
    def apply_2_bldg_usage(self, bldg_usage):
        self.bldg_usage = bldg_usage
        
    def define_range(self, start, stop, step):
        self.parm_range = [start, stop, step]
        
    def define_nparameters(self,pycitygml_reader):
        buildings = pycitygml_reader.get_buildings()
        #filter through the eligible buildings
        eligible_bldg_list = []
        for building in buildings:
            bldg_class = pycitygml_reader.get_building_class(building)
            bldg_function = pycitygml_reader.get_building_function(building)
            bldg_usage = pycitygml_reader.get_building_usage(building)
            
            eligibility = True
            if self.bldg_class != None: 
                if self.bldg_class != bldg_class:
                    eligibility = False
                    
            if self.bldg_function != None:
                if self.bldg_function != bldg_function:
                    eligibility = False
            
            if self.bldg_usage != None:
                if self.bldg_usage != bldg_usage:
                    eligibility = False
                    
            if eligibility == True:
                eligible_bldg_list.append(building)
                
        #because each building has one building height parameter
        nparameters = len(eligible_bldg_list)
        return nparameters
                
    def execute(self, pycitygml_reader, parameters):
        print "test"
        return "implemented"
        
if __name__ == '__main__':
    bp = BldgHeightParm()
    x = bp.execute()
    print x
    print bp