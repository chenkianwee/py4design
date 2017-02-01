import os
import pyliburo
from collada import *
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
#specify the citygml file
current_path = os.path.dirname(__file__)
parent_path = os.path.abspath(os.path.join(current_path, os.pardir))
dae_file = os.path.join(parent_path, "example_files", "collada2citygml_example",  "dae", "example3.dae")
#dae_file = os.path.join(parent_path, "example_files","5x5ptblks", "dae", "5x5ptblks.dae")
#or just insert a dae and citygml file you would like to analyse here 
'''dae_file = "C://file2analyse.gml"'''
#================================================================================
#INSTRUCTION: SPECIFY THE CITYGML FILE
#================================================================================
display_2dlist = []
display_list = []

shell_list = []
edge_list = []
mesh = Collada(dae_file)
unit = mesh.assetInfo.unitmeter or 1
geoms = mesh.scene.objects('geometry')
geoms = list(geoms)
gcnt = 0
print len(geoms)
geom_cnt = 0
for geom in geoms:
    prim2dlist = list(geom.primitives())
    if geom_cnt == 38:
        for primlist in prim2dlist: 
            spyptlist = []
            epyptlist = []
            faces = []
            edges = []
            if primlist:
                for prim in primlist:
                    if type(prim) == polylist.Polygon or type(prim) == triangleset.Triangle:
                        pyptlist = prim.vertices.tolist()
                        sorted_pyptlist = sorted(pyptlist)
                        if sorted_pyptlist not in spyptlist:
                            spyptlist.append(sorted_pyptlist)
                            occpolygon = pyliburo.py3dmodel.construct.make_polygon(pyptlist)
                            if not pyliburo.py3dmodel.fetch.is_face_null(occpolygon):
                                poly_area = pyliburo.py3dmodel.calculate.face_area(occpolygon)
                                if not poly_area < 0.00001:
                                    faces.append(occpolygon)
                            gcnt +=1
                    elif type(prim) == lineset.Line:
                        pyptlist = prim.vertices.tolist()
                        pyptlist.sort()
                        if pyptlist not in epyptlist:
                            epyptlist.append(pyptlist)
                            occedge = pyliburo.py3dmodel.construct.make_edge(pyptlist[0], pyptlist[1])
                            edges.append(occedge)
                        gcnt +=1
                        
                if faces:
                    n_unique_faces = len(faces)
                    if n_unique_faces == 1:
                        shell = pyliburo.py3dmodel.construct.make_shell(faces)
                        shell_list.append(shell)
                    if n_unique_faces >1:
                        shell = pyliburo.py3dmodel.construct.make_shell_frm_faces(faces)
                        if shell:
                            shell_list.append(shell[0])
                else:
                    edge_list.extend(edges)
    geom_cnt+=1
                
display_2dlist.append(shell_list)
colour_list = ["WHITE"]
pyliburo.py3dmodel.construct.visualise(display_2dlist, colour_list)