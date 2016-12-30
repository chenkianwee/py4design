import os
import time
import pyliburo

#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir))
dae_file = os.path.join(parent_path, "example_files", "form_eval_example",  "dae", "grid_tower.dae")
citygml_filepath = os.path.join(parent_path, "example_files", "form_eval_example", "citygml", "grid_tower.gml")
#or just insert a dae and citygml file you would like to analyse here 
'''dae_file = "C://file2analyse.gml"
citygml_filepath = "C://file2analyse.gml"'''
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
display2dlist = []
colourlist = []
time1 = time.clock()

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