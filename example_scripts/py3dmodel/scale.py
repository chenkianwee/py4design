import pyliburo

displaylist = []
points1 = [(0,5,0), (5,5,0), (6,0,0),(5,-5,0),(0,-5,0), (-5,-5,0),(-5,5,0)]#clockwise
face1 = pyliburo.py3dmodel.construct.make_polygon(points1)
extrude1 = pyliburo.py3dmodel.construct.extrude(face1, (0,1,1), 10)

trsfshape = pyliburo.py3dmodel.modify.uniform_scale(extrude1, 2, 2, 2,(0,5,0))
print pyliburo.py3dmodel.fetch.shape2shapetype(trsfshape)
faces = pyliburo.py3dmodel.fetch.geom_explorer(trsfshape, "face")


mesh_face_list = pyliburo.py3dmodel.construct.simple_mesh(trsfshape)

face_list = pyliburo.py3dmodel.fetch.geom_explorer(trsfshape, "face")
sensor_list = []
for face in face_list:
    sensor_surfaces, sensor_pts, sensor_dirs = pyliburo.gml3dmodel.generate_sensor_surfaces(face,3,3)
    sensor_list.extend(sensor_surfaces)

display2dlist = []
#display2dlist.append(sensor_list)
display2dlist.append([extrude1])
display2dlist.append(faces)
pyliburo.py3dmodel.construct.visualise(display2dlist, ["WHITE", 'BLACK'])