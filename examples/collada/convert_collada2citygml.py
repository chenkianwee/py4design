import pyliburo
import time

display2dlist = []
colourlist = []
time1 = time.clock()
#dae_file = "F:\\kianwee_work\\smart\\may2016-oct2016\\pycollada_testout\\dae\\grid_tower.dae"
dae_file = "F:\\kianwee_work\\smart\\journal\\mdpi_sustainability\\case_study\\dae\\grid_tower.dae"
citygml_filepath = "F:\\kianwee_work\\smart\\journal\\mdpi_sustainability\\case_study\\citygml\\grid_tower.gml"

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