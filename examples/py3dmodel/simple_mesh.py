import pyliburo

points1 = [(50,100,50), (75,75,50), (75,60,50),(100,60,50),(100,50,50), (50,0,50),(0,50,50)]#clockwise
points2 = [(60,50,0), (50,75,0),(40,50,0),(50,40,0)]#counterclockwise
face1 = pyliburo.py3dmodel.construct.make_polygon(points2)
extrude1 = pyliburo.py3dmodel.construct.extrude(face1, (0,0,1), 50)

tri_list = pyliburo.py3dmodel.construct.simple_mesh(extrude1)
print len(tri_list)
display_2dlist = []
colour_list = []
display_2dlist.append(tri_list)
#display_2dlist.append([extrude1])
colour_list.append("BLACK")
#colour_list.append("WHITE")
pyliburo.py3dmodel.construct.visualise(display_2dlist, colour_list)