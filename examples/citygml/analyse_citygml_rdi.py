import time
import pyliburo

citygml_filepath = "F:\\kianwee_work\\smart\\journal\\mdpi_sustainability\\case_study\\citygml\\grid_tower1.gml"

displaylist2 = []
evaluations = pyliburo.citygml2eval.Evals(citygml_filepath)

time1 = time.clock()
print "EVALUATING MODEL ... ..."
avg_rdi,rdi_per,plts,pass_plts,fail_plts,rdi_list,edges,peri_pts = evaluations.rdi()

buildings = evaluations.building_occsolids
bcompund = pyliburo.py3dmodel.construct.make_compound(buildings)
building_edges = pyliburo.py3dmodel.fetch.geom_explorer(bcompund, "edge")

print avg_rdi
time2 = time.clock()
print "TOTAL TIME TAKEN", (time2-time1)/60

display2dlist = []
colourlist = []
display2dlist.append(peri_pts)
display2dlist.append(edges)
display2dlist.append(building_edges)
colourlist.append("WHITE")
colourlist.append("WHITE")
colourlist.append("BLACK")
pyliburo.py3dmodel.construct.visualise_falsecolour_topo(rdi_list,plts,
                                                        other_topo2dlist = display2dlist, 
                                                        other_colourlist = colourlist)