import os
import pyliburo
from collada import *

#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir))
dae_file = os.path.join(parent_path, "example_files", "form_eval_example",  "dae", "grid_tower.dae")
dae_file = os.path.join(parent_path, "example_files","5x5ptblks", "dae", "5x5ptblks.dae")
#or just insert a dae and citygml file you would like to analyse here 
'''dae_file = "C://file2analyse.gml"'''
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
display_2dlist = []
display_list = []

mesh = Collada(dae_file)
unit = mesh.assetInfo.unitmeter or 1
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
                    pyliburo.py3dmodel.fetch.is_face_null(occpolygon)
                    if not pyliburo.py3dmodel.fetch.is_face_null(occpolygon):
                        display_list.append(occpolygon)
                    g_cnt +=1
                elif type(prim) == lineset.Line:
                    pyptlist = prim.vertices.tolist()
                    occpolygon = pyliburo.py3dmodel.construct.make_edge(pyptlist[0], pyptlist[1])
                    #displaylist.append(occpolygon)
                    g_cnt +=1
print len(display_list)
display_2dlist.append(display_list[0:1])
colour_list = ["WHITE"]

pyliburo.py3dmodel.construct.visualise(display_2dlist, colour_list)