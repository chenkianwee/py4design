#built in packages
import time 
import uuid

#downloaded package
import shapefile

#non-built in packages
import envuo

#=========================================================================================================================================
#SPECIFY ALL THE NECCESSARY INPUTS
#=========================================================================================================================================
#specify all the shpfiles
shpfile1 = "F:\\kianwee_work\\smart\\conference\\asim2016\\asim_example\\example_files\\shp\\punggol_buildings\\punggol_buildings.shp"
shpfile2 = "F:\\kianwee_work\\smart\\conference\\asim2016\\asim_example\\example_files\\shp\\punggol_stations_stops\\punggol_stations_stops.shp"
shpfile3 = "F:\\kianwee_work\\smart\\conference\\asim2016\\asim_example\\example_files\\shp\\punggol_trpst_network\\punggol_trpst_network.shp"
shpfile4 = "F:\\kianwee_work\\smart\\conference\\asim2016\\asim_example\\example_files\\shp\\punggol_plots\\punggol_plots.shp"
#specify the result citygml file
citygml_filepath = "F:\\kianwee_work\\smart\\conference\\asim2016\\asim_example\\citygml\\punggol_citygml_asim.gml"
citygml_filepath_origlvl = "F:\\kianwee_work\\smart\\conference\\asim2016\\asim_example\\citygml\\punggol_citygml_asim_origlvl.gml"
#=========================================================================================================================================
#SPECIFY ALL THE NECCESSARY INPUTS
#=========================================================================================================================================

#=========================================================================================================================================
#main convert function
#=========================================================================================================================================
def findmedian(lst):
    sortedLst = sorted(lst)
    lstLen = len(lst)
    index = (lstLen - 1) // 2

    if (lstLen % 2):
        return sortedLst[index]
    else:
        return (sortedLst[index] + sortedLst[index + 1])/2.0
        
def convert_ptshpfile(field_name_list, shapeRecs, epsg_num, citygml):
    name_index = field_name_list.index("name")-1
    station_index = field_name_list.index("station")-1
    highway_index = field_name_list.index("highway")-1
    trpst_bldg_list = []
    for rec in shapeRecs:
        poly_attribs=rec.record
        highway = poly_attribs[highway_index]
        highway.strip()
        station = poly_attribs[station_index]
        station.strip()
        name = poly_attribs[name_index]
        name.strip()
        
        if highway == "bus_stop":
            if name.isspace():
                name = "bus_stop" + str(uuid.uuid1())
            generic_attrib_dict = {"highway":highway}
            #transform to the location of the bus stop
            bus_stop_box = envuo.gml3dmodel.make_transit_stop_box(5,2,3)
            shp_pts = rec.shape.points
            for pt in shp_pts:
                geometry_list = []
                pt3d = envuo.shp2citygml.point2d_2_3d(pt,0.0)
                stopbox = envuo.gml3dmodel.create_transit_stop_geometry(bus_stop_box,pt3d)
                face_list = envuo.py3dmodel.fetch.faces_frm_solid(envuo.py3dmodel.fetch.shape2shapetype(stopbox))
                #get the surfaces from the solid 
                for face in face_list:
                    pt_list = envuo.interface2py3d.pyptlist_frm_occface(face)
                    first_pt = pt_list[0]
                    pt_list.append(first_pt)
                    srf = envuo.pycitygml.gmlgeometry.SurfaceMember(pt_list)
                    geometry_list.append(srf)
                    
            citygml.add_cityfurniture("lod1", name,"1000","1110", epsg_num, generic_attrib_dict, geometry_list)
         
        if not station.isspace():
            if name.isspace():
                name = station + str(uuid.uuid1())
            generic_attrib_dict = {"station":station}
            #create a bus stop geometry based on the point
            station_height = 8
            station_storey = 2
            storey_blw_grd = 0
            
            #transform to the location of the bus stop
            transit_station_box = envuo.gml3dmodel.make_transit_stop_box(5,20,3)
            shp_pts = rec.shape.points
            geometry_list = []
            for pt in shp_pts:
                pt3d = envuo.shp2citygml.point2d_2_3d(pt, 0.0)
                stationbox = envuo.gml3dmodel.create_transit_stop_geometry(transit_station_box,pt3d)
                face_list = envuo.py3dmodel.fetch.faces_frm_solid(envuo.py3dmodel.fetch.shape2shapetype(stationbox))
                #get the surfaces from the solid 
                for face in face_list:
                    pt_list = envuo.interface2py3d.pyptlist_frm_occface(face)
                    first_pt = pt_list[0]
                    pt_list.append(first_pt)
                    srf = envuo.pycitygml.gmlgeometry.SurfaceMember(pt_list)
                    geometry_list.append(srf)
                    
            trpst_bldg_list.append(name)                
            citygml.add_building("lod1", name, "1170", "2480", "2480","0", "1000",str(station_height),
             str(station_storey), str(storey_blw_grd), epsg_num, generic_attrib_dict, geometry_list)   
             
    return trpst_bldg_list
             
def convert_polylineshpfile(field_name_list, shapeRecs, epsg_num, citygml):
    railway_index = field_name_list.index("railway")-1
    name_index = field_name_list.index("name")-1
    highway_index = field_name_list.index("highway")-1
    count_shapes = 0
    for rec in shapeRecs:
        poly_attribs=rec.record
        railway = poly_attribs[railway_index]
        railway.strip()
        highway = poly_attribs[highway_index]
        highway.strip()
        name = poly_attribs[name_index]
        name.strip()
        
        if not railway.isspace():
            generic_attrib_dict = {"railway":railway}
            envuo.shp2citygml.trpst2citygml("Railway", rec, name, railway, epsg_num, generic_attrib_dict, citygml)
            
        if not highway.isspace():
            generic_attrib_dict = {"highway":highway}
            envuo.shp2citygml.trpst2citygml("Road", rec, name, highway, epsg_num, generic_attrib_dict, citygml)
        
        count_shapes+=1
        
def convert_apolygon(rec, epsg_num, landuse_index, building_index, name_index, plot_ratio_index, count_shapes, citygml, building_list):
    poly_attribs=rec.record
    landuse = poly_attribs[landuse_index]
    landuse.strip()
    building = poly_attribs[building_index]
    building.strip()
    name = poly_attribs[name_index]
    name.strip()
    total_build_up = 0
    perror_list = []
    constr_buildings = []
    inacc_buildings = []
    #=======================================================================================================
    #if the polygon has no building attrib and has a landuse attribute it is a landuse
    #=======================================================================================================               
    if building.isspace() and not landuse.isspace():
        #the geometry is stored in parts and points
        surface_list = envuo.shp2citygml.get_geometry(rec)
        if surface_list:
            geometry_list = []
            for p_srf in surface_list:
                luse_pts = envuo.shp2citygml.point_list2d_2_3d(p_srf,0.0)
                luse_pts = envuo.gml3dmodel.landuse_surface_cclockwise(luse_pts)
                srf = envuo.pycitygml.gmlgeometry.SurfaceMember(luse_pts)
                geometry_list.append(srf)
                
            if name.isspace():
                name = "plot" + str(count_shapes)
            
            function = envuo.shp2citygml.map_osm2citygml_landuse_function(landuse)
            generic_attrib_dict = {"landuse":landuse}
            
            plot_ratio =  poly_attribs[plot_ratio_index]
            if plot_ratio != None:
                generic_attrib_dict["plot_ratio"] = plot_ratio

            plot_area = envuo.shp2citygml.get_plot_area(rec)
            generic_attrib_dict["plot_area"] = plot_area
            
            citygml.add_landuse("lod1", name, function, epsg_num, generic_attrib_dict, geometry_list)
            
            #=======================================================================================================
            #find the buildings that belong to this plot
            #=======================================================================================================
            buildings_on_plot_list = envuo.shp2citygml.buildings_on_plot(rec, building_list)
            
            #if count_shapes == 93:
            #    print "PLOT NO.:", count_shapes
            #    print "LANDUSE", landuse
            #    print "ON PLOT:", len(buildings_on_plot_list)
            
            in_construction = False
            #check if any of the buildings are under construction 
            for cbuilding in buildings_on_plot_list:
                if cbuilding["building"] == "construction":
                    in_construction = True
                    constr_buildings.append(cbuilding)
                    
            if not in_construction:
                #then separate the buildings that are parkings and usable floor area 
                parking_list = []
                not_parking_list = list(buildings_on_plot_list)
                for building in buildings_on_plot_list:
                    if "amenity" in building:
                        if building["amenity"] == "parking" or building["amenity"] == "carpark" :
                            parking_list.append(building)
                            not_parking_list.remove(building)
                            
                #then measure the total building footprint on this plot
                build_footprint = 0 
                for not_parking in not_parking_list:
                    bgeom_list = not_parking["geometry"]
                    for bgeom in bgeom_list:
                        build_footprint = build_footprint + envuo.py3dmodel.calculate.face_area(bgeom)
                        
                #then measure the total parking footprint on this plot
                multi_parking_footprint = 0
                for parking in parking_list:
                    bgeom_list = parking["geometry"]
                    for bgeom in bgeom_list:
                        multi_parking_footprint = multi_parking_footprint + envuo.py3dmodel.calculate.face_area(bgeom)
    
                #base on the footprints calculate how many storeys are the buildings
                if build_footprint !=0:
                    residential_height = 3
                    commercial_height = 4
    
                    if plot_ratio != None:
                        total_build_up = total_build_up + (plot_area*plot_ratio)
                        num_storeys = int(round(total_build_up/build_footprint))
                        
                        if landuse == "residential":
                            height = num_storeys*residential_height
                            
                            if multi_parking_footprint !=0:
                                #base on the parking footprint estimate how high the multistorey carpark should be 
                                total_parking_area = envuo.shp2citygml.calc_residential_parking_area(total_build_up)
                                parking_storeys = int(round(total_parking_area/multi_parking_footprint))
                                parking_storey_height = 2.5
                                parking_height = parking_storey_height*parking_storeys
                                
                                #write the carparks as buildings
                                for parking in parking_list:
                                    envuo.shp2citygml.building2citygml(parking, parking_height, citygml, landuse, parking_storeys, epsg_num)
                                            
                        #TODO: calculate for commercial buildings in terms of parking space too 
                        else:
                            height = num_storeys*commercial_height
                            
                        
                        for not_parking in not_parking_list:
                            if "building_l" in not_parking:
                                orig_lvl = not_parking["building_l"]
                                percentage_error = float(num_storeys)/float(orig_lvl)
                                perror_list.append(percentage_error-1.0)
                                if (percentage_error-1.0) > 0.2 or (percentage_error-1.0) < -0.2:
                                    inacc_buildings.append(not_parking)
                                    #print not_parking["building"], percentage_error-1.0,"PRE", num_storeys,"ORIG",orig_lvl,not_parking["id"]
                                    
                            envuo.shp2citygml.building2citygml(not_parking, height, citygml, landuse, num_storeys, epsg_num)
                        
                    #================================================================================================================
                    #for those plots without plot ratio and might be educational or civic buildings
                    #================================================================================================================
                    else:
                        if landuse == "transport" or landuse == "recreation_ground" or landuse == "civic" or landuse == "place_of_worship" or landuse == "utility" or landuse == "health":
                            num_storeys = 2
                                
                        if landuse == "education" or landuse == "commercial":
                            num_storeys = 4
                            
                        if landuse == "residential":
                            num_storeys = 10
                            
                        if landuse == "reserve":
                            num_storeys = 1
                        
                        for not_parking in not_parking_list:
                            height = num_storeys*commercial_height
                            envuo.shp2citygml.building2citygml(not_parking, height, citygml, landuse, num_storeys, epsg_num)
                            
    return total_build_up, perror_list, constr_buildings, inacc_buildings
                   
def convert_apolygon_origlvl(rec, epsg_num, landuse_index, building_index, name_index, plot_ratio_index, count_shapes, citygml, building_list):
    poly_attribs=rec.record
    landuse = poly_attribs[landuse_index]
    landuse.strip()
    building = poly_attribs[building_index]
    building.strip()
    name = poly_attribs[name_index]
    name.strip()
    total_build_up = 0
    constr_buildings = []
    #=======================================================================================================
    #if the polygon has no building attrib and has a landuse attribute it is a landuse
    #=======================================================================================================               
    if building.isspace() and not landuse.isspace():
        #the geometry is stored in parts and points
        surface_list = envuo.shp2citygml.get_geometry(rec)
        if surface_list:
            geometry_list = []
            for p_srf in surface_list:
                luse_pts = envuo.shp2citygml.point_list2d_2_3d(p_srf,0.0)
                luse_pts = envuo.gml3dmodel.landuse_surface_cclockwise(luse_pts)
                srf = envuo.pycitygml.gmlgeometry.SurfaceMember(luse_pts)
                geometry_list.append(srf)
                
            if name.isspace():
                name = "plot" + str(count_shapes)
            
            function = envuo.shp2citygml.map_osm2citygml_landuse_function(landuse)
            generic_attrib_dict = {"landuse":landuse}
            
            plot_ratio =  poly_attribs[plot_ratio_index]
            if plot_ratio != None:
                generic_attrib_dict["plot_ratio"] = plot_ratio

            plot_area = envuo.shp2citygml.get_plot_area(rec)
            generic_attrib_dict["plot_area"] = plot_area
            
            citygml.add_landuse("lod1", name, function, epsg_num, generic_attrib_dict, geometry_list)
            
            #=======================================================================================================
            #find the buildings that belong to this plot
            #=======================================================================================================
            buildings_on_plot_list = envuo.shp2citygml.buildings_on_plot(rec, building_list)
            in_construction = False
            #check if any of the buildings are under construction 
            for cbuilding in buildings_on_plot_list:
                if cbuilding["building"] == "construction":
                    in_construction = True
                    constr_buildings.append(cbuilding)
                    
            if not in_construction:
                #then separate the buildings that are parkings and usable floor area 
                parking_list = []
                not_parking_list = list(buildings_on_plot_list)
                for building in buildings_on_plot_list:
                    if "amenity" in building:
                        if building["amenity"] == "parking" or building["amenity"] == "carpark" :
                            parking_list.append(building)
                            not_parking_list.remove(building)
                            
                #then measure the total building footprint on this plot
                build_footprint = 0 
                for not_parking in not_parking_list:
                    bgeom_list = not_parking["geometry"]
                    for bgeom in bgeom_list:
                        build_footprint = build_footprint + envuo.py3dmodel.calculate.face_area(bgeom)
                        
                #then measure the total parking footprint on this plot
                multi_parking_footprint = 0
                for parking in parking_list:
                    bgeom_list = parking["geometry"]
                    for bgeom in bgeom_list:
                        multi_parking_footprint = multi_parking_footprint + envuo.py3dmodel.calculate.face_area(bgeom)
    
                #base on the footprints calculate how many storeys are the buildings
                if build_footprint !=0:
                    residential_height = 3
                    commercial_height = 4
    
                    if plot_ratio != None:
                        total_build_up = total_build_up + (plot_area*plot_ratio)
                        num_storeys = int(round(total_build_up/build_footprint))
                        
                        if landuse == "residential":
                            height = num_storeys*residential_height
                            
                            if multi_parking_footprint !=0:
                                #base on the parking footprint estimate how high the multistorey carpark should be 
                                total_parking_area = envuo.shp2citygml.calc_residential_parking_area(total_build_up)
                                parking_storeys = int(round(total_parking_area/multi_parking_footprint))
                                parking_storey_height = 2.5
                                parking_height = parking_storey_height*parking_storeys
                                
                                #write the carparks as buildings
                                for parking in parking_list:
                                    if "building_l" in parking:
                                        parking_storeys = parking["building_l"]
                                        parking_height = parking_storey_height*parking_storeys
                                        envuo.shp2citygml.building2citygml(parking, parking_height, citygml, landuse, parking_storeys, epsg_num)
                                    else:
                                        envuo.shp2citygml.building2citygml(parking, parking_height, citygml, landuse, parking_storeys, epsg_num)
                                            
                        #TODO: calculate for commercial buildings in terms of parking space too 
                        else:
                            height = num_storeys*commercial_height
                            
                        
                        for not_parking in not_parking_list:
                            if "building_l" in not_parking:
                                num_storeys = not_parking["building_l"]
                                if landuse == "residential":
                                    height = residential_height*num_storeys
                                else:
                                    height = commercial_height*num_storeys
                                envuo.shp2citygml.building2citygml(not_parking, height, citygml, landuse, num_storeys, epsg_num)
                            else:
                                envuo.shp2citygml.building2citygml(not_parking, height, citygml, landuse, num_storeys, epsg_num)
                        
                    #================================================================================================================
                    #for those plots without plot ratio and might be educational or civic buildings
                    #================================================================================================================
                    else:
                        if landuse == "transport" or landuse == "recreation_ground" or landuse == "civic" or landuse == "place_of_worship" or landuse == "utility" or landuse == "health":
                            num_storeys = 2
                                
                        if landuse == "education" or landuse == "commercial":
                            num_storeys = 4
                            
                        if landuse == "residential":
                            num_storeys = 10
                            
                        if landuse == "reserve":
                            num_storeys = 1
                        
                        for not_parking in not_parking_list:
                            if "building_l" in not_parking:
                                num_storeys = not_parking["building_l"]
                                height = commercial_height*num_storeys
                                envuo.shp2citygml.building2citygml(not_parking, height, citygml, landuse, num_storeys, epsg_num)
                            else:
                                height = num_storeys*commercial_height
                                envuo.shp2citygml.building2citygml(not_parking, height, citygml, landuse, num_storeys, epsg_num)
                            
    return total_build_up, constr_buildings
    
def convert_polygonshpfile(field_name_list, shapeRecs, epsg_num, citygml, building_list, origlvl=False):
    #the attributes are mainly base on the attributes from osm 
    landuse_index = field_name_list.index("landuse")-1
    plot_ratio_index = field_name_list.index("plot_ratio")-1
    building_index = field_name_list.index("building")-1
    name_index = field_name_list.index("name")-1
    count_shapes = 0
    total_flr_area = 0
    if origlvl == False:
        shp_perror_list = []
        shp_constr_list = []
        shp_inacc_buildings = []
        for rec in shapeRecs:
            build_footprint, perror_list,constr_list, inacc_buildings = convert_apolygon(rec, epsg_num, landuse_index, building_index, name_index, plot_ratio_index, count_shapes, citygml, building_list)         
            shp_perror_list.extend(perror_list)    
            shp_constr_list.extend(constr_list)
            shp_inacc_buildings.extend(inacc_buildings)
            total_flr_area = total_flr_area + build_footprint
            count_shapes += 1
        return shp_perror_list, shp_constr_list, shp_inacc_buildings
        
    if origlvl == True:
        for rec in shapeRecs:
            build_footprint = convert_apolygon_origlvl(rec, epsg_num, landuse_index, building_index, name_index, plot_ratio_index, count_shapes, citygml, building_list)         
            count_shapes += 1
        
    print "TOTAL FLOOR AREA:", total_flr_area
    

def convert(shpfile_list, citygml):
    #get the building footprints
    building_list = []
    for shpfile in shpfile_list:
        buildings = envuo.shp2citygml.get_buildings(shpfile)
        if buildings:
            building_list.extend(buildings)
            
    print "done with getting buildings"
    print "TOTAL NUMBER OF BUILDINGS:", len(building_list)
    total_perror_list = []
    total_constr_list = []
    total_trpst_bldg_list = []
    total_inacc_buildings = []
    #read the shapefiles
    for shpfile in shpfile_list:
        sf = shapefile.Reader(shpfile)
        shapeRecs=sf.shapeRecords()
        shapetype = shapeRecs[0].shape.shapeType
        
        #get the project CRS of the shapefile
        epsg_num = "EPSG:" + envuo.shp2citygml.get_shpfile_epsg(shpfile)
        field_name_list = envuo.shp2citygml.get_field_name_list(sf)
        
        #shapetype 1 is point, 3 is polyline, shapetype 5 is polygon
        #if it is a point file it must be recording the location of the bus stops and subway stations
        if shapetype == 1:
            trpst_bldg_list = convert_ptshpfile(field_name_list, shapeRecs, epsg_num, citygml)          
            total_trpst_bldg_list.extend(trpst_bldg_list)
            
        if shapetype == 3:
            convert_polylineshpfile(field_name_list, shapeRecs, epsg_num, citygml)
            
        if shapetype == 5:
            shp_perror_list, shp_constr_list, shp_inacc_buildings = convert_polygonshpfile(field_name_list, shapeRecs, epsg_num, citygml, building_list)
            if shp_perror_list:
                total_perror_list.extend(shp_perror_list)
            if shp_constr_list:
                total_constr_list.extend(shp_constr_list)
            if shp_inacc_buildings:
                total_inacc_buildings.extend(shp_inacc_buildings)
                
    print "NUMBER OF BUILDINGS IN CONSTRUCTION:", len(total_constr_list)
    print "NUMBER OF MRT/LRT STATIONS:", len(total_trpst_bldg_list)
    print "NUMBER OF BUILDINGS WITH LEVEL INFORMATION:", len(total_perror_list)
    print "MEAN:", (sum(total_perror_list))/(len(total_perror_list))
    print "MAX:", max(total_perror_list)
    print "MIN:", min(total_perror_list)
    print "MEDIAN:", findmedian(total_perror_list)
    print "NUMBER OF INACCURATE BUILDINGS:", len(total_inacc_buildings)
    
def convert_origlvl(shpfile_list, citygml):
    #get the building footprints
    building_list = []
    for shpfile in shpfile_list:
        buildings = envuo.shp2citygml.get_buildings(shpfile)
        if buildings:
            building_list.extend(buildings)
            
    total_constr_list = []
    print "done with getting buildings"
    print "TOTAL NUMBER OF BUILDINGS:", len(building_list)
    #read the shapefiles
    for shpfile in shpfile_list:
        sf = shapefile.Reader(shpfile)
        shapeRecs=sf.shapeRecords()
        shapetype = shapeRecs[0].shape.shapeType
        
        #get the project CRS of the shapefile
        epsg_num = "EPSG:" + envuo.shp2citygml.get_shpfile_epsg(shpfile)
        field_name_list = envuo.shp2citygml.get_field_name_list(sf)
        
        #shapetype 1 is point, 3 is polyline, shapetype 5 is polygon
        #if it is a point file it must be recording the location of the bus stops and subway stations
        if shapetype == 1:
            trpst_bldg_list = convert_ptshpfile(field_name_list, shapeRecs, epsg_num, citygml)          
            
        if shapetype == 3:
            convert_polylineshpfile(field_name_list, shapeRecs, epsg_num, citygml)
            
        if shapetype == 5:
            shp_constr_list  = convert_polygonshpfile(field_name_list, shapeRecs, epsg_num, citygml, building_list, origlvl=True)
            if shp_constr_list:
                total_constr_list.extend(shp_constr_list)
                
    print "NUMBER OF BUILDINGS IN CONSTRUCTION:", len(total_constr_list)
#=========================================================================================================================================
#main SCRIPT
#=========================================================================================================================================
print "CONVERTING ... ..."
time1 = time.clock()  

#initialise the citygml writer
citygml_writer = envuo.pycitygml.Writer()
citygml_writer_origlvl = envuo.pycitygml.Writer()
#convert the shpfiles into 3d citygml using the citygmlenv library
convert([shpfile1,shpfile2,shpfile3,shpfile4],citygml_writer)
citygml_writer.write(citygml_filepath)

convert_origlvl([shpfile1,shpfile2,shpfile3,shpfile4], citygml_writer_origlvl)
citygml_writer_origlvl.write(citygml_filepath_origlvl)

time2 = time.clock()
time = (time2-time1)/60.0
print "TIME TAKEN:", time
print "CityGML GENERATED"