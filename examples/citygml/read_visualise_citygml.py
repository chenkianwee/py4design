import os
import time
import pyliburo

#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir))
citygml_filepath = os.path.join(parent_path, "example_files", "citygml", "punggol_luse50_53.gml" )

#or just insert a citygml file you would like to analyse here 
'''citygml_filepath = "C://file2analyse.gml"'''
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
time1 = time.clock()
display_2dlist = []
colour_list = []
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

print "nbuildings:", len(buildings)

#get all the polylines of the lod0 roads
road_occedges = []
for road in roads:
    polylines = read_citygml.get_pylinestring_list(road)
    for polyline in polylines:
        occ_wire = pyliburo.py3dmodel.construct.make_wire(polyline)
        edge_list = pyliburo.py3dmodel.fetch.geom_explorer(occ_wire, "edge")
        road_occedges.extend(edge_list)

#get all the polygons of the landuses
for landuse in landuses:
    polygons = read_citygml.get_polygons(landuse)
    
#get all the stations in the buildings and extract their polygons 
stations = []
for building in buildings:
    polygons = read_citygml.get_polygons(building)
    for polygon in polygons:
        polygon_id = polygon.attrib["{%s}id" % read_citygml.namespaces['gml']]
        pos_list = read_citygml.get_poslist(polygon)
        
edgedisplay_list = []
bdisplay_list = []
#extract all the footprint of the buildings 
for building in buildings:
    pypolgon_list = read_citygml.get_pypolygon_list(building)
    solid = pyliburo.py3dmodel.construct.make_occsolid_frm_pypolygons(pypolgon_list)
    edgelist = pyliburo.py3dmodel.fetch.geom_explorer(solid, "edge")
    bdisplay_list.append(solid)
    edgedisplay_list.extend(edgelist)
    

ldisplay_list = []

for landuse in landuses:
    lpolygons = read_citygml.get_polygons(landuse)
    if lpolygons:
        lpolygon = read_citygml.get_polygons(landuse)[0]
        landuse_pts = read_citygml.polygon_2_pt_list(lpolygon)
        lface = pyliburo.py3dmodel.construct.make_polygon(landuse_pts)
        fedgelist = pyliburo.py3dmodel.fetch.geom_explorer(lface, "edge")
        edgedisplay_list.extend(fedgelist)
        ldisplay_list.append(lface)
    
time2 = time.clock()   
time = (time2-time1)/60.0
print "TIME TAKEN", time
print "VISUALISING"  

display_2dlist.append(ldisplay_list)
display_2dlist.append(bdisplay_list)
display_2dlist.append(edgedisplay_list)
display_2dlist.append(road_occedges)
colour_list.append('WHITE')
colour_list.append('WHITE')
colour_list.append('BLACK')
colour_list.append('BLACK')
pyliburo.py3dmodel.construct.visualise(display_2dlist, colour_list)
