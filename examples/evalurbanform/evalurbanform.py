import envuo
displaylist = []
displaylist2 = []

def calculate_srfs_area(occ_srflist):
    area = 0
    for srf in occ_srflist:
        area = area + envuo.py3dmodel.calculate.face_area(srf)
    return area

#construct the urban geometry to calculate
points1 = [(50,100,0), (75,75,0), (75,60,0),(100,60,0),(100,50,0), (50,0,0),(0,50,0)]#clockwise
face1 = envuo.py3dmodel.construct.make_polygon(points1)
extrude1 = envuo.py3dmodel.construct.extrude(face1, (0,0,1), 50)

points2 = [(110,40,0), (110,50,0), (150,50,0),(150,40,0)]#clockwise
face2 = envuo.py3dmodel.construct.make_polygon(points2)
extrude2 = envuo.py3dmodel.construct.extrude(face2, (0,0,1), 80)

points3 = [(-10,-10,0), (-10,110,0), (170,110,0),(170,-20,0)]#clockwise
plane_polygon = envuo.py3dmodel.construct.make_polygon(points3)
plane_pypolygon = envuo.interface2py3d.pyptlist_frm_occface(plane_polygon)

occfaces = []
ext1faces = envuo.py3dmodel.fetch.faces_frm_solid(extrude1)
occfaces.extend(ext1faces)
ext2faces = envuo.py3dmodel.fetch.faces_frm_solid(extrude2)
occfaces.extend(ext2faces)

pyfaces = []
for occface in occfaces:
    pyface = envuo.interface2py3d.pyptlist_frm_occface(occface)
    pyfaces.append(pyface)

fai,fuse_psrfs, projected_faces, windplane, surfaces_projected = envuo.urbanformeval.frontal_area_index(pyfaces, plane_pypolygon, (-1,-1,0))
common_area = calculate_srfs_area(fuse_psrfs)
proj_area = calculate_srfs_area(projected_faces)
print len(fuse_psrfs), common_area
print len(projected_faces), proj_area
displaylist2.extend(fuse_psrfs)
displaylist.extend(occfaces)
displaylist.append(windplane)
displaylist.append(plane_polygon)
displaylist2.extend(surfaces_projected)

display2dlist = []
display2dlist.append(displaylist)
display2dlist.append(displaylist2)
colour_list = ["BLUE", "RED"]

envuo.py3dmodel.construct.visualise(display2dlist, colour_list)