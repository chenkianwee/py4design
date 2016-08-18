import envuo

display_list = []
points1 = [(50,100,0), (75,75,0), (75,60,0),(100,60,0),(100,50,0), (50,0,0),(0,50,0)]#clockwise
points2 = [(60,50,0), (50,75,0),(40,50,0),(50,40,0)]#counterclockwise
points3 = [(50,40,0),(40,50,0),(30,40,0),(40,40,0)]
points4 = [(60,30,0),(70,30,0),(70,40,0),(60,40,0)]

face1 = envuo.py3dmodel.construct.make_polygon(points1)
extrude1 = envuo.py3dmodel.construct.extrude(face1, (0,0,1), 50)
face2 = envuo.py3dmodel.construct.make_polygon(points2)
extrude2 = envuo.py3dmodel.construct.extrude(face2, (0,0,1), 80)
print envuo.py3dmodel.calculate.minimum_distance(extrude1, extrude2)

display_list.append(extrude1)
display_list.append(extrude2)
envuo.py3dmodel.construct.visualise(display_list, "WHITE")