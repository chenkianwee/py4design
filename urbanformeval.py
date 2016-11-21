# ==================================================================================================
#
#    Copyright (c) 2016, Chen Kian Wee (chenkianwee@gmail.com)
#
#    This file is part of pyliburo
#
#    pyliburo is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    pyliburo is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Dexen.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================
import os
import math
import networkx as nx
import py3dmodel
import gml3dmodel
import py2radiance


def calculate_srfs_area(occ_srflist):
    area = 0
    for srf in occ_srflist:
        area = area + py3dmodel.calculate.face_area(srf)
        
    return area
    
def pyptlist2vertlist(pyptlist):
    vertlist = []
    for pypt in pyptlist:
        vert = py3dmodel.construct.make_vertex(pypt)
        vertlist.append(vert)
    return vertlist

def route_ard_obstruction(obstruction_face, crow_wire):        
    res = py3dmodel.fetch.shape2shapetype(py3dmodel.construct.boolean_common(obstruction_face,crow_wire))
    res2 =py3dmodel.fetch.shape2shapetype(py3dmodel.construct.boolean_difference(crow_wire,obstruction_face))
    edgelist = py3dmodel.fetch.geom_explorer(res, "edge")
    edgelist2 = py3dmodel.fetch.geom_explorer(res2, "edge")
    
    wire = py3dmodel.fetch.wires_frm_face(obstruction_face)[0]
    #turn the wire into a degree1 bspline curve edge
    pyptlist = py3dmodel.fetch.occptlist2pyptlist(py3dmodel.fetch.points_frm_wire(wire))
    pyptlist.append(pyptlist[0])
    bspline_edge  = py3dmodel.construct.make_bspline_edge(pyptlist, mindegree=1, maxdegree=1)
    
    interptlist = []
    for edge in edgelist:
        interpts = py3dmodel.calculate.intersect_edge_with_edge(bspline_edge, edge)
        interptlist.extend(interpts)
    
    interptlist = py3dmodel.modify.rmv_duplicated_pts(interptlist)
    eparmlist = []
    
    for interpt in interptlist:
        eparm = py3dmodel.calculate.pt2edgeparameter(interpt, bspline_edge)
        eparmlist.append(eparm)
        
    eparmlist.sort()
    edmin,edmax = py3dmodel.fetch.edge_domain(bspline_edge)
    eparm_range1 = eparmlist[-1] - eparmlist[0]
    eparm_range21 = eparmlist[0] - edmin
    eparm_range22 = edmax-eparmlist[-1]
    eparm_range2 = eparm_range21 + eparm_range22
    
    if eparm_range1 < eparm_range2 or eparm_range1 == eparm_range2 :
        te = py3dmodel.modify.trimedge(eparmlist[0],eparmlist[-1], bspline_edge)
        edgelist2.append(te)
        sorted_edge2dlist = py3dmodel.calculate.sort_edges_into_order(edgelist2)
        
    if eparm_range1 > eparm_range2:
        te1 = py3dmodel.modify.trimedge(edmin, eparmlist[0], bspline_edge)
        te2 = py3dmodel.modify.trimedge(eparmlist[-1], edmax, bspline_edge)
        edgelist2.append(te1)
        edgelist2.append(te2)
        sorted_edge2dlist = py3dmodel.calculate.sort_edges_into_order(edgelist2)
        
    sorted_edgelist = sorted_edge2dlist[0]
    
    #turn the wire into a degree1 bspline curve edge
    new_pyptlist = []
    for sorted_edge in sorted_edgelist:
        if py3dmodel.fetch.is_edge_bspline(sorted_edge):
            pts = py3dmodel.fetch.poles_from_bsplinecurve_edge(sorted_edge)
        if py3dmodel.fetch.is_edge_line(sorted_edge):
            pts = py3dmodel.fetch.occptlist2pyptlist(py3dmodel.fetch.points_from_edge(sorted_edge))
            
        new_pyptlist.extend(pts)
        
    new_bwire = py3dmodel.construct.make_wire(new_pyptlist)
    return new_bwire
    
def calculate_route_directness(startpypt, peripheralpypt, obstruction_occfacelist,G):
    crow_wire = py3dmodel.construct.make_wire([startpypt, peripheralpypt])   
    #need to check if the crow edge intersect any obstruction
    rerouted_wire = crow_wire 
    for obface in obstruction_occfacelist:
        common_compound = py3dmodel.construct.boolean_common(obface, rerouted_wire)
        is_comp_null = py3dmodel.fetch.is_compound_null(common_compound)
        if not is_comp_null:
            #means there is an intersection
            #need to reconstruct the distance
            rerouted_wire = route_ard_obstruction(obface, crow_wire)
            
    #measure the direct distance
    direct_distance = py3dmodel.calculate.wirelength(rerouted_wire)
    #measure the route distance
    shortest_path = nx.shortest_path(G,source=startpypt,target=peripheralpypt)
    nshortpath = len(shortest_path)
    route_distance = 0
    for scnt in range(nshortpath):
        if scnt != nshortpath-1:
            network_edge = G[shortest_path[scnt]][shortest_path[scnt+1]]
            route_distance = route_distance + network_edge["distance"]
            
    route_directness = route_distance/direct_distance
    return route_directness
    
def generate_directions(rot_degree):
    #generate the direction from the midpt to the plot edges 
    orig_vert = py3dmodel.construct.make_vertex((0,1,0))
    pydirlist = []
    for dircnt in range(int(360/rot_degree)):
        degree = rot_degree*dircnt
        rot_vert = py3dmodel.modify.rotate(orig_vert, (0,0,0), (0,0,1), degree)
        gppt = py3dmodel.fetch.vertex2point(rot_vert)
        pypt = py3dmodel.fetch.occpt2pypt(gppt)
        pydirlist.append(pypt)
        
    return pydirlist
    
def construct_network_compound(network_occedgelist, extrusion_height):
    nfacelist = []
    for nedge in network_occedgelist:
        #move the edge upwards then loft it to make a face
        nface = py3dmodel.construct.extrude_edge(nedge, (0,0,1), 10)
        nfacelist.append(nface)

    network_compound = py3dmodel.construct.make_compound(nfacelist)
    return network_compound
    
    
def frontal_area_index(facet_occpolygons, plane_occpolygon, wind_dir):
    '''
    Algorithm to calculate frontal area index
    
    PARAMETERS
    ----------
    :param facet_occpolygons : a list of occ faces of vertical facades 
    :ptype: list(occface)
    
    :param plane_occpolygon: an occ face that is the horizontal plane buildings are sitting on 
    :ptype: occface
    
    :param wind_dir: a 3d tuple specifying the direction of the wind
    :ptype: tuple
    
    RETURNS
    -------
    :returns fai: frontal area index 
    :rtype: float
    
    :returns fuse_srfs: the projected surfaces fused together
    :rtype: list(occface)
    
    :returns projected_facet_faces: the projected surfaces not fuse together
    :rtype: list(occface)
    
    :returns wind_plane: the plane representing the direction of the wind
    :rtype: occface
    
    :returns surfaces_projected: the facade surfaces that are projected
    :rtype: list(occface)
    
    '''
    facet_faces_compound = py3dmodel.construct.make_compound(facet_occpolygons)
     
    #create win dir plane
    #get the bounding box of the compound, so that the wind plane will be placed at the edge of the bounding box
    xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(facet_faces_compound)
    pymidpt = py3dmodel.calculate.get_centre_bbox(facet_faces_compound)
    #calculate the furthest distance of the bounding box
    pycornerpt = (xmin, ymin, 0)
    
    furtherest_dist = py3dmodel.calculate.distance_between_2_pts(pymidpt, pycornerpt)
    #create the wind plane 
    pt4plane = py3dmodel.modify.move_pt(pymidpt, wind_dir, furtherest_dist) 
    wind_plane = py3dmodel.construct.make_plane_w_dir(pt4plane, wind_dir)
    
    surfaces_projected = []
    projected_facet_faces = []
    for facet_face in facet_occpolygons:
        srf_dir = py3dmodel.calculate.face_normal(facet_face)
        #srf_midpt = py3dmodel.calculate.face_midpt(urb_face)
        angle = py3dmodel.calculate.angle_bw_2_vecs(wind_dir, srf_dir)
        #interpt, interface = py3dmodel.calculate.intersect_shape_with_ptdir(wind_plane, srf_midpt, srf_dir)
        if angle<90:
            surfaces_projected.append(facet_face)
            projected_pts = py3dmodel.calculate.project_face_on_faceplane(wind_plane, facet_face)
            projected_srf = py3dmodel.construct.make_polygon(py3dmodel.fetch.occptlist2pyptlist(projected_pts))
            if py3dmodel.calculate.face_area(projected_srf) >0:
                projected_facet_faces.append(projected_srf)
         
    npfaces = len(projected_facet_faces)
    if npfaces == 1:
        fuse_srfs = projected_facet_faces
    else:
        for psrf_cnt in range(npfaces-1):
            if psrf_cnt ==0:
                fuse_shape = py3dmodel.construct.boolean_fuse(projected_facet_faces[psrf_cnt], projected_facet_faces[psrf_cnt+1])
            else:
                fuse_shape = py3dmodel.construct.boolean_fuse(fuse_shape, projected_facet_faces[psrf_cnt+1])
                
        fuse_compound = py3dmodel.fetch.shape2shapetype(fuse_shape) 
        fuse_srfs = py3dmodel.fetch.geom_explorer(fuse_compound,"face")
    
    #calculate the frontal area index
    facet_area = calculate_srfs_area(fuse_srfs)
    plane_area = py3dmodel.calculate.face_area(plane_occpolygon)
    fai = facet_area/plane_area
    
    return fai, fuse_srfs, projected_facet_faces, wind_plane, surfaces_projected
    
def route_directness(network_occedgelist, plot_occfacelist, boundary_occface, obstruction_occfacelist = [], route_directness_threshold = 1.6):
    '''
    Algorithm for Route Directness Test  
    Stangl, P.. 2012 the pedestrian route directness test: A new level of service model.
    urban design international 17, 228-238
    
    A test that measures the connectivity of street network in a neighbourhood
    measuring route directness for each parcel to each of a series
    of points around the periphery of the study area,
    and identifying the percentage of parcels for which
    any of these measures exceed 1.6. Urban area is 1.3, suburban is 1.6
    
    PARAMETERS
    ----------
    :param network_occedgelist : a list of occedges that is the network to be analysed, clearly define network with
        nodes and edges
    :ptype: list(occedge)
    
    :param plot_occfacelist: a list of occfaces that is the land use plots
    :ptype: list(occface)
    
    :param boundary_occface: occface that is the boundary of the area
    :ptype: occface
    
    :param route_directness_threshold: a float specifying the route directness threshold, default value 1.6
    :ptype: float
    
    RETURNS
    -------
    :returns route_directness_measure: route_directness_measure
    :rtype: float
    
    :returns failed_plots: plots that fail the route directness measure
    :rtype: list(occface)
    
    :returns successful_plots: plots that pass the route directness measure
    :rtype: list(occface)
    
    :returns peripheral_pts: peripheral pts
    :rtype: list(occpts)
    
    '''
    displaylist = []
    #======================================================================
    #designate peripheral points
    #======================================================================
    peripheral_ptlist = []
    peripheral_parmlist = []
    boundary_pyptlist = py3dmodel.fetch.pyptlist_frm_occface(boundary_occface)
    boundary_pyptlist.append(boundary_pyptlist[0])
    #extract the wire from the face and convert it to a bspline curve
    bedge = py3dmodel.construct.make_bspline_edge(boundary_pyptlist, mindegree=1, maxdegree=1)
    
    #get all the intersection points 
    interptlist = []
    for network_occedge in network_occedgelist:
        intersect_pts = py3dmodel.calculate.intersect_edge_with_edge(bedge, network_occedge, tolerance=1e-02)
        if intersect_pts!=None:
            interptlist.extend(intersect_pts)
            
    #remove all duplicate points    
    fused_interptlist = py3dmodel.modify.rmv_duplicated_pts(interptlist)
    
    #translate all the points to parameter
    ulist = []
    for fused_interpt in fused_interptlist:
        parmu = py3dmodel.calculate.pt2edgeparameter(fused_interpt,bedge)
        ulist.append(parmu)
    
    ulist = sorted(ulist)
    nulist = len(ulist)
    
    #place a marker at the midpt between thiese intersection
    midptlist = []
    mulist = []
    bedge_lbound, bedge_ubound = py3dmodel.fetch.edge_domain(bedge)
    for ucnt in range(nulist):
        curparm = ulist[ucnt]
        if ucnt == nulist-1:
            if curparm == 1 and ulist[0] != 0:
                terange = ulist[0]-0
                temidparm = terange/2
                
            elif curparm !=1 and ulist[0] != 0:
                terange1 = 1-curparm
                terange2 =  ulist[0]-0
                terange3 = terange1+terange2
                temidparm = curparm + (terange3/2)
                if temidparm > 1:
                    temidparm = temidparm-1
                
            elif curparm !=1 and ulist[0] == 0:
                terange = 1-curparm
                temidparm = terange/2

        else:
            terange = ulist[ucnt+1]-curparm
            temidparm = curparm + (terange/2)
        
        temid = py3dmodel.calculate.edgeparameter2pt(temidparm, bedge)            
        midptlist.append(temid)
        mulist.append(temidparm)
    
    #check the spacing of all the points to ensure they are not more than 106m (350')
    #if they are divide them as accordingly
    umulist = sorted(mulist + ulist)
    numulist = len(umulist)
    for mcnt in range(numulist):
        mcurparm = umulist[mcnt]
        if mcnt == numulist-1:
            if mcurparm == 1 and umulist[0] != 0:
                mcurparm = 0
                mnextparm = umulist[0]
                mrange = mnextparm - mcurparm
                mlength = py3dmodel.calculate.edgelength(mcurparm,mnextparm, bedge)
                
            elif mcurparm !=1 and umulist[0] != 0:
                mlength1 = py3dmodel.calculate.edgelength(mcurparm,1, bedge)
                mlength2 = py3dmodel.calculate.edgelength(0,umulist[0], bedge)
                mrange1 = 1-mcurparm
                mrange2 = umulist[0]-0
                mrange = mrange1+mrange2
                mlength = mlength1+mlength2
        else:
            mnextparm = umulist[mcnt+1]
            mrange = mnextparm - mcurparm
            mlength = py3dmodel.calculate.edgelength(mcurparm,mnextparm, bedge)
            
        #TODO solve the unit problem 
        if (mlength*0.0254) > 106:
            #divide the segment into 106m segments
            nsegments = math.ceil((mlength*0.0254)/106.0)
            segment = mrange/nsegments
            for scnt in range(int(nsegments)-1):
                divparm = mcurparm + ((scnt+1)*segment)
                if divparm >1:
                    divparm = divparm - 1
                
                peripheral_parmlist.append(divparm)
                
    peripheral_parmlist.extend(mulist)
    peripheral_parmlist.sort()
    
    #reconstruct the boundary into curve segments 
    pcurvelist = []
    nplist = len(peripheral_parmlist)
    for pcnt in range(nplist):
        pcurparm = peripheral_parmlist[pcnt]
        if pcnt == nplist-1:
            if pcurparm == 1 and peripheral_parmlist[0] != 0:
                pcurparm = 0
                pnextparm = peripheral_parmlist[0]
                pcurve = py3dmodel.modify.trimedge(pcurparm, pnextparm, bedge)
                pcurvelist.append(pcurve)
                
            elif pcurparm !=1 and peripheral_parmlist[0] != 0:
                pcurve1 = py3dmodel.modify.trimedge(pcurparm, 1, bedge)
                pcurve2 = py3dmodel.modify.trimedge(0, peripheral_parmlist[0], bedge)
                pcurvelist.append(pcurve1)
                pcurvelist.append(pcurve2)
        else:
            pnextparm = peripheral_parmlist[pcnt+1]
            pcurve = py3dmodel.modify.trimedge(pcurparm, pnextparm, bedge)
            pcurvelist.append(pcurve)
            
    for pparm in peripheral_parmlist:
        peripheral_pt = py3dmodel.calculate.edgeparameter2pt(pparm, bedge)
        peripheral_ptlist.append(peripheral_pt)
        
    pedgelist = []
    for pc in pcurvelist:
        ppoles = py3dmodel.fetch.poles_from_bsplinecurve_edge(pc)
        pwire = py3dmodel.construct.make_wire(ppoles)
        pedges = py3dmodel.fetch.edges_frm_wire(pwire)
        pedgelist.extend(pedges)
        
    peripheral_pyptlist = []
    for peredge in pedgelist:
        peripheral_pyptlist.extend(py3dmodel.fetch.occptlist2pyptlist(py3dmodel.fetch.points_from_edge(peredge)))
        
    peripheral_pyptlist = py3dmodel.modify.rmv_duplicated_pts(peripheral_pyptlist, roundndigit = 2)
    
    #======================================================================
    #construct the network between the midpt of the plot to the internal network
    #======================================================================
    plot_edgeptlist = []
    plot_midptlist = []
    network_ptlist = []
    midpt2_network_edgelist = []
    network_compound = construct_network_compound(network_occedgelist, 10)
    #get the mid point of the plot
    for plot_occface in plot_occfacelist:
        pymidpt = py3dmodel.calculate.face_midpt(plot_occface)
        plot_midptlist.append(pymidpt)
        plot_edgeptlist.append([])
        #get all the edges of the plot 
        plotedgelist = py3dmodel.fetch.geom_explorer(plot_occface, "edge")
        #extrude the plot into a solid
        pextrude = py3dmodel.fetch.shape2shapetype(py3dmodel.construct.extrude(plot_occface,(0,0,1), 10))
        #face_list = py3dmodel.fetch.geom_explorer(pextrude, "face")
        for pedge in plotedgelist:
            #find the midpt of the edge 
            pedge_midpypt = py3dmodel.calculate.edge_midpt(pedge)
            #shoot the midpt towards the midpt of the edge
            midpt2pedge = py3dmodel.construct.make_edge(pymidpt, pedge_midpypt)
            midpt2_network_edgelist.append(midpt2pedge)
            gpvec = py3dmodel.construct.make_vector(pymidpt,pedge_midpypt)
            pyvec = py3dmodel.modify.normalise_vec(gpvec)
            inter_occpt, inter_face = py3dmodel.calculate.intersect_shape_with_ptdir(pextrude, pymidpt, pyvec) 
            pydir = py3dmodel.calculate.face_normal(inter_face)
            inter_occpt2, inter_face2 = py3dmodel.calculate.intersect_shape_with_ptdir(network_compound, pedge_midpypt, pydir)             
            if inter_occpt2 !=None:
                #it means according to the normal direction of the surface it will hit a network edge
                inter_pypt = py3dmodel.fetch.occpt2pypt(inter_occpt2)
                pedge2network = py3dmodel.construct.make_edge(pedge_midpypt, inter_pypt)
                network_ptlist.append(inter_pypt)
                midpt2_network_edgelist.append(pedge2network)
                rounded_pedge_midpypt = py3dmodel.modify.round_pypt(pedge_midpypt,2)
                plot_edgeptlist[-1].append(rounded_pedge_midpypt)
                #make sure the plot edge is a free edge
                #if it cuts any of the plots it means it is not a free edge
                for plot_occface2 in plot_occfacelist:
                    dmin,dmax = py3dmodel.fetch.edge_domain(pedge2network)
                    drange = dmax-dmin
                    dquantum = 0.1*drange
                    pypt1 = py3dmodel.calculate.edgeparameter2pt(dmin+dquantum, pedge2network)
                    pypt2 = py3dmodel.calculate.edgeparameter2pt(dmax, pedge2network)
                    pedge2network2 = py3dmodel.construct.make_edge(pypt1, pypt2)
                    is_intersecting = py3dmodel.construct.boolean_common(plot_occface2,pedge2network2)
                    
                    if not py3dmodel.fetch.is_compound_null(is_intersecting):
                        #it is not a free edge
                        midpt2_network_edgelist.remove(midpt2pedge)
                        midpt2_network_edgelist.remove(pedge2network)
                        network_ptlist.remove(inter_pypt)
                        plot_edgeptlist[-1].remove(rounded_pedge_midpypt)
                        break

            else:
                midpt2_network_edgelist.remove(midpt2pedge)

    #reconstruct the network edges with the new network_ptlist
    new_network_occedgelist = network_occedgelist[:]
    for networkpt in network_ptlist:
        network_vert = py3dmodel.construct.make_vertex(networkpt)
        for nedge in new_network_occedgelist:
            #find the edge the point belongs to 
            env_mindist = py3dmodel.calculate.minimum_distance(network_vert,nedge)
            if env_mindist <= 1e-06:
                #that means the point belongs to this edge
                #remove the original edge
                new_network_occedgelist.remove(nedge)
                #find the parameter then reconstruct the edge accordingly
                dmin, dmax = py3dmodel.fetch.edge_domain(nedge)
                domain_list = [dmin, dmax]
                inter_parm = py3dmodel.calculate.pt2edgeparameter(networkpt, nedge)
                domain_list.append(inter_parm)
                domain_list.sort()
                #reconstruct the edge 
                pypt1 = py3dmodel.calculate.edgeparameter2pt(domain_list[0], nedge)
                pypt2 = py3dmodel.calculate.edgeparameter2pt(domain_list[1], nedge)
                pypt3 = py3dmodel.calculate.edgeparameter2pt(domain_list[2], nedge)
                n_nedge1 = py3dmodel.construct.make_edge(pypt1, pypt2)
                new_network_occedgelist.append(n_nedge1)
                n_nedge2 = py3dmodel.construct.make_edge(pypt2, pypt3)
                new_network_occedgelist.append(n_nedge2)
                break
    
    #======================================================================
    #construct the networkx network
    #======================================================================
    #create a graph
    G = nx.Graph()
    #add all the edges for the boundary
    edges4_networkx = new_network_occedgelist + pedgelist + midpt2_network_edgelist
    
    for x_edge in edges4_networkx:
        edge_nodes = py3dmodel.fetch.occptlist2pyptlist(py3dmodel.fetch.points_from_edge(x_edge))
        edge_nodes = py3dmodel.modify.round_pyptlist(edge_nodes, 2)
        xdmin,xdmax = py3dmodel.fetch.edge_domain(x_edge)
        length = py3dmodel.calculate.edgelength(xdmin,xdmax,x_edge)
        G.add_edge(edge_nodes[0],edge_nodes[1], distance = length)
            
    #======================================================================
    #measure route directness
    #======================================================================
    #loop thru all the midpts of the plot
    pass_plots = plot_occfacelist[:]
    fail_plots = []
    plot_midptlist = py3dmodel.modify.round_pyptlist(plot_midptlist,2)
    graph_nodes = G.nodes()
    plcnt = 0
    for midpt in plot_midptlist:
        #check if the plot is a dead plot with no free edges
        plof_occface = plot_occfacelist[plcnt]
        if midpt not in graph_nodes:
            fail_plots.append(plof_occface)
            pass_plots.remove(plof_occface)
        else:        
            #measure the direct distance crow flies distance
            #TODO solve the unit problem 
            plot_area = py3dmodel.calculate.face_area(plof_occface)*0.00064516   
            #1/2 acre
            if plot_area <= 2023: 
                for perpypt in peripheral_pyptlist:
                    route_directness = calculate_route_directness(midpt, perpypt, obstruction_occfacelist,G)
                    print route_directness, plcnt
                    if route_directness > route_directness_threshold:
                        fail_plots.append(plof_occface)
                        pass_plots.remove(plof_occface)
                        break
            else:
                route_directness_list = []
                escnt = 0
                nespt = len(plot_edgeptlist)
                for edgestartpt in plot_edgeptlist[plcnt]:
                    for perpypt in peripheral_pyptlist:
                        route_directness = calculate_route_directness(edgestartpt, perpypt, obstruction_occfacelist,G)
                        route_directness_list.append(route_directness)
                        print route_directness, plcnt, escnt
                        if route_directness > route_directness_threshold and escnt < nespt-1:
                            route_directness_list.remove(route_directness)
                            break
                        elif route_directness > route_directness_threshold and escnt == nespt-1:
                            route_directness_list.remove(route_directness)
                            fail_plots.append(plof_occface)
                            pass_plots.remove(plof_occface)
                            break
                    escnt += 1
        plcnt += 1

    print len(fail_plots), len(pass_plots), len(fail_plots) + len(pass_plots)

    #displaylist.extend(new_network_occedgelist)
    #displaylist.extend(total_pedgelist)
    displaylist.extend(edges4_networkx)
    #displaylist.extend(py3dmodel.construct.circles_frm_pyptlist(py3dmodel.construct.make_gppntlist(peripheral_ptlist), 300))
    #displaylist.extend(py3dmodel.construct.circles_frm_pyptlist(py3dmodel.construct.make_gppntlist(nnedge_pyptlist), 150))
    #displaylist.extend(py3dmodel.construct.circles_frm_pyptlist(py3dmodel.construct.make_gppntlist(peripheral_pyptlist), 150))
    return displaylist
    
def initialise_vol_indexes(building_occsolids, xdim, ydim, rad_folderpath, surface = "facade"):
    #initialise py2radiance 
    rad_base_filepath = os.path.join(os.path.dirname(__file__),'py2radiance','base.rad')
    rad = py2radiance.Rad(rad_base_filepath, rad_folderpath)
    srfmat = "RAL2012"
    
    sensor_ptlist = []
    sensor_dirlist = []
    topo_list = []
    bvol_dict = {}
    gsrf_index_cnt = 0
    bldg_cnt = 0
    for bsolid in building_occsolids:
        gsrf_cnt = 0
        #separate the solid into facade footprint and roof
        
        facades, roofs, footprints = gml3dmodel.identify_building_surfaces(bsolid)
        bsrflist = facades + roofs + footprints
        #measure the volume of the solid
        bvol = py3dmodel.calculate.solid_volume(bsolid)
        if surface == "roof":
            for roof in roofs:
                sensor_surfaces, sensor_pts, sensor_dirs = gml3dmodel.generate_sensor_surfaces(roof, xdim, ydim)
                gsrf_cnt += len(sensor_surfaces)
                sensor_ptlist.extend(sensor_pts)
                sensor_dirlist.extend(sensor_dirs)
                topo_list.extend(sensor_surfaces)
                
        if surface == "facade":
            for facade in facades:
                sensor_surfaces, sensor_pts, sensor_dirs = gml3dmodel.generate_sensor_surfaces(facade, xdim, ydim)
                gsrf_cnt += len(sensor_surfaces)
                sensor_ptlist.extend(sensor_pts)
                sensor_dirlist.extend(sensor_dirs)
                topo_list.extend(sensor_surfaces)
          
        bsrf_cnt = 0
        for bsrf in bsrflist:
            pypolygon = py3dmodel.fetch.pyptlist_frm_occface(bsrf)
            srfname = "srf" + str(bldg_cnt) + str(bsrf_cnt)
            py2radiance.RadSurface(srfname, pypolygon, srfmat, rad)
            bsrf_cnt+=1
            
        gsrf_range1 = gsrf_index_cnt
        gsrf_range2= gsrf_index_cnt + gsrf_cnt
        
        bvol_dict[bvol] = [gsrf_range1, gsrf_range2]
        gsrf_index_cnt +=  gsrf_cnt    
        bldg_cnt += 1 
    #get the sensor grid points
    rad.set_sensor_points(sensor_ptlist, sensor_dirlist)
    rad.create_sensor_input_file()
    #create the geometry files
    rad.create_rad_input_file()
    
    return rad, sensor_ptlist, sensor_dirlist, topo_list, bvol_dict
    
def shgfai(irrad_ress,irrad_threshold, topo_list):
    high_irrad = []
    high_irrad_faces = []
    
    irrad_cnt = 0
    for irrad_res in irrad_ress:
        if irrad_res> irrad_threshold:
            high_irrad.append(irrad_res)
            #measure the area of the grid 
            high_irrad_faces.append(topo_list[irrad_cnt])
        irrad_cnt +=1
        
    total_area = gml3dmodel.faces_surface_area(topo_list)
    high_irrad_area = gml3dmodel.faces_surface_area(high_irrad_faces)
    shgfai = (high_irrad_area/total_area) * 100
    return shgfai

def shgfavi(building_occsolids, irrad_threshold, epwweatherfile, xdim, ydim,
            rad_folderpath, mode = "facade", shgfavi_threshold = None):
    '''
    Algorithm to calculate Solar Heat Gain Facade Area to Volume Index
    
    Solar Heat Gain Facade Area to Volume Index (SHGFAVI) calculates the ratio of facade area that 
    receives irradiation above a specified level over the building volume.    
    
    Solar Gain Facade Area Index (SGFAI) calculates the ratio of facade area that 
    receives irradiation below a specified level over the net facade area. 
    SGFAI is represented as an area ratio.
        
    
    PARAMETERS
    ----------
    :param building_occsolids : a list of buildings occsolids
    :ptype: list(occsolid)
    
    :param irrad_threshold: a solar irradiance threshold value
    :ptype: float
    
    :param epwweatherfile: file path of the epw weatherfile
    :ptype: string
    
    :param xdim: x dimension grid size
    :ptype: float
    
    :param ydim: y dimension grid size
    :ptype: float
    
    :param shgfavi_threshold: a shgfavi threshold value
    :ptype: float
    
    RETURNS
    -------
    :returns shgfavi: average solar heat gain facade area volume index
    :rtype: float
    
    :returns shgfavi_percent: percentage of buildings achieving the shgfavi_threshold
    :rtype: float
    
    :returns grid_srfs_list: surfaces of the grid used for solar irradiation calculation, for visualisation purpose
    :rtype: list(occface)
    
    :returns irrad_ress: solar irradiation results from the simulation, for visualisation purpose
    :rtype: list(float)
    '''
    rad, sensor_ptlist, sensor_dirlist, topo_list, bvol_dict = initialise_vol_indexes(building_occsolids, xdim, ydim, 
                                                                                      rad_folderpath, surface = mode)   
    time = str(0) + " " + str(24)
    date = str(1) + " " + str(1) + " " + str(12) + " " + str(31)
    rad.execute_cumulative_oconv(time, date, epwweatherfile)
    #execute cumulative_rtrace
    rad.execute_cumulative_rtrace(str(2))#EXECUTE!! 
    #retrieve the results
    irrad_ress = rad.eval_cumulative_rad()
    
    shgfavi_list = []
    low_shgfavi_list = []
    for bvol in bvol_dict.keys():
        gsrf_range = bvol_dict[bvol]
        birradlist = irrad_ress[gsrf_range[0]:gsrf_range[1]]
        
        high_irrad = []
        high_irrad_faces = []
        
        bradcnt = 0
        for birrad in birradlist:
            if birrad > irrad_threshold:
                high_irrad.append(birrad)
                high_irrad_faces.append(topo_list[gsrf_range[0]+bradcnt])
            bradcnt+=1

        high_irrad_area = gml3dmodel.faces_surface_area(high_irrad_faces)
        shgfavi = high_irrad_area/bvol
        shgfavi_list.append(shgfavi)
        if shgfavi_threshold != None:
            if shgfavi < shgfavi_threshold:
                low_shgfavi_list.append(shgfavi)
        
    
    avg_shgfavi = sum(shgfavi_list)/float(len(shgfavi_list))
    if shgfavi_threshold != None:
        shgfavi_percent = float(len(low_shgfavi_list))/float(len(low_shgfavi_list))
    else:
        shgfavi_percent = None
        
    shgfai_value = shgfai(irrad_ress,irrad_threshold, topo_list)
    
    return avg_shgfavi, shgfavi_percent, shgfai_value, topo_list, irrad_ress
    
def dfai(illum_ress, sunuphrs, illum_threshold, topo_list):
    high_illum = []
    high_illum_faces = []
    mean_illum_ress = []
    illum_cnt = 0
    for illum_res in illum_ress:
        mean_illum = (illum_res/float(sunuphrs))
        mean_illum_ress.append(mean_illum)
        if mean_illum > illum_threshold:
            high_illum.append(mean_illum)
            #measure the area of the grid 
            high_illum_faces.append(topo_list[illum_cnt])
        illum_cnt +=1
        
    total_area = gml3dmodel.faces_surface_area(topo_list)
    high_illum_area = gml3dmodel.faces_surface_area(high_illum_faces)
    sgfai = (high_illum_area/total_area) * 100
    return sgfai
    
def dfavi(building_occsolids, illum_threshold, epwweatherfile, xdim, ydim,
            rad_folderpath,daysim_folderpath, dfavi_threshold = None):
    '''
    Algorithm to calculate Solar Heat Gain Facade Area to Volume Index
    
    Daylighting Facade Area to Volume Index (DFAVI) calculates the ratio of facade area that 
    receives daylighting above a specified level over the volume of the building. 
    
    Daylighting Facade Area Index (DFAI) calculates the ratio of facade area that 
    receives daylighting above a specified level over the total facade area. 
    
    PARAMETERS
    ----------
    :param building_occsolids : a list of buildings occsolids
    :ptype: list(occsolid)
    
    :param illum_threshold: a solar illuminance threshold value
    :ptype: float
    
    :param epwweatherfile: file path of the epw weatherfile
    :ptype: string
    
    :param xdim: x dimension grid size
    :ptype: float
    
    :param ydim: y dimension grid size
    :ptype: float
    
    :param dfavi_threshold: a shgfavi threshold value
    :ptype: float
    
    RETURNS
    -------
    :returns dfavi: average dfavi facade area volume index
    :rtype: float
    
    :returns dfavi_percent: percentage of buildings achieving the dfavi_threshold
    :rtype: float
    
    :returns grid_srfs_list: surfaces of the grid used for solar irradiation calculation, for visualisation purpose
    :rtype: list(occface)
    
    :returns illum_ress: solar irradiation results from the simulation, for visualisation purpose
    :rtype: list(float)
    '''
    
    rad, sensor_ptlist, sensor_dirlist, topo_list, bvol_dict = initialise_vol_indexes(building_occsolids, xdim, ydim, rad_folderpath)   
    time = str(0) + " " + str(24)
    date = str(1) + " " + str(1) + " " + str(12) + " " + str(31)
    rad.execute_cumulative_oconv(time, date, epwweatherfile, output = "illuminance")
    #execute cumulative_rtrace
    rad.execute_cumulative_rtrace(str(2))#EXECUTE!! 
    #retrieve the results
    illum_ress = rad.eval_cumulative_rad(output = "illuminance")
    
    rad.initialise_daysim(daysim_folderpath)
    #a 60min weatherfile is generated
    rad.execute_epw2wea(epwweatherfile)
    sunuphrs = rad.sunuphrs
    
    dfavi_list = []
    high_dfavi_list = []
    for bvol in bvol_dict.keys():
        gsrf_range = bvol_dict[bvol]
        billumlist = illum_ress[gsrf_range[0]:gsrf_range[1]]
        
        high_illum = []
        high_illum_faces = []
        
        bradcnt = 0
        for billum in billumlist:
            mean_billum = (billum/float(sunuphrs))
            if mean_billum > illum_threshold:
                high_illum.append(mean_billum)
                high_illum_faces.append(topo_list[gsrf_range[0]+bradcnt])
            bradcnt+=1

        high_illum_area = gml3dmodel.faces_surface_area(high_illum_faces)
        dfavi = high_illum_area/bvol
        dfavi_list.append(dfavi)
        if dfavi_threshold != None:
            if dfavi > dfavi_threshold:
                high_dfavi_list.append(dfavi)
        
    
    avg_dfavi = sum(dfavi_list)/float(len(dfavi_list))
    if dfavi_threshold != None:
        dfavi_percent = float(len(high_dfavi_list))/float(len(high_dfavi_list))
    else:
        dfavi_percent = None
        
    dfai_value = dfai(illum_ress, sunuphrs, illum_threshold, topo_list)
    return avg_dfavi, dfavi_percent, dfai_value, topo_list, illum_ress
    
def pvavi(building_occsolids, irrad_threshold, epwweatherfile, xdim, ydim,
            rad_folderpath, mode = "roof", pvavi_threshold = None):
                
    """
    PV Area to Volume  Index (PVAVI) calculates the ratio of roof/facade area that 
    receives irradiation above a specified level over the building volume. 
    
    Roof PV Potential (RPVP) calculates the potential electricity 
    that can be generated on the roof of buildings annually.
    RPVP is represented in kWh/yr.
    
    PV Roof Area Index (PVAI) calculates the ratio of roof area that 
    receives irradiation above a specified level over the net envelope/roof/facade area. 
    PVRAI is represented as an area ratio.
        
        
    PARAMETERS
    ----------
    :param building_occsolids : a list of buildings occsolids
    :ptype: list(occsolid)
    
    :param illum_threshold: a solar illuminance threshold value
    :ptype: float
    
    :param epwweatherfile: file path of the epw weatherfile
    :ptype: string
    
    :param xdim: x dimension grid size
    :ptype: float
    
    :param ydim: y dimension grid size
    :ptype: float
    
    :param dfavi_threshold: a shgfavi threshold value
    :ptype: float
    
    RETURNS
    -------
    :returns dfavi: average dfavi facade area volume index
    :rtype: float
    
    :returns dfavi_percent: percentage of buildings achieving the dfavi_threshold
    :rtype: float
    
    :returns grid_srfs_list: surfaces of the grid used for solar irradiation calculation, for visualisation purpose
    :rtype: list(occface)
    
    :returns illum_ress: solar irradiation results from the simulation, for visualisation purpose
    :rtype: list(float)
    '''
    """    
    
    avg_pvavi, pvavi_percent, pvai_value, topo_list, irrad_ress = shgfavi(building_occsolids, irrad_threshold, 
                                                                                epwweatherfile, xdim, ydim, rad_folderpath, 
                                                                                mode = mode, 
                                                                                shgfavi_threshold = pvavi_threshold)
    '''
    eqn to calculate the energy produce by pv
    epv = apv*fpv*gt*nmod*ninv
    epv is energy produced by pv (kwh/yr)
    apv is area of pv (m2)
    fpv is faction of surface with active solar cells (ratio)
    gt is total annual solar radiation energy incident on pv (kwh/m2/yr)
    nmod is the pv efficiency (12%)
    ninv is the avg inverter efficiency (90%)
    '''
    apv = gml3dmodel.faces_surface_area(topo_list)
    fpv = 0.8
    gt = (sum(irrad_ress))/(float(len(irrad_ress)))
    nmod = 0.12
    ninv = 0.9
    epv = apv*fpv*gt*nmod*ninv
    
    return avg_pvavi, pvavi_percent, pvai_value, epv, topo_list, irrad_ress