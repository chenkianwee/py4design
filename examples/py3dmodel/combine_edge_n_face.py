import pyliburo

points1 = [(50,100,0), (75,75,0), (75,60,0),(100,60,0),(100,50,0), (50,0,0),(0,50,0)]#clockwise
face1 = pyliburo.py3dmodel.construct.make_polygon(points1)


pypt1 = (0,0,0)
pypt2 = (100,80,0)
edge = pyliburo.py3dmodel.construct.make_edge(pypt1, pypt2)

res = pyliburo.py3dmodel.fetch.shape2shapetype(pyliburo.py3dmodel.construct.boolean_common(face1,edge))
res2 =pyliburo.py3dmodel.fetch.shape2shapetype(pyliburo.py3dmodel.construct.boolean_difference(edge,face1))
edgelist = pyliburo.py3dmodel.fetch.geom_explorer(res, "edge")
edgelist2 = pyliburo.py3dmodel.fetch.geom_explorer(res2, "edge")

wire = pyliburo.py3dmodel.fetch.wires_frm_face(face1)[0]
#turn the wire into a degree1 bspline curve edge
pyptlist = pyliburo.py3dmodel.fetch.occptlist2pyptlist(pyliburo.py3dmodel.fetch.points_frm_wire(wire))
pyptlist.append(pyptlist[0])
bspline_edge  =  pyliburo.py3dmodel.construct.make_bspline_edge(pyptlist, mindegree = 1, maxdegree=1)

interptlist = []
for edge in edgelist:
    interpts = pyliburo.py3dmodel.calculate.intersect_edge_with_edge(bspline_edge, edge)
    interptlist.extend(interpts)

interptlist = pyliburo.py3dmodel.modify.rmv_duplicated_pts(interptlist)
eparmlist = []
for interpt in interptlist:
    eparm = pyliburo.py3dmodel.calculate.pt2edgeparameter(interpt, bspline_edge)
    eparmlist.append(eparm)
    
eparmlist.sort()
edmin,edmax = pyliburo.py3dmodel.fetch.edge_domain(bspline_edge)
eparm_range1 = eparmlist[-1] - eparmlist[0]
eparm_range21 = eparmlist[0] - edmin
eparm_range22 = edmax-eparmlist[-1]
eparm_range2 = eparm_range21 + eparm_range22

new_route_pyptlist = []
if eparm_range1 < eparm_range2 or eparm_range1 == eparm_range2 :
    te = pyliburo.py3dmodel.modify.trimedge(eparmlist[0],eparmlist[-1], bspline_edge)
    telength = pyliburo.py3dmodel.calculate.edgelength(eparmlist[0],eparmlist[-1], bspline_edge)
    sorted_edge2dlist = pyliburo.py3dmodel.calculate.sort_edges_into_order([edgelist2[0],te, edgelist2[1]])
    
if eparm_range1 > eparm_range2:
    te1 = pyliburo.py3dmodel.modify.trimedge(edmin, eparmlist[0], bspline_edge)
    te2 = pyliburo.py3dmodel.modify.trimedge(eparmlist[-1], edmax, bspline_edge)
    telength1 = pyliburo.py3dmodel.calculate.edgelength(edmin, eparmlist[0], bspline_edge)
    telength2 = pyliburo.py3dmodel.calculate.edgelength(eparmlist[-1],edmax, bspline_edge)
    telength = telength1+telength2
    sorted_edge2dlist = pyliburo.py3dmodel.calculate.sort_edges_into_order([edgelist2[0], te1, te2, edgelist2[1]])
    
sorted_edgelist = sorted_edge2dlist[0]
#turn the wire into a degree1 bspline curve edge
new_pyptlist = []

for sorted_edge in sorted_edgelist:
    
    if pyliburo.py3dmodel.fetch.is_edge_bspline(sorted_edge):
        pts = pyliburo.py3dmodel.fetch.poles_from_bsplinecurve_edge(sorted_edge)
    if pyliburo.py3dmodel.fetch.is_edge_line(sorted_edge):
        pts = pyliburo.py3dmodel.fetch.occptlist2pyptlist(pyliburo.py3dmodel.fetch.points_from_edge(sorted_edge))
        
    print pts
    new_pyptlist.extend(pts)
    
new_bspline_edge = pyliburo.py3dmodel.construct.make_bspline_edge(new_pyptlist, mindegree = 1, maxdegree=1)    

e2length = 0
for edge2 in edgelist2:
    e2dmin, e2dmax = pyliburo.py3dmodel.fetch.edge_domain(edge2)
    e2length = e2length + pyliburo.py3dmodel.calculate.edgelength(e2dmin, e2dmax, edge2)
    
print telength + e2length

display2dlist = []
display2dlist.append([new_bspline_edge])
#display2dlist.append(pyliburo.py3dmodel.fetch.pyptlist2vertlist(te1poles)[0:4])
#display2dlist.append([edgelist2[0],edgelist2[1]])
pyliburo.py3dmodel.construct.visualise(display2dlist, ["WHITE", "RED"])
