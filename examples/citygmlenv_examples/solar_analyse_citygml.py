import time
import os
import envuo

#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir))
citygml_filepath = os.path.join(parent_path, "punggol_case_study", "citygml", "punggol_luse5.gml")

#change the filepath to where you want to save the file to 
image_file = "F:\\kianwee_work\\spyder_workspace\\envuo\\examples\\punggol_case_study\\citygml\\py2radiance_data\\result.png"
falsecolour_file = "F:\\kianwee_work\spyder_workspace\envuo\examples\punggol_case_study\citygml\py2radiance_data\\falsecolour.png"
print falsecolour_file

evaluations = envuo.citygml2eval.Evals(citygml_filepath)
xdim = 6
ydim = 6
weatherfilepath = os.path.join(parent_path, "punggol_case_study", "weatherfile", "SGP_Singapore.486980_IWEC.epw")

time1 = time.clock()
print "EVALUATING MODEL ... ..."

'''
irrad_threshold (kwh/m2)
50w/m2 is the benchmark envelope thermal transfer value for spore greenmark basic for commercial buildings
its calculated as an hourly average, multiplying it by 8760 hrs, we get the rough value for the permissible annual solar heat gain
1.5 is a factor to account for the raw irradiation falling on the surface, the higher we assume the better your envelope quality 
factor of 1.5 means we expect 60% of the heat to be transmitted indoor 
'''
irrad_threshold = (50*8760*1.5)/1000.0
topo_list, irrad_res, sgfai = evaluations.sgfai(irrad_threshold,weatherfilepath,xdim,ydim)

'''
illum threshold (lux)

'''
illum_threshold = 15000
topo_list, illum_res, dfai = evaluations.dfai(illum_threshold,weatherfilepath,xdim,ydim)

#solar potential measures the potential energy that can be generated on the rooftop
pv_potential = evaluations.rpvp(weatherfilepath,xdim,ydim)
          
time2 = time.clock()
print (time2-time1)/60
print "MODEL EVALUATED!"

print "VISUALISING RESULT"
print "SOLAR GAIN FACADE AREA INDEX:" + str(sgfai)
print "DAYLIGHT FACADE AREA INDEX:" + str(dfai)
print "ROOF PV POTENTIAL:" + str(pv_potential) + "kWh/yr"
envuo.py3dmodel.construct.visualise_falsecolour_topo(illum_res, topo_list, falsecolour_file, image_file)
time3 = time.clock()
print "TIME TAKEN", (time3-time1)/60
print "VISUALISED"