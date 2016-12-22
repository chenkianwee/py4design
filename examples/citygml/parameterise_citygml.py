import time
import random
import pyliburo

#specify the citygml file
citygml_filepath = "F:\\kianwee_work\\spyder_workspace\\pyliburo\\examples\\punggol_case_study\\citygml\\punggol_luse24.gml"
result_citygml_filepath = "F:\\kianwee_work\\spyder_workspace\\pyliburo\\examples\\punggol_case_study\\citygml\\punggol_variant.gml"
time1 = time.clock()   
display_2dlist = []
colour_list = []
citygml_reader = pyliburo.pycitygml.Reader(citygml_filepath)

#define the parameter
bldg_parm = pyliburo.gmlparmpalette.BldgFlrAreaHeightParm()
parm_range = bldg_parm.define_int_range(1,10,1)
nparameters = bldg_parm.define_nparameters(citygml_reader)

r_parm_list = []
for _ in range(nparameters):
    r_parm = random.random()
    r_parm_list.append(r_parm)
    
citygml_writer = bldg_parm.execute(citygml_reader, r_parm_list)
citygml_writer.write(result_citygml_filepath)
print "READER", citygml_reader.citymodelnode
print "WRITER", citygml_writer.et
time2 = time.clock() 
print "TIME TAKEN", (time2-time1)/60.0

print "VISUALISING"  
#display_2dlist.append(dlist)
#colour_list.append("RED")
#pyliburo.py3dmodel.construct.visualise(display_2dlist, colour_list)