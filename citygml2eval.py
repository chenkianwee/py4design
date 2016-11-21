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
import os

import pycitygml
import py3dmodel
import py2radiance
import gml3dmodel
import urbanformeval
import threedmodel

class Evals(object):
    def __init__(self, citygmlfile):
        self.citygml = pycitygml.Reader(citygmlfile)
        self.citygmlfilepath = citygmlfile
        self.buildings = self.citygml.get_buildings()
        self.landuses = self.citygml.get_landuses()
        self.stops = self.citygml.get_bus_stops()
        self.roads = self.citygml.get_roads()
        self.railways = self.citygml.get_railways()
        #occ geometries
        self.roof_occfaces = None
        self.facade_occfaces = None
        self.footprint_occfaces = None
        self.building_dictlist = None
        self.buildings_on_plot_2dlist = None #2d list of building dictlist according to the plot they belong to 
        self.landuse_occpolygons = None
        #radiance parameters
        self.rad_base_filepath = os.path.join(os.path.dirname(__file__),'py2radiance','base.rad')
        self.sgfai_folderpath = os.path.join(os.path.dirname(self.citygmlfilepath), 'sgfai_data')
        self.dfai_folderpath = os.path.join(os.path.dirname(self.citygmlfilepath), 'dfai_data')
        self.pvai_folderpath = os.path.join(os.path.dirname(self.citygmlfilepath), 'pvai_data')
        self.daysim_folderpath = os.path.join(os.path.dirname(self.citygmlfilepath), 'daysim_data')
        self.solarxdim = None
        self.solarydim = None
        self.rad = None
        #rad results 
        self.irrad_results = None
        self.illum_results = None
        self.facade_grid_srfs = None
        self.roof_grid_srfs = None
        
    def initialise_occgeom(self):
        buildings = self.buildings
        roof_list = []
        facade_list = []
        footprint_list = []
        building_dictlist = []
        for building in buildings:
            building_dict ={}
            #get all the polygons from the building 
            pypolygonlist = self.citygml.get_pypolygon_list(building) 
            bsolid = threedmodel.pypolygons2occsolid(pypolygonlist)
            #extract the polygons from the building and separate them into facade, roof, footprint
            facades, roofs, footprints = gml3dmodel.identify_building_surfaces(bsolid)
            building_dict["facade"] = facades
            building_dict["footprint"] = footprints[0]
            building_dict["roof"] = roofs
            building_dict["solid"] = bsolid
            building_dictlist.append(building_dict)
            facade_list.extend(facades)
            roof_list.extend(roofs)
            footprint_list.extend(footprints)
            
        self.building_dictlist = building_dictlist
        self.facade_occfaces = facade_list
        self.roof_occfaces = roof_list
        self.footprint_occfaces = footprint_list
        
                
    def initialise_solar_analyse_facade(self, epweatherfile, xdim, ydim, folderpath):
        #check if the building surfaces has been identified
        if self.facade_occfaces == None:
            self.initialise_occgeom()
        
        self.solarxdim = xdim
        self.solarydim = ydim
        #generate sensor points from the facades
        facade_list = self.facade_occfaces
        topo_list = []
        sensor__ptlist = []
        sensor_dirlist = []
        
        
        for facade in facade_list:
            sensor_surfaces, sensor_pts, sensor_dirs = gml3dmodel.generate_sensor_surfaces(facade, xdim, ydim)
            sensor__ptlist.extend(sensor_pts)
            sensor_dirlist.extend(sensor_dirs)
            topo_list.extend(sensor_surfaces)
            
        #initialise py2radiance 
        rad = py2radiance.Rad(self.rad_base_filepath, folderpath)
        #get all the geometry of the buildings for shading in radiance
        buildings = self.buildings
        bcnt = 0
        for building in buildings:
            #extract the surfaces from the buildings for shading geometry in radiance
            gmlpolygons = self.citygml.get_polygons(building) 
            for gmlpolygon in gmlpolygons:
                #TODO: need to account for polygons with holes
                #get all the polygons into a list
                pypolygon = self.citygml.polygon_2_pt_list(gmlpolygon)
                del pypolygon[-1]
                #extract the shading geometry 
                srfname = gmlpolygon.attrib["{%s}id" % self.citygml.namespaces['gml']]
                #material with reflectance 0.2
                srfmat = "RAL2012"
                py2radiance.RadSurface(srfname, pypolygon, srfmat, rad)
                
            bcnt +=1
            
        #get the sensor grid points
        rad.set_sensor_points(sensor__ptlist, sensor_dirlist)
        rad.create_sensor_input_file()
        #create the geometry files
        rad.create_rad_input_file()
        self.rad = rad
        self.facade_grid_srfs = topo_list
        
    def sgfai(self, irrad_threshold, epweatherfile, xdim, ydim):
        """
        Solar Gain Facade Area Index (SGFAI) calculates the ratio of facade area that 
        receives irradiation below a specified level over the net facade area. 
        SGFAI is represented as an area ratio.
        """
        self.initialise_solar_analyse_facade(epweatherfile, xdim, ydim, self.sgfai_folderpath )
        #execute cumulative oconv for the whole year
        rad = self.rad
        time = str(0) + " " + str(24)
        date = str(1) + " " + str(1) + " " + str(12) + " " + str(31)
        rad.execute_cumulative_oconv(time, date, epweatherfile)
        #execute cumulative_rtrace
        rad.execute_cumulative_rtrace(str(2))#EXECUTE!! 
        #retrieve the results
        irrad_ress = rad.eval_cumulative_rad()
        facade_list = self.facade_occfaces
        topo_list = self.facade_grid_srfs
        
        high_irrad = []
        high_irrad_faces = []
        
        irrad_cnt = 0
        for irrad_res in irrad_ress:
            if irrad_res> irrad_threshold:
                high_irrad.append(irrad_res)
                #measure the area of the grid 
                high_irrad_faces.append(topo_list[irrad_cnt])
            irrad_cnt +=1
            
        total_area = gml3dmodel.faces_surface_area(facade_list)
        high_irrad_area = gml3dmodel.faces_surface_area(high_irrad_faces)
        sgfai = (high_irrad_area/total_area) * 100
        
        self.irrad_results = irrad_ress
        return sgfai, topo_list, irrad_ress 
        
    def dfai(self, daylight_threshold, epweatherfile, xdim, ydim):
        """
        Daylighting Facade Area Index (DFAI) calculates the ratio of facade area that 
        receives daylighting above a specified level, 
        above a specified percentage of the annual daytime hours
        over the net facade area. 
        DFAI is represented as an area ratio.
        """            
        self.initialise_solar_analyse_facade(epweatherfile, xdim, ydim, self.dfai_folderpath )
        #execute cumulative oconv for the whole year
        rad = self.rad
        #execute cumulative oconv for the whole year
        rad = self.rad
        time = str(0) + " " + str(24)
        date = str(1) + " " + str(1) + " " + str(12) + " " + str(31)
        rad.execute_cumulative_oconv(time, date, epweatherfile, output = "illuminance")
        #execute cumulative_rtrace
        rad.execute_cumulative_rtrace(str(2))#EXECUTE!! 
        #retrieve the results
        illum_ress = rad.eval_cumulative_rad(output = "illuminance")
        facade_list = self.facade_occfaces
        topo_list = self.facade_grid_srfs
        
        #get the number of sunuphrs
        #once the geometries are created initialise daysim
        daysim_dir = self.daysim_folderpath
        rad.initialise_daysim(daysim_dir)
        #a 60min weatherfile is generated
        rad.execute_epw2wea(epweatherfile)
        sunuphrs = rad.sunuphrs
        
        high_illum = []
        high_illum_faces = []
        mean_illum_ress = []
        illum_cnt = 0
        for illum_res in illum_ress:
            mean_illum = (illum_res/float(sunuphrs))
            mean_illum_ress.append(mean_illum)
            if mean_illum > daylight_threshold:
                high_illum.append(mean_illum)
                #measure the area of the grid 
                high_illum_faces.append(topo_list[illum_cnt])
            illum_cnt +=1
            
        total_area = gml3dmodel.faces_surface_area(facade_list)
        high_illum_area = gml3dmodel.faces_surface_area(high_illum_faces)
        sgfai = (high_illum_area/total_area) * 100
        
        self.illum_results = mean_illum_ress
        #return dfai, topo_list, illum_ress
        return sgfai, topo_list, mean_illum_ress 
        
    def hourly_solar_analysis(self, epweatherfile, xdim, ydim, irradiance = True):
        """
        Run Daysim hourly simulation 
        returns: a dictionary with each day as a key
        the key points to a 2d list 
        each row is the sensor pts
        each column is the hourly values 
        """
        if self.rad == None:
            self.initialise_solar_analyse_facade(epweatherfile, xdim, ydim)
            
        elif (self.solarxdim, self.solarydim) != (xdim, ydim):
            self.solar_analyse_facade(epweatherfile, xdim, ydim)
            
        #execute cumulative oconv for the whole year
        rad = self.rad
 
        #once the geometries are created initialise daysim
        daysim_dir = self.daysim_folderpath
        rad.initialise_daysim(daysim_dir)
        #a 60min weatherfile is generated
        rad.execute_epw2wea(epweatherfile)
        rad.execute_radfiles2daysim()
        #execute daysim
        rad.write_default_radiance_parameters()#the default settings are the complex scene 1 settings of daysimPS
        if irradiance == True :
            rad.execute_gen_dc("w/m2")
        else:
            rad.execute_gen_dc("lux")
            
        rad.execute_ds_illum()
        
        res_dict = rad.eval_ill()

        return res_dict
        
    def avg_illuminance(self, res_dict):
        """
        for daysim hourly simulation
        """
        rad = self.rad
        npts = len(res_dict.values()[0])
        sensorptlist = []
        for _ in range(npts):
            sensorptlist.append([])
            
        for res in res_dict.values():
            for rnum in range(npts):
                sensorptlist[rnum].append(res[rnum])
                
        cumulative_list = []
        sunuphrs = rad.sunuphrs
        illum_ress = []
        for sensorpt in sensorptlist:
            cumulative_sensorpt = sum(sensorpt)
            avg_illuminance = cumulative_sensorpt/sunuphrs
            cumulative_list.append(cumulative_sensorpt)
            illum_ress.append(avg_illuminance)
            
        return illum_ress
        
    def pvai(self, irrad_threshold, epweatherfile, xdim, ydim, surface = "roof"):
        '''
        Roof PV Potential (RPVP) calculates the potential electricity 
        that can be generated on the roof of buildings annually.
        RPVP is represented in kWh/yr.
        
        PV Roof Area Index (PVAI) calculates the ratio of roof area that 
        receives irradiation above a specified level, 
        receives irradiation above a specified level over the net roof area. 
        PVRAI is represented as an area ratio.
        '''
        
        #check if the building surfaces has been identified
        if self.facade_occfaces == None:
            self.initialise_occgeom()
            
        #generate sensor points from the surrfaces
        if surface == "roof":
            srf_list = self.roof_occfaces
        if surface == "facade":
            srf_list = self.facade_occfaces
            
        topo_list = []
        sensor__ptlist = []
        sensor_dirlist = []
        
        for srf in srf_list:
            sensor_surfaces, sensor_pts, sensor_dirs = gml3dmodel.generate_sensor_surfaces(srf, xdim, ydim)
            sensor__ptlist.extend(sensor_pts)
            sensor_dirlist.extend(sensor_dirs)
            topo_list.extend(sensor_surfaces)
            
        
        #initialise py2radiance 
        rad = py2radiance.Rad(self.rad_base_filepath, self.pvai_folderpath)
        #get all the geometry of the buildings for shading in radiance
        buildings = self.buildings
        bcnt = 0
        for building in buildings:
            #extract the surfaces from the buildings for shading geometry in radiance
            gmlpolygons = self.citygml.get_polygons(building) 
            for gmlpolygon in gmlpolygons:
                #TODO: need to account for polygons with holes
                #get all the polygons into a list
                pypolygon = self.citygml.polygon_2_pt_list(gmlpolygon)
                del pypolygon[-1]
                #extract the shading geometry 
                srfname = gmlpolygon.attrib["{%s}id" % self.citygml.namespaces['gml']]
                #just use pure white paint
                srfmat = "RAL9010_pur_white_paint"
                py2radiance.RadSurface(srfname, pypolygon, srfmat, rad)
                
            bcnt +=1
            
        #get the sensor grid points
        rad.set_sensor_points(sensor__ptlist, sensor_dirlist)
        rad.create_sensor_input_file()
        #create the geometry files
        rad.create_rad_input_file()
        #execute cumulative oconv for the whole year
        time = str(0) + " " + str(24)
        date = str(1) + " " + str(1) + " " + str(12) + " " + str(31)
        rad.execute_cumulative_oconv(time, date, epweatherfile)
        #execute cumulative_rtrace
        rad.execute_cumulative_rtrace(str(2))#EXECUTE!! 
        #retrieve the results
        irrad_ress = rad.eval_cumulative_rad()
        #get the avg irrad_res on the roof
        
        '''
        eqn to calculate the energy produce by pv
        epv = apv*fpv*gt*nmod*ninv
        epv is energy produced by pv (kwh/yr)
        apv is area of pv (m2)
        fpv is faction of surface with active solar cells (ratio)
        gt is total annual solar radiation energy incident on pv (kwh/m2/yr)
        nmod is the pv efficiency (12%)
        ninv is the avg inverter efficiency (90%)
        '''
        apv = gml3dmodel.faces_surface_area(srf_list)
        fpv = 0.8
        gt = (sum(irrad_ress))/(float(len(irrad_ress)))
        nmod = 0.12
        ninv = 0.9
        epv = apv*fpv*gt*nmod*ninv
        '''
        pvrai
        '''  
        high_irrad = []
        high_irrad_faces = []
        
        irrad_cnt = 0
        for irrad_res in irrad_ress:
            if irrad_res>= irrad_threshold:
                high_irrad.append(irrad_res)
                #measure the area of the grid 
                high_irrad_faces.append(topo_list[irrad_cnt])
            irrad_cnt +=1
            
        total_area = gml3dmodel.faces_surface_area(srf_list)
        high_irrad_area = gml3dmodel.faces_surface_area(high_irrad_faces)
        pvai = (high_irrad_area/total_area) * 100
        
        return pvai, epv, irrad_ress, topo_list, high_irrad_area 
    
    def initialise_fai(self):
        
        if self.building_dictlist == None:
            self.initialise_occgeom()
            
        landuses = self.landuses
        building_dictlist = self.building_dictlist
        building_dictlist2 = building_dictlist[:]
        landuse_occpolygons = []
        buildings_on_plot_2dlist = []
        
        for landuse in landuses:
            pypolygonlist = self.citygml.get_pypolygon_list(landuse)
            for pypolygon in pypolygonlist:    
                landuse_occpolygon = py3dmodel.construct.make_polygon(pypolygon)
                if building_dictlist2:
                    buildings_on_plot = gml3dmodel.buildings_on_landuse(landuse_occpolygon, building_dictlist2)
                    
                    if buildings_on_plot:
                        buildings_on_plot_2dlist.append(buildings_on_plot)
                        landuse_occpolygons.append(landuse_occpolygon)
                        for abuilding in buildings_on_plot:
                            building_dictlist2.remove(abuilding)
        
        self.buildings_on_plot_2dlist = buildings_on_plot_2dlist
        self.landuse_occpolygons = landuse_occpolygons

    def fai(self, wind_dir):
        """
        Frontal Area Index (FAI)
        """
        if self.buildings_on_plot_2dlist == None:
            self.initialise_fai()
            
        print "DONE WITH INITIALISATION"
        landuse_occpolygons = self.landuse_occpolygons
        buidlings_on_plot_2dlist = self.buildings_on_plot_2dlist
        fai_list = []
        fuse_psrfs_list = []
        surfaces_projected_list = []
        lcnt = 0
        for landuse_occpolygon in landuse_occpolygons:
            facade_occpolygons = []
            for building in buidlings_on_plot_2dlist[lcnt]:
                occfacades = building["facade"]
                facade_occpolygons.extend(occfacades)
                        
            fai,fuse_psrfs, projected_faces, windplane, surfaces_projected = urbanformeval.frontal_area_index(facade_occpolygons, landuse_occpolygon, wind_dir)
            fai_list.append(fai)
            fuse_psrfs_list.extend(fuse_psrfs)
            surfaces_projected_list.extend(surfaces_projected)
            lcnt+=1
            
        avg_fai = sum(fai_list)/float(len(fai_list))
        return avg_fai, fuse_psrfs_list, surfaces_projected_list
        
    def rdi(self):
        """
        Route Directness Index
        """
        pass


#===================================================================================================================================================