import pylibudo

displaylist1 = []
displaylist2 = []

#point for projection
pypt = (0,0,10)
occ_origcircle = pylibudo.py3dmodel.construct.make_circle(pypt, (0,0,1),5)

#face for projection or intersection
pyptlist = [(50,100,0), (75,60,0), (75,60,50),(50,100,60)]#clockwise
occ_face = pylibudo.py3dmodel.construct.make_polygon(pyptlist)

#intersect edge with face
#define an edge
dest_pypt = (75,90,10)
occ_edge = pylibudo.py3dmodel.construct.make_edge(pypt, dest_pypt)
displaylist1.append(occ_edge)
interss = pylibudo.py3dmodel.calculate.intersect_edge_with_face(occ_edge, occ_face)
if interss:
    pyinterpt = (interss[0].X(),interss[0].Y(),interss[0].Z())
    interss_occcircle = pylibudo.py3dmodel.construct.make_circle(pyinterpt, (0,0,1),3)
    displaylist1.append(interss_occcircle.Edge())

#specify a point and a direction and it will intersect anything thats along the path
occ_interpt, occ_interface = pylibudo.py3dmodel.calculate.intersect_shape_with_ptdir(occ_face, pypt, (1,1,0))

if occ_interpt != None:
    interpt_occcircle = pylibudo.py3dmodel.construct.make_circle((occ_interpt.X(),occ_interpt.Y(),occ_interpt.Z()), (0,0,1),3)
    displaylist2.append(interpt_occcircle.Edge())
    displaylist2.append(occ_interface)
    interpath = pylibudo.py3dmodel.construct.make_edge(pypt, (occ_interpt.X(),occ_interpt.Y(),occ_interpt.Z()))
    displaylist2.append(interpath)

#create the 2dlist
display2dlist = []
display2dlist.append(displaylist1)
display2dlist.append(displaylist2)
colour_list = ["WHITE", "BLUE"]

pylibudo.py3dmodel.construct.visualise(display2dlist, colour_list)