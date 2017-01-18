import pyliburo

displaylist = []
points1 = [(0,5,0), (5,5,0), (6,0,0),(5,-5,0),(0,-5,0), (-5,-5,0),(-5,5,0)]#clockwise
face1 = pyliburo.py3dmodel.construct.make_polygon(points1)
extrude1 = pyliburo.py3dmodel.construct.extrude(face1, (0,0,1), 10)

trsfshape = pyliburo.py3dmodel.modify.uniform_scale(extrude1, 0.024, 0.024, 0.024,(0,5,0))
mesh_face_list = pyliburo.py3dmodel.construct.simple_mesh(extrude1)

display2dlist = []
display2dlist.append(mesh_face_list)
display2dlist.append([extrude1])
pyliburo.py3dmodel.construct.visualise(display2dlist, ["WHITE", 'BLACK'])