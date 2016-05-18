import os 
import envuo

#create all the relevant folders 
current_path = os.path.dirname(__file__)
base_filepath = os.path.join(current_path, 'base.rad')
data_folderpath = os.path.join(current_path, 'py2radiance_data')
display2dlist = []
#initialise py2radiance 
rad = envuo.py2radiance.Rad(base_filepath, data_folderpath)

#create a box 10x10x10m
box = envuo.py3dmodel.construct.make_box(10,10,10)
occfaces = envuo.py3dmodel.fetch.faces_frm_solid(box)
displaylist = []
displaylist.append(box)
#display2dlist.append(displaylist)

sensor_pts = []
sensor_dirs = []
face_cnt = 0
displaylist2 = []
for occface in occfaces:
    radsrfname = "srf" + str(face_cnt)
    rad_polygon = envuo.interface2py3d.pyptlist_frm_occface(occface)
    srfmat = "RAL9010_pur_white_paint"
    envuo.py2radiance.RadSurface(radsrfname,rad_polygon,srfmat,rad)
    
    #get the surface that is pointing upwards, the roof
    normal = envuo.py3dmodel.calculate.face_normal(occface)
    if normal == (0,0,1):
        #generate the sensor points
        grid_occfaces = envuo.py3dmodel.construct.grid_face(occface,3,3)
        display2dlist.append(grid_occfaces)
        #calculate the midpt of each surface
        for grid_occface in grid_occfaces:
            midpt = envuo.py3dmodel.calculate.face_midpt(grid_occface)
            sensor_pts.append(midpt)
            sensor_dirs.append(normal)
    face_cnt+=1

#set the sensor grid points and direction
rad.set_sensor_points(sensor_pts, sensor_dirs)
rad.create_rad_input_file()

#once the geometries are created initialise daysim
daysim_dir = os.path.join(current_path, 'daysim_data')
rad.initialise_daysim(daysim_dir)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir))
#a 60min weatherfile is generated
epweatherfile = os.path.join(parent_path, "punggol_case_study", "weatherfile", "SGP_Singapore.486980_IWEC.epw")
rad.execute_epw2wea(epweatherfile)
rad.execute_radfiles2daysim()
#create sensor points
rad.set_sensor_points(sensor_pts,sensor_dirs)
rad.create_sensor_input_file()
rad.write_default_radiance_parameters()#the default settings are the complex scene 1 settings of daysimPS
rad.execute_gen_dc("w/m2")
rad.execute_ds_illum()

print display2dlist
envuo.py3dmodel.construct.visualise(display2dlist, ["WHITE"])