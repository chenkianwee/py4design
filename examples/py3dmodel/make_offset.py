import pyliburo
points1 = [(50,100,0), (75,75,0), (75,60,0),(100,60,0),(100,50,0), (50,0,0),(0,50,0)]#clockwise
face1 = pyliburo.py3dmodel.construct.make_polygon(points1)
extrude = pyliburo.py3dmodel.construct.extrude(face1, (1,1,1), 50)
face_list = pyliburo.py3dmodel.fetch.geom_explorer(extrude, "face")
face4 = face_list[3]
ref_pypt = pyliburo.py3dmodel.calculate.face_midpt(face4)
scaled_face4 = pyliburo.py3dmodel.modify.uniform_scale(face4, 0.5,0.5,0.5,ref_pypt)
#offset_face4 = pyliburo.py3dmodel.construct.make_offset(face4, -10)

display_2dlist = []
display_2dlist.append([face4])
display_2dlist.append([scaled_face4])
#display_2dlist.append([offset_face4])
#display_2dlist.append([extrude])
colour_list = []
colour_list.append("WHITE")
colour_list.append("RED")
#colour_list.append("BLUE")
#colour_list.append("YELLOW")
pyliburo.py3dmodel.construct.visualise(display_2dlist, colour_list)