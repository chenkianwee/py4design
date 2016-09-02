import pyliburo
from collada import *

display2dlist = []
displaylist = []

dae_file = "F:\\kianwee_work\\smart\\may2016-oct2016\\pycollada_testout\\dae\\terrain.dae"
mesh = Collada(dae_file)
unit = mesh.assetInfo.unitmeter or 1
geoms = mesh.scene.objects('geometry')
print geoms
g_cnt = 0
for geom in geoms:    
    print geom
    for primlist in geom.primitives():     
        for prim in primlist:
            if type(prim) == polylist.Polygon or type(prim) == triangleset.Triangle:
                pyptlist = prim.vertices.tolist()
                if g_cnt == 531:
                    print pyptlist
                occpolygon = pyliburo.py3dmodel.construct.make_polygon(pyptlist)
                displaylist.append(occpolygon)
                g_cnt +=1
            elif type(prim) == lineset.Line:
                pyptlist = prim.vertices.tolist()
                occpolygon = pyliburo.py3dmodel.construct.make_edge(pyptlist[0], pyptlist[1])
                displaylist.append(occpolygon)
                g_cnt +=1
            
            
print len(displaylist)
display2dlist.append(displaylist[590:530]) #[0:531])
colourlist = ["WHITE"]
pyliburo.py3dmodel.construct.visualise(display2dlist, colourlist)
