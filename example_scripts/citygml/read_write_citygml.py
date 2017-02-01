import os
import time
import pyliburo
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir, os.pardir))
citygml_filepath = os.path.join(parent_path, "pyliburo_example_files", "shp2citygml_punggol_example", "citygml","punggol_citygml_asim_origlvl.gml")
result_citygml_filepath = os.path.join(parent_path, "pyliburo_example_files", "citygml","punggol_luse50_53.gml")

print "READING CITYGML FILE ... ..."
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
display_2dlist = []
colour_list = []
time1 = time.clock()
#===================================================================================================
#read the citygml file 
#===================================================================================================
read_citygml = pyliburo.pycitygml.Reader()
read_citygml.load_filepath(citygml_filepath)
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
    luse_lod = "lod1"
    luse_name = read_citygml.get_landuse_name(landuse)
    luse_function = read_citygml.get_landuse_function(landuse)
    luse_generic_attrib_dict = read_citygml.get_generic_attribs(landuse)
    
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
       
print "SORTING CITYGML FILE ... ..."
#===================================================================================================
#get a specific plot of landuse and the buildings on the plot
#===================================================================================================
indexes = [50,53]
landuses = [landuses[x] for x in indexes]

#find all the buildings inside the landuse 
bldgs_2_write = []
for landuse in landuses:
    bldgs_on_luse = pyliburo.gml3dmodel.buildings_on_landuse(landuse,buildings,read_citygml)
    bldgs_2_write.extend(bldgs_on_luse)

#===================================================================================================
#only write the specific plot and the buildings into a new citygml file
#write the citygml from scratch 
#===================================================================================================
print "WRITING CITYGML FILE ... ..."
citygml_writer = pyliburo.pycitygml.Writer()

for luse in landuses:
    cityobj = citygml_writer.create_cityobjectmember()
    cityobj.append(luse)
    citygml_writer.citymodelnode.append(cityobj)

for building in bldgs_2_write:
    cityobj = citygml_writer.create_cityobjectmember()
    cityobj.append(building)
    citygml_writer.citymodelnode.append(cityobj)
                   

citygml_writer.write(result_citygml_filepath)
time2 = time.clock()
time = (time2-time1)/60.0
print "TIME TAKEN", time
print "CITYGML FILE GENERATED"