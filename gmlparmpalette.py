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
import gml3dmodel
import py3dmodel
import pycitygml
import utility

class BaseParm(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def define_int_range(self, start, stop, step):
        """ the method defines the int_range of the parm_range"""
        parm_range = range(start, stop+step, step)
        for parm in parm_range:
            if parm > stop:
                parm_range.remove(parm)
        return parm_range
        
    @abc.abstractmethod
    def define_float_range(self, start, stop, step):
        """ the method defines the float_range of the parm_range"""
        parm_range = utility.frange(start, stop + step, step)
        for parm in parm_range:
            if parm > stop:
                parm_range.remove(parm)
        return parm_range
        
    @abc.abstractmethod
    def set_parm_range(self, parm_range):
        """ the method sets the parm_range attribute"""
        return 
        
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
        
class BldgFlrAreaHeightParm(BaseParm):
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
        
    def eligibility_test(self, gml_bldg_list, pycitygml_reader):
        eligible_bldg_list = []
        for gml_bldg in gml_bldg_list:
            bldg_class = pycitygml_reader.get_building_class(gml_bldg)
            bldg_function = pycitygml_reader.get_building_function(gml_bldg)
            bldg_usage = pycitygml_reader.get_building_usage(gml_bldg)
            
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
                eligible_bldg_list.append(gml_bldg)
                
        return eligible_bldg_list
        
    def define_int_range(self, start, stop, step):
        parm_range = super(BldgFlrAreaHeightParm, self).define_int_range(start, stop, step)
        self.parm_range = parm_range
        return parm_range
        
    def define_float_range(self, start, stop, step):
        parm_range = super(BldgFlrAreaHeightParm, self).define_float_range(start, stop, step)
        self.parm_range = parm_range
        return parm_range
        
    def set_parm_range(self, parm_range):
        self.parm_range = parm_range
        
    def map_nrmlise_parms_2_parms(self, nrmlised_parm_list):
        if self.parm_range == None:
            raise Exception("please define parm range")
        parm_range = self.parm_range
        n_parm_range = len(parm_range)-1
        parm_list = []
        for nrml_parm in nrmlised_parm_list:
            parm_index = int(round(nrml_parm*n_parm_range))
            parm = parm_range[parm_index]
            parm_list.append(parm)
        return parm_list
        
    def define_nparameters(self,pycitygml_reader):
        gml_bldg_list = pycitygml_reader.get_buildings()
        #filter through the eligible buildings
        eligible_bldg_list = self.eligibility_test(gml_bldg_list, pycitygml_reader)
        #because each building has one building height parameter
        nparameters = len(eligible_bldg_list)
        return nparameters
                
    def execute(self, pycitygml_reader, nrmlised_parm_list):
        parm_list = self.map_nrmlise_parms_2_parms(nrmlised_parm_list)
        citygml_writer = pycitygml.Writer()
        gml_landuses = pycitygml_reader.get_landuses()
        gml_bldg_list = pycitygml_reader.get_buildings()
        bcnt = 0
        for gml_landuse in gml_landuses:
            #echeck which buildings are on this plot
            gml_bldg_on_luse = gml3dmodel.buildings_on_landuse(gml_landuse,gml_bldg_list, pycitygml_reader)
            
            #check which buildings should this parameter be applied to
            eligibility_bldg_list = self.eligibility_test(gml_bldg_on_luse, pycitygml_reader)
            n_eligibility_bldgs = len(eligibility_bldg_list)
            
            #calculate the total landuse floor area
            luse_flr_area = 0
            for eligible_gml_bldg in eligibility_bldg_list:
                height, nstorey, storey_height = gml3dmodel.get_building_height_storey(eligible_gml_bldg, pycitygml_reader)
                bldg_flr_area, flrplates = gml3dmodel.get_bulding_floor_area(eligible_gml_bldg, nstorey, storey_height, pycitygml_reader)
                luse_flr_area += bldg_flr_area
               
            #get the parameters for this landuse plot
            parms_4_luse = parm_list[bcnt:n_eligibility_bldgs]
            total_prop = float(sum(parms_4_luse))
            
            #redistribute the flr area
            new_bldg_flr_area_list = []
            for parm in parms_4_luse:
                new_bldg_flr_area = float(parm)/total_prop * luse_flr_area
                new_bldg_flr_area_list.append(new_bldg_flr_area)
                
            #reconstuct the buildings according to the new distribuition
            for cnt in range(n_eligibility_bldgs):
                gml_bldg = eligibility_bldg_list[cnt]
                bldg_occsolid = gml3dmodel.get_building_occsolid(gml_bldg,pycitygml_reader)
                height, nstorey, storey_height = gml3dmodel.get_building_height_storey(gml_bldg, pycitygml_reader)
                new_bldg_flr_area = new_bldg_flr_area_list[cnt]
                new_building_solid = gml3dmodel.construct_building_through_floorplates(bldg_occsolid,new_bldg_flr_area,storey_height)
                new_height, new_n_storey = gml3dmodel.calculate_bldg_height_n_nstorey(new_building_solid, storey_height)
                gml3dmodel.update_gml_building(gml_bldg,new_building_solid, pycitygml_reader, 
                                               citygml_writer, new_height = new_height, new_nstorey = new_n_storey)
                
            bcnt += n_eligibility_bldgs
        
        non_bldg_cityobjs = pycitygml_reader.get_non_xtype_cityobject("bldg:Building")
        gml3dmodel.write_citygml(non_bldg_cityobjs, citygml_writer)
        citymodel_node = citygml_writer.citymodelnode
        reader = pycitygml.Reader()
        reader.load_citymodel_node(citymodel_node)
        return reader
        
class BldgOrientationParm(BaseParm):
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
        
    def eligibility_test(self, gml_bldg_list, pycitygml_reader):
        eligible_bldg_list = []
        for gml_bldg in gml_bldg_list:
            bldg_class = pycitygml_reader.get_building_class(gml_bldg)
            bldg_function = pycitygml_reader.get_building_function(gml_bldg)
            bldg_usage = pycitygml_reader.get_building_usage(gml_bldg)
            
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
                eligible_bldg_list.append(gml_bldg)
                
        return eligible_bldg_list
        
    def define_int_range(self, start, stop, step):
        parm_range = super(BldgOrientationParm, self).define_int_range(start, stop, step)
        self.parm_range = parm_range
        return parm_range
        
    def define_float_range(self, start, stop, step):
        parm_range = super(BldgOrientationParm, self).define_float_range(start, stop, step)
        self.parm_range = parm_range
        return parm_range
        
    def set_parm_range(self, parm_range):
        self.parm_range = parm_range
        
    def map_nrmlise_parms_2_parms(self, nrmlised_parm_list):
        if self.parm_range == None:
            raise Exception("please define parm range")
        parm_range = self.parm_range
        n_parm_range = len(parm_range)-1
        parm_list = []
        for nrml_parm in nrmlised_parm_list:
            parm_index = int(round(nrml_parm*n_parm_range))
            parm = parm_range[parm_index]
            parm_list.append(parm)
        return parm_list
        
    def define_nparameters(self,pycitygml_reader):
        gml_bldg_list = pycitygml_reader.get_buildings()
        #filter through the eligible buildings
        eligible_bldg_list = self.eligibility_test(gml_bldg_list, pycitygml_reader)
        #because each building has one building height parameter
        nparameters = len(eligible_bldg_list)
        return nparameters
                
    def execute(self, pycitygml_reader, nrmlised_parm_list, clash_detection = True):
        parm_list = self.map_nrmlise_parms_2_parms(nrmlised_parm_list)
        citygml_writer = pycitygml.Writer()
        gml_landuses = pycitygml_reader.get_landuses()
        gml_bldg_list = pycitygml_reader.get_buildings()
        bcnt = 0
        for gml_landuse in gml_landuses:
            #echeck which buildings are on this plot
            gml_bldg_on_luse = gml3dmodel.buildings_on_landuse(gml_landuse,gml_bldg_list, pycitygml_reader)
            
            #check which buildings should this parameter be applied to
            eligibility_bldg_list = self.eligibility_test(gml_bldg_on_luse, pycitygml_reader)
            n_eligibility_bldgs = len(eligibility_bldg_list)
            
            #get the parameters for this landuse plot
            parms_4_luse = parm_list[bcnt:n_eligibility_bldgs]
            
            #get all the bldg_occsolid 
            roting_bldg_occsolid_list = []
            for gml_bldg in eligibility_bldg_list:
                bldg_occsolid = gml3dmodel.get_building_occsolid(gml_bldg, pycitygml_reader)
                roting_bldg_occsolid_list.append(bldg_occsolid)
                
            #rotate the buildings
            for cnt in range(n_eligibility_bldgs):
                eligible_gml_bldg = eligibility_bldg_list[cnt]
                rot_angle = parms_4_luse[cnt]
                rot_bldg_occsolid = gml3dmodel.rotate_bldg(eligible_gml_bldg, rot_angle, pycitygml_reader)
                if clash_detection == True:
                    roting_bldg_occsolid_list2 = roting_bldg_occsolid_list[:]
                    del roting_bldg_occsolid_list2[cnt]
                    rot_compound = py3dmodel.construct.make_compound(roting_bldg_occsolid_list2)
                    common_compound = py3dmodel.construct.boolean_common(rot_bldg_occsolid, rot_compound)
                    common_compound = py3dmodel.fetch.shape2shapetype(common_compound)
                    is_cmpd_null = py3dmodel.fetch.is_compound_null(common_compound)
                    if is_cmpd_null:
                        #there is no clash
                        roting_bldg_occsolid_list[cnt] = rot_bldg_occsolid
                        
                elif clash_detection == False:
                    roting_bldg_occsolid_list[cnt] = rot_bldg_occsolid
            
            for up_cnt in range(n_eligibility_bldgs):
                gml_bldg = eligibility_bldg_list[up_cnt]
                new_building_solid = roting_bldg_occsolid_list[up_cnt]
                gml3dmodel.update_gml_building(gml_bldg,new_building_solid, pycitygml_reader, 
                                               citygml_writer)

            bcnt += n_eligibility_bldgs
        
        non_bldg_cityobjs = pycitygml_reader.get_non_xtype_cityobject("bldg:Building")
        gml3dmodel.write_citygml(non_bldg_cityobjs, citygml_writer)
        citymodel_node = citygml_writer.citymodelnode
        reader = pycitygml.Reader()
        reader.load_citymodel_node(citymodel_node)
        return reader
    
if __name__ == '__main__':
    bp = BldgFlrAreaHeightParm()
    x = bp.execute()
    print x
    print bp