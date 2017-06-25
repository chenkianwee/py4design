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
import math
import utility3d
import py3dmodel
import pycitygml
    
#==============================================================================================================================
#citygml2eval functions
#==============================================================================================================================
def generate_sensor_surfaces(occface, xdim, ydim):
    normal = py3dmodel.calculate.face_normal(occface)
    mid_pt = py3dmodel.calculate.face_midpt(occface)
    location_pt = py3dmodel.modify.move_pt(mid_pt, normal, 0.01)
    moved_oface = py3dmodel.fetch.shape2shapetype(py3dmodel.modify.move(mid_pt, location_pt, occface))
    #put it into occ and subdivide surfaces 
    sensor_surfaces = py3dmodel.construct.grid_face(moved_oface, xdim, ydim)
    sensor_pts = []
    sensor_dirs = []
    for sface in sensor_surfaces:
        smidpt = py3dmodel.calculate.face_midpt(sface)
        sensor_pts.append(smidpt)
        sensor_dirs.append(normal)
    
    return sensor_surfaces, sensor_pts, sensor_dirs
        
def identify_srfs_according_2_angle(occface_list):
    roof_list = []
    facade_list = []
    footprint_list = []
    vec1 = (0,0,1)
    for f in occface_list:
        #get the normal of each face
        n = py3dmodel.calculate.face_normal(f)
        angle = py3dmodel.calculate.angle_bw_2_vecs(vec1, n)
        #means its a facade
        if angle>45 and angle<170:
            facade_list.append(f)
        elif angle<=45:
            roof_list.append(f)
        elif angle>=170:
            footprint_list.append(f)
    return facade_list, roof_list, footprint_list
            
def identify_building_surfaces(bldg_occsolid):
    face_list = py3dmodel.fetch.faces_frm_solid(bldg_occsolid)
    facade_list, roof_list, footprint_list = identify_srfs_according_2_angle(face_list)     
    return facade_list, roof_list, footprint_list
    
def faces_surface_area(occface_list):
    total_sa = 0
    for occface in occface_list:
        sa = py3dmodel.calculate.face_area(occface)
        total_sa = total_sa + sa
    return total_sa
    
#==============================================================================================================================
#gmlparameterise functions
#==============================================================================================================================
def get_building_footprint(gml_bldg, citygml_reader):
    bldg_occsolid = get_building_occsolid(gml_bldg, citygml_reader)
    bldg_footprint_list = get_bldg_footprint_frm_bldg_occsolid(bldg_occsolid)
    return bldg_footprint_list
            
def get_bldg_footprint_frm_bldg_occsolid(bldg_occsolid, tolerance = 1e-05, roundndigit = 6, distance = 0.1):
    bounding_footprint = get_building_bounding_footprint(bldg_occsolid)
    b_midpt = py3dmodel.calculate.face_midpt(bounding_footprint)
    loc_pt = (b_midpt[0], b_midpt[1], b_midpt[2]+tolerance)
    bounding_footprint = py3dmodel.fetch.shape2shapetype(py3dmodel.modify.move(b_midpt, loc_pt, bounding_footprint))
    bldg_footprint_cmpd = py3dmodel.construct.boolean_section(bldg_occsolid, bounding_footprint, roundndigit = roundndigit, distance = distance)
    bldg_footprint_cmpd = py3dmodel.fetch.shape2shapetype(py3dmodel.modify.move(loc_pt, b_midpt, bldg_footprint_cmpd))
    bldg_footprint_list = py3dmodel.fetch.geom_explorer(bldg_footprint_cmpd, "face")
    return bldg_footprint_list

def get_building_roofplates(bldg_occsolid, nstorey, storey_height, tolerance = 1e-05, roundndigit = 6, distance = 0.1):
    loc_pt = get_building_location_pt(bldg_occsolid)
    bounding_footprint = get_building_bounding_footprint(bldg_occsolid)
    z = loc_pt[2]+(nstorey*storey_height)
    moved_pt = (loc_pt[0], loc_pt[1], z)
    moved_f = py3dmodel.modify.move(loc_pt, moved_pt, bounding_footprint)
           
    moved_pt2 = (loc_pt[0], loc_pt[1], loc_pt[2] + tolerance)
    moved_occsolid = py3dmodel.modify.move(loc_pt, moved_pt2, bldg_occsolid)
    floors = py3dmodel.construct.boolean_section(moved_f, moved_occsolid, roundndigit = roundndigit, distance = distance)
    inter_face_list = py3dmodel.fetch.geom_explorer(floors, "face")
    return inter_face_list#, bounding_list
    
def get_building_flrplates(bldg_occsolid, nstorey, storey_height):
    intersection_list = []
    bounding_list = []
    loc_pt = get_building_location_pt(bldg_occsolid)
    bounding_footprint = get_building_bounding_footprint(bldg_occsolid)
    bldg_footprint_list = get_bldg_footprint_frm_bldg_occsolid(bldg_occsolid)
    intersection_list.extend(bldg_footprint_list)
    for scnt in range(nstorey):
        z = loc_pt[2]+(scnt*storey_height)
        moved_pt = (loc_pt[0], loc_pt[1], z)
        moved_f = py3dmodel.modify.move(loc_pt, moved_pt, bounding_footprint)
        bounding_list.append(moved_f)
           
    bounding_compound = py3dmodel.construct.make_compound(bounding_list)
    floors = py3dmodel.construct.boolean_common(bldg_occsolid, bounding_compound)
    common_compound = py3dmodel.fetch.shape2shapetype(floors)
    inter_face_list = py3dmodel.fetch.geom_explorer(common_compound, "face")
    if inter_face_list:
        for inter_face in inter_face_list:
            intersection_list.append(inter_face)
    return intersection_list#, bounding_list

def get_building_plates_by_level(bldg_occsolid, nstorey, storey_height, roundndigit = 6, distance = 0.1):
    intersection_2dlist = []
    bounding_list = []
    
    loc_pt = get_building_location_pt(bldg_occsolid)
    bounding_footprint = get_building_bounding_footprint(bldg_occsolid)
    bldg_footprint_list = get_bldg_footprint_frm_bldg_occsolid(bldg_occsolid, roundndigit = roundndigit, distance = distance)
    intersection_2dlist.append(bldg_footprint_list)
    
    for scnt in range(nstorey):
        z = loc_pt[2]+((scnt+1)*storey_height)
        moved_pt = (loc_pt[0], loc_pt[1], z)
        moved_f = py3dmodel.modify.move(loc_pt, moved_pt, bounding_footprint)
        floor_cmpd = py3dmodel.construct.boolean_section(moved_f, bldg_occsolid, roundndigit = roundndigit, distance = distance)
        floor_list = py3dmodel.fetch.geom_explorer(floor_cmpd, "face")
        if floor_list:
            intersection_2dlist.append(floor_list)
        bounding_list.append(moved_f)
            

    new_2d_list = []
    for intersection_list in intersection_2dlist:
        new_flr_list = []
        for floor in intersection_list:
            wire_list = py3dmodel.fetch.geom_explorer(floor, "wire")
            to_be_cut_list = []
            cutting_list = []
            for wire in wire_list:
                bspline_edge = py3dmodel.modify.wire_2_bsplinecurve_edge(wire)
                lbound, ubound = py3dmodel.fetch.edge_domain(bspline_edge)
                bound = ubound - lbound
                n_interval = 30
                b_interval = bound/float(n_interval)
                pyptlist = []
                for i in range(n_interval):
                    u = lbound + (i*b_interval)
                    e_pypt = py3dmodel.calculate.edgeparameter2pt(u, bspline_edge)
                    pyptlist.append(e_pypt)
                
                #pyref_vec = (0,0,1)
                pyref_vec = py3dmodel.calculate.face_normal(floor)
                is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, pyref_vec)
                new_floor = py3dmodel.construct.make_polygon(pyptlist)
                if is_anticlockwise:
                    to_be_cut_list.append(new_floor)
                else:
                    cutting_list.append(new_floor) 
                    
            if len(cutting_list) !=0:
                extrude_list = []
                for cut in cutting_list:
                    midpt = py3dmodel.calculate.face_midpt(cut)
                    loc_pt = py3dmodel.modify.move_pt(midpt, (0,0,-1),0.3)
                    #move the face down
                    m_occface = py3dmodel.modify.move(midpt, loc_pt, cut)
                    m_occface = py3dmodel.fetch.shape2shapetype(m_occface)
                    #extrude the face
                    extrude_solid = py3dmodel.construct.extrude(m_occface, (0,0,1), 0.6)
                    extrude_list.append(extrude_solid)
                    
                cmpd = py3dmodel.construct.make_compound(extrude_list)
        
                for tbc in to_be_cut_list:
                    diff_cmpd = py3dmodel.construct.boolean_difference(tbc, cmpd)
                    cut_new_flr_list = py3dmodel.fetch.geom_explorer(diff_cmpd, "face")
                    new_flr_list.extend(cut_new_flr_list)
            else:
                new_flr_list.extend(to_be_cut_list)
            '''
            print ac_list
            #print len(wire_list)
            wire = py3dmodel.fetch.geom_explorer(floor, "wire")[0]
            bspline_edge = py3dmodel.modify.wire_2_bsplinecurve_edge(wire)
            
            lbound, ubound = py3dmodel.fetch.edge_domain(bspline_edge)
            bound = ubound - lbound
            n_interval = 30
            b_interval = bound/float(n_interval)
            pyptlist = []
            for i in range(n_interval):
                u = lbound + (i*b_interval)
                e_pypt = py3dmodel.calculate.edgeparameter2pt(u, bspline_edge)
                pyptlist.append(e_pypt)
            
            pyref_vec = (0,0,1)
            is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, pyref_vec)
            if not is_anticlockwise:
                pyptlist.reverse()
                
            new_floor = py3dmodel.construct.make_polygon(pyptlist)
            new_flr_list.append(new_floor)
            '''
        new_2d_list.append(new_flr_list)
            
    return new_2d_list#, bounding_list

def gml_landuse_2_occface(gml_landuse, citygml_reader):
    lpolygon = citygml_reader.get_polygons(gml_landuse)[0]
    landuse_pts = citygml_reader.polygon_2_pt_list(lpolygon)
    landuse_occface = py3dmodel.construct.make_polygon(landuse_pts)
    return landuse_occface
            
def buildings_on_landuse(gml_landuse, gml_bldg_list, citygml_reader):
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
            face_list = py3dmodel.fetch.geom_explorer(common_cmpd, "face")
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
    
def detect_clash(bldg_occsolid, other_occsolids):
    compound = py3dmodel.construct.make_compound(other_occsolids)
    #extract all the faces as the boolean dun work well with just the solid
    bldg_faces = py3dmodel.fetch.geom_explorer(bldg_occsolid, "face")
    face_cmpd = py3dmodel.construct.make_compound(bldg_faces)
    common_compound = py3dmodel.construct.boolean_common(bldg_occsolid, compound)
    common_compound2 = py3dmodel.construct.boolean_common(face_cmpd, compound)
    is_cmpd_null = py3dmodel.fetch.is_compound_null(common_compound)
    is_cmpd_null2 = py3dmodel.fetch.is_compound_null(common_compound2)
    if is_cmpd_null == True and is_cmpd_null2 == True:
        return False
    else:
        return True
    
def detect_in_boundary(bldg_occsolid, luse_occface):
    luse_occsolid = py3dmodel.construct.extrude(luse_occface,(0,0,1), 10000)
    diff_cmpd = py3dmodel.construct.boolean_difference(bldg_occsolid, luse_occsolid)
    is_cmpd_null = py3dmodel.fetch.is_compound_null(diff_cmpd)
    return is_cmpd_null
            
def get_building_occsolid(gml_bldg, citygml_reader):
    pypolygon_list = citygml_reader.get_pypolygon_list(gml_bldg)
    solid = py3dmodel.construct.make_occsolid_frm_pypolygons(pypolygon_list)
    return solid
    
def get_building_height_storey(gml_bldg, citygml_reader, flr2flr_height = 3):
    height = citygml_reader.get_building_height(gml_bldg)
    nstorey = citygml_reader.get_building_storey(gml_bldg)
    if height == None or nstorey == None:
        bldg_occsolid = get_building_occsolid(gml_bldg, citygml_reader)
        storey_height = flr2flr_height
        height, nstorey = calculate_bldg_height_n_nstorey(bldg_occsolid, storey_height)        
        return height, nstorey, storey_height
    else:
        storey_height = height/nstorey
        return height, nstorey, storey_height
    
def calculate_bldg_height(bldg_occsolid):
    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(bldg_occsolid)
    height = zmax - zmin
    return round(height,2)
    
def calculate_bldg_height_n_nstorey(bldg_occsolid, storey_height):
    height = calculate_bldg_height(bldg_occsolid)
    nstorey = int(math.floor(float(height)/float(storey_height)))
    return height,nstorey
    
def get_building_bounding_footprint(bldg_occsolid):
    xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(bldg_occsolid)
    bounding_footprint = py3dmodel.construct.make_polygon([(xmin,ymin,zmin),(xmin,ymax,zmin),(xmax, ymax, zmin),(xmax, ymin, zmin)])
    return bounding_footprint
    
def get_building_location_pt(bldg_occsolid):
    bounding_footprint = get_building_bounding_footprint(bldg_occsolid)
    loc_pt = py3dmodel.calculate.face_midpt(bounding_footprint)
    return loc_pt
    
def get_bulding_floor_area(gml_bldg, nstorey, storey_height, citygml_reader):
    bldg_occsolid = get_building_occsolid(gml_bldg,citygml_reader)
    flr_plates = get_building_flrplates(bldg_occsolid, nstorey, storey_height)
    flr_area = 0
    for flr in flr_plates:
        flr_area = flr_area + py3dmodel.calculate.face_area(flr)
        
    return flr_area , flr_plates

def reconstruct_building_through_floorplates(bldg_occsolid, bldg_flr_area, storey_height):
    intersection_list = []
    bounding_list = []
    loc_pt  = get_building_location_pt(bldg_occsolid)
    bounding_footprint = get_building_bounding_footprint(bldg_occsolid)
    bldg_footprint_list = get_bldg_footprint_frm_bldg_occsolid(bldg_occsolid)
    intersection_list.extend(bldg_footprint_list)
    scnt = 0
    while bldg_flr_area > 0:
        if scnt == 0:
            for bldg_footprint in bldg_footprint_list:
                flr_area = py3dmodel.calculate.face_area(bldg_footprint)
                bldg_flr_area = bldg_flr_area - flr_area
        else:
            z = loc_pt[2]+((scnt)*storey_height)
            moved_pt = (loc_pt[0], loc_pt[1], z)
            moved_f = py3dmodel.modify.move(loc_pt, moved_pt, bounding_footprint)
            bounding_list.append(py3dmodel.fetch.shape2shapetype(moved_f))
            floors = py3dmodel.construct.boolean_common(bldg_occsolid, moved_f)
            #py3dmodel.construct.visualise([[moved_f,building_solid]], ["WHITE"])
            compound = py3dmodel.fetch.shape2shapetype(floors)
            inter_face_list = py3dmodel.fetch.geom_explorer(compound,"face")
            if inter_face_list:
                for inter_face in inter_face_list:
                    flr_area = py3dmodel.calculate.face_area(inter_face)
                    bldg_flr_area = bldg_flr_area - flr_area
                    intersection_list.append(inter_face)
            else:
                #it means the original solid is not so tall
                #need to move a storey up 
                loc_pt2 = (moved_pt[0], moved_pt[1], (moved_pt[2]-storey_height))
                previous_flr = intersection_list[-1]
                moved_f2 = py3dmodel.fetch.shape2shapetype(py3dmodel.modify.move(loc_pt2, moved_pt, previous_flr))
                flr_area = py3dmodel.calculate.face_area(moved_f2)
                bldg_flr_area = bldg_flr_area - flr_area
                intersection_list.append(moved_f2)

        scnt += 1
            
    last_flr = intersection_list[-1]
    rs_midpt = py3dmodel.calculate.face_midpt(last_flr)
    moved_pt = (rs_midpt[0], rs_midpt[1], (rs_midpt[2]+storey_height))
    roof_srf = py3dmodel.fetch.shape2shapetype(py3dmodel.modify.move(rs_midpt, moved_pt, last_flr))

    intersection_list.append(roof_srf)
    flr_srf = intersection_list[0]
    
    new_building_shell = py3dmodel.construct.make_loft(intersection_list, rule_face = False)
    
    face_list = py3dmodel.fetch.faces_frm_shell(new_building_shell) 
    face_list.append(roof_srf)
    face_list.append(flr_srf)
    closed_shell = py3dmodel.construct.make_shell_frm_faces(face_list)[0]
    shell_list = py3dmodel.fetch.topos_frm_compound(closed_shell)["shell"]
    new_bldg_occsolid = py3dmodel.construct.make_solid(shell_list[0])
    
    return new_bldg_occsolid#, intersection_list, bounding_list

def rotate_bldg(gml_bldg, rot_angle, citygml_reader):
    bldg_occsolid = get_building_occsolid(gml_bldg,citygml_reader)
    loc_pt = get_building_location_pt(bldg_occsolid)
    rot_bldg_occshape = py3dmodel.modify.rotate(bldg_occsolid, loc_pt, (0,0,1), rot_angle)
    rot_bldg_occsolid = py3dmodel.fetch.geom_explorer(rot_bldg_occshape, "solid")[0]
    return rot_bldg_occsolid
    
def landuse_2_grid(landuse_occface, xdim, ydim):
    pt_list = []
    grid_faces = py3dmodel.construct.grid_face(landuse_occface, xdim, ydim)
    for f in grid_faces:
        pt = py3dmodel.calculate.face_midpt(f)
        pt_list.append(pt)
        
    return pt_list, grid_faces

def rearrange_building_position(bldg_occsolid_list, luse_gridded_pypt_list, luse_occface, parameters, other_occsolids = [], clash_detection = True, 
                                boundary_detection = True):
    
    moved_buildings = []
    n_other_occsolid = len(other_occsolids)
    moved_buildings.extend(other_occsolids)
    npypt_list = len(luse_gridded_pypt_list)
    nbldgs = len(bldg_occsolid_list)
    for cnt in range(nbldgs):      
        bldg_occsolid = bldg_occsolid_list[cnt]
        pos_parm = parameters[cnt]
        loc_pt = get_building_location_pt(bldg_occsolid)
        
        isclash = True
        for clash_cnt in range(npypt_list):
            #print "clash_cnt", clash_cnt
            #map the location point to the grid points
            mpt_index = pos_parm+clash_cnt
            if mpt_index >= npypt_list:
                mpt_index = mpt_index-(npypt_list-1) 
                
            moved_pt = luse_gridded_pypt_list[mpt_index]
            moved_solid = py3dmodel.fetch.shape2shapetype(py3dmodel.modify.move(loc_pt, moved_pt, bldg_occsolid))
            #shell = py3dmodel.fetch.geom_explorer(moved_solid,"shell")[0]
            moved_solid = py3dmodel.modify.fix_close_solid(moved_solid)
            #=======================================================================================
            if clash_detection == True and boundary_detection == False:
                if moved_buildings:
                    clash_detected = detect_clash(moved_solid, moved_buildings)                    
                    if not clash_detected:
                        #means there is no intersection and there is no clash
                        #print "I am not clashing onto anyone!!!"
                        isclash = False
                        break
                
                else:
                    isclash = False
                    break
                
            #=======================================================================================
            elif boundary_detection == True and clash_detection == False:
                is_in_boundary = detect_in_boundary(moved_solid, luse_occface)
                if is_in_boundary:
                    isclash = False
                    break
            #=======================================================================================
            elif boundary_detection == True and clash_detection == True:
                #need to check if the moved building is within the boundaries of the landuse 
                is_in_boundary = detect_in_boundary(moved_solid, luse_occface)
                    
                if is_in_boundary:
                    #test if it clashes with the other buildings 
                    if moved_buildings:
                        clash_detected = detect_clash(moved_solid, moved_buildings)                    
                        if not clash_detected:
                            #print "I am not clashing onto anyone!!!"
                            isclash = False
                            break
                    
                    else:
                        isclash = False
                        break
            #=======================================================================================  
            elif clash_detection == False and boundary_detection == False:
                isclash = False
                break
            
        if isclash == True:
            print "it is not feasible with these parameters to create a design variant"
            #just append the original arrangements into the list
            return bldg_occsolid_list
        
        if isclash == False:
            #print "successfully positioned the building"
            moved_buildings.append(moved_solid)
            
    if other_occsolids:
        moved_buildings = moved_buildings[n_other_occsolid:]
    print "successfully positioned the buildings"
    return moved_buildings
    
#===========================================================================================================================
def update_gml_building(orgin_gml_building, new_bldg_occsolid, citygml_reader, citygml_writer, 
                        new_height = None, new_nstorey = None):
    building_name = citygml_reader.get_gml_id(orgin_gml_building)
    bclass = citygml_reader.get_building_class(orgin_gml_building)
    bfunction = citygml_reader.get_building_function(orgin_gml_building)
    rooftype = citygml_reader.get_building_rooftype(orgin_gml_building)
    stry_blw_grd = citygml_reader.get_building_storey_blw_grd(orgin_gml_building)
    #generic_attrib_dict = citygml_reader.get_generic_attribs(orgin_gml_building)        
    new_bldg_occsolid = py3dmodel.fetch.geom_explorer(new_bldg_occsolid, "solid")[0]
    new_bldg_occsolid = py3dmodel.modify.fix_close_solid(new_bldg_occsolid)
    face_list = py3dmodel.fetch.faces_frm_solid(new_bldg_occsolid)
    geometry_list = write_gml_srf_member(face_list)
    if new_height == None:
        new_height = calculate_bldg_height(new_bldg_occsolid)
        
    if new_nstorey !=None:
        citygml_writer.add_building("lod1", building_name, geometry_list, bldg_class =  bclass, 
                                    function = bfunction, usage = bfunction, rooftype = rooftype,height = str(new_height),
                                    stry_abv_grd = str(new_nstorey), stry_blw_grd = stry_blw_grd)
    if new_nstorey ==None:
        citygml_writer.add_building("lod1", building_name, geometry_list, bldg_class =  bclass, 
                                    function = bfunction, usage = bfunction, rooftype = rooftype,height = str(new_height),
                                    stry_blw_grd = stry_blw_grd)
        
def write_citygml(cityobjmembers, citygml_writer):
        citygml_root = citygml_writer.citymodelnode
        for cityobj in cityobjmembers:
            citygml_root.append(cityobj)
            
def write_non_eligible_bldgs(non_eligible_bldgs, citygml_writer):
    citygml_root = citygml_writer.citymodelnode
    for non_eligible_bldg in non_eligible_bldgs:
        city_obj = citygml_writer.create_cityobjectmember()
        city_obj.append(non_eligible_bldg)
        citygml_root.append(city_obj)
            
#===========================================================================================================================
#for massing2gml
#===========================================================================================================================
def write_a_gml_srf_member(occface):
    pypt_list = py3dmodel.fetch.pyptlist_frm_occface(occface)
    #pypt_list = py3dmodel.modify.rmv_duplicated_pts(pypt_list, roundndigit = 6)
    if len(pypt_list)>=3:
        face_nrml = py3dmodel.calculate.face_normal(occface)
        is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pypt_list, face_nrml)
        if is_anticlockwise == False:
            pypt_list.reverse()
    
        first_pt = pypt_list[0]
        pypt_list.append(first_pt)
        srf = pycitygml.gmlgeometry.SurfaceMember(pypt_list)
        return srf
    else:
        return None
    
def write_gml_srf_member(occface_list):
    gml_geometry_list = []
    for face in occface_list:
        srf = write_a_gml_srf_member(face)
        if srf != None:
            gml_geometry_list.append(srf)

    return gml_geometry_list

def write_gml_triangle(occface_list):
    gml_geometry_list = []
    for face in occface_list:
        pypt_list = py3dmodel.fetch.pyptlist_frm_occface(face)
        n_pypt_list = len(pypt_list)
        if n_pypt_list>3:
            occtriangles = py3dmodel.construct.simple_mesh(face)
            for triangle in occtriangles:
                is_face_null = py3dmodel.fetch.is_face_null(triangle)
                if not is_face_null:
                    t_pypt_list = py3dmodel.fetch.pyptlist_frm_occface(triangle)
                    #face_nrml = py3dmodel.calculate.face_normal(triangle)
                    #is_anticlockwise = py3dmodel.calculate.is_anticlockwise(t_pypt_list, face_nrml)
                    #if is_anticlockwise == False:
                    #    t_pypt_list.reverse()
                    gml_tri = pycitygml.gmlgeometry.Triangle(t_pypt_list)
                    gml_geometry_list.append(gml_tri)
        else:
            #face_nrml = py3dmodel.calculate.face_normal(face)
            #is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pypt_list, face_nrml)
            #if is_anticlockwise == False:
            #    pypt_list.reverse()
            gml_tri = pycitygml.gmlgeometry.Triangle(pypt_list)
            gml_geometry_list.append(gml_tri)
            
    return gml_geometry_list
    
def write_gml_linestring(occedge):
    gml_edge_list = []
    occpt_list = py3dmodel.fetch.points_from_edge(occedge)
    pypt_list = py3dmodel.fetch.occptlist2pyptlist(occpt_list)
    linestring = pycitygml.gmlgeometry.LineString(pypt_list)
    gml_edge_list.append(linestring)
    return gml_edge_list
    
def extrude_move_down_occ_faces(occface_list):
    extrude_list = []
    for occface in occface_list:
        midpt = py3dmodel.calculate.face_midpt(occface)
        loc_pt = py3dmodel.modify.move_pt(midpt, (0,0,-1),1)
        #move the face down
        m_occface = py3dmodel.modify.move(midpt, loc_pt, occface)
        m_occface = py3dmodel.fetch.shape2shapetype(m_occface)
        #extrude the face
        extrude = py3dmodel.construct.extrude(m_occface, (0,0,1), 2)
        extrude_list.append(extrude)
    return extrude_list
    
def redraw_occ_faces(occface_list):
    recon_faces = []
    for occface in occface_list:
        pyptlist = py3dmodel.fetch.pyptlist_frm_occface(occface)
        recon_face = py3dmodel.construct.make_polygon(pyptlist)
        recon_faces.append(recon_face)
    return recon_faces
            
def redraw_occ_shell(occcompound, tolerance):
    recon_shelllist = []
    shells = py3dmodel.fetch.geom_explorer(occcompound, "shell")
    for shell in shells:
        faces = py3dmodel.fetch.geom_explorer(shell, "face")
        recon_faces = []
        for face in faces:
            pyptlist = py3dmodel.fetch.pyptlist_frm_occface(face)
            recon_face = py3dmodel.construct.make_polygon(pyptlist)
            recon_faces.append(recon_face)
        nrecon_faces = len(recon_faces)
        if nrecon_faces == 1:
            recon_shell = py3dmodel.construct.make_shell(recon_faces)
        if nrecon_faces > 1:
            #py3dmodel.construct.visualise([recon_faces], ['WHITE'])
            recon_shell = py3dmodel.construct.make_shell_frm_faces(recon_faces, tolerance = tolerance )[0]
        recon_shelllist.append(recon_shell)    
        
    recon_compound = py3dmodel.construct.make_compound(recon_shelllist)
    return recon_compound
    
def redraw_occ_edge(occcompound, tolerance):
    edges = py3dmodel.fetch.geom_explorer(occcompound, "edge")
    recon_edgelist = []
    for edge in edges:
        eptlist = py3dmodel.fetch.points_from_edge(edge)
        epyptlist = py3dmodel.fetch.occptlist2pyptlist(eptlist)
        recon_edgelist.append(py3dmodel.construct.make_edge(epyptlist[0], epyptlist[1]))
        
    recon_compound = py3dmodel.construct.make_compound(recon_edgelist)
    return recon_compound
        
def identify_open_close_shells(occshell_list):
    close_shell_list = []
    open_shell_list = []
    for shell in occshell_list:
        is_closed = py3dmodel.calculate.is_shell_closed(shell)
        if is_closed:
            close_shell_list.append(shell)
        else:
            open_shell_list.append(shell)
            
    return close_shell_list, open_shell_list
    
def reconstruct_open_close_shells(occshell_list):
    close_shell_list, open_shell_list = identify_open_close_shells(occshell_list)
    if open_shell_list:
        open_shell_compound = py3dmodel.construct.make_compound(open_shell_list)
        open_shell_faces = py3dmodel.fetch.geom_explorer(open_shell_compound, "face")
        #sew all the open shell faces together to check if there are solids among the open shells
        recon_shell_list = py3dmodel.construct.make_shell_frm_faces(open_shell_faces)
        recon_close_shell_list, recon_open_shell_list = identify_open_close_shells(recon_shell_list)
        if recon_close_shell_list:
            open_shell_list2 = []
            open_shell_rmv_index = []
            #boolean difference the close shells from the open shells 
            for recon_close_shell in recon_close_shell_list:
                os_cnt = 0
                for open_shell in open_shell_list:
                    #common_cmpd = py3dmodel.construct.boolean_common(recon_close_shell, open_shell)
                    difference_cmpd = py3dmodel.construct.boolean_difference(open_shell, recon_close_shell)
                    is_diff_null = py3dmodel.fetch.is_compound_null(difference_cmpd)
                    if is_diff_null:
                        open_shell_rmv_index.append(os_cnt)
                    os_cnt+=1
                    
            for os_cnt2 in range(len(open_shell_list)):
                if os_cnt2 not in open_shell_rmv_index:
                    open_shell2 = open_shell_list[os_cnt2]
                    open_shell_list2.append(open_shell2)
                    
            return close_shell_list + recon_close_shell_list + open_shell_list2
        else:
            return occshell_list
    else:
        return occshell_list
        
def reconstruct_bldg_shell(bldg_occshell):
    bldg_occsolid = py3dmodel.construct.make_solid(bldg_occshell)
    bldg_occsolid = py3dmodel.modify.fix_close_solid(bldg_occsolid)
    intersection_list = []
    bounding_list = []
    loc_pt  = get_building_location_pt(bldg_occsolid)
    bounding_footprint = get_building_bounding_footprint(bldg_occsolid)
    
    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(bldg_occsolid)
    height = zmax-zmin
    flr_height = 3.0
    remainder = height%flr_height
    division = int(height/flr_height)
    if remainder >0:
        division = int(math.ceil(division))
        flr_height = height/math.ceil(division)
    
    for scnt in range(division):
        if scnt==0:
            moved_pt = (loc_pt[0], loc_pt[1], loc_pt[2]-0.1)
            moved_bldg_occsolid = py3dmodel.modify.move(loc_pt,moved_pt, bldg_occsolid)
            #intersection_list.append(moved_bldg_occsolid)
            flr1_list = py3dmodel.construct.boolean_common(moved_bldg_occsolid,bounding_footprint)
            flr1_list = py3dmodel.fetch.geom_explorer(flr1_list, "face")
            nflr1 = len(flr1_list)
            if nflr1 > 1:
                break
            flr1 = flr1_list[0]
            
        if scnt !=0 or scnt !=division-1:
            z = loc_pt[2]+((scnt)*flr_height)
            moved_pt = (loc_pt[0], loc_pt[1], z)
            moved_f = py3dmodel.modify.move(loc_pt, moved_pt, bounding_footprint)
            bounding_list.append(py3dmodel.fetch.shape2shapetype(moved_f))
            
        if scnt == division-1:
            z = loc_pt[2]+((scnt)*flr_height)
            moved_pt = (loc_pt[0], loc_pt[1], z)
            moved_f = py3dmodel.modify.move(loc_pt, moved_pt, bounding_footprint)
            
            moved_pt = (loc_pt[0], loc_pt[1], loc_pt[2]+0.1)
            moved_bldg_occsolid = py3dmodel.modify.move(loc_pt,moved_pt, bldg_occsolid)
            flr_last = py3dmodel.construct.boolean_common(moved_bldg_occsolid,moved_f )
            flr_last = py3dmodel.fetch.geom_explorer(flr_last, "face")[0]
        
    if nflr1 ==1:
        bounding_cmpd = py3dmodel.construct.make_compound(bounding_list)
        floors = py3dmodel.construct.boolean_common(bounding_cmpd, bldg_occsolid)
        floors = py3dmodel.fetch.geom_explorer(floors, "face")
        intersection_list.append(flr1)
        intersection_list.extend(floors)
        intersection_list.append(flr_last)
    
        loft = py3dmodel.construct.make_loft(intersection_list)
        loft = py3dmodel.fetch.shape2shapetype(loft)
        lface_list = py3dmodel.fetch.geom_explorer(loft, "face")
        
        recon_faces = []
        recon_faces.append(flr1)
        recon_faces.extend(lface_list)
        recon_faces.append(flr_last)
        recon_shell = py3dmodel.construct.make_shell_frm_faces(recon_faces)[0]
        recon_shell = py3dmodel.modify.fix_shell_orientation(recon_shell)
        r_loft_faces = py3dmodel.construct.simple_mesh(recon_shell)
        recon_shell = py3dmodel.construct.make_shell_frm_faces(r_loft_faces)[0]
        recon_shell = py3dmodel.modify.fix_shell_orientation(recon_shell)
        return recon_shell
    else:
        return bldg_occshell
        
def is_shell_faces_planar(occshell):
    face_list = py3dmodel.fetch.geom_explorer(occshell, "face")
    for face in face_list:
        is_face_planar = py3dmodel.calculate.is_face_planar(face, 1e-06)
        if not is_face_planar:
            return False
    return True
    
def is_shell_simple(occshell):
    #if the shell has more than triangle polygon and has more than 6 faces
    #it is not simple
    face_list = py3dmodel.fetch.geom_explorer(occshell, "face")
    nface = len(face_list)
    for face in face_list:
        pypt_list = py3dmodel.fetch.pyptlist_frm_occface(face)
        npypt = len(pypt_list)
        if npypt == 3 and nface>6:
            return False
    return True

def citygml2collada(citygml_filepath, collada_filepath):
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
        bldg_shell_list = py3dmodel.fetch.geom_explorer(solid, "shell")
        occshell_list.extend(bldg_shell_list)

    for landuse in landuses:
        lpolygons = reader.get_polygons(landuse)
        if lpolygons:
            for lpolygon in lpolygons:
                landuse_pts = reader.polygon_2_pt_list(lpolygon)
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
            edge_list = py3dmodel.fetch.geom_explorer(occ_wire, "edge")
            occedge_list.extend(edge_list)
    
    for rail in railways:
        polylines = reader.get_pylinestring_list(rail)
        for polyline in polylines:
            occ_wire = py3dmodel.construct.make_wire(polyline)
            edge_list = py3dmodel.fetch.geom_explorer(occ_wire, "edge")
            occedge_list.extend(edge_list)
            
    for stop in stops:
        pypolgon_list = reader.get_pypolygon_list(stop)
        solid = py3dmodel.construct.make_occsolid_frm_pypolygons(pypolgon_list)
        stop_shell_list = py3dmodel.fetch.geom_explorer(solid, "shell")
        occshell_list.extend(stop_shell_list)
    
    utility3d.write_2_collada(occshell_list, collada_filepath, occedge_list = occedge_list)
    
        
    