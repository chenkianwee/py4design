import envuo

displaylist1 = []
displaylist2 = []
displaylist3 = []
#point for projection
pypt = (0,0,10)

#face for projection
pyptlist = [(50,100,0), (60,80,0), (60,80,50),(50,100,60)]#clockwise
occ_face = envuo.py3dmodel.construct.make_polygon(pyptlist)

projected_pt = envuo.py3dmodel.calculate.project_point_on_faceplane(occ_face, pypt)
pyprojpt = (projected_pt.X(), projected_pt.Y(),projected_pt.Z())
projpt_occcircle = envuo.py3dmodel.construct.make_circle(pyprojpt, (0,0,1),5)
#create the edge between the origpt and the projpt
projpt_occedge = envuo.py3dmodel.construct.make_edge(pypt, pyprojpt)

displaylist1.append(occ_face)
displaylist1.append(projpt_occcircle.Edge())
displaylist1.append(projpt_occedge)

#project point to edge
dest_occedge = envuo.py3dmodel.construct.make_edge((50,100,0), (50,20,0))
interedgept =envuo.py3dmodel.calculate.project_point_on_infedge(dest_occedge, pypt)
interedgept_occcircle = envuo.py3dmodel.construct.make_circle((interedgept.X(), interedgept.Y(), interedgept.Z()), (0,0,1),3)
interedgept_path = envuo.py3dmodel.construct.make_edge(pypt, (interedgept.X(), interedgept.Y(), interedgept.Z()))

displaylist2.append(interedgept_path)
displaylist2.append(dest_occedge)
displaylist2.append(interedgept_occcircle.Edge())

#create the 2dlist
display2dlist = []
display2dlist.append(displaylist1)
display2dlist.append(displaylist2)
colour_list = ["WHITE", "BLUE"]

envuo.py3dmodel.construct.visualise(display2dlist, colour_list)