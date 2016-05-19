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
        #radiance and daysim parameters
        self.rad_base_filepath = os.path.join(os.path.dirname(__file__),'py2radiance','base.rad')
        self.radiance_folderpath = os.path.join(os.path.dirname(self.citygmlfilepath), 'py2radiance_data')
        self.daysim_folderpath = os.path.join(os.path.dirname(self.citygmlfilepath), 'daysim_data')
                
    def sgfai(self, irrad_threshold, epweatherfile, xdim, ydim):
        """
        Solar Gain Facade Area Index (SGFAI) calculates the ratio of facade area that 
        receives irradiation below a specified level over the net facade area. 
        SGFAI is represented as an area ratio.
        """
        
        #initialise py2radiance 
        rad = py2radiance.Rad(self.rad_base_filepath, self.radiance_folderpath)
        
        buildings = self.buildings
        topo_list = []
        sensor_pts = []
        sensor_dirs = []
        
        bcnt = 0
        for building in buildings:
            #extract the polygons from the building generate sensor pts, sensor_pts_dir and sensor_srf with it 
            b_sensor_pts, b_sensor_dirs, b_sensor_srfs = gml3dmodel.generate_sensor_pts_4_building_facades(building, self.citygml, xdim, ydim)
            sensor_pts.extend(b_sensor_pts)
            sensor_dirs.extend(b_sensor_dirs)
            topo_list.extend(b_sensor_srfs)
                     
            #extract the surfaces from the buildings for shading geometry in radiance
            polygons = self.citygml.get_polygons(building)     
            for polygon in polygons:
                #TODO: need to account for polygons with holes
                #get all the polygons into a list
                a_polygon = self.citygml.polygon_2_pt_list(polygon)
                del a_polygon[-1]
                #extract the shading geometry 
                srfname = polygon.attrib["{%s}id" % self.citygml.namespaces['gml']]
                #just use pure white paint
                srfmat = "RAL9010_pur_white_paint"
                py2radiance.RadSurface(srfname, a_polygon, srfmat, rad)
                
            bcnt +=1
            
        #get the sensor grid points
        rad.set_sensor_points(sensor_pts, sensor_dirs)
        rad.create_sensor_input_file()
        #create the geometry files
        rad.create_rad_input_file()
        #execute cumulative_rtrace
        rad.execute_cumulative_rtrace(str(2))#EXECUTE!! 
        #retrieve the results
        irrad_res = rad.eval_cumulative_rad()
        return topo_list, irrad_res
        
    def dfai(self, daylight_threshold, time_percentage):
        """
        Daylighting Facade Area Index (DFAI) calculates the ratio of facade area that 
        receives daylighting above a specified level, 
        above a specified percentage of the annual daytime hours
        over the net facade area. 
        DFAI is represented as an area ratio.
        """
        pass
    
    def rpvp(self):
        """
        Roof PV Potential (RPVP) calculates the potential electricity 
        that can be generated on the roof of buildings annually.
        RPVP is represented in Wh.
        
        #parameters for the radiance 
        base_file_path = os.path.join(os.path.dirname(__file__),'py2radiance','base.rad')
        data_folder_path = os.path.join(os.path.dirname(self.citygmlfilepath), 'py2radiance_data')
        time = str(start_hour) + " " + str(end_hour)
        date = str(start_mth) + " " + str(start_day) + " " + str(end_mth) + " " + str(end_day)
        rad = py2radiance.Rad(base_file_path, data_folder_path)
        
        buildings = self.buildings
                   
        
        """
        pass
            
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