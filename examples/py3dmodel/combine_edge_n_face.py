import pyliburo

points1 = [(50,100,0), (75,75,0), (75,60,0),(100,60,0),(100,50,0), (50,0,0),(0,50,0)]#clockwise
face1 = pyliburo.py3dmodel.construct.make_polygon(points1)


pypt1 = (0,0,0)
pypt2 = (100,95,0)
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

interptlist = pyliburo.py3dmodel.modify.rmv_duplicated_pts(interptlist,roundndigit = 2)
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
    new_route_pyptlist.extend(pyliburo.py3dmodel.fetch.points_from_edge(edgelist2[0]))
    new_route_pyptlist.extend(pyliburo.py3dmodel.fetch.poles_from_bsplinecurve_edge(te))
    new_route_pyptlist.extend(pyliburo.py3dmodel.fetch.points_from_edge(edgelist2[1]))
    new_route_wire = pyliburo.py3dmodel.construct.make_wire(new_route_pyptlist)
    
if eparm_range1 > eparm_range2:
    te1 = pyliburo.py3dmodel.modify.trimedge(edmin, eparmlist[0], bspline_edge)
    te2 = pyliburo.py3dmodel.modify.trimedge(eparmlist[-1], edmax, bspline_edge)
    telength1 = pyliburo.py3dmodel.calculate.edgelength(edmin, eparmlist[0], bspline_edge)
    telength2 = pyliburo.py3dmodel.calculate.edgelength(eparmlist[-1],edmax, bspline_edge)
    telength = telength1+telength2
    closew, openw = pyliburo.py3dmodel.calculate.identify_open_close_wires_frm_loose_edges([edgelist2[0], edgelist2[1],te1,te2])  
    #new_route_pyptlist.extend(pyliburo.py3dmodel.fetch.occptlist2pyptlist(pyliburo.py3dmodel.fetch.points_from_edge(edgelist2[0])))
    new_route_pyptlist.extend(pyliburo.py3dmodel.fetch.poles_from_bsplinecurve_edge(te1))
    new_route_pyptlist.extend(pyliburo.py3dmodel.fetch.poles_from_bsplinecurve_edge(te2))
    #new_route_pyptlist.extend(pyliburo.py3dmodel.fetch.occptlist2pyptlist(pyliburo.py3dmodel.fetch.points_from_edge(edgelist2[1])))
    new_route_pyptlist = pyliburo.py3dmodel.modify.rmv_duplicated_pts(new_route_pyptlist, roundndigit = 2)
    print new_route_pyptlist
    new_route_wire = pyliburo.py3dmodel.construct.make_wire(new_route_pyptlist)
    
#turn the wire into a degree1 bspline curve edge
#new_pyptlist = pyliburo.py3dmodel.fetch.occptlist2pyptlist(pyliburo.py3dmodel.fetch.points_frm_wire(new_route_wire))
#new_bspline_edge = pyliburo.py3dmodel.construct.make_bspline_edge(new_pyptlist, mindegree = 1, maxdegree=1)    
    
    
e2length = 0
for edge2 in edgelist2:
    e2dmin, e2dmax = pyliburo.py3dmodel.fetch.edge_domain(edge2)
    e2length = e2length + pyliburo.py3dmodel.calculate.edgelength(e2dmin, e2dmax, edge2)
    
print telength + e2length

display2dlist = []
display2dlist.append([new_route_wire])
display2dlist.append([edgelist2[0],edgelist2[1]])
pyliburo.py3dmodel.construct.visualise(display2dlist, ["WHITE", "RED"])