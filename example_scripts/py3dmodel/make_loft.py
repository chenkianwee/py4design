import pyliburo
points1 = [(50,100,0), (75,75,0), (75,60,0),(100,60,0),(100,50,0), (50,0,0),(0,50,0)]#clockwise
face1 = pyliburo.py3dmodel.construct.make_polygon(points1)
moved_face_list = []
flr2flr = 3
for cnt in range(3):
    orig_pt = pyliburo.py3dmodel.calculate.face_midpt(face1)
    loc_pt = pyliburo.py3dmodel.modify.move_pt(orig_pt, (0,0,1), cnt*flr2flr)
    moved_face = pyliburo.py3dmodel.modify.move(orig_pt, loc_pt, face1)
    moved_face_list.append(moved_face)
    
loft = pyliburo.py3dmodel.construct.make_loft(moved_face_list)
print pyliburo.py3dmodel.fetch.get_shapetype(loft)
print len(pyliburo.py3dmodel.fetch.geom_explorer(loft, "face"))
display_2dlist = []
display_2dlist.append([loft])
colour_list = []
colour_list.append("WHITE")
pyliburo.py3dmodel.construct.visualise(display_2dlist, colour_list)