import pyliburo
from collada import *

plots_occfacelist = []
network_occedgelist = []

display2dlist = []

dae_file = "F:\\kianwee_work\\spyder_workspace\\pyliburo\\examples\\punggol_case_study\\collada\\simple_case_connectivity.dae"
mesh = Collada(dae_file)
unit = mesh.assetInfo.unitmeter or 1
#print unit
geoms = mesh.scene.objects('geometry')
geoms = list(geoms)
g_cnt = 0
for geom in geoms:   
    prim2dlist = list(geom.primitives())
    for primlist in prim2dlist:     
        if primlist:
            for prim in primlist:
                if type(prim) == polylist.Polygon or type(prim) == triangleset.Triangle:
                    pyptlist = prim.vertices.tolist()
                    occpolygon = pyliburo.py3dmodel.construct.make_polygon(pyptlist)
                    plots_occfacelist.append(occpolygon)
                    g_cnt +=1
                elif type(prim) == lineset.Line:
                    pyptlist = prim.vertices.tolist()
                    occedge = pyliburo.py3dmodel.construct.make_edge(pyptlist[0], pyptlist[1])
                    network_occedgelist.append(occedge)
                    g_cnt +=1

#find the boundary surface: the surface with the biggest area
plot_arealist = []
plot_wirelist = []

for pf in plots_occfacelist:
    parea = pyliburo.py3dmodel.calculate.face_area(pf)
    plot_arealist.append(parea)
    plot_wire = pyliburo.py3dmodel.fetch.wires_frm_face(pf)
    plot_wirelist.extend(plot_wire)
    
boundary_area = max(plot_arealist) 
boundary_index = plot_arealist.index(boundary_area)
boundary_occface = plots_occfacelist[boundary_index]
plots_occfacelist.remove(boundary_occface)
displayitem = pyliburo.urbanformeval.route_directness(network_occedgelist, plots_occfacelist, boundary_occface)
    
#DISPLAY & VISUALISE
display2dlist.append(plots_occfacelist)
display2dlist.append(displayitem)
#display2dlist.append(plot_wirelist)
#display2dlist.append([displayitem[1]])
#display2dlist.append(network_occedgelist)

colourlist = ["WHITE", "RED"]
pyliburo.py3dmodel.construct.visualise(display2dlist, colourlist)
