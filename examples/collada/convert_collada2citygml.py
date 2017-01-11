import os
import time
import pyliburo

#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir))
dae_file = os.path.join(parent_path, "example_files", "form_eval_example",  "dae", "complex_testout_rhino.dae")
citygml_filepath = os.path.join(parent_path, "example_files", "form_eval_example", "citygml", "complex.gml")
#or just insert a dae and citygml file you would like to analyse here 
'''dae_file = "C://file2analyse.gml"
citygml_filepath = "C://file2analyse.gml"'''
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
display2dlist = []
colourlist = []
time1 = time.clock()

#first set up the massing2citygml object
massing_2_citygml = pyliburo.massing2citygml.Massing2Citygml()
massing_2_citygml.read_collada(dae_file)

#first set up the analysis rule necessary for the template rules
is_shell_closed = pyliburo.analysisrulepalette.IsShellClosed()
is_shell_in_boundary = pyliburo.analysisrulepalette.IsShellInBoundary()
shell_contains = pyliburo.analysisrulepalette.ShellContains()
is_edge_in_boundary = pyliburo.analysisrulepalette.IsEdgeInBoundary()

#then set up the template rules and append it into the massing2citygml obj
id_bldgs = pyliburo.templaterulepalette.IdentifyBuildingMassings()
id_bldgs.add_analysis_rule(is_shell_closed, True)
id_bldgs.add_analysis_rule(is_shell_in_boundary, True)
id_bldgs.add_analysis_rule(shell_contains, False)

id_terrains = pyliburo.templaterulepalette.IdentifyTerrainMassings()
id_terrains.add_analysis_rule(is_shell_closed, False)
id_terrains.add_analysis_rule(is_shell_in_boundary, False)
id_terrains.add_analysis_rule(shell_contains, True)

id_landuses = pyliburo.templaterulepalette.IdentifyLandUseMassings()
id_landuses.add_analysis_rule(is_shell_closed, False)
id_landuses.add_analysis_rule(is_shell_in_boundary, True)
id_landuses.add_analysis_rule(shell_contains, True)

id_roads = pyliburo.templaterulepalette.IdentifyRoadMassings()
id_roads.add_analysis_rule(is_edge_in_boundary, True)

massing_2_citygml.add_template_rule(id_bldgs)
massing_2_citygml.add_template_rule(id_terrains)
massing_2_citygml.add_template_rule(id_landuses)
massing_2_citygml.add_template_rule(id_roads)

#execute the massing2citygml obj
massing_2_citygml.execute_analysis_rule()
massing_2_citygml.execute_template_rule(citygml_filepath)

'''
#then set up the 
cityobj_dict = pyliburo.collada2citygml.auto_convert_dae2gml(dae_file, citygml_filepath)
bldg_list = cityobj_dict["building"]
landuse_list = cityobj_dict["landuse"]
terrain_list =  cityobj_dict["terrain"]
network_list =  cityobj_dict["network"]

time2 = time.clock()
tt1 = time2-time1
print "TotatTime:", tt1
display2dlist.append(bldg_list)
colourlist.append("RED")
display2dlist.append(landuse_list)
colourlist.append("BLUE")
display2dlist.append(terrain_list)
colourlist.append("GREEN")
display2dlist.append(network_list)
colourlist.append("BLACK")
pyliburo.py3dmodel.construct.visualise(display2dlist, colourlist)
'''