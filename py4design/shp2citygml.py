# ==================================================================================================
#
#    Copyright (c) 2016, Chen Kian Wee (chenkianwee@gmail.com)
#
#    This file is part of py4design
#
#    py4design is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    py4design is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with py4design.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================
import re
import uuid
import shapefile

import pycitygml
import py3dmodel
import gml3dmodel

#=========================================================================================================================================
#NUMERIC AND STRING INPUTS
#=========================================================================================================================================
def map_osm2citygml_landuse_function(landuse):
    """
    This function maps these landuse to the gml function codes.
 
    Parameters
    ----------
    landuse : str
        The landuse to be mapped. Options: "residential", "transport", "recreation_ground", "education", "commercial", "civic", "mixed", "place_of_worship", "reserve", "utility", "health".
    
    Returns
    -------        
    gml function code : str
        The code of the gml landuse function.
    """
    if landuse == "residential":
        #residential
        function = "1010"
    if landuse == "transport":
        #special function area
        function = "1040"
    if landuse == "recreation_ground":
        #Sports, leisure and recreation
        function = "1130"
    if landuse == "education":
        #special function area
        function = "1040"
    if landuse == "commercial":
        #Industry and Business
        function = "1020"
    if landuse == "civic":
        #special function area
        function = "1040"
    if landuse == "mixed":
        #MIxed use
        function = "1030"
    if landuse == "place_of_worship":
        #special function area
        function = "1040"
    if landuse == "reserve":
        #special function area
        function = "1040"
    if landuse == "utility":
        #special function area
        function = "1040"
    if landuse == "health":
        #special function area
        function = "1040"
    else:
        #special function area
        function = "1040"
    return function

def map_osm2citygml_building_class(bldg_class):
    """
    This function maps these building class to the gml function codes.
 
    Parameters
    ----------
    bldg_class : str
        The class to be mapped. Options: "residential", "transport", "recreation_ground", "education", "commercial", "civic", "mixed", "place_of_worship", "reserve", "utility", "health".
    
    Returns
    -------        
    gml function code : str
        The code of the gml class.
    """
    if bldg_class == "residential":
        #habitation
        bclass = "1000"
    elif bldg_class == "transport":
        #traffic area
        bclass = "1170"
    elif bldg_class == "recreation_ground":
        #recreation
        bclass = "1050"
    elif bldg_class == "education":
        #schools education research 
        bclass = "1100"
    elif bldg_class == "commercial":
        #business trade
        bclass = "1030"
    elif bldg_class == "civic":
        #administration
        bclass = "1020"
    elif bldg_class == "mixed":
        #habitation
        bclass = "1000"
    elif bldg_class == "place_of_worship":
        #church instituition
        bclass = "1080"
    elif bldg_class == "reserve":
        #function
        bclass = "1180"
    elif bldg_class == "utility":
        #function
        bclass = "1180"
    elif bldg_class == "health":
        #healthcare
        bclass = "1120"
    else:
        bclass = "1180"
    return bclass

def map_osm2citygml_building_function(bldg_function):
    """
    This function maps these building function to the gml function codes.
 
    Parameters
    ----------
    bldg_function : str
        The function to be mapped. Options: "residential", "transport", "recreation_ground", "education", "commercial", "civic", "mixed", "place_of_worship", "reserve", "utility", "health".
    
    Returns
    -------        
    gml function code : str
        The code of the gml function.
    """
    if bldg_function == "residential":
        #residential building
        function = "1000"
    elif bldg_function == "transport":
        #others
        function = "2700"
    elif bldg_function == "recreation_ground":
        #others
        function = "2700"
    elif bldg_function == "education":
        #building for education and research
        function = "2070"
    elif bldg_function == "commercial":
        #business building
        function = "1150"
    elif bldg_function == "civic":
        #public building
        function = "1960"
    elif bldg_function == "mixed":
        #residential and commercial building
        function = "1080"
    elif bldg_function == "place_of_worship":
        #place of worship
        function = "2260"
    elif bldg_function == "reserve":
        #others
        function = "2700"
    elif bldg_function == "utility":
        #others
        function = "2700"
    elif bldg_function == "health":
        #building for health care
        function = "2300"
    else:
        function = "2700"
    return function

def map_osm2citygml_building_amenity_function(amenity):
    """
    This function maps these amenity to the gml function codes.
 
    Parameters
    ----------
    amenity : str
        The amenity to be mapped. Options: "parking".
        
    Returns
    -------        
    gml function code : str
        The code of the gml amenity function.
    """
    if amenity == "parking":
        #multi storey car park
        function = "1610"
    else:
        #others
        function = "2700"
    return function

def map_osm2citygml_trpst_complex_class(trpst):
    """
    This function maps these transportation to the gml function codes.
 
    Parameters
    ----------
    trpst : str
        The transport to be mapped. Options: "subway", "light_rail", "unclassified", "tertiary", "service", "secondary_link", "secondary", "residential", "primary", "motoway_link", "motorway",
        "construction".
        
    Returns
    -------        
    gml function code : str
        The code of the gml amenity function.
    """
    if trpst == "subway":
        #subway
        tclass = "1080"
        
    if trpst == "light_rail":
        #rail_traffic
        tclass = "1060"
        
    if trpst == "unclassified" or trpst == "tertiary" or\
    trpst == "service" or trpst == "secondary_link" or trpst == "secondary" or\
    trpst == "residential" or trpst == "primary" or trpst == "motorway_link" or trpst == "motorway" or trpst == "construction" :
        #road_traffic
        tclass = "1040"
    else:
        #others
        tclass = "1090"
        
    return tclass

def map_osm2citygml_trpst_complex_function(trpst):
    """
    This function maps these transportation complex to the gml function codes.
 
    Parameters
    ----------
    trpst : str
        The transport to be mapped. Options: "subway", "light_rail", "unclassified", "tertiary", "service", "secondary_link", "secondary", "residential", "primary", "motoway_link", "motorway",
        "construction", "track", "steps", "path", "footway", "cycleway".
        
    Returns
    -------        
    gml function code : str
        The code of the gml amenity function.
    """
    if trpst == "subway":
        #subway
        function = "1825"
    if trpst == "light_rail":
        #rail transport
        function = "1800"
    if trpst == "unclassified" or trpst == "tertiary" or\
    trpst == "service" or trpst == "secondary_link" or trpst == "secondary" or\
    trpst == "residential" or trpst == "primary" or trpst == "motorway_link" or trpst == "motorway" or trpst == "construction" :
        #road
        function = "1000"
    if trpst == "track":
        #hiking trail
        function = "1230"
    if trpst == "steps" or trpst == "path" or trpst == "footway":
        #footpath/footway
        function = "1220"
    if trpst == "cycleway":
        #bikeway/cyclepath
        function = "1240"
    else:
        #others
        function = "2700"
    return function

def calc_residential_parking_area(total_build_up):
    """
    This function calculates the parking area required based on the built up area.
 
    Parameters
    ----------
    total_build_up : float
        The total built up area.
        
    Returns
    -------        
    the parking area : float
        The calculated parking area.
    """
    #TODO: verify the carpark calculation
    #base on the building footprint estimate how high the multistorey carpark should be
    hsehold_size = 3.43 #based on census data
    avg_hse_size = 87.4 #based on census data
    num_of_hse = total_build_up/avg_hse_size
    plot_pop_size = num_of_hse * hsehold_size
    #car_ownership = 9.4 #cars/100persons
    #plot_car_pop = car_ownership*(plot_pop_size/100)
    motorbike_ownership = 2.6 #motobikes/100persons
    plot_bike_pop = motorbike_ownership*(plot_pop_size/100)
    parking_lot_size = 2.4*4.8 #m2
    motorbike_lot_size = 1*2.5 #m2
    total_carlot_size = num_of_hse*parking_lot_size #m2 minimum provision is one car for a house
    total_bikelot_size = plot_bike_pop*motorbike_lot_size #m2
    total_parklot_size = total_carlot_size + total_bikelot_size + (total_carlot_size*1) #(factoring in the aisle and ramps is in ratio 1:2 of the parking lot) #m2
    return total_parklot_size

#=========================================================================================================================================
#SHAPEFILE INPUTS
#=========================================================================================================================================
def get_buildings(shpfile):
    """
    This function get all the building polygons in this shapefile and convert them into a dictionary format.
 
    Parameters
    ----------
    shpfile : str
        The file path of the shape file.
        
    Returns
    -------        
    list of building dictionary : list of dictionary
        The list of building dictionary that documents all the information from the shape file. Each dictionary has this information:
        building_dictionary = {"building": string describing the building,  "geometry": OCCface list, "amenity": amenity string, "parking": parking string, "name": building name string, 
        "building_l": number of building level int}
    """
    building_list = []
    sf = shapefile.Reader(shpfile)
    shapeRecs=sf.shapeRecords()
    shapetype = shapeRecs[0].shape.shapeType
    
    #shapetype 1 is point, 3 is polyline, shapetype 5 is polygon
    if shapetype ==5:
        field_name_list = get_field_name_list(sf)
        
        #the attributes are mainly base on the attributes from osm 
        building_index = field_name_list.index("building")-1
        amenity_index = field_name_list.index("amenity")-1
        parking_index = field_name_list.index("parking")-1
        name_index = field_name_list.index("name")-1
        building_l_index = field_name_list.index("building_l")-1
        id_index = field_name_list.index("id")-1
        
        for rec in shapeRecs:
            poly_attribs=rec.record
            building = poly_attribs[building_index]
            building.strip()
            
            #if the polygon has a building attribute it is a building footprint
            if building != "":
                building_dict = {}
                #get the geometry of the building footprint
                geom = get_geometry(rec)
                #only create a building if the records have geometry information
                if geom:
                    building_dict["building"] = building
                    pypolygon_list3d = pypolygon_list2d_2_3d(geom, 0.0)
                    face_list = shp_pypolygon_list3d_2_occface_list(pypolygon_list3d)
                        
                    building_dict["geometry"] = face_list
                    
                    amenity = poly_attribs[amenity_index]
                    amenity.strip()
                    if not amenity.isspace():
                        building_dict["amenity"] = amenity
                        
                    parking = poly_attribs[parking_index]
                    parking.strip()
                    if not parking.isspace():
                        building_dict["parking"] = parking
                        
                    name = poly_attribs[name_index]
                    name.strip()
                    if not name.isspace():
                        building_dict["name"] = name
                        
                    building_l = poly_attribs[building_l_index]
                    building_l.strip()
                    if not building_l.isspace():
                        try:
                            building_dict["building_l"] = int(building_l)
                        except:
                            pass
                            
                    building_list.append(building_dict)
                    
                    id_ = poly_attribs[id_index]
                    if id_:
                        building_dict["id"] = id_
                
    return building_list

def terrain2d23d_tin(terrain_shpfile, elev_attrib_name):
    """
    This function generate a TIN from a terrain shpfile that is polygonised.
 
    Parameters
    ----------
    terrain_shpfile : str
        The file path of the terrain shape file.
        
    elev_attrib_name : str
        The name of the attribute that documents the height of each polygon.
        
    Returns
    -------        
    triangle surfaces : list of OCCfaces
        The triangle TIN faces.
    """
    sf = shapefile.Reader(terrain_shpfile)
    shapeRecs=sf.shapeRecords()
    shapetype = shapeRecs[0].shape.shapeType
    if shapetype !=5:
        raise Exception("this is not a polygonised shpfile")
        
    field_name_list = get_field_name_list(sf)
    elev_index = field_name_list.index(elev_attrib_name)-1
    elev_pts = []

    for rec in shapeRecs:
        poly_attribs=rec.record
        elev = poly_attribs[elev_index]
        part_list = get_geometry(rec)
        #if it is a close the first and the last vertex is the same
        if elev:
            for part in part_list:
                point_list = pypt_list2d_2_3d(part, elev)
                face = py3dmodel.construct.make_polygon(point_list)
                face_midpt = py3dmodel.calculate.face_midpt(face)
                elev_pts.append(face_midpt)
            
    occtriangles = py3dmodel.construct.delaunay3d(elev_pts)
    return occtriangles
    
def terrain2d23d_contour_line(terrain_shpfile, elev_attrib_name):
    """
    This function extrude each polygon according to its elevation attribute.
 
    Parameters
    ----------
    terrain_shpfile : str
        The file path of the terrain shape file.
        
    elev_attrib_name : str
        The name of the attribute that documents the height of each polygon.
        
    Returns
    -------        
    solids : list of OCCsolids
        The extruded polygons.
        
    faces : list of OCCfaces
        The faces of the polygons.
    """
    sf = shapefile.Reader(terrain_shpfile)
    shapeRecs=sf.shapeRecords()
    #shapeRecs = shapeRecs[0:10]
    shapetype = shapeRecs[0].shape.shapeType
    if shapetype !=5:
        raise Exception("this is not a polygonised shpfile")
        
    field_name_list = get_field_name_list(sf)
    dn_index = field_name_list.index(elev_attrib_name)-1
    face_list = []
    elev_dict = {}
    for rec in shapeRecs:
        poly_attribs=rec.record
        elev = round(poly_attribs[dn_index], -1)
        if elev not in elev_dict:
            elev_dict[elev] = []
        part_list = get_geometry(rec)
        #if it is a close the first and the last vertex is the same
        for part in part_list:
            point_list = pypt_list2d_2_3d(part, elev)
            face = py3dmodel.construct.make_polygon(point_list)
            elev_dict[elev].append(face)
            
    for key in elev_dict:
        elev_faces = elev_dict[key]
        merged_faces = py3dmodel.construct.merge_faces(elev_faces)
        face_list.extend(merged_faces)
        
    solid_list = []
    for face in face_list:
        ext_shp = py3dmodel.construct.extrude(face, (0,0,-1), 10)
        ext_solid = py3dmodel.fetch.topo2topotype(ext_shp)
        solid_list.append(ext_solid)
        
    return solid_list, face_list

def building2d23d(building_shpfile, height_attrib_name, terrain_surface_list):
    """
    This function extrude each building and place them on the terrain.
 
    Parameters
    ----------
    building_shpfile : str
        The file path of the building shape file.
        
    height_attrib_name : str
        The name of the attribute that documents the building height.
    
    terrain_surface_list : list of OCCfaces
        The TIN of the terrain. Each OCCface is triangular.
        
    Returns
    -------        
    list of extruded buildings : list of OCCsolids
        The extruded buildings.
    """
    sf = shapefile.Reader(building_shpfile)
    shapeRecs=sf.shapeRecords()
    shapetype = shapeRecs[0].shape.shapeType
    if shapetype !=5:
        raise Exception("this is not a polygon building shpfile")
        
    field_name_list = get_field_name_list(sf)
    height_index = field_name_list.index(height_attrib_name)-1
    
    terrainshell = py3dmodel.construct.sew_faces(terrain_surface_list)
    terrain_z = []
    for ts in terrain_surface_list:
        vertexes = py3dmodel.fetch.points_frm_occface(ts)
        for vert in vertexes:
            z = vert[2]
            terrain_z.append(z)
            
    max_z = max(terrain_z)
    min_z = min(terrain_z)
    
    solid_list = []
    for rec in shapeRecs:
        poly_attribs=rec.record
        height = float(poly_attribs[height_index])
        part_list = get_geometry(rec)
        #if it is a close the first and the last vertex is the same
        pypolgyonlist = pypolygon_list2d_2_3d(part_list, (min_z-10))
        face = py3dmodel.construct.make_occfaces_frm_pypolygons(pypolgyonlist)[0]
        #create a bounding box to boolean the terrain
        bbox = py3dmodel.construct.extrude(face, (0,0,1), (max_z+10))
        bbox_terrain = py3dmodel.fetch.topo2topotype(py3dmodel.construct.boolean_common(bbox,terrainshell))
        #extract the terrain from in the bbox
        if not py3dmodel.fetch.is_compound_null(bbox_terrain):
            bbox_faces = py3dmodel.fetch.topos_frm_compound(bbox_terrain)["face"]
            midpt_zs = []
            for bbox_face in bbox_faces:
                bbox_face_midptz = py3dmodel.calculate.face_midpt(bbox_face)[2]
                midpt_zs.append(bbox_face_midptz)
            belev = max(midpt_zs)
        else:
            belev = 0

        pypolgyonlist3d = pypolygon_list2d_2_3d(part_list, belev)
        face3d = py3dmodel.construct.make_polygon(pypolgyonlist3d)
        building_extrude_shp = py3dmodel.construct.extrude(face3d, (0,0,1), height)
        building_extrude_solid = py3dmodel.fetch.topo2topotype(building_extrude_shp)
        solid_list.append(building_extrude_solid)

    return solid_list

def get_shpfile_epsg(shpfile):
    """
    This function gets the epsg of the shape file.
 
    Parameters
    ----------
    shpfile : str
        The file path of the shape file.
        
    Returns
    -------        
    epsg : str
        The epsg of the shape file.
    """
    #read the qpj file and find out wat epsg is the file base on 
    qpj_filepath = shpfile.replace(".shp", ".qpj")
    qpj = open(qpj_filepath, "r")
    epsg_num = qpj.read().split(",")[-1]
    m = re.search('"(.+?)"', epsg_num)
    if m:
        epsg = m.group(1)
    else:
        epsg = ""
    return epsg

def get_field_name_list(sf):
    """
    This function gets all the attribute names of the shapefile.
 
    Parameters
    ----------
    sf : shapefile.Reader() class instance
        The reader class instance of a shape file.
        
    Returns
    -------        
    list of attribute names : list of str
        The list of attribute names in the shape file.
    """
    fields = sf.fields
    field_name_list = []
    for field in fields:
        field_name_list.append(field[0])
    return field_name_list
            
def get_geometry(shape_record):
    """
    This function gets all the geometry in the shape record.
 
    Parameters
    ----------
    shape_record : list of shapefile.Reader().shapeRecords()
        The shape records for extraction of geometry.
        
    Returns
    -------        
    list of geometries : pypolygonlist (polygon and polylines shape file) or pyptlist (point shape file)
        Pypolygon_list is a 2d list of tuples.
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z). 
        A pypolygon or pyptlist is a list of pypt e.g. [(x1,y1,z1), (x2,y2,z2), ...].
        A pypolygon_list is a 2d list of tuples e.g. [[(x11,y11,z11), (x12,y12,z12), ...], [(x21,y21,z21), (x22,y22,z22), ...], ...]
    """
    #takes in a single shape record and extract the parts and point of a shape file
    part_list = []
    shape = shape_record.shape
    shapetype = shape.shapeType
    if shapetype == 5 or shapetype == 3:
        #A ring is a connected sequence of four or more
        #points that form a closed, non-self-intersecting loop
        #The rings of a polygon are referred to as its parts
        parts=shape.parts
        
        num_parts=len(parts)
        points=shape.points
        count_parts=0
        for part in parts:
            part_s = parts[count_parts]
            if count_parts==num_parts-1:
                part_e=len(points)
            else:
                part_e=parts[count_parts+1]
            part_points=points[part_s:part_e]
            part_list.append(part_points)
            count_parts+=1
        return part_list
    if shapetype == 1:
        points=shape.points
        return points
         
def buildings_on_plot(plot_rec, building_dict_list):
    """
    This function identify the buildings that is on this landuse plot.
 
    Parameters
    ----------
    plot_rec : shapefile.Reader().shapeRecords()
        The plot shape record.
    
    building_dict_list : list of dictionaries
        The building to be identified. The list of dictionary is generated from the function get_buildings().
        
    Returns
    -------        
    buildings on plot : list of dictionaries
        The building dictionary that are on the plot.
               
    """
    #building_list is a list of dictionary from method get_buildings(shpfile)
    #check which building belongs to this plot
    buildings_on_plot_list = []
    part_list = get_geometry(plot_rec)
    if part_list:
        for part in part_list:
            part3d = pypt_list2d_2_3d(part,0.0)
            luse_face = py3dmodel.construct.make_polygon(part3d)
    
            for building in building_dict_list:
                geometry_list = building["geometry"]
                for building_face in geometry_list:
                    face_inside = face_almost_inside(building_face, luse_face)
                    if face_inside:
                        buildings_on_plot_list.append(building)
                    
    return buildings_on_plot_list

def get_plot_area(plot_rec):
    """
    This function calculate the plot area.
 
    Parameters
    ----------
    plot_rec : A shapefile.Reader().shapeRecords()
        The plot shape record.
        
    Returns
    -------        
    area : float
        The plot area (m2).
               
    """
    plot_area = 0
    part_list = get_geometry(plot_rec)
    if part_list:
        for part in part_list:
            ptlist3d = pypt_list2d_2_3d(part,0.0)
            luse_face = py3dmodel.construct.make_polygon(ptlist3d)
            plot_area = plot_area + py3dmodel.calculate.face_area(luse_face)
    return plot_area

def trpst2citygml(trpt_type, rec, name, trpst_attrib, generic_attrib_dict, citygml_writer):
    """
    This function converts records from the shapefile into transportation GML.
 
    Parameters
    ----------
    trpt_type : str
        The transportation type. The options are: "Road", "Railway", "Track", "Square".
    
    plot_rec : A shapefile.Reader().shapeRecords()
        The shape record of the roads, must be a polyline shape file.
        
    name : str
            The name of the transportation object.
    
    trpst_attrib : str
        The class/function of the transportation. Options: "subway", "light_rail", "unclassified", "tertiary", "service", "secondary_link", "secondary", "residential", "primary", "motoway_link", "motorway",
        "construction".
        
    generic_attrib_dict : dictionary, optional
        Extra attributes to be appended to the object, Default = None.
        The dictionary must have a string key which will be the name of the generic attributes, and either an int, float or str value.
        
    citygml_writer : Pycitygml.Writer() class instance
        The writer is used to write information to the GML transportation.
               
    """
    if name.isspace():
        name = trpst_attrib + str(uuid.uuid1())
    trpst_class = map_osm2citygml_trpst_complex_class(trpst_attrib)
    function = map_osm2citygml_trpst_complex_function(trpst_attrib)
    #get the geometry
    part_list = get_geometry(rec)
    geometry_list = []
    for part in part_list:
        linestring = pycitygml.LineString(pypt_list2d_2_3d(part,0.0))
        geometry_list.append(linestring)
        
    citygml_writer.add_transportation(trpt_type, "lod0", name, geometry_list, rd_class = trpst_class, 
                               function = function, generic_attrib_dict = generic_attrib_dict)

#=========================================================================================================================================
#DICTIONARY INPUT
#=========================================================================================================================================
def building2citygml(building_dict, height, citygml_writer, building_function, storey):
    """
    This function converts the building dictionariesinto building GML.
 
    Parameters
    ----------
    building_dict : dictionary
        The building to be converted. The dictionary is generated from the function get_buildings().
    
    height : float
        The building height.
        
    citygml_writer : Pycitygml.Writer() class instance
        The writer is used to write information to the GML transportation.
        
    name : str
            The name of the transportation object.
    
    building_function : str
        The class/function of the building. Options: Options: "residential", "transport", "recreation_ground", "education", "commercial", "civic", "mixed", "place_of_worship", "reserve", "utility", "health".
        
    storey : int
        The number of storeys of the building.
    """
    storey_blw_grd = "0"
    bclass = map_osm2citygml_building_class(building_function)
    if "name" in building_dict:
        name = building_dict["name"]
    else:
        name = "building" + str(uuid.uuid1())
        
    if "amenity" in building_dict:
        function = map_osm2citygml_building_amenity_function(building_dict["amenity"])
    else:
        function = map_osm2citygml_building_function(building_function)
        
    generic_attrib_dict = {"landuse":building_function}
    if "amenity" in building_dict:
        generic_attrib_dict["amenity"] = building_dict["amenity"]
        
    if "parking" in building_dict:
        generic_attrib_dict["parking"] = building_dict["parking"]

    bgeom_list = building_dict["geometry"]
    for bface in bgeom_list:
        #extrude the buildings according to their height
        face_list = extrude_building_n_fetch_faces(bface, height)
        geometry_list = gml3dmodel.write_gml_srf_member(face_list)
        
    citygml_writer.add_building("lod1", name,geometry_list, bldg_class = bclass, function = function, usage = function,
                         rooftype = "1000", height = str(height),
                         stry_abv_grd = str(storey), stry_blw_grd = storey_blw_grd, generic_attrib_dict = generic_attrib_dict)

#=========================================================================================================================================
#GEOMETRY INPUTS
#=========================================================================================================================================
def pypt2d_2_3d(pypt2d, z):
    """
    This function converts the pypt 2d to pypt 3d.
 
    Parameters
    ----------
    pypt2d : pypt2d
        The pypt2d to be converted. A pypt2d is a tuple that documents the xy coordinates of a pt e.g. (x,y). 
    
    z : float
        The z-value of pypt3d
        
    Returns
    -------        
    pypt3d : pypt
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z). 
    """
    pypt3d = (pypt2d[0],pypt2d[1],z)
    return pypt3d

def pypt_list2d_2_3d(pypt_list2d, z):
    """
    This function converts a list of pypt 2d to a list of pypt 3d.
 
    Parameters
    ----------
    pypt_list2d : pypt2d
        The list pypt2d to be converted. A pypt2d is a tuple that documents the xy coordinates of a pt e.g. (x,y). A list of pypt2d is [(x1,y1), (x2,y2), ...]
    
    z : float
        The z-value of pypt3d
        
    Returns
    -------        
    list of pypt3d : pyptlist
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z). A pyptlist is a list of pypt e.g. [(x1,y1,z1), (x2,y2,z2), ...].
    """
    pypt_list3d = []
    for pt in pypt_list2d:
        pt3d = pypt2d_2_3d(pt, z)
        pypt_list3d.append(pt3d)
        
    return pypt_list3d
    
def pypolygon_list2d_2_3d(pypolygon_list2d, z):
    """
    This function converts a list of pypolygon 2d to a list of pypolygon 3d.
 
    Parameters
    ----------
    pypolygon_list2d : pypolygon_list2d
        The list pypolgon 2d to be converted. A pypolygon_list2d is a 2d list of tuples e.g. [[(x11,y11), (x12,y12), ...], [(x21,y21), (x22,y22), ...], ...]
    
    z : float
        The z-value of pypolygon3d
        
    Returns
    -------        
    list of pypolygon3d : pypolygon_list
        A pypolygon_list is a 2d list of tuples e.g. [[(x11,y11,z11), (x12,y12,z12), ...], [(x21,y21,z21), (x22,y22,z22), ...], ...]
    """
    pypolygon_list3d = []
    for pypolygon in pypolygon_list2d:
        pypt_list3d = pypt_list2d_2_3d(pypolygon,z)
        pypolygon_list3d.append(pypt_list3d)
    return pypolygon_list3d

def shp_pypolygon_list3d_2_occface_list(pypolygon_list):
    """
    This function converts a pypolygon_list to list of OCCfaces.
 
    Parameters
    ----------
    pypolygon_list : pypolygon_list
        Pypolygon_list is a 2d list of tuples.
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z). 
        A pypolygon or pyptlist is a list of pypt e.g. [(x1,y1,z1), (x2,y2,z2), ...].
        A pypolygon_list is a 2d list of tuples e.g. [[(x11,y11,z11), (x12,y12,z12), ...], [(x21,y21,z21), (x22,y22,z22), ...], ...]
        
    Returns
    -------        
    list of faces : list of OCCfaces
        A list of OCCfaces.        
    """
    clockwise = []
    anti_clockwise = []#hole
    for pyptlist in pypolygon_list:
        is_anti_clockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, (0,0,1))
        if is_anti_clockwise:
            anti_clockwise.append(pyptlist)
        else:
            clockwise.append(pyptlist)
            
    nholes = len(anti_clockwise)
    if nholes > 0:
        occface_list_holes = py3dmodel.construct.make_occfaces_frm_pypolygons(anti_clockwise)
        occface_list = py3dmodel.construct.make_occfaces_frm_pypolygons(clockwise)
        
        hole_solid_list = []
        for hole in occface_list_holes:
            hole_midpt = py3dmodel.calculate.face_midpt(hole)
            hole_solid = py3dmodel.construct.extrude(hole,(0,0,1),1)
            hole_midpt_mv = py3dmodel.modify.move_pt(hole_midpt, (0,0,-1), 0.5)
            hole_solid_mv = py3dmodel.modify.move(hole_midpt, hole_midpt_mv, hole_solid)
            hole_solid_list.append(hole_solid_mv)
            
        occface_list_cmpd = py3dmodel.construct.make_compound(occface_list)
        hole_solid_list_cmpd = py3dmodel.construct.make_compound(hole_solid_list)
        diff_cmpd = py3dmodel.construct.boolean_difference(occface_list_cmpd, hole_solid_list_cmpd)
        diff_occface_list = py3dmodel.fetch.topo_explorer(diff_cmpd, "face")
        return diff_occface_list
    else:
        occface_list = py3dmodel.construct.make_occfaces_frm_pypolygons(clockwise)
        return occface_list
    
def extrude_building_n_fetch_faces(building_footprint, height):
    """
    This function extrudes a building and returns all its faces.
 
    Parameters
    ----------
    building_footprint : OCCface
        The building footprint to be extruded.
        
    height : float
        The building height.
        
    Returns
    -------        
    list of faces : list of OCCfaces
        A list of OCCfaces of the extruded building.        
    """
    face_list = []
    #polygons from shpfiles are always clockwise
    #holes are always counter-clockwise
    extrude = py3dmodel.construct.extrude(building_footprint,(0,0,1), height )
    face_list = py3dmodel.fetch.faces_frm_solid(extrude)
    return face_list

def face_almost_inside(occface, boundary_occface):
    """
    This functions measures if occ_face is almost inside the boundary face. Almost inside is define as 50% of the occ face is inside the boundary face
 
    Parameters
    ----------
    occface : OCCface
        The face to analyse.
        
    boundary_occface : OCCface
        The boundary face.
                
    Returns
    -------        
    is almost inside : bool
        True or False, if True face is almost inside, if False face is not almost inside.    
    """
    #measure the srf area of the occ face
    occ_face_area = py3dmodel.calculate.face_area(occface)
    common = py3dmodel.construct.boolean_common(occface, boundary_occface)
    shapetype = py3dmodel.fetch.topo2topotype(common)
    face_list = py3dmodel.fetch.topo_explorer(shapetype,"face")
    
    if face_list:
        common_area = 0
        for common_face in face_list:
            acommon_area = py3dmodel.calculate.face_area(common_face)
            common_area = common_area +  acommon_area
            
        common_ratio = common_area/occ_face_area
        #print "COMMON RATIO:", common_ratio
        if common_ratio >= 0.5:
            return True
        else:
            return False
    else:
        return False
    
def create_transit_stop_geometry(transit_occsolid, location_pt):
    """
    This functions creates the geometry for the transit stop.
 
    Parameters
    ----------
    transit_occsolid : OCCsolid
        The geometry of the transit stop.
        
    location_pt : pypt
        The location of the transit box. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z).
                
    Returns
    -------        
    the box moved to the location point : OCCsolid
        The box that is moved to the transit stop. 
    """
    trsf_shp = py3dmodel.modify.move((0,0,0), location_pt, transit_occsolid)
    trsf_solid = py3dmodel.fetch.topo2topotype(trsf_shp)
    trsf_solid = py3dmodel.modify.fix_close_solid(trsf_solid)
    return trsf_solid