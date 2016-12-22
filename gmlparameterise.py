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
import gml3dmodel
import gmlparmpalette

class Parameterise(object):
    def __init__(self, citygmlfile):
        self.citygml = pycitygml.Reader(citygmlfile)
        self.parm_obj_list = []
        self.nparameters = None
        
        self.buildings = self.citygml.get_buildings()
        self.landuses = self.citygml.get_landuses()
        self.stops = self.citygml.get_bus_stops()
        self.roads = self.citygml.get_roads()
        self.railways = self.citygml.get_railways()
        self.building_footprints = None
        
        self.buildings2landuses = None
        self.nparms_abuilding = 3
        
    def add_bldg_flr_area_height_parm(self, bldg_class= None, bldg_function = None, bldg_usage = None):
        """specify the class, function and usage of the buildings this parameter will be applied to, if none are given, 
        this parameter will apply to all buildings"""

        bldg_parm = gmlparmpalette.BldgFlrAreaHeightParm()
        bldg_parm.define_int_range(1,10,1)
        if bldg_class !=None:
            bldg_parm.apply_2_bldg_class(bldg_class)
        if bldg_function != None:
            bldg_parm.apply_2_bldg_function(bldg_function)
        if bldg_usage != None:
            bldg_parm.apply_2_bldg_usage(bldg_usage)
        self.parm_obj_list.append(bldg_parm)
        
    def define_nparameters(self):
        parm_obj_list = self.parm_obj_list
        citygml_reader = self.citygml
        total_nparms = 0
        for parm_obj in parm_obj_list:
            nparms = parm_obj.define_nparameters(citygml_reader)
            total_nparms += nparms
        self.nparameters = total_nparms
        
    def generate_random_parameters(self):
        if self.nparameters == None:
            raise Exception("please run define_nparameters() before running this ")
        parameters = []
        for _ in range(self.nparameters):
            random.seed()
            parameters.append(random.random())
        return parameters
        
    def generate_design_variant(self, parameters, dv_citygml_filepath):
        parm_obj_list = self.parm_obj_list
        citygml_reader = self.citygml
        for parm_obj in parm_obj_list:
            parm_obj.execute(citygml_reader, parameters)
        pass 
        '''
        if self.buildings2landuses == None:
            raise Exception 
            
        citygml = self.citygml
        citygml_writer = pycitygml.Writer()
        buildings2landuses = self.buildings2landuses
        nparms_abuilding = self.nparms_abuilding
        newblist = []
        plot_faces_list = []
        gcnt_list = []
        
        bounding_list_list = []
        
        lcnt = 0
        for b2l in buildings2landuses:
            print "LANDUSE", lcnt
            
            #get the buildings on the landuse
            landuse_pts = b2l["landuse_pts"]
            buildings_on_landuse = b2l["buildings"]
            nbuildings_on_landuse = len(buildings_on_landuse)
            print nbuildings_on_landuse, "BUILDINGS ON LANDUSE", 
            b_attribs_list = []
            building_flr_area_list = []
            
            #print "GCNT_LIST", gcnt_list
            
            bcnt = 0
            #calculate the total build up flr area of the landuse
            for building_footprint_dict in buildings_on_landuse:
                b_attribs = {}
                gml_building = building_footprint_dict["building"]
                bfunction = citygml.get_building_function(gml_building)
                
                gcnt = []
                #carpark only have 2 parameters it does not have the build area parameters
                if bfunction == "1610": #carpark
                    print "CARPARK!!"
                    for i in range(nparms_abuilding-1):
                        if gcnt_list:
                            gcnt.append(gcnt_list[-1][-1] + i + 1)
                        else:
                            gcnt.append(0+i)
                        #gcnt.append(parameter_cnt + ((bcnt*nparms_abuilding)+i))
                        
                else: 
                    for i in range(nparms_abuilding):
                        if gcnt_list:
                            gcnt.append(gcnt_list[-1][-1] + i + 1)
                        else:
                            gcnt.append(0+i)
                        #print parameter_cnt + ((bcnt*nparms_abuilding)+i)
                        #gcnt.append(parameter_cnt + ((bcnt*nparms_abuilding)+i))
                        
                gcnt_list.append(gcnt)
                
                b_attribs["gcnt"] = gcnt
                building_solid = gml3dmodel.get_building_solid(gml_building, citygml)
                b_attribs["solid"] = building_solid
                loc_pt, bounding_footprint = gml3dmodel.get_building_location_pt(building_solid)
                b_attribs["loc_pt"] = loc_pt
                b_attribs["bounding_footprint"] = bounding_footprint
                height, nstorey, storey_height = gml3dmodel.get_building_height_storey(building_footprint_dict["building"], citygml)
                b_attribs["height"] = height
                b_attribs["nstorey"] = nstorey
                b_attribs["storey_height"] = storey_height
                building_footprint = building_footprint_dict["footprint"]
                b_attribs["building_footprint"] = building_footprint
                b_attribs_list.append(b_attribs)
                
                if bfunction != "1610":
                    flr_area = gml3dmodel.get_bulding_floor_area(building_solid, loc_pt, bounding_footprint, nstorey, 
                                                                        storey_height, building_footprint)
                                                                        
                    building_flr_area_list.append(flr_area)
                    
                bcnt += 1
                
            build_area = sum(building_flr_area_list)
            
            #rearrange the buildings on the plot 
            b_attribs_list, plot_faces = gml3dmodel.rearrange_building_location(b_attribs_list, landuse_pts, parameters, 5, 5)
            plot_faces_list.extend(plot_faces)
            
            #determine the floor area distribution of the buildings according to the parameters
            rproportion = []
            total_prop = 0
            ba_cnt = 0
            for ba_cnt in range(nbuildings_on_landuse):
                b_attribs = b_attribs_list[ba_cnt]
                gml_building = buildings_on_landuse[ba_cnt]["building"]
                bfunction = citygml.get_building_function(gml_building)
                if bfunction != "1610": #carpark do not include in the redistribuition of floor area
                    rprop_cnt = b_attribs["gcnt"][nparms_abuilding-1]
                    rprop = parameters[rprop_cnt]
                    rproportion.append(rprop)
                    total_prop += rprop
                if  bfunction == "1610":
                    rprop = None
                    rproportion.append(rprop)
                ba_cnt +=1
                
            #construct the buildings according to the new distribuition
            pcnt = 0
            for p in rproportion:
                building = buildings_on_landuse[pcnt]["building"]
                height = citygml.get_building_height(building)
                storey = citygml.get_building_storey(building)
                if p != None:
                    prop = p/total_prop
                    p_area = prop*build_area
                    storey_height = height/storey
                    #get the solid and bounding footprint
                    building_solid = b_attribs_list[pcnt]["solid"]
                    new_building_solid, floorplates, bounding_list = gml3dmodel.construct_building_through_floorplates(building_solid, p_area, 
                                                                                                               storey_height, citygml)
                    bounding_list_list.append(bounding_list)  
                                                                     
                    new_nstorey = len(floorplates)-1 #minus away the roof
                    new_height = new_nstorey*storey_height
                    
                else:
                    new_building_solid = building_solid = b_attribs_list[pcnt]["solid"]
                    new_nstorey = storey
                    new_height = height
                    bounding_list_list.append([])  
                    
                self.update_gml_building(building, new_height, new_nstorey, new_building_solid, citygml_writer)
                newblist.append(new_building_solid)
                pcnt += 1
                
            lcnt+=1
            
        self.write_citygml(self.landuses, self.stops, self.roads, self.railways, citygml_writer)
        return citygml_writer, newblist, plot_faces_list, b_attribs_list, bounding_list_list
        '''
#===================================================================================================================================================