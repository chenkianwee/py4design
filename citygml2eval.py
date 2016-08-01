import os

from . import pycitygml
from . import py2radiance
from . import gml3dmodel
from . import interface2py3d

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
        #radiance parameters
        self.rad_base_filepath = os.path.join(os.path.dirname(__file__),'py2radiance','base.rad')
        self.sfgai_folderpath = os.path.join(os.path.dirname(self.citygmlfilepath), 'sgfai_data')
        self.dfai_folderpath = os.path.join(os.path.dirname(self.citygmlfilepath), 'dfai_data')
        self.rpvp_folderpath = os.path.join(os.path.dirname(self.citygmlfilepath), 'rpvp_data')
        self.solarxdim = None
        self.solarydim = None
        self.rad = None
        #rad results 
        self.irrad_results = None
        self.illum_results = None
        self.facade_grid_srfs = None

        
    def initialise_occgeom(self):
        buildings = self.buildings
        roof_list = []
        facade_list = []
        footprint_list = []
        for building in buildings:
            #get all the polygons from the building 
            pypolygonlist = self.citygml.get_pypolygon_list(building) 
            bsolid = interface2py3d.pypolygons2occsolid(pypolygonlist)
            #extract the polygons from the building and separate them into facade, roof, footprint
            facades, roofs, footprints = gml3dmodel.identify_building_surfaces(bsolid)
            facade_list.extend(facades)
            roof_list.extend(roofs)
            footprint_list.extend(footprints)
            
        self.facade_occfaces = facade_list
        self.roof_occfaces = roof_list
        self.footprint_occfaces = footprint_list
        
                
    def initialise_solar_analyse_facade(self, epweatherfile, xdim, ydim):
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
        rad = py2radiance.Rad(self.rad_base_filepath, self.sfgai_folderpath)
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
        self.rad = rad
        self.facade_grid_srfs = topo_list
        
    def sgfai(self, irrad_threshold, epweatherfile, xdim, ydim):
        """
        Solar Gain Facade Area Index (SGFAI) calculates the ratio of facade area that 
        receives irradiation below a specified level over the net facade area. 
        SGFAI is represented as an area ratio.
        """
        
        if self.rad == None:
            self.initialise_solar_analyse_facade(epweatherfile, xdim, ydim)
            
        elif (self.solarxdim, self.solarydim) != (xdim, ydim):
            self.solar_analyse_facade(epweatherfile, xdim, ydim)
        
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
        if self.rad == None:
            self.initialise_solar_analyse_facade(epweatherfile, xdim, ydim)
            
        elif (self.solarxdim, self.solarydim) != (xdim, ydim):
            self.solar_analyse_facade(epweatherfile, xdim, ydim)
            
        #execute cumulative oconv for the whole year
        rad = self.rad
        '''
        #once the geometries are created initialise daysim
        daysim_dir = self.dfai_folderpath
        rad.initialise_daysim(daysim_dir)
        #a 60min weatherfile is generated
        rad.execute_epw2wea(epweatherfile)
        rad.execute_radfiles2daysim()
        
        #create sensor points
 
        rad.write_default_radiance_parameters()#the default settings are the complex scene 1 settings of daysimPS
        rad.execute_gen_dc("w/m2")
        rad.execute_ds_illum()
        
        '''
        time = str(0) + " " + str(24)
        date = str(1) + " " + str(1) + " " + str(12) + " " + str(31)
        
        
        rad.execute_cumulative_oconv(time, date, epweatherfile, output = "illuminance")
        #execute cumulative_rtrace
        rad.execute_cumulative_rtrace(str(2))#EXECUTE!! 
        #retrieve the results
        illum_ress = rad.eval_cumulative_rad(output = "illuminance")
        facade_list = self.facade_occfaces
        topo_list = self.facade_grid_srfs
        high_illum = []
        high_illum_faces = []
        illum_cnt = 0
        for illum_res in illum_ress:
            if illum_res> daylight_threshold:
                high_illum.append(illum_res)
                #measure the area of the grid 
                high_illum_faces.append(topo_list[illum_cnt])
            illum_cnt +=1
            
        total_area = gml3dmodel.faces_surface_area(facade_list)
        high_illum_area = gml3dmodel.faces_surface_area(high_illum_faces)
        dfai = (high_illum_area/total_area) * 100
        
        self.illum_results = illum_ress
    
        #return topo_list, illum_ress, dfai
    
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
        rad = py2radiance.Rad(self.rad_base_filepath, self.rpvp_folderpath)
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
        
    def ptui(self):
        """
        Public Transport Usability Index (PTUI) is based on CASBEE calculation
        """
        pass

    def fai(self):
        """
        Frontal Area Index (FAI)
        """
        pass
#===================================================================================================================================================