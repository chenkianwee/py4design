import os

from . import pycitygml
from . import py2radiance
from . import gml3dmodel

class Evals(object):
    def __init__(self, citygmlfile):
        self.citygml = pycitygml.Reader(citygmlfile)
        self.citygmlfilepath = citygmlfile
        self.buildings = self.citygml.get_buildings()
        self.landuses = self.citygml.get_landuses()
        self.stops = self.citygml.get_bus_stops()
        self.roads = self.citygml.get_roads()
        self.railways = self.citygml.get_railways()

    #function to round the points
    def round_points(self,point_list):
        rounded =  []
        for point in point_list:
            rounded_pt = (round(point[0],5), round(point[1],5), round(point[2],5))
            rounded.append(rounded_pt)
        return rounded
        
    def building_solar(self, weatherfilepath, latitude, longtitude, meridian, start_mth,
                       end_mth, start_day, end_day, start_hour, end_hour, ab, xdim, ydim):
                           
        #parameters for the radiance 
        base_file_path = os.path.join(os.path.dirname(__file__),'py2radiance','base.rad')
        data_folder_path = os.path.join(os.path.dirname(self.citygmlfilepath), 'py2radiance_data')
        time = str(start_hour) + " " + str(end_hour)
        date = str(start_mth) + " " + str(start_day) + " " + str(end_mth) + " " + str(end_day)
        rad = py2radiance.Rad(base_file_path, data_folder_path)
        
        buildings = self.buildings
        
        topo_list = []
        sensor_pts = []
        sensor_dirs = []
        
        bcnt = 0
        for building in buildings:
            #extract the polygons from the building generate sensor pts, sensor_pts_dir and sensor_srf with it 
            b_sensor_pts, b_sensor_dirs, b_sensor_srfs = gml3dmodel.generate_sensor_surfaces_for_building(building, self.citygml, xdim, ydim)
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
        
        #execute radiance cumulative oconv (will create input files for sky and geometry)
        rad.execute_cumulative_oconv(time, date, weatherfilepath)#EXECUTE
                                     
        #execute cumulative_rtrace
        rad.execute_cumulative_rtrace(str(ab))#EXECUTE!! 
        #retrieve the results
        irrad_res = rad.eval_cumulative_rad()
        return topo_list, irrad_res
            
    def trpst_usability(self):
        pass

    def fai(self):
        pass
#===================================================================================================================================================