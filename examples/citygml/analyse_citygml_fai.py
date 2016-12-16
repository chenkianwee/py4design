import time
import pyliburo

#specify the citygml file
#current_path = os.path.dirname(__file__)
#parent_path = os.path.abspath(os.path.join(current_path, os.pardir))
#citygml_filepath = os.path.join(parent_path, "punggol_case_study", "citygml", "punggol_citygml_asim.gml")
citygml_filepath = "F:\\kianwee_work\\smart\\journal\\mdpi_sustainability\\case_study\\citygml\\grid_tower1.gml"

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