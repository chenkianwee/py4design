import time
import os
import envuo
from envuo import py3dmodel 

#change the filepath to where you want to save the file to 
image_file = "F:\\kianwee_work\\spyder_workspace\\envuo_examples\\citygmlenv_examples\\py2radiance_data\\punggol_irradiance.png"
falsecolour_file = "F:\\kianwee_work\\spyder_workspace\\envuo_examples\\citygmlenv_examples\\py2radiance_data\\punggol_falsecolour_bar.png"


#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir))
citygml_filepath = os.path.join(parent_path, "punggol_case_study", "citygml", "punggol_luse24.gml")

evaluations = envuo.citygml2eval.Evals(citygml_filepath)
xdim = 6
ydim = 6
weatherfilepath = os.path.join(parent_path, "punggol_case_study", "weatherfile", "SGP_Singapore.486980_IWEC.epw")
latitude = 1.37
longtitude = -103.98
meridian = -120
start_mth = 1
end_mth = 1
start_day = 1
end_day = 31
start_hour = 7
end_hour = 19
ab = 2
time1 = time.clock()
print "EVALUATING MODEL ... ..."
topo_list, irrad_res = evaluations.building_solar(weatherfilepath, latitude, longtitude, meridian, 
                           start_mth, end_mth, start_day, end_day, start_hour, end_hour, ab, xdim, ydim)
          
time2 = time.clock()
print (time2-time1)/60
print "MODEL EVALUATED!"

print "VISUALISING RESULT"
envuo.py3dmodel.construct.visualise_falsecolour_topo(irrad_res, topo_list, falsecolour_file, image_file)
time3 = time.clock()
print "TIME TAKEN", (time3-time1)/60
print "VISUALISED"