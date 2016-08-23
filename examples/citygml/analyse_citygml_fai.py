import time
import os
import envuo

#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir))
citygml_filepath = os.path.join(parent_path, "punggol_case_study", "citygml", "punggol_luse5.gml")

evaluations = envuo.citygml2eval.Evals(citygml_filepath)
weatherfilepath = os.path.join(parent_path, "punggol_case_study", "weatherfile", "SGP_Singapore.486980_IWEC.epw")

time1 = time.clock()
print "EVALUATING MODEL ... ..."
wind_dir = (1,1,0)
fai_list = evaluations.fai(wind_dir)