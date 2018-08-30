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
import urbangeom
import py3dmodel
import pycitygml
    
#===========================================================================================================================
#NUMERIC AND STRING INPUTS
#===========================================================================================================================
def citygml2collada(citygml_filepath, collada_filepath):
    """
    This function convert a CityGML to Collada. Currently only works with LOD1 buildings, landuses and terrain. LOD0 transportation network.
 
    Parameters
    ----------
    citygml_filepath : str
        The file path of the CityGML file.
        
    collada_filepath : str
        The file path of the Collada file.
    
    """
    reader = pycitygml.Reader()
    reader.load_filepath(citygml_filepath)
    buildings = reader.get_buildings()
    landuses = reader.get_landuses()
    stops = reader.get_bus_stops()
    roads = reader.get_roads()
    railways = reader.get_railways()
    relief_features = reader.get_relief_feature()
    occshell_list = []
    occedge_list = []
    
    for building in buildings:
        pypolgon_list = reader.get_pypolygon_list(building)
        solid = py3dmodel.construct.make_occsolid_frm_pypolygons(pypolgon_list)
        bldg_shell_list = py3dmodel.fetch.topo_explorer(solid, "shell")
        occshell_list.extend(bldg_shell_list)

    for landuse in landuses:
        lpolygons = reader.get_polygons(landuse)
        if lpolygons:
            for lpolygon in lpolygons:
                landuse_pts = reader.polygon_2_pyptlist(lpolygon)
                lface = py3dmodel.construct.make_polygon(landuse_pts)
                occshell_list.append(lface)
          
    rf_face_list = []
    for relief in relief_features:
        pytri_list = reader.get_pytriangle_list(relief)
        for pytri in pytri_list:
            rface = py3dmodel.construct.make_polygon(pytri)
            rf_face_list.append(rface)
            
    if rf_face_list:
        rf_cmpd = py3dmodel.construct.make_compound(rf_face_list)
        centre_pt = py3dmodel.calculate.get_centre_bbox(rf_cmpd)
        move_centre_pt = py3dmodel.modify.move_pt(centre_pt, (0,0,-1), 0.1)
        moved_cmpd = py3dmodel.modify.move(centre_pt,move_centre_pt,rf_cmpd)
        occshell_list.append(moved_cmpd)
            
    for road in roads:
        polylines = reader.get_pylinestring_list(road)
        for polyline in polylines:
            occ_wire = py3dmodel.construct.make_wire(polyline)
            edge_list = py3dmodel.fetch.topo_explorer(occ_wire, "edge")
            occedge_list.extend(edge_list)
    
    for rail in railways:
        polylines = reader.get_pylinestring_list(rail)
        for polyline in polylines:
            occ_wire = py3dmodel.construct.make_wire(polyline)
            edge_list = py3dmodel.fetch.topo_explorer(occ_wire, "edge")
            occedge_list.extend(edge_list)
            
    for stop in stops:
        pypolgon_list = reader.get_pypolygon_list(stop)
        solid = py3dmodel.construct.make_occsolid_frm_pypolygons(pypolgon_list)
        stop_shell_list = py3dmodel.fetch.topo_explorer(solid, "shell")
        occshell_list.extend(stop_shell_list)
    
    py3dmodel.export_collada.write_2_collada(occshell_list, collada_filepath, occedge_list = occedge_list)
    
#==============================================================================================================================
#GML BUILDING INPUTS
#==============================================================================================================================
def get_building_footprint(gml_bldg, citygml_reader):
    """
    This function gets the footprint of a building.
 
    Parameters
    ----------
    gml_bldg : lxml.etree Element 
        The GML building to be analysed.
        
    citygml_reader : Pycitygml.Reader() class instance
        The reader is used to extract information from the GML building.
    
    Returns
    -------        
    footprints : list of OCCfaces
        List of OCCfaces identified as footprints.
    
    """
    bldg_occsolid = get_building_occsolid(gml_bldg, citygml_reader)
    bldg_footprint_list = urbangeom.get_bldg_footprint_frm_bldg_occsolid(bldg_occsolid)
    return bldg_footprint_list

def get_building_occsolid(gml_bldg, citygml_reader):
    """
    This function gets the geometry of a building.
 
    Parameters
    ----------
    gml_bldg : lxml.etree Element 
        The GML building to be analysed.
        
    citygml_reader : Pycitygml.Reader() class instance
        The reader is used to extract information from the GML building.
    
    Returns
    -------        
    building solid : OCCsolid
        The geometry (OCCsolid) of the building.
    
    """
    pypolygon_list = citygml_reader.get_pypolygon_list(gml_bldg)
    solid = py3dmodel.construct.make_occsolid_frm_pypolygons(pypolygon_list)
    return solid

def get_building_height_storey(gml_bldg, citygml_reader, flr2flr_height = 3):
    """
    This function gets the height, number of storeys and storey height of a building.
 
    Parameters
    ----------
    gml_bldg : lxml.etree Element 
        The GML building to be analysed.
        
    citygml_reader : Pycitygml.Reader() class instance
        The reader is used to extract information from the GML building.
    
    flr2flr_height : float, optional
        The floor to floor height of the building, Default = 3.
    
    Returns
    -------        
    height : float
        The building height.
    
    storey : int
        The the number of storeys of the building.
        
    storey height : float
        The floor to floor height of the building.
    
    """
    height = citygml_reader.get_building_height(gml_bldg)
    nstorey = citygml_reader.get_building_storey(gml_bldg)
    if height == None or nstorey == None:
        bldg_occsolid = get_building_occsolid(gml_bldg, citygml_reader)
        storey_height = flr2flr_height
        height, nstorey = urbangeom.calculate_bldg_height_n_nstorey(bldg_occsolid, storey_height)        
        return height, nstorey, storey_height
    else:
        storey_height = height/nstorey
        return height, nstorey, storey_height
    
def get_bulding_floor_area(gml_bldg, nstorey, storey_height, citygml_reader):
    """
    This function gets the floor area of a building.
 
    Parameters
    ----------
    gml_bldg : lxml.etree Element 
        The GML building to be analysed.
        
    nstorey : int
        The the number of storeys of the building.
        
    storey height : float
        The floor to floor height of the building.
        
    citygml_reader : Pycitygml.Reader() class instance
        The reader is used to extract information from the GML building.
    
    Returns
    -------        
    height : float
        The floor area of the building.
    
    floor plates : list of OCCfaces
        The list of floor plates of the buildings.
    
    """
    bldg_occsolid = get_building_occsolid(gml_bldg,citygml_reader)
    flr_plates = urbangeom.get_building_flrplates(bldg_occsolid, nstorey, storey_height)
    flr_area = 0
    for flr in flr_plates:
        flr_area = flr_area + py3dmodel.calculate.face_area(flr)
        
    return flr_area , flr_plates

def rotate_bldg(gml_bldg, rot_angle, citygml_reader):
    """
    This function rotates the building.
 
    Parameters
    ----------
    gml_bldg : lxml.etree Element 
        The GML building to be analysed.
        
    rot_angle : float
        The the angle of rotation.
        
    citygml_reader : Pycitygml.Reader() class instance
        The reader is used to extract information from the GML building.
    
    Returns
    -------        
    rotated building : OCCsolid
        The rotated building OCCsolid.
    
    """
    bldg_occsolid = get_building_occsolid(gml_bldg,citygml_reader)
    loc_pt = urbangeom.get_building_location_pt(bldg_occsolid)
    rot_bldg_occshape = py3dmodel.modify.rotate(bldg_occsolid, loc_pt, (0,0,1), rot_angle)
    rot_bldg_occsolid = py3dmodel.fetch.topo_explorer(rot_bldg_occshape, "solid")[0]
    return rot_bldg_occsolid

def update_gml_building(orgin_gml_building, new_bldg_occsolid, citygml_reader, citygml_writer, 
                        new_height = None, new_nstorey = None):
    
    """
    This function updates the information of the GML building.
 
    Parameters
    ----------
    gml_bldg : lxml.etree Element 
        The GML building to be updated.
        
    new_bldg_occsolid building : OCCsolid
        The new geometry of the building. The update is based on this geometry.
        
    citygml_reader : Pycitygml.Reader() class instance
        The reader is used to extract information from the GML building.
        
    citygml_writer : Pycitygml.Writer() class instance
        The writer is used to write information to the GML building.
        
    new_height : float, optional
        The new building height, Default = None.
    
    new_nstorey : int, optional
        The new number of storeys of the building, Default = None.
    
    """
    building_name = citygml_reader.get_gml_id(orgin_gml_building)
    bclass = citygml_reader.get_building_class(orgin_gml_building)
    bfunction = citygml_reader.get_building_function(orgin_gml_building)
    rooftype = citygml_reader.get_building_rooftype(orgin_gml_building)
    stry_blw_grd = citygml_reader.get_building_storey_blw_grd(orgin_gml_building)
    #generic_attrib_dict = citygml_reader.get_generic_attribs(orgin_gml_building)        
    new_bldg_occsolid = py3dmodel.fetch.topo_explorer(new_bldg_occsolid, "solid")[0]
    new_bldg_occsolid = py3dmodel.modify.fix_close_solid(new_bldg_occsolid)
    face_list = py3dmodel.fetch.faces_frm_solid(new_bldg_occsolid)
    geometry_list = write_gml_srf_member(face_list)
    if new_height == None:
        new_height = urbangeom.calculate_bldg_height(new_bldg_occsolid)
        
    if new_nstorey !=None:
        citygml_writer.add_building("lod1", building_name, geometry_list, bldg_class =  bclass, 
                                    function = bfunction, usage = bfunction, rooftype = rooftype,height = str(new_height),
                                    stry_abv_grd = str(new_nstorey), stry_blw_grd = str(stry_blw_grd))
    if new_nstorey ==None:
        citygml_writer.add_building("lod1", building_name, geometry_list, bldg_class =  bclass, 
                                    function = bfunction, usage = bfunction, rooftype = rooftype,height = str(new_height),
                                    stry_blw_grd = str(stry_blw_grd))
        
def write_non_eligible_bldgs(gml_bldgs, citygml_writer):
    """
    This function updates the information of the GML building.
 
    Parameters
    ----------
    gml_bldgs : list of lxml.etree Element 
        The GML building to be updated.
        
    citygml_writer : Pycitygml.Writer() class instance
        The writer is used to write information to the GML building.
    
    """
    citygml_root = citygml_writer.citymodel_node
    for non_eligible_bldg in gml_bldgs:
        city_obj = citygml_writer.create_cityobjectmember()
        city_obj.append(non_eligible_bldg)
        citygml_root.append(city_obj)
#==============================================================================================================================
#GML LANDUSE INPUTS
#==============================================================================================================================
def gml_landuse_2_occface(gml_landuse, citygml_reader):
    """
    This function gets the geometry from the landuse and converts it to an OCCface.
 
    Parameters
    ----------
    gml_landuse : lxml.etree Element 
        The GML landuse to be analysed.
        
    citygml_reader : Pycitygml.Reader() class instance
        The reader is used to extract information from the GML building.
    
    Returns
    -------        
    landuse geometry : OCCface
        The landuse OCCface.
    
    """
    lpolygon = citygml_reader.get_polygons(gml_landuse)[0]
    landuse_pts = citygml_reader.polygon_2_pyptlist(lpolygon)
    landuse_occface = py3dmodel.construct.make_polygon(landuse_pts)
    return landuse_occface
            
def buildings_on_landuse(gml_landuse, gml_bldg_list, citygml_reader):
    """
    This function identify the GML buildings that is on this GML landuse plot.
 
    Parameters
    ----------
    gml_landuse : lxml.etree Element 
        The GML landuse to be analysed.
        
    gml_bldg_list : list of lxml.etree Element 
        The GML building to be identified.
        
    citygml_reader : Pycitygml.Reader() class instance
        The reader is used to extract information from the GML building.
    
    Returns
    -------        
    buildings on plot : list of lxml.etree Element 
        The GML building that are on the plot.
    
    """
    buildings_on_plot_list = []
    landuse_occface = gml_landuse_2_occface(gml_landuse, citygml_reader)
    flatten_landuse_occface = py3dmodel.modify.flatten_face_z_value(landuse_occface)
    for gml_bldg in gml_bldg_list:
        bldg_fp_list = get_building_footprint(gml_bldg, citygml_reader)
        is_inside = False
        for bldg_fp in bldg_fp_list:
            flatten_fp = py3dmodel.modify.flatten_face_z_value(bldg_fp)
            occface_area = py3dmodel.calculate.face_area(flatten_fp)
            common_cmpd = py3dmodel.construct.boolean_common(flatten_fp, flatten_landuse_occface)
            face_list = py3dmodel.fetch.topo_explorer(common_cmpd, "face")
            if face_list:
                common_area = 0
                for common_face in face_list:
                    acommon_area = py3dmodel.calculate.face_area(common_face)
                    common_area = common_area +  acommon_area
                common_ratio = common_area/occface_area
                if common_ratio >= 0.5:
                    is_inside = True
                
        if is_inside:
            buildings_on_plot_list.append(gml_bldg)
            
    return buildings_on_plot_list

#===========================================================================================================================
#GML CITYOBJECTMEMBER INPUTS
#===========================================================================================================================     
def write_citygml(cityobjmembers, citygml_writer):
    """
    This function identify the GML buildings that is on this GML landuse plot.
 
    Parameters
    ----------        
    cityobjmembers : list of lxml.etree Element 
        The GML cityobjectmembers to be written.
        
    citygml_writer : Pycitygml.Writer() class instance
        The writer is used to write information to the GML building.
    
    """
    citygml_root = citygml_writer.citymodel_node
    for cityobj in cityobjmembers:
        citygml_root.append(cityobj)
                  
#===========================================================================================================================
#OCCTOPOLOGY INPUTS
#===========================================================================================================================
def write_a_gml_srf_member(occface):
    """
    This function writes a OCCface to GML surface member.
 
    Parameters
    ----------
    occface : OCCface
        OCCface to be written.
        
    Returns
    -------
    surface : pycitygml.SurfaceMember class instance
        The written surface.
        
    """
    pypt_list = py3dmodel.fetch.points_frm_occface(occface)
    #pypt_list = py3dmodel.modify.rmv_duplicated_pts(pypt_list, roundndigit = 6)
    if len(pypt_list)>=3:
        face_nrml = py3dmodel.calculate.face_normal(occface)
        is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pypt_list, face_nrml)
        if is_anticlockwise == False:
            pypt_list.reverse()
    
        first_pt = pypt_list[0]
        pypt_list.append(first_pt)
        srf = pycitygml.SurfaceMember(pypt_list)
        return srf
    else:
        return None
    
def write_gml_srf_member(occface_list):
    """
    This function writes a OCCface to GML surface member.
 
    Parameters
    ----------
    occface_list : list of OCCfaces
        List of OCCface to be written.
        
    Returns
    -------
    list of surface : list of pycitygml.SurfaceMember class instances
        The written list of surfaces.
        
    """
    gml_geometry_list = []
    for face in occface_list:
        srf = write_a_gml_srf_member(face)
        if srf != None:
            gml_geometry_list.append(srf)

    return gml_geometry_list

def write_gml_triangle(occface_list):
    """
    This function writes a OCCface to GML triangle.
 
    Parameters
    ----------
    occface_list : list of OCCfaces
        List of OCCface to be written.
        
    Returns
    -------
    list of surface : list of pycitygml.SurfaceMember class instances
        The written list of surfaces.
        
    """
    gml_geometry_list = []
    for face in occface_list:
        pypt_list = py3dmodel.fetch.points_frm_occface(face)
        n_pypt_list = len(pypt_list)
        if n_pypt_list>3:
            occtriangles = py3dmodel.construct.simple_mesh(face)
            for triangle in occtriangles:
                is_face_null = py3dmodel.fetch.is_face_null(triangle)
                if not is_face_null:
                    t_pypt_list = py3dmodel.fetch.points_frm_occface(triangle)
                    #face_nrml = py3dmodel.calculate.face_normal(triangle)
                    #is_anticlockwise = py3dmodel.calculate.is_anticlockwise(t_pypt_list, face_nrml)
                    #if is_anticlockwise == False:
                    #    t_pypt_list.reverse()
                    gml_tri = pycitygml.Triangle(t_pypt_list)
                    gml_geometry_list.append(gml_tri)
        else:
            #face_nrml = py3dmodel.calculate.face_normal(face)
            #is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pypt_list, face_nrml)
            #if is_anticlockwise == False:
            #    pypt_list.reverse()
            gml_tri = pycitygml.Triangle(pypt_list)
            gml_geometry_list.append(gml_tri)
            
    return gml_geometry_list
    
def write_gml_linestring(occedge):
    """
    This function writes a OCCedge to GML linestring.
 
    Parameters
    ----------
    occedge : OCCedge
        OCCedge to be written.
        
    Returns
    -------
    edge : pycitygml.LineString class instance
        The written edge.
        
    """
    gml_edge_list = []
    pypt_list = py3dmodel.fetch.points_frm_edge(occedge)
    linestring = pycitygml.LineString(pypt_list)
    gml_edge_list.append(linestring)
    return gml_edge_list