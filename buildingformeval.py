# ==================================================================================================
#
#    Copyright (c) 2017, Chen Kian Wee (chenkianwee@gmail.com)
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
import tempfile
import shutil
import os
    
import utility
import py3dmodel
import gml3dmodel
import py2radiance
import shapeattributes
#================================================================================================================
#ETTV
#================================================================================================================
def calc_ettv( srfs_shp_attribs_obj_list, epwweatherfile, mode = "ettv"):
    srfs_shp_attribs_obj_list = calc_dir_pitch_angle(srfs_shp_attribs_obj_list, mode = mode)
    srfs_shp_attribs_obj_list = glazing_sc2(srfs_shp_attribs_obj_list,epwweatherfile)
    cf_list = []
    
    #find all the unique cfs
    for srf_shp_attribs in srfs_shp_attribs_obj_list:
        cf = srf_shp_attribs.get_value("cf")
        if cf not in cf_list:
            cf_list.append(cf)
    
    ettv_area_list = []
    cf_env_area_list = []
    rttv_area_list = []
    cf_rf_area_list = []
    for ref_cf in cf_list:
        ref_cf_env_area = 0
        ref_cf_rf_area = 0
        wall_area_uvalue_list = []
        roof_area_uvalue_list = []
        win_area_uvalue_list = []
        win_area_sc_list = []
        skylight_area_uvalue_list = []
        skylight_area_sc_list = []
        
        for srf_shp_attribs in srfs_shp_attribs_obj_list:
            srf_type = srf_shp_attribs.get_value("type")
            if srf_type != "footprint" or srf_type != "shade" or srf_type != "surrounding":
                cf = srf_shp_attribs.get_value("cf")
                
                if cf == ref_cf:
                    occ_face = srf_shp_attribs.shape
                    area = py3dmodel.calculate.face_area(occ_face)
                    uvalue = srf_shp_attribs.get_value("uvalue")
                    if srf_type == "wall":
                        ref_cf_env_area+=area
                        wall_area_uvalue = area*uvalue
                        wall_area_uvalue_list.append(wall_area_uvalue)
                    if srf_type == "roof":
                        ref_cf_rf_area+= area
                        roof_area_uvalue = area*uvalue
                        roof_area_uvalue_list.append(roof_area_uvalue)
                    if srf_type == "window":
                        ref_cf_env_area+=area
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
                 
        cf_rttv_wallcon = (sum(roof_area_uvalue_list) * 3.4)/ref_cf_rf_area
        cf_rttv_wincon = (sum(win_area_uvalue_list) * 1.3)/ref_cf_rf_area
        cf_rttv_winrad = (sum(win_area_sc_list) * 58.6 * ref_cf)/ref_cf_rf_area 
        cf_rttv = cf_rttv_wallcon + cf_rttv_wincon + cf_rttv_winrad
        rttv_area_list.append(cf_rttv * ref_cf_rf_area)
        cf_rf_area_list.append(ref_cf_rf_area)
            
        if mode == "ettv":
            cf_ettv_wallcon = (sum(wall_area_uvalue_list) * 12)/ref_cf_env_area
            cf_ettv_wincon = (sum(win_area_uvalue_list) * 3.4)/ref_cf_env_area
            cf_ettv_winrad = (sum(win_area_sc_list) * 211 * ref_cf)/ref_cf_env_area 
            cf_ettv = cf_ettv_wallcon + cf_ettv_wincon + cf_ettv_winrad
            ettv_area_list.append(cf_ettv * ref_cf_env_area)
            cf_env_area_list.append(ref_cf_env_area)
        if mode == "retv":
            cf_retv_wallcon = (sum(wall_area_uvalue_list) * 3.4)/ref_cf_env_area
            cf_retv_wincon = (sum(win_area_uvalue_list) * 1.3)/ref_cf_env_area
            cf_retv_winrad = (sum(win_area_sc_list) * 58.6 * ref_cf)/ref_cf_env_area 
            cf_retv = cf_retv_wallcon + cf_retv_wincon + cf_retv_winrad
            ettv_area_list.append(cf_retv * ref_cf_env_area)
            cf_env_area_list.append(ref_cf_env_area)

    total_env_area = sum(cf_env_area_list)
    ettv = sum(ettv_area_list)/total_env_area
    total_rf_area = sum(cf_rf_area_list)
    rttv = sum(rttv_area_list)/total_rf_area
    result_dict = {}

    result_dict[mode] = ettv
    result_dict["envelope_area"] = total_env_area
    result_dict["rttv"] = rttv
    result_dict["roof_area"] = total_rf_area
    return result_dict

def glazing_sc2(srfs_shp_attribs_obj_list, epwweatherfile):
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
    
    scnt = 0
    pcnt = 0
    for srf_shp_attribs in srfs_shp_attribs_obj_list:
        srf_type = srf_shp_attribs.get_value("type")
        occ_face = srf_shp_attribs.shape
        pypolygon = py3dmodel.fetch.pyptlist_frm_occface(occ_face)
        srfname = "srf" + str(scnt)
        if srf_type == "window" or srf_type == "skylight":
            sensor_surfaces, sensor_pts, sensor_dirs = gml3dmodel.generate_sensor_surfaces(occ_face, 0.5, 0.5)
            sensor_ptlist.extend(sensor_pts)
            sensor_dirlist.extend(sensor_dirs)
            sensor_surfacelist.extend(sensor_surfaces)
            n_sensor_srfs = len(sensor_ptlist)
            srf_shp_attribs.set_key_value("sensor_indices", [pcnt, pcnt+n_sensor_srfs])
            py2radiance.RadSurface(srfname, pypolygon, srfmat, rad)
            py2radiance.RadSurface(srfname, pypolygon, srfmat, rad2)
        else:
            py2radiance.RadSurface(srfname, pypolygon, srfmat, rad)
            
        pcnt+=n_sensor_srfs
        scnt += 1
            
    time = str(0) + " " + str(24)
    date = str(1) + " " + str(1) + " " + str(12) + " " + str(31)
    #calculate the shaded windows and skylight
    rad.set_sensor_points(sensor_ptlist, sensor_dirlist)
    rad.create_sensor_input_file()
    rad.create_rad_input_file()
    rad.execute_cumulative_oconv(time, date, epwweatherfile)
    rad.execute_cumulative_rtrace(str(2))#EXECUTE!! 
    irrad_ress = rad.eval_cumulative_rad()
    #calculate the unshaded windows and skylight
    rad2.set_sensor_points(sensor_ptlist, sensor_dirlist)
    rad2.create_sensor_input_file()
    rad2.create_rad_input_file()
    rad2.execute_cumulative_oconv(time, date, epwweatherfile)
    rad2.execute_cumulative_rtrace(str(2))#EXECUTE!! 
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
    for srf_shp_attribs in srfs_shp_attribs_obj_list:
        srf_type = srf_shp_attribs.get_value("type")
        if srf_type != "footprint" or srf_type != "shade" or srf_type != "surrounding":
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
                dir_angle = py3dmodel.calculate.angle_bw_2_vecs_w_ref(ref_dir_vec,flatten_nrml,
                                                                      ref_plane_vec)
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
                if 157.5>=dir_angle>=202.5:
                    direction = "south"
                if 202.5>dir_angle>247.5:
                    direction = "southeast"
                if 247.5>=dir_angle>=292.5:
                    direction = "east"
                if 292.5>dir_angle>337.5:
                    direction = "northeast"
            else:
                direction = "north"
                
            #get the correction factor for all the surfaces
            if srf_type == "roof" or srf_type == "skylight":
                cf_filepath = os.path.join(os.path.dirname(__file__),'databases','ettv','rttv_correctionfactor_roof.csv')
                pitch_angle = utility.round2nearest_base(pitch_angle)
                if pitch_angle < 0:
                    print "error: pitch angle out of range... choosing the nearest angle 0"
                    cf = read_cf_file(cf_filepath, 0, direction)
                elif pitch_angle > 65:
                    print "error: pitch angle out of range... choosing the nearest angle 65"
                    cf = read_cf_file(cf_filepath, 65, direction)#TODO: fix this 
                else:
                    cf = read_cf_file(cf_filepath, pitch_angle, direction)
                    
            if srf_type == "wall" or srf_type == "window": 
                if mode == "ettv":
                    cf_filepath = os.path.join(os.path.dirname(__file__),'databases','ettv','ettv_correctionfactor_wall.csv')
                    pitch_angle = utility.round2nearest_base(pitch_angle)
                    if pitch_angle < 70:
                        print "error: pitch angle out of range... choosing the nearest angle 70"
                        cf = read_cf_file(cf_filepath, 70, direction)
                    elif pitch_angle > 120:
                        print "error: pitch angle out of range... choosing the nearest angle 120"
                        cf = read_cf_file(cf_filepath, 120, direction)#TODO: fix this 
                    else:
                        cf = read_cf_file(cf_filepath, pitch_angle, direction)
                        
                if mode == "retv":
                    cf_filepath = os.path.join(os.path.dirname(__file__),'databases','ettv','retv_correctionfactor_wall.csv')
                    pitch_angle = utility.round2nearest_base(pitch_angle, base=10)
                    if pitch_angle < 70:
                        print "error: pitch angle out of range... choosing the nearest angle 70"
                        cf = read_cf_file(cf_filepath, 70, direction)
                    elif pitch_angle > 90:
                        print "error: pitch angle out of range... choosing the nearest angle 90"
                        cf = read_cf_file(cf_filepath, 90, direction)#TODO: fix this 
                    else:
                        cf = read_cf_file(cf_filepath, pitch_angle, direction)
                    
            srf_shp_attribs.set_key_value("cf", cf)
            srf_shp_attribs.set_key_value("pitch_angle", pitch_angle)
            srf_shp_attribs.set_key_value("direction", direction)
            
    return srfs_shp_attribs_obj_list

def create_glazing_shape_attribute(occ_face, uvalue, shading_coefficient1, srf_type):
    """ srf_type can be either window or skylight"""
    shp_attribs = shapeattributes.ShapeAttributes()
    shp_attribs.set_shape(occ_face)
    shp_attribs.set_key_value("uvalue", uvalue)
    shp_attribs.set_key_value("sc1", shading_coefficient1)
    shp_attribs.set_key_value("type", srf_type)
    return shp_attribs

def create_opaque_srf_shape_attribute(occ_face, uvalue, srf_type):
    """ srf_type can be either wall or roof"""
    shp_attribs = shapeattributes.ShapeAttributes()
    shp_attribs.set_shape(occ_face)
    shp_attribs.set_key_value("uvalue", uvalue)
    shp_attribs.set_key_value("type", srf_type)
    return shp_attribs

def create_shading_srf_shape_attribute(occ_face, srf_type):
    """ srf_type can be either footprint, shade, surrounding"""
    shp_attribs = shapeattributes.ShapeAttributes()
    shp_attribs.set_shape(occ_face)
    shp_attribs.set_key_value("type", srf_type)
    return shp_attribs

def read_cf_file(filepath, pitch_angle, direction):
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
    return float(cf)

#================================================================================================================
#ETTV END
#================================================================================================================