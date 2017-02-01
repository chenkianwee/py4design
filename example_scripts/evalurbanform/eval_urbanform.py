import os
import time
import pyliburo
import read_collada_4_evalurbanform as read_collada

#========================================================================================================================================
#SPECIFY ALL THE NECCESSARY INPUTS
#=========================================================================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir, os.pardir))

dae_file = os.path.join(parent_path, "pyliburo_example_files","5x5ptblks", "dae", "5x5ptblks.dae")
weatherfilepath = os.path.join(parent_path, "pyliburo_example_files", "weatherfile", "SGP_Singapore.486980_IWEC.epw" )
shgfavi_filepath = os.path.join(parent_path, "pyliburo_example_files","form_eval_example", "dae", "py2radiance_dfavi")
dfavi_filepath = os.path.join(parent_path, "pyliburo_example_files","form_eval_example", "dae", "py2radiance_dfavi")
pvavi_filepath = os.path.join(parent_path, "pyliburo_example_files","form_eval_example", "dae", "py2radiance_pvavi")
pveavi_filepath = os.path.join(parent_path, "pyliburo_example_files","form_eval_example", "dae", "py2radiance_pveavi")
daysim_filepath = os.path.join(parent_path, "pyliburo_example_files","form_eval_example", "dae", "daysim_data")

irrad_threshold = (50*8760*1.5)/1000.0
illum_threshold = 10000
pv_facade_threshold = 512 #kwh/m2
pv_roof_threshold = 1280 #kwh/m2

display2dlist = []
colourlist = []
#==================================================================================================
#read and sort collada file
#==================================================================================================
print "READING COLLADA ..."
time1 = time.clock()

solid_list, opengeom_shells, opengeom_faces, edges = read_collada.read_collada(dae_file)
pyliburo.gml3dmodel.re

boundary = opengeom_faces[-1]#the last face of the open faces is the boundary for this case
nfaces = len(opengeom_faces)
plots = opengeom_faces[0:nfaces-1]
time2 = time.clock()
tt1 = time2-time1
print "TIME TAKEN 4 COLLADA:", tt1/60.0

#==================================================================================================
#calculate RDI
#==================================================================================================
#print "CALCULATING RDI ..."
time3 = time.clock()

rdi,rdi_per,dplots,pplots,fplots,maxrdi_list,edges,peripts=pyliburo.urbanformeval.route_directness(edges, plots, boundary, 
                                                                                                   rdi_threshold = 1.6)

time4 = time.clock()
tt2 = time4-time3

print "RDI:", rdi
print "TIME TAKEN2 4 RDI:", tt2/60.0

#VISUALISE
#display2dlist.append(edges + peripts)
#colourlist.append("BLACK")
#pyliburo.py3dmodel.construct.visualise_falsecolour_topo(maxrdi_list,dplots, other_topo2dlist=display2dlist,
#                                                        other_colourlist = colourlist, maxval_range = 2)

#==================================================================================================
#calculate FAI
#==================================================================================================
print "CALCULATING FAI ..."
time5 = time.clock()

avg_fai, grids,fai_list, fs_list, wp_list, os_list = pyliburo.urbanformeval.frontal_area_index(solid_list, boundary, (1,1,0), 
                                                                                               xdim = 100, ydim = 100)

print 'AVG FAI:',avg_fai
    
time6 = time.clock()
tt3 = time6-time5
print "TIME TAKEN3 4 FAI:", tt3/60.0

#VISUALISE
#display2dlist.append(os_list)
#colourlist.append("WHITE")

#pyliburo.py3dmodel.construct.visualise_falsecolour_topo(fai_list,grids, other_topo2dlist = display2dlist, 
#                                                        other_colourlist = colourlist, minval_range = 0, maxval_range=1)

#==================================================================================================
#calculate SHGFAVI
#==================================================================================================
print "CALCULATING SHGFAVI ..."
time7 = time.clock()
avg_shgfavi, shgfavi_percent, shgfai, topo_list, irrad_ress = pyliburo.urbanformeval.shgfavi(solid_list, irrad_threshold, 
                                                                                     weatherfilepath, 10,10, shgfavi_filepath)
                                                                                     
print "SHGFAVI", avg_shgfavi
time8 = time.clock()
tt4 = time8-time7
print "TIME TAKEN4 4 SHGFAVI:", tt4/60.0

#==========================================================================================================================
#calculate DFAVI
#==========================================================================================================================
print "CALCULATING DFAVI ..."
time9 = time.clock()
avg_dfavi, dfavi_percent, dfai, topo_list, illum_ress = pyliburo.urbanformeval.dfavi(solid_list, illum_threshold, 
                                                                                     weatherfilepath, 10,10, 
                                                                                     dfavi_filepath, daysim_filepath)

print "DFAVI", avg_dfavi
time10 = time.clock()
tt5 = time10-time9
print "TIME TAKEN5 4 DFAVI:", tt5/60.0
#==========================================================================================================================
#calculate PVEAVI
#==========================================================================================================================
print "CALCULATING PVEAVI ..."
time11 = time.clock()
avg_pveavi, pvavi_percent, pveai, epv, topo_list, irrad_ress = pyliburo.urbanformeval.pveavi(solid_list, 
                                                                                             pv_roof_threshold, 
                                                                                             pv_facade_threshold, 
                                                                                             weatherfilepath, 10, 10, 
                                                                                             pveavi_filepath, 
                                                                                             pvravi_threshold = None, 
                                                                                             pvfavi_threshold = None, 
                                                                                             pveavi_threshold = None)
                                                                                             
print 'PVEAVI', avg_pveavi
print "PVEAI", pveai
time12 = time.clock()  
tt7 = time12- time11
print "TIME TAKEN7 4 PVEAVI:", tt7/60.0
print "TOTAL TIME TAKEN:", (time12-time1)/60.0

#VISUALISE
#pyliburo.py3dmodel.construct.visualise_falsecolour_topo(irrad_ress,topo_list)