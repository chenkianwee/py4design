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
import os
import math
import shutil
import tempfile
    
from . import utility
from . import py3dmodel
from . import urbangeom
from . import py2radiance
from . import shapeattributes
#================================================================================================================
#ETTV
#================================================================================================================
def calc_ettv( srfs_shp_attribs_obj_list, epwweatherfile, mode = "ettv"):
    """
    This function calculates the ETTV or RETV of a building.
    
    Parameters
    ----------
    srfs_shp_attribs_obj_list : list of ShapeAttributes objects
        The geometry with all the attributes required for the calculation. All the surfaces of the buildings need to be defined through these functions:
        create_opaque_srf_shape_attribute(), create_glazing_shape_attribute(), create_shading_srf_shape_attribute(). 
    
    epwweatherfile : str
        The file path of the epw weatherfile.
    
    mode : str
        The calculation mode, options are "ettv" or "retv".
    
    Returns
    -------
    result dictionary : dictionary
        A dictionary with this keys : {mode, "facade_area", "rttv", "roof_area"}. The key mode is dependent on what the user has specified at the mode parameter, so it can be ettv/retv.
        
        mode("ettv" or "retv") : float
            The ETTV/RETV of the building.
        
        facade_area : float
            The area of the facade.
        
        rttv : float
            The Roof Thermal Transfer Value of the building.   
        
        roof_area : float
            The area of the roof of the building. 
    """
    
    srfs_shp_attribs_obj_list = calc_dir_pitch_angle(srfs_shp_attribs_obj_list, mode = mode)
    srfs_shp_attribs_obj_list = glazing_sc2(srfs_shp_attribs_obj_list,epwweatherfile)
    cf_list = []
    #find all the unique cfs
    for srf_shp_attribs in srfs_shp_attribs_obj_list:
        srf_type = srf_shp_attribs.get_value("type")
        if srf_type == "wall" or srf_type == "roof" or srf_type == "window" or srf_type == "skylight":
            cf = srf_shp_attribs.get_value("cf")
            if cf not in cf_list:
                cf_list.append(cf)

    ettv_area_list = []
    cf_facade_area_list = []
    rttv_area_list = []
    cf_rf_area_list = []
    for ref_cf in cf_list:
        ref_cf_facade_area = 0
        ref_cf_rf_area = 0
        wall_area_uvalue_list = []
        roof_area_uvalue_list = []
        win_area_uvalue_list = []
        win_area_sc_list = []
        skylight_area_uvalue_list = []
        skylight_area_sc_list = []
        
        for srf_shp_attribs in srfs_shp_attribs_obj_list:
            srf_type = srf_shp_attribs.get_value("type")
            if srf_type == "wall" or srf_type == "roof" or srf_type == "window" or srf_type == "skylight":
                cf = srf_shp_attribs.get_value("cf")
                
                if cf == ref_cf:
                    occ_face = srf_shp_attribs.shape
                    area = py3dmodel.calculate.face_area(occ_face)
                    uvalue = srf_shp_attribs.get_value("uvalue")
                    if srf_type == "wall":
                        ref_cf_facade_area+=area
                        wall_area_uvalue = area*uvalue
                        wall_area_uvalue_list.append(wall_area_uvalue)
                    if srf_type == "roof":
                        ref_cf_rf_area+= area
                        roof_area_uvalue = area*uvalue
                        roof_area_uvalue_list.append(roof_area_uvalue)
                    if srf_type == "window":
                        ref_cf_facade_area+=area
                        win_area_uvalue = area*uvalue
                        win_area_uvalue_list.append(win_area_uvalue)
                        sc = srf_shp_attribs.get_value("sc")
                        win_area_sc = area*sc
                        win_area_sc_list.append(win_area_sc)
                    if srf_type == "skylight":
                        ref_cf_rf_area+= area
                        skylight_area_uvalue = area*uvalue
                        skylight_area_uvalue_list.append(skylight_area_uvalue)
                        sc = srf_shp_attribs.get_value("sc")
                        skylight_area_sc = area*sc
                        skylight_area_sc_list.append(skylight_area_sc)
           
        if ref_cf_rf_area !=0:
            cf_rttv_wallcon = (sum(roof_area_uvalue_list) * 12.5)/ref_cf_rf_area
            cf_rttv_wincon = (sum(skylight_area_uvalue_list) * 4.8)/ref_cf_rf_area
            cf_rttv_winrad = (sum(skylight_area_sc_list) * 485 * ref_cf)/ref_cf_rf_area 
            cf_rttv = cf_rttv_wallcon + cf_rttv_wincon + cf_rttv_winrad
            rttv_area_list.append(cf_rttv * ref_cf_rf_area)
            cf_rf_area_list.append(ref_cf_rf_area)
            
        if mode == "ettv":
            if ref_cf_facade_area !=0:
                cf_ettv_wallcon = (sum(wall_area_uvalue_list) * 12)/ref_cf_facade_area
                cf_ettv_wincon = (sum(win_area_uvalue_list) * 3.4)/ref_cf_facade_area
                cf_ettv_winrad = (sum(win_area_sc_list) * 211 * ref_cf)/ref_cf_facade_area 
                cf_ettv = cf_ettv_wallcon + cf_ettv_wincon + cf_ettv_winrad
                ettv_area_list.append(cf_ettv * ref_cf_facade_area)
                cf_facade_area_list.append(ref_cf_facade_area)
        if mode == "retv":
            if ref_cf_facade_area !=0:
                cf_retv_wallcon = (sum(wall_area_uvalue_list) * 3.4)/ref_cf_facade_area
                cf_retv_wincon = (sum(win_area_uvalue_list) * 1.3)/ref_cf_facade_area
                cf_retv_winrad = (sum(win_area_sc_list) * 58.6 * ref_cf)/ref_cf_facade_area 
                cf_retv = cf_retv_wallcon + cf_retv_wincon + cf_retv_winrad
                ettv_area_list.append(cf_retv * ref_cf_facade_area)
                cf_facade_area_list.append(ref_cf_facade_area)

    total_facade_area = sum(cf_facade_area_list)
    ettv = sum(ettv_area_list)/total_facade_area
    total_rf_area = sum(cf_rf_area_list)
    rttv = sum(rttv_area_list)/total_rf_area
    result_dict = {}

    result_dict[mode] = ettv
    result_dict["facade_area"] = total_facade_area
    result_dict["rttv"] = rttv
    result_dict["roof_area"] = total_rf_area
    return result_dict

def calc_env_conductance(srfs_shp_attribs_obj_list):
    """
    This function calculates the ETTV or RETV of a building.
    
    Parameters
    ----------
    srfs_shp_attribs_obj_list : list of ShapeAttributes objects
        The geometry with all the attributes required for the calculation. All the surfaces of the buildings need to be defined through these functions:
        create_opaque_srf_shape_attribute(), create_glazing_shape_attribute(), create_shading_srf_shape_attribute(). 
    
    Returns
    -------
    env_conductance : float
        The envelope thermal conductance (W/K)
        
    """
    conductance_list = []
    for srf_shp_attribs in srfs_shp_attribs_obj_list:
        srf_type = srf_shp_attribs.get_value("type")
        if srf_type == "wall" or srf_type == "roof" or srf_type == "window" or srf_type == "skylight":
                occ_face = srf_shp_attribs.shape
                area = py3dmodel.calculate.face_area(occ_face)
                uvalue = srf_shp_attribs.get_value("uvalue")
                conductance = area*uvalue
                conductance_list.append(conductance)
    env_conductance = sum(conductance_list)
    return env_conductance

def cal_envelope_conductance_load(srfs_shp_attribs_obj_list, outdoor_temp, indoor_temp):
    """
    This function calculates the ETTV or RETV of a building.
    
    Parameters
    ----------
    srfs_shp_attribs_obj_list : list of ShapeAttributes objects
        The geometry with all the attributes required for the calculation. All the surfaces of the buildings need to be defined through these functions:
        create_opaque_srf_shape_attribute(), create_glazing_shape_attribute(), create_shading_srf_shape_attribute().
        
    outdoor_temp : float
        The outdoor air temperature in (C).
    
    indoor_temp : float
        The indoor air temperature in (C).
    
    Returns
    -------
    env_conduct_load : float
        The envelope conductance load(W)
        
    """
    env_conductance = calc_env_conductance(srfs_shp_attribs_obj_list)
    td = outdoor_temp - indoor_temp
    env_cond_load = env_conductance*td
    return env_cond_load
    
def glazing_sc2(srfs_shp_attribs_obj_list, epwweatherfile):
    """
    This function calculates the shading coefficient 2 of the glazings.
    
    Parameters
    ----------
    srfs_shp_attribs_obj_list : list of ShapeAttributes objects
        The geometry with all the attributes required for the calculation. All the surfaces of the buildings need to be defined through these functions:
        create_opaque_srf_shape_attribute(), create_glazing_shape_attribute(), create_shading_srf_shape_attribute(). 
    
    epwweatherfile : str
        The file path of the epw weatherfile.
    
    Returns
    -------
    srfs_shp_attribs_obj_list : list of ShapeAttributes objects
        List of ShapeAttributes objects appended with the sc2 attribute.
        
    """
    
    rad_base_filepath = os.path.join(os.path.dirname(__file__),'py2radiance','base.rad')
    #radiance simulation for shaded windows
    rad_folderpath = tempfile.mkdtemp()
    rad = py2radiance.Rad(rad_base_filepath, rad_folderpath) #with shades
    #radiance simulation for unshaded windows
    rad_folderpath2 = tempfile.mkdtemp()
    rad2 = py2radiance.Rad(rad_base_filepath, rad_folderpath2) #without shades
    
    #loop thru the geometries and set up the radiance scene
    srfmat = "RAL2012" #reflectivity of 0.2 materials in the base file
    sensor_ptlist = []
    sensor_dirlist = []
    sensor_surfacelist = []
    other_occface_list = []
    scnt = 0
    pcnt = 0
    for srf_shp_attribs in srfs_shp_attribs_obj_list:
        srf_type = srf_shp_attribs.get_value("type")
        occ_face = srf_shp_attribs.shape
        pypolygon = py3dmodel.fetch.points_frm_occface(occ_face)
        srfname = "srf" + str(scnt)
        if srf_type == "window" or srf_type == "skylight":
            sensor_surfaces, sensor_pts, sensor_dirs = urbangeom.generate_sensor_surfaces(occ_face, 1, 1)
            sensor_ptlist.extend(sensor_pts)
            sensor_dirlist.extend(sensor_dirs)
            sensor_surfacelist.extend(sensor_surfaces)
            n_sensor_srfs = len(sensor_ptlist)
            
            srf_shp_attribs.set_key_value("sensor_indices", [n_sensor_srfs-len(sensor_pts), n_sensor_srfs])
            
            py2radiance.RadSurface(srfname, pypolygon, srfmat, rad)
            py2radiance.RadSurface(srfname, pypolygon, srfmat, rad2)
            pcnt+=n_sensor_srfs
        else:
            py2radiance.RadSurface(srfname, pypolygon, srfmat, rad)
            other_occface_list.append(occ_face)
            
        scnt += 1
            
    time = str(0) + " " + str(24)
    date = str(1) + " " + str(1) + " " + str(12) + " " + str(31)
    #calculate the shaded windows and skylight
    rad.set_sensor_points(sensor_ptlist, sensor_dirlist)
    rad.create_sensor_input_file()
    rad.create_rad_input_file()
    rad.execute_cumulative_oconv(time, date, epwweatherfile)
    rad.execute_cumulative_rtrace(str(1))#EXECUTE!! 
    irrad_ress = rad.eval_cumulative_rad()
    #calculate the unshaded windows and skylight
    rad2.set_sensor_points(sensor_ptlist, sensor_dirlist)
    rad2.create_sensor_input_file()
    rad2.create_rad_input_file()
    rad2.execute_cumulative_oconv(time, date, epwweatherfile)
    rad2.execute_cumulative_rtrace(str(1))#EXECUTE!! 
    irrad_ress2 = rad2.eval_cumulative_rad()
    
    #calculate the avg solar irradiance and the sc2 
    for srf_shp_attribs in srfs_shp_attribs_obj_list:
        srf_type = srf_shp_attribs.get_value("type")
        if srf_type == "window" or srf_type == "skylight":
            sensor_indices = srf_shp_attribs.get_value("sensor_indices")
            index1 = sensor_indices[0]
            index2 = sensor_indices[1]
            
            glz_ress1 = irrad_ress[index1:index2]
            glz_ress2 = irrad_ress2[index1:index2]
            glz_srfs = sensor_surfacelist[index1:index2]
            
            glz_area_list = []
            glz_area_res_list1 = []
            glz_area_res_list2 = []
            for glz_cnt in range(len(glz_srfs)):
                glz_area = py3dmodel.calculate.face_area(glz_srfs[glz_cnt])
                glz_area_res1 = glz_ress1[glz_cnt]*glz_area
                glz_area_res2 = glz_ress2[glz_cnt]*glz_area
                glz_area_list.append(glz_area)
                glz_area_res_list1.append(glz_area_res1)
                glz_area_res_list2.append(glz_area_res2)
                
            total_glz_area = sum(glz_area_list)
            total_glz_area_res1 = sum(glz_area_res_list1)
            total_glz_area_res2 = sum(glz_area_res_list2)
            avg_glz_res1 = total_glz_area_res1/total_glz_area
            avg_glz_res2 = total_glz_area_res2/total_glz_area
            sc1 = srf_shp_attribs.get_value("sc1")
            sc2 = avg_glz_res1/avg_glz_res2
            sc = sc1*sc2
            srf_shp_attribs.set_key_value("sc2", sc2)
            srf_shp_attribs.set_key_value("sc", sc)
            
    shutil.rmtree(rad_folderpath)
    shutil.rmtree(rad_folderpath2)
    return srfs_shp_attribs_obj_list

def calc_dir_pitch_angle(srfs_shp_attribs_obj_list, mode = "ettv"):
    """
    This function calculates the Correction factor, direction and pitch angle of each face of the building.
    
    Parameters
    ----------
    srfs_shp_attribs_obj_list : list of ShapeAttributes objects
        The geometry with all the attributes required for the calculation. All the surfaces of the buildings need to be defined through these functions:
        create_opaque_srf_shape_attribute(), create_glazing_shape_attribute(), create_shading_srf_shape_attribute(). 
    
    mode : str
        The calculation will be done according to whether it is for "ettv" or "retv" calculation.
        
    Returns
    -------
    srfs_shp_attribs_obj_list : list of ShapeAttributes objects
        List of ShapeAttributes objects appended with the "cf", "pitch_angle" and "direction" attributes.
        
    """
    for srf_shp_attribs in srfs_shp_attribs_obj_list:
        srf_type = srf_shp_attribs.get_value("type")
        if srf_type == "wall" or srf_type == "roof" or srf_type == "window" or srf_type == "skylight":
            occ_face = srf_shp_attribs.shape
            #calculate the correction factor
            nrml = py3dmodel.calculate.face_normal(occ_face)
            #measure the pitch angle
            ref_pitch_vec = (0,0,1)
            pitch_angle = py3dmodel.calculate.angle_bw_2_vecs(ref_pitch_vec, nrml)
            if pitch_angle !=0:
                #measure direction
                ref_dir_vec = (0,1,0)
                ref_plane_vec = (0,0,1)
                flatten_nrml = (nrml[0],nrml[1],0)
                #the angle is measuring counter-clockwise
                dir_angle = py3dmodel.calculate.angle_bw_2_vecs_w_ref(ref_dir_vec,flatten_nrml, ref_plane_vec)
                                                                      
                if 22.5>=dir_angle>=0:
                    direction = "north"
                if 360>=dir_angle>=337.5:
                    direction = "north"
                if 67.5>dir_angle>22.5:
                    direction = "northwest"
                if 112.5>=dir_angle>=67.5:
                    direction = "west"
                if 157.5>dir_angle>112.5:
                    direction = "southwest"
                if 202.>=dir_angle>=157.5:
                    direction = "south"
                if 247.5>dir_angle>202.5:
                    direction = "southeast"
                if 292.5>=dir_angle>=247.5:
                    direction = "east"
                if 337.5>dir_angle>292.5:
                    direction = "northeast"
            else:
                direction = "north"
                
            #get the correction factor for all the surfaces
            if srf_type == "roof" or srf_type == "skylight":
                cf_filepath = os.path.join(os.path.dirname(__file__),'databases','ettv','rttv_correctionfactor_roof.csv')
                pitch_angle = utility.round2nearest_base(pitch_angle)
                if pitch_angle < 0:
                    print("error: pitch angle" + str(pitch_angle) + "out of range... choosing the nearest angle 0")
                    cf = read_cf_file(cf_filepath, 0, direction)
                elif pitch_angle > 65:
                    print("error: pitch angle" + str(pitch_angle) + "out of range... choosing the nearest angle 65")
                    cf = read_cf_file(cf_filepath, 65, direction)#TODO: fix this 
                else:
                    cf = read_cf_file(cf_filepath, pitch_angle, direction)
                    
            if srf_type == "wall" or srf_type == "window": 
                if mode == "ettv":
                    cf_filepath = os.path.join(os.path.dirname(__file__),'databases','ettv','ettv_correctionfactor_wall.csv')
                    pitch_angle = utility.round2nearest_base(pitch_angle)
                    if pitch_angle < 70:
                        print("error: pitch angle" + str(pitch_angle) + "out of range... choosing the nearest angle 70")
                        cf = read_cf_file(cf_filepath, 70, direction)
                    elif pitch_angle > 120:
                        print("error: pitch angle" + str(pitch_angle) + "out of range... choosing the nearest angle 120")
                        cf = read_cf_file(cf_filepath, 120, direction)#TODO: fix this 
                    else:
                        cf = read_cf_file(cf_filepath, pitch_angle, direction)
                        
                if mode == "retv":
                    cf_filepath = os.path.join(os.path.dirname(__file__),'databases','ettv','retv_correctionfactor_wall.csv')
                    pitch_angle = utility.round2nearest_base(pitch_angle, base=10)
                    if pitch_angle < 70:
                        print("error: pitch angle" + str(pitch_angle) + "out of range... choosing the nearest angle 70")
                        cf = read_cf_file(cf_filepath, 70, direction)
                    elif pitch_angle > 90:
                        print("error: pitch angle" + str(pitch_angle) + "out of range... choosing the nearest angle 90")
                        cf = read_cf_file(cf_filepath, 90, direction)#TODO: fix this 
                    else:
                        cf = read_cf_file(cf_filepath, pitch_angle, direction)
                    
            srf_shp_attribs.set_key_value("cf", cf)
            srf_shp_attribs.set_key_value("pitch_angle", pitch_angle)
            srf_shp_attribs.set_key_value("direction", direction)
            
    return srfs_shp_attribs_obj_list

def create_glazing_shape_attribute(occ_face, uvalue, shading_coefficient1, srf_type):
    """
    This function creates the glazing ShapeAttributes class and its attributes.
    
    Parameters
    ----------
    occ_face : list of OCCfaces
        The faces to be appended with the glazing attributes.
    
    uvalue : float
        The value of the "uvalue" attribute to be appended to the surface.
        
    sc1 : float
        The value of the "sc1" attribute to be appended to the surface.
        
    srf_type : str
        The type of the surface, srf_type can be either "window" or "skylight".
        
    Returns
    -------
    srfs_shp_attribs_obj_list : list of ShapeAttributes objects
        List of ShapeAttributes objects appended with the "uvalue", "sc1" and "type" attributes.
        
    """
    shp_attribs = shapeattributes.ShapeAttributes()
    shp_attribs.set_shape(occ_face)
    shp_attribs.set_key_value("uvalue", uvalue)
    shp_attribs.set_key_value("sc1", shading_coefficient1)
    shp_attribs.set_key_value("type", srf_type)
    return shp_attribs

def create_opaque_srf_shape_attribute(occ_face, uvalue, srf_type):
    """
    This function creates the opaque surface ShapeAttributes class and its attributes.
    
    Parameters
    ----------
    occ_face : list of OCCfaces
        The faces to be appended with the opaque surface attributes.
    
    uvalue : float
        The value of the "uvalue" attribute to be appended to the surface.
        
    srf_type : str
        The type of the surface, srf_type can be either "wall" or "roof".
        
    Returns
    -------
    srfs_shp_attribs_obj_list : list of ShapeAttributes objects
        List of ShapeAttributes objects appended with the "uvalue" and "type" attributes.
        
    """
    shp_attribs = shapeattributes.ShapeAttributes()
    shp_attribs.set_shape(occ_face)
    shp_attribs.set_key_value("uvalue", uvalue)
    shp_attribs.set_key_value("type", srf_type)
    return shp_attribs

def create_shading_srf_shape_attribute(occ_face, srf_type):
    """
    This function creates the shading surface ShapeAttributes class and its attributes.
    
    Parameters
    ----------
    occ_face : list of OCCfaces
        The faces to be appended with the shading attributes.
        
    srf_type : str
        The type of the surface, srf_type can be either "footprint", "shade" or "surrounding".
        
    Returns
    -------
    srfs_shp_attribs_obj_list : list of ShapeAttributes objects
        List of ShapeAttributes objects appended with the "type" attributes.
        
    """
    shp_attribs = shapeattributes.ShapeAttributes()
    shp_attribs.set_shape(occ_face)
    shp_attribs.set_key_value("type", srf_type)
    return shp_attribs

def read_cf_file(filepath, pitch_angle, direction):
    """
    This function reads the correction factor csv file.
    
    Parameters
    ----------
    filepath : str
        The file path of the correction csv file.
        
    pitch_angle : float
        The pitch angle of the surface.
        
    direction : str
        The direction of the surface, the options are "north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest".
        
    Returns
    -------
    correction factor : float
        The correction factor from the csv file.
        
    """
    if direction == "north":
        col = 1
    if direction == "south":
        col = 5
    if direction == "east":
        col = 3
    if direction == "west":
        col = 7
    if direction == "northeast":
        col = 2
    if direction == "northwest":
        col = 8
    if direction == "southeast":
        col = 4
    if direction == "southwest":
        col = 6
    #read the file and get the correction factor
    f = open(filepath, "r")
    lines = f.readlines()
    content_rows = map(lambda x: x.replace("\n",""), lines)
    for row in content_rows:
        ref_pitch_angle = int(row.split(" ")[0])
        if ref_pitch_angle == pitch_angle :
            cf = row.split(" ")[col]
            break 
        else:
            cf = 1 
            
    f.close()
    return float(cf)

#================================================================================================================
#ETTV END
#================================================================================================================
#================================================================================================================
#SIMPLIFIED COOLING ENERGY CONSUMPTION CALCULATION
#================================================================================================================
def calc_cooling_energy_consumption(facade_area, roof_area, floor_area, ettv, rttv, equip_load_per_area = 25.0, 
                                    occ_load_per_person = 75.0, light_load_per_area = 15.0, area_per_person = 10.0,
                                    m3_sec_per_person = 0.006, operation_hrs = 3120):
    
    """
    This function calculates the cooling energy consumption of the conditioned space using two different systems (dvu & radiant panels and central all air).
    
    Parameters
    ----------
    facade_area : float
        The total area of the facade of the conditioned space.
        
    roof_area : float
        The total area of the roof of the conditioned space.
        
    floor_area : float
        The total area of the floor of the conditioned space.
        
    ettv : float
        The ettv/retv of the conditioned space.
    
    rttv : float
        The rttv of the conditioned space.
        
    equip_load_per_area : float, optional
        The equipment load per area of the conditioned space, default = 25.0 W/m2
        
    occ_load_per_person : float, optional
        The occupancy load per person of the conditioned space, default = 75.0 W/person.
    
    light_load_per_area : float, optional
        The lighting load per area of the conditioned space, default = 15.0 W/m2.
        
    area_per_person : float, optional
        The amount of area for a person in the conditioned space, default = 10.0 m2/person.
        
    m3_sec_per_person : float, optional
        The ventilation rate per person of the conditioned space, default = 0.006 m3/person.
        
    operation_hrs : int, optional
        The total operational hours of the conditioned space, default =3120 hrs, assuming a a 12hrs day, 5 days week for 52 weeks a year.
        
    Returns
    -------
    results for the two systems: list of dictionaries
         Refer to radiant_panel_dvu_system() & central_all_air_system() for the description of the dictionaries.
         
    """
    #calculate the loads
    sensible_load = calc_sensible_load(facade_area, roof_area, floor_area, ettv, rttv, equip_load_per_area = equip_load_per_area, 
                       occ_load_per_person = occ_load_per_person, light_load_per_area = light_load_per_area, 
                       area_per_person = area_per_person)
    
    latent_load = calc_vent_load(floor_area, area_per_person = area_per_person, m3_sec_per_person = m3_sec_per_person)
    
    #calculate the consumption if different systems are used
    system_dict_list = []
    rp_dvu_consumption = radiant_panel_dvu_system(sensible_load, latent_load, floor_area, area_per_person = area_per_person, 
                                                  m3_sec_per_person = m3_sec_per_person, operation_hrs = operation_hrs)
    system_dict_list.append(rp_dvu_consumption)
    
    all_air_consumption = central_all_air_system(sensible_load, latent_load, floor_area, operation_hrs = operation_hrs)
    
    system_dict_list.append(all_air_consumption)
    return system_dict_list

def choose_efficient_cooling_system(system_dict_list):
    """
    This function chooses the more efficient systems of the two systems (dvu & radiant panels and central all air).
    
    Parameters
    ----------
    system_dict_list : list of dictionaries
        The systems to be compared and chosen. Refer to radiant_panel_dvu_system() & central_all_air_system() for the description of the dictionaries.
        
    Returns
    -------
    efficient system: list of dictionaries
         The chosen dictionary of the system.
         
    """
    chosen_systems = []
    energy_consumption = float("inf")
    for system_dict in system_dict_list:
        is_feasible = system_dict["feasible"]
        if is_feasible:
            energy_consumed_yr_m2 = system_dict["energy_consumed_yr_m2"]
            if energy_consumed_yr_m2 <= energy_consumption:
                energy_consumption = energy_consumed_yr_m2
                chosen_systems.append(system_dict)
        
    return chosen_systems

def con_free_panels_w_fans(floor_area, supply_temp_c, aust_c, operation_hrs = 3120, out_temp_c = 32.8,
                           m2_per_fan= 10, fan_power = 100, 
                           percent_ceiling = 0.6, chiller_efficiency = 0.4, sup_srf_td = 3.0):
    """
    This function calculates the cooling energy demand of the conditioned space using membrane-assisted radiant panels and fans.
    
    Parameters
    ----------
    floor_area : float
        The floor area of the conditioned space.
        
    supply_temp_c : float
        The chilled water supply temperature required for a comfortable space.
        
    aust_c : float
        The area weighted surface temperature.
        
    operation_hrs : int, optional
        The total operational hours of the conditioned space, default =3120 hrs, assuming a a 12hrs day, 5 days week for 52 weeks a year.
    
    out_temp_c : float, optional
        The air temperature, default =32.8 C, it is the hottest air temp of spore climate.

    m2_per_fan : float, optional
        The area per fan in the space, default = 10m2/fan.
        
    fan_power : float, optional
        The power consumption per fan, default = 100W.
        
    percent_ceiling : float, optional
        The percentage of ceiling for cooling, default = 0.6.
        
    chiller_efficiency : float, optional
        The efficiency of the chiller, default = 0.4. A good chiller can have an efficiency of up to 0.6.
        
    Returns
    -------
    system result dictionary : dictionary
        A dictionary with this keys : {energy_consumed_hr", "energy_consumed_yr", "energy_consumed_yr_m2", "sensible_cop", 
        "required_panel_area", "available_panel_area", "supply_temperature_for_panels", "sensible_load", "sensible_panel", "panel_max_capacity", "cooling_system"}.
        
        energy_consumed_hr : float
            The average energy consumed by the cooling system (Wh).
            
        energy_consumed_yr : float
            The energy consumed by the cooling system in a year (kWh), equals to energy_consumed_hr x operation hours. 
            
        energy_consumed_yr_m2 : float
            The energy consumed by the cooling system in a year normalised by the floor area (kWh/m2), equals to (energy_consumed_hr x operation hours)/floor area. 
        
        sensible_cop : float
            The Coefficient of Performance of the sensible chiller.
            
        available_panel_area : float
            The area available for the radiant panels to provide sensible cooling (m2). 
            
        supply_temperature_for_panels : float
            The supply temperature used by the radiant panels to provide sensible cooling (K).
            
        sensible_load : float
            The sensible load of the conditioned space (W).
        
        nfans : int
            The number of fans.
        
        fan_power : float
            The total energy demand of fans.
            
        cooling_rate : float
            The radiant heat flux from the radiant panel.
            
        cooling_system : str
            Specifies the cooling system used, the value is "Condensation-Free Panels with Fans".
    """
    #calculate the sensible load that needs to be removed by the radiant panels
    panel_srf_area = floor_area*percent_ceiling 
    cooling_rate = calc_con_free_panel(supply_temp_c + 273.15, aust_kelvin = aust_c + 273.15, sup_srf_td = sup_srf_td)
    radiant_load = cooling_rate * panel_srf_area
    nfans = int(floor_area/m2_per_fan)
    
    heat_rejection_temp =  out_temp_c + 273.15
    sens_cop = calc_cooling_cop(supply_temp_c+273.15, heat_rejection_temp, chiller_efficiency = chiller_efficiency)
    energy_consumed_hr = radiant_load/sens_cop#wh
    total_fan_power = nfans*fan_power
    energy_consumed_hr = energy_consumed_hr + total_fan_power
    energy_consumed_yr = (energy_consumed_hr*operation_hrs)/1000 #kwh
    energy_consumed_yr_m2 = energy_consumed_yr/floor_area #kwh
    
    result_dict = {}
    result_dict["energy_consumed_hr"] = energy_consumed_hr
    result_dict["energy_consumed_yr"] = energy_consumed_yr
    result_dict["energy_consumed_yr_m2"] = energy_consumed_yr_m2
    
    result_dict["sensible_cop"] = sens_cop
    result_dict["available_panel_area"] = panel_srf_area
    result_dict["supply_temperature_for_panels"] = supply_temp_c + 273.15
    
    result_dict["sensible_load"] = radiant_load
    result_dict["nfans"] = nfans
    result_dict["fan_power"] = total_fan_power
    result_dict["cooling_rate"] = cooling_rate
    result_dict["cooling_system"] = "Condensation-Free Panels with Fans"
    return result_dict
    
def calc_ach_4_equip(floor_area, flr2flr_height, equip_load, lighting_load, 
                     solar_gain, solve4, mx_ach = 50, air_temp_c = 32.8):
    """
    This function calculates the air change rate required to remove the internal loads and the internal loads to be removed by the panels.
    
    Parameters
    ----------
    floor_area : float
        The floor area of the space (m2).
        
    flr2flr_height : float
        The floor to floor height of the space. This is used to calculate the volume of the space (m). 
                
    win_area : float
        The window area in m2.
    
    equip_load : float
        The equipment load (w/m2). 
        
    lighting_load : float
        The lighting load (w/m2).
        
    solar_gain : float
        The solar load (w).
        
    solve4 : list
        list of parameters only two options ['air_velocity', area of windows in m2: float] or ['win_area', air velocity in m/s: float]
        
    mx_ach : int, optional
        the maximum ACH that can be achieved, default = 50
        
    air_temp_c : float, optional
        The air temperature in C, default = 32.8C.
        
    air_vel : float, optional
        The air velocity in m/s, default = 0.1m/s.
        
    Returns
    -------
    result_dict: dict
         A dictionary with this keys : {"win_area", "temp_increase", "ach"}.
        
        win_area : float
            Required window area.
            
        temp_increase : float
            The increase in air temp due to solar, equip and lighting load.
            
        ach : float
            The air change per hour required to to keep the air temp within the temp increase parameter.
    """
    air_density = 1.225 #kg/m3
    specific_heat_capcity = 1005 #j/kgk
    
    load = (equip_load+lighting_load) * floor_area
    load = load + solar_gain
    vol_rm = floor_area * flr2flr_height
    
    air_temp_c2 = air_temp_c
    tskin = 0.3182*air_temp_c + 22.406
    td_list = [0]
    cnt=1
    while tskin < air_temp_c2:
        allow_td = cnt*0.1
        air_temp_c2 = air_temp_c + allow_td
        tskin = 0.3182*air_temp_c2 + 22.406
        td_list.append(allow_td)
        cnt+=1
    
    if len(td_list) == 1:
        td = 0.1
    else:
        td = td_list[-1]
        
    mass = load/(specific_heat_capcity*td)
    vol = mass/air_density
    vol_hr = vol*3600
    ach = vol_hr/vol_rm
    
    if ach > mx_ach:
        vol_hr = mx_ach*vol_rm
        vol = vol_hr/3600
        mass = vol*air_density
        td = round(load/(mass*specific_heat_capcity), 1)
        ach = mx_ach
    
    if solve4[0] == 'air_velocity':
        win_area = solve4[1]
        air_vel = vol/win_area
        
    elif solve4[1] == 'win_area':
        air_vel = solve4[1]
        win_area = vol/air_vel
        
    res_dict = {'air_vel':air_vel, 'temp_increase':td, 
                'ach':ach, 'win_area':win_area}
    return res_dict

def calc_solar_gain_rad(srfs_shp_attribs_obj_list, epwweatherfile, mode = "max"):
    """
    This function calculates the radiative solar gain from the open windows, daysim is ran to obtain the radiative solar gain.
    
    Parameters
    ----------
    srfs_shp_attribs_obj_list : list of ShapeAttributes objects
        The geometry with all the attributes required for the calculation. All the surfaces of the buildings need to be defined through these functions:
        create_opaque_srf_shape_attribute(), create_glazing_shape_attribute(), create_shading_srf_shape_attribute(). 
    
    epwweatherfile : str
        The file path of the epw weatherfile.
        
    mode : str, optional
        The result to return from the calculation. It can be "max", "99" and "avg". Max returns the maximum solar load, 90 returns the 90 percentile, and "avg" returns the average. Default = "max".
        
    Returns
    -------
    rmv_watts: float
         The remaining watts that is required to be removed by the condensation free panels.
         
    ach_required: float
         The required air change rate required for the air to be of the max air temperature.   
    """
    
    def chose_solar_gain(res, sensor_surfacelist, other_occface_list, mode):
        import numpy as np
        sunhrs = rad.sunuphrs
        zip_res = zip(*res)
        
        watt_list = []
        watt_list2 = []
        for h in zip_res:
            rad_hr = sum(h)
            watt_list.append(rad_hr)
            if rad_hr !=0:
                watt_list2.append(rad_hr)
            
        mx = max(watt_list)

        percentile_99 = np.percentile(watt_list2, 99)
        
        avg_list = []
        for r in res:
            avg = sum(r)/sunhrs
            avg_list.append(avg)
            
        avg = sum(avg_list)
#        mx_index = watt_list.index(mx)
#        hottest_hrs = zip_res[mx_index]
#        cmpd = py3dmodel.construct.make_compound(other_occface_list)
#        edges = py3dmodel.fetch.topo_explorer(cmpd, "edge")
#        py3dmodel.utility.visualise_falsecolour_topo(sensor_surfacelist, hottest_hrs, other_occtopo_2dlist = [edges], other_colour_list = ["BLACK"])
#        dae = "F:\\kianwee_work\\princeton\\journal\\air2srf_conditioning\\model3d\\collada\\solar.dae"
#        py3dmodel.export_collada.write_2_collada_falsecolour(sensor_surfacelist, hottest_hrs, "w/m2",dae, other_occedge_list = edges)
        
        if mode == "max":
            return mx
        elif mode == "99":
            return percentile_99
        elif mode == "avg":
            return avg

    #create all the relevant folders 
    rad_base_filepath = os.path.join(os.path.dirname(__file__),'py2radiance','base.rad')
    data_folderpath = tempfile.mkdtemp()
    rad = py2radiance.Rad(rad_base_filepath, data_folderpath)
    
    #loop thru the geometries and set up the radiance scene
    srfmat = "RAL2012" #reflectivity of 0.2 materials in the base file
    sensor_ptlist = []
    sensor_dirlist = []
    sensor_surfacelist = []
    other_occface_list = []
    scnt = 0
    pcnt = 0
    for srf_shp_attribs in srfs_shp_attribs_obj_list:
        srf_type = srf_shp_attribs.get_value("type")
        occ_face = srf_shp_attribs.shape
        pypolygon = py3dmodel.fetch.points_frm_occface(occ_face)
        srfname = "srf" + str(scnt)
        if srf_type == "footprint":
            sensor_surfaces, sensor_pts, sensor_dirs = urbangeom.generate_sensor_surfaces(occ_face, 1, 1)
            sensor_ptlist.extend(sensor_pts)
            
            n_sensor_srfs = len(sensor_ptlist)
            #make sure the sensor points are always pointing up as the is a footprint
            sensor_dirs = []
            for _ in range(n_sensor_srfs):
                sensor_dirs.append((0,0,1))
                
            sensor_dirlist.extend(sensor_dirs)
            sensor_surfacelist.extend(sensor_surfaces)
            
            srf_shp_attribs.set_key_value("sensor_indices", [n_sensor_srfs-len(sensor_pts), n_sensor_srfs])
            
            py2radiance.RadSurface(srfname, pypolygon, srfmat, rad)
            pcnt+=n_sensor_srfs
            
        elif srf_type == "wall" or srf_type == "shade" or srf_type == "roof":
            py2radiance.RadSurface(srfname, pypolygon, srfmat, rad)
            other_occface_list.append(occ_face)
            
        scnt += 1
        
    rad.create_rad_input_file()
    
    #once the geometries are created initialise daysim
    daysim_dir = tempfile.mkdtemp()
    rad.initialise_daysim(daysim_dir)
    #a 60min weatherfile is generated
    rad.execute_epw2wea(epwweatherfile)
    rad.execute_radfiles2daysim()
    
    #create sensor points
    rad.set_sensor_points(sensor_ptlist, sensor_dirlist)
    rad.create_sensor_input_file()
    
    rad_ab = 1
    rad_ad = 1000
    rad_as = 20
    rad_ar = 300
    rad_aa = 0.1
    rad_lr = 6
    rad_st = 0.15
    rad_sj = 1.0
    rad_lw = 0.004
    rad_dj = 0.0
    rad_ds = 0.2
    rad_dr = 2
    rad_dp = 512
        
    rad.write_radiance_parameters(rad_ab, rad_ad, rad_as, rad_ar, rad_aa, rad_lr, rad_st, rad_sj, rad_lw, rad_dj,
                                  rad_ds, rad_dr, rad_dp)
    rad.execute_gen_dc("w/m2")
    rad.execute_ds_illum()
    res = rad.eval_ill_per_sensor()
    solar_gain = chose_solar_gain(res, sensor_surfacelist, other_occface_list, mode)
    
    shutil.rmtree(data_folderpath)
    shutil.rmtree(daysim_dir)
    
    return solar_gain

def calc_con_free_panel(supply_temp_kelvin, aust_kelvin = 298.15, sup_srf_td = 3.0):
    """
    This function calculates the cooling rate of the radiant panels (W/m2). The calculation is based on the ASHRAE guide.
    
    Parameters
    ----------
    supply_temp_kelvin : float
        The supply temperature used by the radiant panels to provide sensible cooling (K).
        
    aust_kelvin : float, optional
        The area weighted temperature of all indoor surfaces (K), default = 298.15.
        
    Returns
    -------
    cooling_rate : float
        The cooling rate of the panels in W/m2.
         
    """
    tp = supply_temp_kelvin + sup_srf_td
    tp_aust = (tp**4) - (aust_kelvin**4)
    
    qr_constant = 5*10**-8 
    qr = qr_constant*tp_aust
    return qr*-1

def radiant_panel_dvu_system(sensible_load, latent_load, floor_area, area_per_person = 10.0, m3_sec_per_person = 0.006, 
                             operation_hrs = 3120, dvu_airflow_rate_m3_sec = 0.02, chiller_efficiency = 0.4):
    
    """
    This function calculates the cooling energy consumption of the conditioned space using dvu & radiant panels.
    
    Parameters
    ----------
    sensible_load : float
        The sensible load of the conditioned space (W).
        
    latent_load : float
        The latent load of the conditioned space (W).
        
    floor_area : float
        The floor area of the conditioned space.
        
    area_per_person : float, optional
        The amount of area for a person in the conditioned space, default = 10.0 m2/person.
        
    m3_sec_per_person : float, optional
        The ventilation rate per person of the conditioned space, default = 0.006 m3/person.
        
    operation_hrs : int, optional
        The total operational hours of the conditioned space, default =3120 hrs, assuming a a 12hrs day, 5 days week for 52 weeks a year.
        
    dvu_airflow_rate_m3_sec : float, optional
        The ventilation rate of the dvu system, default = 0.02 m3/s.
        
    chiller_efficiency : float, optional
        The efficiency of the chiller, default = 0.4. A good chiller can have an efficiency of up to 0.6.
        
    Returns
    -------
    system result dictionary : dictionary
        A dictionary with this keys : {"feasible", "energy_consumed_hr", "energy_consumed_yr", "energy_consumed_yr_m2", "sensible_cop", "latent_cop", "overall_cop", 
        "required_panel_area", "available_panel_area", "supply_temperature_for_panels", "sensible_load", "latent_load", "sensible_load_dvu", "sensible_panel", "panel_max_capacity",
        "required_dvus", "cooling_system"}.
        
        feasible : bool
            True or False, if True the space can be conditioned with dvus + panels, if False cannot be conditioned.
            
        energy_consumed_hr : float
            The average energy consumed by the cooling system (Wh). This key exist only if feasible = True.
            
        energy_consumed_yr : float
            The energy consumed by the cooling system in a year (kWh), equals to energy_consumed_hr x operation hours. This key exist only if feasible = True.
            
        energy_consumed_yr_m2 : float
            The energy consumed by the cooling system in a year normalised by the floor area (kWh/m2), equals to (energy_consumed_hr x operation hours)/floor area. This key exist only if feasible = True.
        
        sensible_cop : float
            The Coefficient of Performance of the sensible chiller. This key exist only if feasible = True.
        
        latent_cop : float
            The Coefficient of Performance of the latent chiller. This key exist only if feasible = True.
            
        overall_cop : float
            The Coefficient of Performance of the overall system. This key exist only if feasible = True.
            
        required_panel_area : float
            The area required for the radiant panels to provide sufficient sensible cooling (m2). This key exist only if feasible = True.
            
        available_panel_area : float
            The area available for the radiant panels to provide sensible cooling (m2). This key exist only if feasible = True.
            
        supply_temperature_for_panels : float
            The supply temperature used by the radiant panels to provide sensible cooling (K). This key exist only if feasible = True.
            
        sensible_load : float
            The sensible load of the conditioned space (W).
            
        latent_load : float
            The latent load of the conditioned space (W).
            
        sensible_load_dvu : float
            The sensible cooling provided by the DVUs (W). This key exist only if feasible = True.
            
        sensible_panel : float
            The sensible load that has to be cooled by the radiant panel (W), it is equal to sensible_load - sensible_load_dvu. This key exist only if feasible = True.
            
        panel_max_capacity : float
            The maximum cooling capacity of the radiant panels (W).
        
        required_dvus : int
            The number of DVUs required. This key exist only if feasible = True.
            
        cooling_system : str
            Specifies the cooling system used, the value is "Radiant Panels & DVUs".
         
    """
    #calculate the amount of sensible cooling that will be provided by the ventilation 
    occupancy = floor_area/area_per_person
    mass_of_air = calc_mass_of_air(occupancy, m3_sec_per_person)
    specific_heat_capcity = 1005 #j/kgk
    delta_t = 25-14 #k
    sens_load_vu = (mass_of_air*specific_heat_capcity*delta_t)
    #calculate number of dvu required
    vol_air_required = m3_sec_per_person*occupancy
    n_dvu = int(vol_air_required/dvu_airflow_rate_m3_sec)
    
    #calculate the sensible load that needs to be removed by the radiant panels
    sensible_panels = sensible_load - sens_load_vu
    panel_srf_area = floor_area*0.9 #assume 90% of the ceiling is available for radiant cooling
    
    #calculate the total cooling capacity of the cooling panels
    #The chilled water cooling the surface needs to be 1.5K above the dew-point temperature of the space to avoid condensation
    #space with 50% RH, 25 dry bulb temp has dew point of 13 assuming AUST is 25
    sens_supply_temp_kelvin1 = 18.5+273.15
    sens_supply_temp_kelvin2 = 17.5+273.15
    sens_supply_temp_kelvin3 = 16.5+273.15
    sens_supply_temp_kelvin4 = 15.5+273.15
    sens_supply_temp_kelvin5 = 14.5+273.15
    
    cooling_r1 = calc_radiant_panel_cooling_rate(sens_supply_temp_kelvin1)
    cooling_r2 = calc_radiant_panel_cooling_rate(sens_supply_temp_kelvin2)
    cooling_r3 = calc_radiant_panel_cooling_rate(sens_supply_temp_kelvin3)
    cooling_r4 = calc_radiant_panel_cooling_rate(sens_supply_temp_kelvin4)
    cooling_r5 = calc_radiant_panel_cooling_rate(sens_supply_temp_kelvin5)

    max_cap1 = ((panel_srf_area * cooling_r1) + sens_load_vu)
    max_cap2 = ((panel_srf_area * cooling_r2) + sens_load_vu)
    max_cap3 = ((panel_srf_area * cooling_r3) + sens_load_vu)
    max_cap4 = ((panel_srf_area * cooling_r4) + sens_load_vu)
    max_cap5 = ((panel_srf_area * cooling_r5) + sens_load_vu)

    latent_supply_temp = 8.0 + 273.15
    heat_rejection_temp = 28.0 + 273.15
    
    #check which supply temperature is enuf for removing the sensible load
    if sensible_load <= max_cap1:
        req_panel_srf_area = sensible_panels/cooling_r1
        panel_temp = sens_supply_temp_kelvin1
        
    elif sensible_load <= max_cap2:
        req_panel_srf_area = sensible_panels/cooling_r2 
        panel_temp = sens_supply_temp_kelvin2
        
    elif sensible_load <= max_cap3:
        req_panel_srf_area = sensible_panels/cooling_r3
        panel_temp = sens_supply_temp_kelvin3
        
    elif sensible_load <= max_cap4:
        req_panel_srf_area = sensible_panels/cooling_r4
        panel_temp = sens_supply_temp_kelvin4
        
    elif sensible_load <= max_cap5:
        req_panel_srf_area = sensible_panels/cooling_r5
        panel_temp = sens_supply_temp_kelvin5
        
    else:
        result_dict = {}
        result_dict["feasible"] = False
        result_dict["cooling_system"] = "Radiant Panels & DVUs"
        result_dict["sensible_load"] = sensible_load
        result_dict["latent_load"] = latent_load
        result_dict["panel_max_capacity"] = max_cap5
        return result_dict
        
    sens_cop = calc_cooling_cop(panel_temp, heat_rejection_temp, chiller_efficiency = chiller_efficiency)
    latent_cop = calc_cooling_cop(latent_supply_temp, heat_rejection_temp, chiller_efficiency = chiller_efficiency)
    energy_consumed_hr = (sensible_panels/sens_cop) + ((latent_load + sens_load_vu)/latent_cop)#wh
    overall_cop = (sensible_load + latent_load)/energy_consumed_hr
    energy_consumed_yr = (energy_consumed_hr*operation_hrs)/1000 #kwh
    energy_consumed_yr_m2 = energy_consumed_yr/floor_area #kwh
    
    result_dict = {}
    result_dict["feasible"] = True
    result_dict["energy_consumed_hr"] = energy_consumed_hr
    result_dict["energy_consumed_yr"] = energy_consumed_yr
    result_dict["energy_consumed_yr_m2"] = energy_consumed_yr_m2
    
    result_dict["sensible_cop"] = sens_cop
    result_dict["latent_cop"] = latent_cop
    result_dict["overall_cop"] = overall_cop
    
    result_dict["required_panel_area"] = req_panel_srf_area
    result_dict["available_panel_area"] = panel_srf_area
    result_dict["supply_temperature_for_panels"] = panel_temp
    
    result_dict["sensible_load"] = sensible_load
    result_dict["latent_load"] = latent_load
    result_dict["sensible_load_dvu"] = sens_load_vu
    result_dict["sensible_panel"] = sensible_panels
    result_dict["panel_max_capacity"] = max_cap5
    
    result_dict["required_dvus"] = n_dvu
    
    result_dict["cooling_system"] = "Radiant Panels & DVUs"
    return result_dict

def calc_radiant_panel_cooling_rate(supply_temp_kelvin, aust_kelvin = 298.15, indoor_air_temp_kelvin = 298.15):
    """
    This function calculates the cooling rate of the radiant panels (W/m2). The calculation is based on the ASHRAE guide.
    
    Parameters
    ----------
    supply_temp_kelvin : float
        The supply temperature used by the radiant panels to provide sensible cooling (K).
        
    aust_kelvin : float, optional
        The area weighted temperature of all indoor surfaces (K), default = 298.15.
        
    indoor_air_temp_kelvin : float, optional
        The average indoor air temperature (K), default = 298.15.
        
    Returns
    -------
    cooling_rate : float
        The cooling rate of the panels in W/m2.
         
    """
    tp = supply_temp_kelvin + 3.0
    tp_aust = (tp**4) - (aust_kelvin**4)
    qr_constant = 5*10**-8 
    qr = qr_constant*tp_aust
    
    tp_ta_pos = supply_temp_kelvin - indoor_air_temp_kelvin
    if tp_ta_pos <0:
        tp_ta_pos = tp_ta_pos*-1
        
    tp_ta_032 = tp_ta_pos**0.32 
    
    tp_ta = supply_temp_kelvin - indoor_air_temp_kelvin
    qc = 1.78*tp_ta_032*tp_ta
    cooling_rate  = qr+qc
    return cooling_rate*-1

def central_all_air_system(sensible_load, latent_load, floor_area,
                           supply_temp_c = 8.0, rej_temp_c = 28.0,
                           operation_hrs = 3120, chiller_efficiency = 0.4):
    """
    This function calculates the cooling energy consumption of the conditioned space using a central all air system.
    
    Parameters
    ----------
    sensible_load : float
        The sensible load of the conditioned space (W).
        
    latent_load : float
        The latent load of the conditioned space (W).
        
    floor_area : float
        The floor area of the conditioned space.
        
    supply_temp_c : float, optional
        The supply temperature of the cooling system, default = 8.0 C.
        
    rej_temp_c : float
        The heat rejection temperature of the cooling system, default = 28.0 C.
        
    operation_hrs : int, optional
        The total operational hours of the conditioned space, default =3120 hrs, assuming a a 12hrs day, 5 days week for 52 weeks a year.
        
    chiller_efficiency : float, optional
        The efficiency of the chiller, default = 0.4. A good chiller can have an efficiency of up to 0.6.
        
    Returns
    -------
    system result dictionary : dictionary
        A dictionary with this keys : {"feasible", "energy_consumed_hr", "energy_consumed_yr", "energy_consumed_yr_m2", "overall_cop", "sensible_load", "latent_load", "cooling_system"}
        
        feasible : bool
            True or False, if True the space can be conditioned with dvus + panels, if False cannot be conditioned.
            
        energy_consumed_hr : float
            The average energy consumed by the cooling system (Wh). This key exist only if feasible = True.
            
        energy_consumed_yr : float
            The energy consumed by the cooling system in a year (kWh), equals to energy_consumed_hr x operation hours. This key exist only if feasible = True.
            
        energy_consumed_yr_m2 : float
            The energy consumed by the cooling system in a year normalised by the floor area (kWh/m2), equals to (energy_consumed_hr x operation hours)/floor area. This key exist only if feasible = True.
            
        overall_cop : float
            The Coefficient of Performance of the overall system. This key exist only if feasible = True.
            
        sensible_load : float
            The sensible load of the conditioned space (W).
            
        latent_load : float
            The latent load of the conditioned space (W).
            
        cooling_system : str
            Specifies the cooling system used, the value is "Central All-Air System".
         
    """
    supply_temp = supply_temp_c + 273.15
    heat_rejection_temp = rej_temp_c + 273.15
    cooling_cop = calc_cooling_cop(supply_temp, heat_rejection_temp, chiller_efficiency = chiller_efficiency)
    total_load = sensible_load+latent_load
    energy_consumed_hr = total_load/cooling_cop
    energy_consumed_yr = (energy_consumed_hr*operation_hrs)/1000  #kwh
    energy_consumed_yr_m2 =  energy_consumed_yr/floor_area #kwh
    
    result_dict = {}
    result_dict["feasible"] = True
    result_dict["energy_consumed_hr"] = energy_consumed_hr
    result_dict["energy_consumed_yr"] = energy_consumed_yr
    result_dict["energy_consumed_yr_m2"] = energy_consumed_yr_m2
    
    result_dict["sensible_load"] = sensible_load
    result_dict["latent_load"] = latent_load
    
    result_dict["overall_cop"] = cooling_cop    
    result_dict["cooling_system"] = "Central All-Air System"
    
    return result_dict

def calc_cooling_cop(supply_temp_kelvin, heat_rej_temp_kelvin , chiller_efficiency = 0.4):
    """
    This function calculates the cooling Coefficient of Performance (COP) of the chiller.
    
    Parameters
    ----------
    supply_temp_kelvin : float
        The supply temperature used by the system to provide sensible cooling (K).
        
    heat_rej_temp_kelvin : float
        The heat rejection temperature achieved by the heat rejection system. In Singapore, about 28 degree celsius can be used.
        
    chiller_efficiency : float, optional
        The efficiency of the chiller, default = 0.4. A good chiller can have an efficiency of up to 0.6.
        
    Returns
    -------
    cooling_cop : float
        The cooling cop of the system.
         
    """
    tr_ts = heat_rej_temp_kelvin - supply_temp_kelvin
    cooling_cop = chiller_efficiency*(supply_temp_kelvin/tr_ts)
    return cooling_cop
    
def calc_sensible_load(facade_area, roof_area, floor_area, ettv, rttv, equip_load_per_area = 25.0, 
                       occ_load_per_person = 75.0, light_load_per_area = 15.0, area_per_person = 10.0):
    
    """
    This function calculates the sensible load of an air conditioned space.
    
    Parameters
    ----------
    facade_area : float
        The total area of the facade of the conditioned space.
        
    roof_area : float
        The total area of the roof of the conditioned space.
        
    floor_area : float
        The total area of the floor of the conditioned space.
        
    ettv : float
        The ettv/retv of the conditioned space.
    
    rttv : float
        The rttv of the conditioned space.
        
    equip_load_per_area : float, optional
        The equipment load per area of the conditioned space, default = 25.0 W/m2
        
    occ_load_per_person : float, optional
        The occupancy load per person of the conditioned space, default = 75.0 W/person.
    
    light_load_per_area : float, optional
        The lighting load per area of the conditioned space, default = 15.0 W/m2.
        
    area_per_person : float, optional
        The amount of area for a person in the conditioned space, default = 10.0 m2/person.
    
        
    Returns
    -------
    sensible_load: float
         The sensible load of the conditioned space (W).
         
    """
    #calc equipment load
    equip_load = equip_load_per_area*floor_area
    #calc occupancy load
    occupancy = floor_area/area_per_person
    occ_load = occ_load_per_person*occupancy
    #calc lighting load
    light_load = light_load_per_area*floor_area
    #calc envelope load
    env_load = ettv*facade_area
    #calc roof load
    roof_load = rttv*roof_area
    #calc total load
    sensible_load = env_load + roof_load + equip_load + occ_load + light_load
    return sensible_load

def calc_vent_load(floor_area, area_per_person = 10.0, m3_sec_per_person = 0.006):
    """
    This function calculates the latent load of an air conditioned space.
    
    Parameters
    ----------
    floor_area : float
        The total area of the floor of the conditioned space.
        
    area_per_person : float, optional
        The amount of area for a person in the conditioned space, default = 10.0 m2/person.
        
    m3_sec_per_person : float, optional
        The ventilation rate per person of the conditioned space, default = 0.006 m3/person.
        
    Returns
    -------
    laten_load: float
         The latent load of the conditioned space (W).
         
    """
    #airflow_per_person is in m3/s/person
    occupancy = floor_area/area_per_person
    mass_of_air = calc_mass_of_air(occupancy, m3_sec_per_person)
    # energy to remove humidity 40KJ/kg 
    latent_load = mass_of_air*40000
    return latent_load

def calc_latent_load(floor_area, area_per_person = 10.0, watts_per_person = 70):
    """
    This function calculates the latent load of an air conditioned space.
    
    Parameters
    ----------
    floor_area : float
        The total area of the floor of the conditioned space.
        
    area_per_person : float, optional
        The amount of area for a person in the conditioned space, default = 10.0 m2/person.
        
    watts_per_person : float, optional
        The latent load per person of the conditioned space, default = 70 watts.
        
    Returns
    -------
    laten_load: float
         The latent load of the conditioned space (W).
         
    """
    #airflow_per_person is in m3/s/person
    occupancy = floor_area/area_per_person
    latent_load = occupancy * watts_per_person
    return latent_load

def calc_mass_of_air(occupancy, m3_sec_per_person):
    """
    This function calculates the mass of air for the ventilation.
    
    Parameters
    ----------
    occupancy : int
        The occupancy of the conditioned space.
        
    m3_sec_per_person : float
        The ventilation rate per person of the conditioned space, in Singapore it is 0.006 m3/person.
        
    Returns
    -------
    mass_of_air: float
         The mass of air required for ventilation (kg).
         
    """
    vol_of_air = m3_sec_per_person*occupancy
    air_density = 1.225 #kg/m3
    mass_of_air = air_density * vol_of_air
    return mass_of_air

def calc_mech_space(total_load, setpt_temp_c, outdoor_temp_c, duct_air_vel = 15):
    """
    This function calculates the mechanical space required for centralised air ducts.
    
    Parameters
    ----------
    total_load : float
        The total sensible and latent load of the space (W.
        
    setpt_temp_c : float
        The setpt of the interior space (C).
    
    outdoor_temp_c : float
        Outdoor temperature (C).
    
    duct_air_vel : float, optional
        air velocity in the duct for delivering air (m/s), default = 15m/s.
    
    Returns
    -------
    plenum_height: float
         The height of the plenum space.
         
    """
    import math
    air_density = 1.225 #kg/m3
    specific_heat_capacity = 1005 #j/kgk
    td = outdoor_temp_c - setpt_temp_c
    #loads = m x c x td
    m = total_load/(specific_heat_capacity*td)
    vol = m/air_density
    cross_section = vol/duct_air_vel
    height = math.sqrt((cross_section/2))
    # height2 = total_load/(air_density*specific_heat_capacity*td*duct_air_vel*0.38)
    return height
    
#================================================================================================================
#SIMPLIFIED COOLING ENERGY CONSUMPTION CALCULATION END
#================================================================================================================