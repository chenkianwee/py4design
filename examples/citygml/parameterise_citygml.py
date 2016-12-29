import time
import pyliburo

#specify the citygml file
citygml_filepath = "F:\\kianwee_work\\spyder_workspace\\pyliburo\\examples\\punggol_case_study\\citygml\\punggol_luse50_53.gml"
result_citygml_filepath = "F:\\kianwee_work\\spyder_workspace\\pyliburo\\examples\\punggol_case_study\\citygml\\punggol_variant.gml"
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