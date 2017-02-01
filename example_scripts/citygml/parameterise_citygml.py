import os
import time
import pyliburo
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir, os.pardir))
citygml_filepath = os.path.join(parent_path, "pyliburo_example_files", "citygml", "punggol_luse50_53.gml")
result_citygml_filepath = os.path.join(parent_path, "pyliburo_example_files", "citygml", "punggol_variant.gml" )

'''citygml_filepath = "C://file2analyse.gml"
result_citygml_filepath = "C://result.gml'''
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================

time1 = time.clock()   
display_2dlist = []
colour_list = []

parameterise = pyliburo.gmlparameterise.Parameterise(citygml_filepath)
parameterise.add_bldg_flr_area_height_parm(parm_definition = [3,10,1])
parameterise.add_bldg_orientation_parm([0.0,350.0], clash_detection = True, boundary_detection = True)
parameterise.add_bldg_pos_parm(xdim = 10, ydim = 10)
parameters = parameterise.generate_random_parameters()


parameterise.generate_design_variant(parameters, result_citygml_filepath)
print parameters
time2 = time.clock() 
print "TIME TAKEN", (time2-time1)/60.0
print "VISUALISING"  
#display_2dlist.append(dlist)
#colour_list.append("RED")
#pyliburo.py3dmodel.construct.visualise(display_2dlist, colour_list)