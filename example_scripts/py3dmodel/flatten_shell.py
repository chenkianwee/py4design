import pyliburo

points1 = [(5,5,0), (10,5,0), (10,10,0),(15,10,0),(15,15,0), (5,15,0)]#clockwise
face1 = pyliburo.py3dmodel.construct.make_polygon(points1)

extrude1 = pyliburo.py3dmodel.construct.extrude(face1, (0,0,1), 10)
shell = pyliburo.py3dmodel.fetch.geom_explorer(extrude1, "shell")[0]
flatten_face = pyliburo.py3dmodel.modify.flatten_shell_z_value(shell)


display_2dlist = []
colour_list = []
#display_2dlist.append([extrude1])
display_2dlist.append([flatten_face])

#colour_list.append("WHITE")
colour_list.append("RED")
pyliburo.py3dmodel.construct.visualise(display_2dlist, colour_list)