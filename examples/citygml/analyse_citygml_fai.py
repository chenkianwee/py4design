import os
import time
import pyliburo
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir))
citygml_filepath = os.path.join(parent_path, "example_files", "form_eval_example","citygml", "grid_tower.gml" )
#or just insert a citygml file you would like to analyse here 
'''citygml_filepath = "C://file2analyse.gml"'''
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================

displaylist2 = []
evaluations = pyliburo.citygml2eval.Evals(citygml_filepath)

time1 = time.clock()
print "EVALUATING MODEL ... ..."
wind_dir = (1,1,0)
avg_fai, gridded_boundary,fai_list, fs_list, wp_list, os_list = evaluations.fai(wind_dir)
solids = evaluations.building_occsolids
time2 = time.clock()
print (time2-time1)/60

print avg_fai
display2dlist = []
colourlist = []
display2dlist.append(os_list)
colourlist.append("WHITE")
#pyliburo.py3dmodel.construct.visualise(display2dlist,colourlist)
pyliburo.py3dmodel.construct.visualise_falsecolour_topo(fai_list,gridded_boundary,
                                                        other_topo2dlist = display2dlist, 
                                                        other_colourlist = colourlist)