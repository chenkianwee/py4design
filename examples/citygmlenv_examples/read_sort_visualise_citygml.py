import os
import time
import envuo

#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir))
citygml_filepath = os.path.join(parent_path, "punggol_case_study", "citygml", "punggol_citygml.gml")
result_citygml_filepath = os.path.join(parent_path, "punggol_case_study", "citygml", "punggol_variant.gml")

time1 = time.clock()
display_2dlist = []
#===================================================================================================
#read the citygml file 
#===================================================================================================
read_citygml = envuo.pycitygml.Reader(citygml_filepath)
buildings = read_citygml.get_buildings()
landuses = read_citygml.get_landuses()
stops = read_citygml.get_bus_stops()
roads = read_citygml.get_roads()
railways = read_citygml.get_railways()

#get all the polylines of the lod0 roads
for road in roads:
    polylines = read_citygml.get_linestring(road)

#get all the polygons of the landuses
for landuse in landuses:
    polygons = read_citygml.get_polygons(landuse)
    
#get all the stations in the buildings and extract their polygons 
stations = []
for building in buildings:
    bclass = building.find("bldg:class", namespaces=read_citygml.namespaces).text
    bfunction = building.find("bldg:function", namespaces=read_citygml.namespaces).text
    
    if bclass == "1170" and bfunction == "2480":
        stations.append(building)
    polygons = read_citygml.get_polygons(building)
    for polygon in polygons:
        polygon_id = polygon.attrib["{%s}id" % read_citygml.namespaces['gml']]
        pos_list = read_citygml.get_poslist(polygon)
        
#extract all the footprint of the buildings 
building_footprints = []
for building in buildings:
    footprint_dict = {}
    pypolygon_list = read_citygml.get_pypolygon_list(building)
    solid = envuo.interface2py3d.pypolygons2occsolid(pypolygon_list)
    face_list = envuo.py3dmodel.fetch.faces_frm_solid(solid)
    for face in face_list:
        normal = envuo.py3dmodel.calculate.face_normal(face)
        if normal == (0,0,-1):
            fpt_list = envuo.interface2py3d.pyptlist_frm_occface(face)
            
    footprint_dict["footprint"] = fpt_list
    footprint_dict["building"] = building
    building_footprints.append(footprint_dict)
    
#find all the buildings inside the landuse 
ldisplay_list = []
bdisplay_list = []
for landuse in landuses:
    lpolygon = read_citygml.get_polygons(landuse)[0]
    landuse_pts = read_citygml.polygon_2_pt_list(lpolygon)
    lface = envuo.py3dmodel.construct.make_polygon(landuse_pts)
    ldisplay_list.append(lface)
    buildings_on_plot_list = []
    
    for bf in building_footprints:
        fp = bf["footprint"]
        cbuilding = bf["building"]
        fface = envuo.py3dmodel.construct.make_polygon(fp)
        if envuo.py3dmodel.calculate.face_is_inside(fface, lface):
            buildings_on_plot_list.append(cbuilding)
    

    #get the solid of each building on the plot
    for building in buildings_on_plot_list:
        pypolgon_list = read_citygml.get_pypolygon_list(building)
        solid = envuo.interface2py3d.pypolygons2occsolid(pypolgon_list)
        bdisplay_list.append(solid)
 
    
time2 = time.clock()   
time = (time2-time1)/60.0
print "TIME TAKEN", time
print "VISUALISING"  
display_2dlist.append(ldisplay_list)
display_2dlist.append(bdisplay_list)
colour_list = ["WHITE", "WHITE"]
envuo.py3dmodel.construct.visualise(display_2dlist, colour_list)
