import time
import os
import envuo

#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir))

#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
citygml_filepath = "F:\\kianwee_work\\smart\\conference\\asim2016\\asim_example\\citygml\\punggol_citygml_asim.gml"
#change the filepath to where you want to save the file to 
image_file = "F:\\kianwee_work\\smart\\conference\\asim2016\\asim_example\\citygml\\rpvp\\result.png"
falsecolour_file = "F:\\kianwee_work\\smart\\conference\\asim2016\\asim_example\\citygml\\rpvp\\falsecolour.png"
#specify weatherfilepath
weatherfilepath = "F:\\kianwee_work\\spyder_workspace\\envuo\\examples\\punggol_case_study\\weatherfile\\SGP_Singapore.486980_IWEC.epw"
#specify the grid size
xdim = 6
ydim = 6

#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
time1 = time.clock()
print "EVALUATING MODEL ... ..."

evaluations = envuo.citygml2eval.Evals(citygml_filepath)
irrad_threshold = 1000 #kwh/m2
pvrai, pv_potential, irrad_res, topo_list = evaluations.pvrai(1000, weatherfilepath,xdim,ydim)

time2 = time.clock()
print "TIME TAKEN FOR EVALUATION", (time2-time1)/60
print "MODEL EVALUATED!"

print "VISUALISING RESULT"
print "ROOF PV POTENTIAL:" + str(pv_potential) + "kWh/yr"
envuo.py3dmodel.construct.visualise_falsecolour_topo(irrad_res, topo_list, falsecolour_file, image_file, [evaluations.facade_occfaces],["WHITE"])
time3 = time.clock()
print "TIME TAKEN", (time3-time1)/60
print "VISUALISED"