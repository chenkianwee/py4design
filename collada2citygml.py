# ==================================================================================================
#
#    Copyright (c) 2016, Chen Kian Wee (chenkianwee@gmail.com)
#
#    This file is part of pyliburo
#
#    pyliburo is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    pyliburo is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Dexen.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================

import py3dmodel
from collada import *

'''
script to automatically convert a collada file into citygml file
the script is tested with a collada file exported from sketchup
'''

display2dlist = []
displaylist = []

dae_file = "F:\\kianwee_work\\smart\\may2016-oct2016\\pycollada_testout\\dae\\plot_n_3buildings_terrain.dae"
dae = Collada(dae_file)
unit = dae.assetInfo.unitmeter or 1
meshs = list(dae.scene.objects('geometry'))
g_cnt = 0
for mesh in meshs:
    prim2dlist = list(mesh.primitives())
    for primlist in prim2dlist:     
        print primlist
        if primlist:
            for prim in primlist:
                if type(prim) == polylist.Polygon or type(prim) == triangleset.Triangle:
                    pyptlist = prim.vertices.tolist()
                    #if g_cnt == 0:
                    #    print pyptlist
                    occpolygon = py3dmodel.construct.make_polygon(pyptlist)
                    displaylist.append(occpolygon)
                    g_cnt +=1
                elif type(prim) == lineset.Line:
                    pyptlist = prim.vertices.tolist()
                    occpolygon = py3dmodel.construct.make_edge(pyptlist[0], pyptlist[1])
                    displaylist.append(occpolygon)
                    g_cnt +=1
            
            
#print len(displaylist)
#print br_ptlist
display2dlist.append(displaylist) #[0:531])
colourlist = ["WHITE"]
py3dmodel.construct.visualise(display2dlist, colourlist)