import time
import os
import pyliburo
#=========================================================================================================================================
#SPECIFY ALL THE NECCESSARY INPUTS
#=========================================================================================================================================

#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir))
citygml_filepath = os.path.join(parent_path, "example_files", "form_eval_example","citygml", "grid_tower.gml" )
#or just insert a citygml file you would like to analyse here 
'''citygml_filepath = "C://file2analyse.gml"'''

#change the filepath to where you want to save the file to 
image_file = os.path.join(parent_path, "example_files", "form_eval_example", "citygml", "res_img", "result.png" )
falsecolour_file = os.path.join(parent_path, "example_files", "form_eval_example", "citygml", "res_img", "falsecolour.png" )
weatherfilepath = os.path.join(parent_path, "example_files", "weatherfile", "SGP_Singapore.486980_IWEC.epw" )

evaluations = pyliburo.citygml2eval.Evals(citygml_filepath)
xdim = 9
ydim = 9
#==========================================================================================================================

#50w/m2 is the benchmark envelope thermal transfer value for spore greenmark basic for commercial buildings
#its calculated as an hourly average, multiplying it by 8760 hrs, we get the rough value for the permissible annual solar heat gain
#1.5 is a factor to account for the raw irradiation falling on the surface, the higher we assume the better your envelope quality. 
#factor of 1.5 means we expect 60% of the heat to be transmitted through the envelope 
#==========================================================================================================================

irrad_threshold = (50*8760*1.5)/1000.0#kw/m2
illum_threshold = 10000#lux
roof_irrad_threshold = 1280 #kwh/m2
facade_irrad_threshold = 512 #kwh/m2
#=========================================================================================================================================
#SPECIFY ALL THE NECCESSARY INPUTS
#=========================================================================================================================================
#==========================================================================================================================
#irrad_threshold (kwh/m2)
#==========================================================================================================================
time1 = time.clock()
print "EVALUATING MODEL ... ..."

avg_shgfavi, shgfavi_percent, shgfai, topo_list, irrad_ress  = evaluations.shgfavi(irrad_threshold,weatherfilepath,xdim,ydim)
print "SOLAR GAIN FACADE AREA VOLUME INDEX:", avg_shgfavi

#==========================================================================================================================
#illum threshold (lux)
#==========================================================================================================================
avg_dfavi, dfavi_percent, dfai, topo_list, illum_ress = evaluations.dfavi(illum_threshold,weatherfilepath,xdim,ydim)
print "DAYLIGHT FACADE AREA VOLUME INDEX:", avg_dfavi

#==========================================================================================================================
#solar potential measures the potential energy that can be generated on the building surfaces
#==========================================================================================================================
avg_pvravi, pvravi_percent, pvrai, epv, topo_list, irrad_ress = evaluations.pvavi(roof_irrad_threshold, weatherfilepath,xdim,ydim, 
                                                                                  surface = "roof")
print "PV ROOF AREA VOLUME INDEX :", avg_pvravi

avg_pvfavi, pvfavi_percent, pvfai, epv, topo_list, irrad_ress = evaluations.pvavi(facade_irrad_threshold, weatherfilepath,xdim,ydim, 
                                                                                  surface = "facade")   
print "PV FACADE AREA VOLUME INDEX :", avg_pvfavi
                                                                          
avg_pveavi, pveavi_percent, pveai, epv, topo_list, irrad_ress = evaluations.pveavi(roof_irrad_threshold, facade_irrad_threshold,
                                                                                   weatherfilepath,xdim,ydim)
print "PV ENVELOPE AREA VOLUME INDEX :", avg_pveavi

time2 = time.clock()
print (time2-time1)/60
print "MODEL EVALUATED!"

print "VISUALISING RESULT"
#pyliburo.py3dmodel.construct.visualise_falsecolour_topo(illum_ress, topo_list, falsecolour_file = falsecolour_file , image_file= image_file)
time3 = time.clock()
print "TIME TAKEN", (time3-time1)/60
print "VISUALISED"
