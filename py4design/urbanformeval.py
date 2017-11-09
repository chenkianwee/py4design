# ==================================================================================================
#
#    Copyright (c) 2016, Chen Kian Wee (chenkianwee@gmail.com)
#
#    This file is part of py4design
#
#    py4design is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    py4design is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with py4design.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================
import os
import math
import networkx as nx
import py3dmodel
import urbangeom
import py2radiance
    
#================================================================================================================
#FRONTAL AREA INDEX
#================================================================================================================
def frontal_area_index(building_occsolids, boundary_occface, wind_dir, xdim = 100, ydim = 100):
    """
    This function calculates the frontal area index of an urban massing.
    
    Parameters
    ----------
    building_occsolids : a list of OCCsolids
        The buildings to be analysed.
    
    boundary_occface : OCCface 
        The boundary of the FAI analysis. This face will be gridded.
    
    wind_dir : pyvec
        Pyvec is a tuple of floats that documents the xyz vector of a dir e.g. (x,y,z)
    
    xdim : float
        X-dimension of the grid for the boundary occface, in metres (m)
    
    ydim : float
        Y-dimension of the grid for the boundary occface, in metres (m)
    
    Returns
    -------
    result dictionary : dictionary
        A dictionary with this keys : {"average", "grids", "fai_list", "projected_surface_list" , "wind_plane_list", "vertical_surface_list" }
        
        average : float
            Average frontal area index of the whole design.
        
        grids : list of OCCfaces
            The grid used for the frontal area index.
        
        fai_list : list of floats
            List of all the FAI of each grid.   
        
        projected_surface_list : list of OCCfaces
            The projected surfaces merged together.
        
        wind_plane_list : list of OCCfaces
            The plane representing the direction of the wind
        
        vertical_surface_list : list of OCCfaces
            The facade surfaces that are projected.
    
    """
    fai_list = []
    fs_list = []
    wp_list = []
    os_list = []
    gridded_boundary = py3dmodel.construct.grid_face(boundary_occface, xdim, ydim)
    bldg_dict_list = []
    bldg_fp = []
    for building_occsolid in building_occsolids:
        bldg_dict = {}
        footprints = urbangeom.get_bldg_footprint_frm_bldg_occsolid(building_occsolid)
        
        if not footprints:
            face_list = py3dmodel.fetch.topo_explorer(building_occsolid, "face")
            xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(building_occsolid)
            bounding_footprint = py3dmodel.construct.make_polygon([(xmin,ymin,zmin),(xmin,ymax,zmin),(xmax, ymax, zmin),(xmax, ymin, zmin)])
            bldg_footprint_list = []
            for face in face_list:
                normal = py3dmodel.calculate.face_normal(face)
                if normal == (0,0,-1):
                    if py3dmodel.calculate.face_is_inside(face,bounding_footprint):
                        bldg_footprint_list.append(face)
                
                
            nrml_edges = py3dmodel.calculate.visualise_face_normal_as_edges(face_list, normal_magnitude = 10)
            py3dmodel.construct.visualise([[building_occsolid], nrml_edges],["WHITE", "BLACK"])
            
        bldg_fp.extend(footprints)
        bldg_dict["footprint"] = footprints
        bldg_dict["solid"] = building_occsolid
        bldg_dict_list.append(bldg_dict)
    gcnt = 0
    
    for grid in gridded_boundary:
        grid_midpt = py3dmodel.calculate.face_midpt(grid)
        dest_pt = py3dmodel.modify.move_pt(grid_midpt, (0,0,-1), 10)
        m_grid = py3dmodel.modify.move(grid_midpt,dest_pt, grid)
        m_grid = py3dmodel.fetch.topo2topotype(m_grid)
        grid_extrude = py3dmodel.construct.extrude(m_grid, (0,0,1), 1000)
        bldg_list = []
        for bldg_dict in bldg_dict_list:
            footprints = bldg_dict["footprint"]
            fp_cmpd = py3dmodel.construct.make_compound(footprints)
            fp_common_shape = py3dmodel.construct.boolean_common(grid_extrude,fp_cmpd)
            is_cmpd_null = py3dmodel.fetch.is_compound_null(fp_common_shape)
                
            if not is_cmpd_null:
                bsolid = bldg_dict["solid"]
                bldg_list.append(bsolid)
                
        
        if bldg_list:
            #close_compound = py3dmodel.construct.make_compound(bldg_list)
            agrid_facade_list = []
            for bldg in bldg_list:
                common_shape = py3dmodel.construct.boolean_common(grid_extrude,bldg)
                compound_faces = py3dmodel.fetch.topo_explorer(common_shape, "face")
                facade_list, roof_list, ftprint_list = urbangeom.identify_srfs_according_2_angle(compound_faces)
                agrid_facade_list.extend(facade_list)
            if agrid_facade_list:
                fai,fuse_srfs,wind_plane,origsrf_prj= frontal_area_index_aplot(agrid_facade_list, grid, wind_dir)
                fai_list.append(fai)
                fs_list.extend(fuse_srfs)
                wp_list.append(wind_plane)
                os_list.extend(origsrf_prj)
            else:
                fai_list.append(0)
        else:
            fai_list.append(0)
            
        gcnt+=1
        
    avg_fai = float(sum(fai_list))/float(len(fai_list))
    res_dict = {}
    res_dict["average"] = avg_fai
    res_dict["grids"] = gridded_boundary
    res_dict["fai_list"] = fai_list
    res_dict["projected_surface_list"] = fs_list
    res_dict["wind_plane_list"] = wp_list
    res_dict["vertical_surface_list"] = os_list
    
    return res_dict
    
def frontal_area_index_aplot(facade_occfaces, plane_occface, wind_dir):
    """
    This function calculates the frontal area index for a single grid.
    
    Parameters
    ----------
    facade_occfaces : list of OCCfaces 
        List of occfaces of vertical facades 
    
    plane_occface : OCCface
        An occface that is the horizontal plane buildings are sitting on, the single grid.
    
    wind_dir : pyvec
        Pyvec is a tuple of floats that documents the xyz vector of a dir e.g. (x,y,z).
    
    Returns
    -------
    fai : float
        Frontal area index. 
    
    fuse_srfs : list of OCCfaces
        The projected surfaces fused together
    
    wind_plane : OCCface
        The plane representing the direction of the wind
    
    surfaces_projected : list of OCCfaces
        the facade surfaces that are projected
    
    """
    facade_faces_compound = py3dmodel.construct.make_compound(facade_occfaces)
     
    #create win dir plane
    #get the bounding box of the compound, so that the wind plane will be placed at the edge of the bounding box
    xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(facade_faces_compound)
    pymidpt = py3dmodel.calculate.get_centre_bbox(facade_faces_compound)
    #calculate the furthest distance of the bounding box
    pycornerpt = (xmin, ymin, 0)
    
    furtherest_dist = py3dmodel.calculate.distance_between_2_pts(pymidpt, pycornerpt)
    #create the wind plane 
    pt4plane = py3dmodel.modify.move_pt(pymidpt, wind_dir, furtherest_dist) 
    wind_plane = py3dmodel.construct.make_plane_w_dir(pt4plane, wind_dir)
    
    surfaces_projected = []
    projected_facet_faces = []
    for facade_face in facade_occfaces:
        surfaces_projected.append(facade_face)
        projected_pts = py3dmodel.calculate.project_face_on_faceplane(wind_plane, facade_face)
        projected_srf = py3dmodel.construct.make_polygon(projected_pts)
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
                
        fuse_compound = py3dmodel.fetch.topo2topotype(fuse_shape) 
        fuse_srfs = py3dmodel.fetch.topo_explorer(fuse_compound,"face")
    
    #calculate the frontal area index
    facet_area = urbangeom.faces_surface_area(fuse_srfs)
    plane_area = py3dmodel.calculate.face_area(plane_occface)
    fai = facet_area/plane_area
    
    return fai, fuse_srfs, wind_plane, surfaces_projected
   
#================================================================================================================
#ROUTE DIRECTNESS INDEX
#================================================================================================================
def route_directness(network_occedgelist, plot_occfacelist, boundary_occface, obstruction_occfacelist = [], rdi_threshold = 0.6):
    """
    This function measures the connectivity of street network in a neighbourhood by measuring route 
    directness for each parcel to a series of points around the periphery of the study area. It
    identifies the percentage of good plots that exceed a rdi of 0.8 (urban area) and 0.6 (suburban). 
    Algorithm for Route Directness Test, Stangl, P.. 2012 the pedestrian route directness test: A new level of service model.
    urban design international 17, 228-238.
    
    Parameters
    ----------
    network_occedgelist : list of OCCedges
        The network to be analysed with nodes and edges.
    
    plot_occfacelist : list of OCCfaces
        The land use plots to be analysed.
    
    boundary_occface : OCCface
        The boundary of the analysed area.
    
    obstruction_occface_list : list of OCCfaces, optional
        The obstructions represented as OCCfaces for the analysis, default value = [].
        
    rdi_threshold : float, optional
        A threshold Route Directness Index, default value = 0.6.
    
    Returns
    -------
    result dictionary : dictionary
        A dictionary with this keys : {"average", "percent", "plots", "pass_plots" , 
        "fail_plots", "rdi_list", "network_edges", "peripheral_points" }
        
        average : float
            Average rdi of the whole design.
        
        percent : float
            The percentage of the plots that has RDI higher than the threshold.
        
        plots : list of OCCfaces
            The plots that are analysed.   
        
        pass_plots : list of OCCfaces
            The plots that has RDI higher than the threshold.
        
        fail_plots : list of OCCfaces
            The plots that has RDI lower than the threshold.
            
        rdi_list : list of floats
            The RDI of each plot, corresponds to the list of plots.
            
        network_edges : list of OCCedges
            The network that was analysed.
            
        peripheral_points : list of OCCedges
            The peripheral points visualised as OCCedges circles.    
    """
    ndecimal = 3
    precision = 1e-02
    #======================================================================
    #designate peripheral points
    #======================================================================
    peripheral_ptlist, pedgelist, interptlist = designate_peripheral_pts(boundary_occface, network_occedgelist, precision)
    print "NPLOTS", len(plot_occfacelist)
    #======================================================================
    #connect the street network: connect midpt of each plot to the street network
    #======================================================================
    inter_peri_ptlist = peripheral_ptlist + interptlist    
    
    new_network_occedgelist, midpt2_network_edgelist, plot_midptlist = connect_street_network2plot(network_occedgelist, plot_occfacelist, inter_peri_ptlist, precision)
    
    #======================================================================
    #construct the networkx network
    #======================================================================
    #create a graph
    G = nx.Graph()
    #add all the edges for the boundary
    edges4_networkx = new_network_occedgelist + pedgelist + midpt2_network_edgelist
    fused_ntpts = []
    for ne in edges4_networkx:
        edge_nodes = py3dmodel.fetch.points_frm_edge(ne)
        edge_nodes = py3dmodel.modify.round_pyptlist(edge_nodes, ndecimal)
        if len(edge_nodes) == 2:
            xdmin,xdmax = py3dmodel.fetch.edge_domain(ne)
            length = py3dmodel.calculate.edgelength(xdmin,xdmax,ne)
            node1 = edge_nodes[0]
            node2 = edge_nodes[1]
            G.add_edge(node1,node2, distance = length)
            if node1 not in fused_ntpts:
                fused_ntpts.append(node1)
            if node2 not in fused_ntpts:
                fused_ntpts.append(node2)
            
    #======================================================================
    #measure route directness
    #======================================================================
    #loop thru all the midpts of the plot
    pass_plots = plot_occfacelist[:]
    fail_plots = []
    display_plots = []
    total_route_directness_aplot = []
    
    plcnt = 0
    for midpt in plot_midptlist:
        midpt = py3dmodel.modify.round_pypt(midpt,ndecimal)
        #check if the plot is a dead plot with no free edges
        plof_occface = plot_occfacelist[plcnt]
        if midpt not in fused_ntpts:
            print "DEAD END PLOT"
            fail_plots.append(plof_occface)
            pass_plots.remove(plof_occface)
        else:        
            #measure the direct distance crow flies distance
            plot_area = py3dmodel.calculate.face_area(plof_occface) 
            display_plots.append(plof_occface)
            aplot_avg_rdi_list = []
            for perpypt in peripheral_ptlist:
                perpypt = py3dmodel.modify.round_pypt(perpypt,ndecimal)
                route_directness = calculate_route_directness(midpt, perpypt, obstruction_occfacelist,G, plot_area = plot_area)
                if route_directness < rdi_threshold:
                    fail_plots.append(plof_occface)
                    pass_plots.remove(plof_occface)
                    break
                
            for perpypt in peripheral_ptlist:
                perpypt = py3dmodel.modify.round_pypt(perpypt,ndecimal)
                route_directness = calculate_route_directness(midpt, perpypt, obstruction_occfacelist,G)
                aplot_avg_rdi_list.append(route_directness)
                
            max_rdi_aplot = min(aplot_avg_rdi_list)
            total_route_directness_aplot.append(max_rdi_aplot)
        plcnt += 1

    avg_rdi = float(sum(total_route_directness_aplot))/float(len(total_route_directness_aplot))
    rdi_percentage = float(len(pass_plots))/float((len(fail_plots) + len(pass_plots))) * 100
    circles_peri_pts = py3dmodel.construct.circles_frm_pyptlist(peripheral_ptlist, 5)    
    
    #circles_inter_pts = py3dmodel.construct.circles_frm_pyptlist(py3dmodel.construct.make_gppntlist(midptlist), 5)  
    res_dict = {}
    res_dict["average"] = avg_rdi
    res_dict["percent"] = rdi_percentage
    res_dict["plots"] = display_plots
    res_dict["pass_plots"] = pass_plots
    res_dict["fail_plots"] = fail_plots
    res_dict["rdi_list"] = total_route_directness_aplot
    res_dict["network_edges"] = edges4_networkx
    res_dict["peripheral_points"] = circles_peri_pts
    return res_dict

def calculate_route_directness(startpypt, peripheralpypt, obstruction_occfacelist,G, plot_area = None):
    """
    This function measures the route directness index of a plot.
    
    Parameters
    ----------
    startpypt : pypt
        The mid point of the plot. Pypt is a tuple of floats. A pypt is a tuple that documents 
        the xyz coordinates of a pt e.g. (x,y,z).
    
    peripheralpypt : pypt
        The end point. Pypt is a tuple of floats. A pypt is a tuple that documents 
        the xyz coordinates of a pt e.g. (x,y,z).
    
    obstruction_occface_list : list of OCCfaces
        The obstructions represented as OCCfaces for the analysis.
        
    G : Networkx Graph class instance
        The networkx graph used for calculating the route distance of the shortest path between
        the mid point and ending point.
    
    plot_area : float, optional
        The area of the plot. If the area is less than 2023m2 (1/2 acre), the function will not
        consider the distane from the midpoint to the edge of the plot.
        
    Returns
    -------
    rdi : float
        The route directness index of the plot and this peripheral point. 
        rdi = direct distance/ route distance.
        
    """
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
    shortest_path = nx.shortest_path(G,source=startpypt,target=peripheralpypt, weight = "distance")
    nshortpath = len(shortest_path)
    route_distance = 0
    
    for scnt in range(nshortpath):
        if scnt != nshortpath-1:
            network_edge = G[shortest_path[scnt]][shortest_path[scnt+1]]
            route_distance = route_distance + network_edge["distance"]
            
    if plot_area != None:
        if plot_area <= 2023:#1/2 acre
            #the route distance is from the frontage edge not from the midpt
            #so we will minus of the distance from the midpt to the frontage
            midpt_2_edge = G[shortest_path[0]][shortest_path[1]]
            m2e_dist = midpt_2_edge["distance"]
            route_distance = route_distance - m2e_dist
            
    route_directness = direct_distance/route_distance
    return route_directness

def designate_peripheral_pts(boundary_occface, network_occedgelist, precision):
    """
    This function calculates the peripheral points around the boundary.
    
    Parameters
    ----------
    boundary_occface : OCCface
        The boundary of the analysed area.
        
    network_occedgelist : list of OCCedges
        The network to be analysed with nodes and edges.
    
    precision : float
        The tolerance to be used for intersection calculations.
    
    Returns
    -------
    peripheral_ptlist : pyptlist
        The peripheral points. List of tuples of floats. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...].
    
    pedgelist : list of OCCedges
        The edges of the boundary.
    
    interptlist : pyptlist
        The intersections of the internal network and the boundary edges.
        List of tuples of floats. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...].
        
    """
    peripheral_ptlist = []
    peripheral_parmlist = []
    peripheral_parmlist4network = []
    boundary_pyptlist = py3dmodel.fetch.points_frm_occface(boundary_occface)
    boundary_pyptlist.append(boundary_pyptlist[0])
    #extract the wire from the face and convert it to a bspline curve
    bedge = py3dmodel.construct.make_bspline_edge(boundary_pyptlist, mindegree=1, maxdegree=1)
    
    #get all the intersection points 
    interptlist = []
    for network_occedge in network_occedgelist:
        intersect_pts = py3dmodel.calculate.intersect_edge_with_edge(bedge, network_occedge, tolerance=precision)
        if intersect_pts!=None:
            interptlist.extend(intersect_pts)
            
    #remove all duplicate points    
    fused_interptlist = py3dmodel.modify.rmv_duplicated_pts_by_distance(interptlist, distance = precision)
    
    #translate all the points to parameter
    ulist = []
    for fused_interpt in fused_interptlist:
        parmu = py3dmodel.calculate.pt2edgeparameter(fused_interpt,bedge)
        ulist.append(parmu)
    
    ulist = sorted(ulist)
    nulist = len(ulist)
    #place a marker at the midpt between these intersection
    midptlist = []
    mulist = []
    bedge_lbound, bedge_ubound = py3dmodel.fetch.edge_domain(bedge)
    
    for ucnt in range(nulist):
        curparm = ulist[ucnt]
        
        if ucnt == nulist-1:
            if curparm == bedge_ubound and ulist[0] != bedge_lbound:
                terange = ulist[0]-bedge_lbound
                temidparm = terange/2
                
            elif curparm !=bedge_ubound and ulist[0] != bedge_lbound:
                terange1 = bedge_ubound-curparm
                terange2 =  ulist[0]-bedge_lbound
                terange3 = terange1+terange2
                temidparm = curparm + (terange3/2)
                if temidparm > bedge_ubound:
                    temidparm = temidparm-bedge_ubound
                
            elif curparm !=bedge_ubound and ulist[0] == bedge_lbound:
                terange = bedge_ubound-curparm
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
            if mcurparm == bedge_ubound and umulist[0] != bedge_lbound:
                mcurparm = bedge_lbound
                mnextparm = umulist[0]
                mrange = mnextparm - mcurparm
                mlength = py3dmodel.calculate.edgelength(mcurparm,mnextparm, bedge)
                
            elif mcurparm !=bedge_ubound and umulist[0] != bedge_lbound:
                mlength1 = py3dmodel.calculate.edgelength(mcurparm, bedge_ubound, bedge)
                mlength2 = py3dmodel.calculate.edgelength(bedge_lbound, umulist[0], bedge)
                mrange1 = bedge_ubound-mcurparm
                mrange2 = umulist[0]- bedge_lbound
                mrange = mrange1+mrange2
                mlength = mlength1+mlength2
                
            elif mcurparm !=bedge_ubound and umulist[0] == bedge_lbound:
                mnextparm = bedge_ubound
                mrange = mnextparm - mcurparm
                mlength = py3dmodel.calculate.edgelength(mcurparm, bedge_ubound, bedge)
        else:
            mnextparm = umulist[mcnt+1]
            mrange = mnextparm - mcurparm
            mlength = py3dmodel.calculate.edgelength(mcurparm,mnextparm, bedge)
            
        if mlength > 106:
            #divide the segment into 106m segments
            nsegments = math.ceil((mlength)/106.0)
            segment = mrange/nsegments
            for scnt in range(int(nsegments)-1):
                divparm = mcurparm + ((scnt+1)*segment)
                if divparm > bedge_ubound:
                    divparm = divparm - bedge_ubound
                
                peripheral_parmlist.append(divparm)
            
    peripheral_parmlist4network = peripheral_parmlist + umulist
    peripheral_parmlist4network.sort()
    #reconstruct the boundary into curve segments 
    pcurvelist = []
    #py3dmodel.utility.visualise([pcurvelist],["BLACK"])
    nplist = len(peripheral_parmlist4network)
    for pcnt in range(nplist):
        pcurparm = peripheral_parmlist4network[pcnt]
        if pcnt == nplist-1:
            if pcurparm == bedge_ubound and peripheral_parmlist4network[0] != bedge_lbound:
                pcurparm = bedge_lbound
                pnextparm = peripheral_parmlist4network[0]
                pcurve = py3dmodel.modify.trimedge(pcurparm, pnextparm, bedge)
                pcurvelist.append(pcurve)
                
            elif pcurparm !=bedge_ubound and peripheral_parmlist4network[0] != bedge_lbound:
                pcurve1 = py3dmodel.modify.trimedge(pcurparm, bedge_ubound, bedge)
                pcurve2 = py3dmodel.modify.trimedge(0, peripheral_parmlist4network[0], bedge)
                pcurvelist.append(pcurve1)
                pcurvelist.append(pcurve2)
            
            elif pcurparm !=bedge_ubound and peripheral_parmlist4network[0] == bedge_lbound:
                pcurve1 = py3dmodel.modify.trimedge(pcurparm, bedge_ubound, bedge)
                pcurvelist.append(pcurve1)
        else:
            pnextparm = peripheral_parmlist4network[pcnt+1]
            pcurve = py3dmodel.modify.trimedge(pcurparm, pnextparm, bedge)
            pcurvelist.append(pcurve)
            
    #===========================================================================
    peripheral_parmlist.extend(mulist)
    peripheral_parmlist.sort()
    for pparm in peripheral_parmlist:
        peripheral_pt = py3dmodel.calculate.edgeparameter2pt(pparm, bedge)
        peripheral_ptlist.append(peripheral_pt)
        
    pedgelist = []
    ppoles_all = []
    
    for pc in pcurvelist:
        ppoles = py3dmodel.fetch.poles_from_bsplinecurve_edge(pc)
        ppoles_all.append(ppoles)
        pwire = py3dmodel.construct.make_wire(ppoles)
        pedges = py3dmodel.fetch.edges_frm_wire(pwire)
        pedgelist.extend(pedges)
        
    #ppts = py3dmodel.construct.circles_frm_pyptlist(peripheral_ptlist, 10)
    #py3dmodel.utility.visualise([pedgelist, ppts], ["BLACK", "BLACK"])
    return peripheral_ptlist, pedgelist, fused_interptlist
    
def connect_street_network2plot(network_occedgelist, plot_occfacelist, peripheral_n_inter_ptlist, precision):
    """
    This function connects the network edges to the mid point of each plot.
    
    Parameters
    ----------
    network_occedgelist : list of OCCedges
        The network to be analysed with nodes and edges.
        
    plot_occfacelist : list of OCCfaces
        The land use plots to be analysed.
        
    peripheral_n_inter_ptlist : pyptlist
        The peripheral points and the intersections of the internal network and the boundary edges. 
        List of tuples of floats. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...].
    
    precision : float
        The tolerance to be used for intersection calculations.
    
    Returns
    -------
    new_network_occedgelist : list of OCCedges
        The new network that has been connected to the plots.
    
    midpt2_network_edgelist : list of OCCedges
        The edges that connect the mid point of each plot to the new_network_occedgelist.
        
    plot_midptlist : pyptlist
        The mid points of all the plots.
        List of tuples of floats. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...].
        
    """
    plot_midptlist = []
    network_ptlist = []
    midpt2_network_edgelist = []
    network_compound = construct_network_compound(network_occedgelist, 10)
    #get the mid point of the plot
    for plot_occface in plot_occfacelist:
        pymidpt = py3dmodel.calculate.face_midpt(plot_occface)
        plot_midptlist.append(pymidpt)
        #extrude the plot into a solid
        pextrude = py3dmodel.fetch.topo2topotype(py3dmodel.construct.extrude(plot_occface,(0,0,1), 10))
        pface_list = py3dmodel.fetch.topo_explorer(pextrude, "face")
        for pface in pface_list:
            xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(pface)
            pface_nrml = py3dmodel.calculate.face_normal(pface)
            pface_midpt = py3dmodel.calculate.face_midpt(pface)
            pedge_midpypt = (pface_midpt[0],pface_midpt[1],zmin + 1e-06)
            inter_pypt, inter_face = py3dmodel.calculate.intersect_shape_with_ptdir(network_compound, pedge_midpypt, pface_nrml)
            
            if inter_pypt != None:
                #it means this is an open boundary edge
                network_ptlist.append(inter_pypt)
                midpt2pedge = py3dmodel.construct.make_edge(pymidpt, pedge_midpypt)
                pedge2network = py3dmodel.construct.make_edge(pedge_midpypt, inter_pypt)
                midpt2_network_edgelist.append(midpt2pedge)
                midpt2_network_edgelist.append(pedge2network)
                #make sure the plot edge is a free edge
                #if it cuts any of the plots it means it is not a free edge
                for plot_occface2 in plot_occfacelist:
                    dmin,dmax = py3dmodel.fetch.edge_domain(pedge2network)
                    drange = dmax-dmin
                    dquantum = 0.1*drange
                    pypt1 = py3dmodel.calculate.edgeparameter2pt(dmin+dquantum, pedge2network)
                    pypt2 = py3dmodel.calculate.edgeparameter2pt(dmax, pedge2network)
                    pedge2network2 = py3dmodel.construct.make_edge(pypt1, pypt2)
                    #pextrude2 = py3dmodel.construct.extrude(plot_occface2,(0,0,1), 10)
                    is_intersecting = py3dmodel.construct.boolean_common(plot_occface2,pedge2network2)
                    if not py3dmodel.fetch.is_compound_null(is_intersecting):
                        #it is not a free edge
                        midpt2_network_edgelist.remove(midpt2pedge)
                        midpt2_network_edgelist.remove(pedge2network)
                        network_ptlist.remove(inter_pypt)
                        break
    
    
    #reconstruct the network edges with the new network_ptlist
    new_network_occedgelist = network_occedgelist[:]
    network_ptlist = network_ptlist + peripheral_n_inter_ptlist
    for networkpt in network_ptlist:
        network_vert = py3dmodel.construct.make_vertex(networkpt)
        for nedge in new_network_occedgelist:
            #find the edge the point belongs to 
            nnedgepts = len(py3dmodel.fetch.points_frm_edge(nedge))
            if nnedgepts == 2:
                env_mindist = py3dmodel.calculate.minimum_distance(network_vert,nedge)     
                if env_mindist <= precision:
                    #that means the point belongs to this edge
                    #remove the original edge
                    new_network_occedgelist.remove(nedge)
                    #find the parameter then reconstruct the edge accordingly
                    dmin, dmax = py3dmodel.fetch.edge_domain(nedge)
                    domain_list = [dmin, dmax]
                    inter_parm = py3dmodel.calculate.pt2edgeparameter(networkpt, nedge)
                    domain_list.append(round(inter_parm, 5))
                    #make domain_list unique
                    domain_list = list(set(domain_list))
                    domain_list.sort()
                    #reconstruct the edge 
                    if len(domain_list) == 2:
                        pypt1 = py3dmodel.calculate.edgeparameter2pt(domain_list[0], nedge)
                        pypt2 = py3dmodel.calculate.edgeparameter2pt(domain_list[1], nedge)
                        n_nedge1 = py3dmodel.construct.make_edge(pypt1, pypt2)
                        new_network_occedgelist.append(n_nedge1)
                    if len(domain_list) == 3:
                        pypt1 = py3dmodel.calculate.edgeparameter2pt(domain_list[0], nedge)
                        pypt2 = py3dmodel.calculate.edgeparameter2pt(domain_list[1], nedge)
                        pypt3 = py3dmodel.calculate.edgeparameter2pt(domain_list[2], nedge)
                        if pypt1 != pypt2:
                            n_nedge1 = py3dmodel.construct.make_edge(pypt1, pypt2)
                            new_network_occedgelist.append(n_nedge1)
                        if pypt2 != pypt3:
                            n_nedge2 = py3dmodel.construct.make_edge(pypt2, pypt3)
                            new_network_occedgelist.append(n_nedge2)
                    break
  
    return new_network_occedgelist, midpt2_network_edgelist, plot_midptlist
    
    
def route_ard_obstruction(obstruction_face, crow_wire):    
    """
    This function calculates the direct distance when met with an obstruction.
    
    Parameters
    ----------
    obstruction_face : OCCface
        The obstructions represented as OCCface for the analysis.
        
    crow_wire : OCCwire
        The direct way from start to peripheral point not taking into account of the obstruction.
    
    Returns
    -------
    new crow wire : OCCwire
        The direct way from start to peripheral point taking into account of the obstruction.
        The wire will go around the obstruction OCCface.
        
    """    
    res = py3dmodel.fetch.topo2topotype(py3dmodel.construct.boolean_common(obstruction_face,crow_wire))
    res2 =py3dmodel.fetch.topo2topotype(py3dmodel.construct.boolean_difference(crow_wire,obstruction_face))
    edgelist = py3dmodel.fetch.topo_explorer(res, "edge")
    edgelist2 = py3dmodel.fetch.topo_explorer(res2, "edge")
    
    wire = py3dmodel.fetch.wires_frm_face(obstruction_face)[0]
    #turn the wire into a degree1 bspline curve edge
    pyptlist = py3dmodel.modify.occpt_list_2_pyptlist(py3dmodel.fetch.points_frm_wire(wire))
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
            pts = py3dmodel.fetch.points_from_edge(sorted_edge)
            
        new_pyptlist.extend(pts)
        
    new_bwire = py3dmodel.construct.make_wire(new_pyptlist)
    return new_bwire
    
def generate_directions(rot_degree):
    """
    This function generates a list of direction according to the interval of rotation degree.
    
    Parameters
    ----------
    rot_degree : float
        The interval rotation degree.
    
    Returns
    -------
    list of directions : pydirlist
        The generated directions. List of tuples of floats. 
        A pydir is a tuple that documents the xyz vector of a dir e.g. (x,y,z), 
        thus a pydirlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...].
        
    """  
    #generate the direction from the midpt to the plot edges 
    orig_vert = py3dmodel.construct.make_vertex((0,1,0))
    pydirlist = []
    for dircnt in range(int(360/rot_degree)):
        degree = rot_degree*dircnt
        rot_vert = py3dmodel.modify.rotate(orig_vert, (0,0,0), (0,0,1), degree)
        gppt = py3dmodel.modify.occvertex_2_occpt(rot_vert)
        pypt = py3dmodel.modify.occpt_2_pypt(gppt)
        pydirlist.append(pypt)
        
    return pydirlist
    
def construct_network_compound(network_occedgelist, extrusion_height):
    """
    This function extrudes the network edges and consolidate it into an OCCcompound.
    
    Parameters
    ----------
    network_occedgelist : list of OCCedges
        The network to be analysed with nodes and edges.
    
    extrusion_height : float
        The extrusion height.
    
    Returns
    -------
    extruded network compound : OCCcompound
        The extruded network compound.
        
    """
    nfacelist = []
    for nedge in network_occedgelist:
        #move the edge upwards then loft it to make a face
        nface = py3dmodel.construct.extrude_edge(nedge, (0,0,1), 10)
        nfacelist.append(nface)

    network_compound = py3dmodel.construct.make_compound(nfacelist)
    return network_compound
    
def draw_street_graph(networkx_graph, node_index):
    """
    This function draws the networkx graph and visualise it.
    
    PARAMETERS
    ----------
    networkx_graph : networkx graph class instance
        The networkx graph to be visualised.
    
    node_index : list of floats
        The index of the nodes in the networkx graph.
        
    """
    import matplotlib.pyplot as plt
    node_pos = {}
    ntcnt = 0
    for np in node_index:
        node_pos[ntcnt] = (np[0],np[1])
        ntcnt+=1

    nx.draw_networkx_labels(networkx_graph,pos=node_pos)
    nx.draw_networkx_nodes(networkx_graph,node_pos, node_size  = 10)
    nx.draw_networkx_edges(networkx_graph,node_pos,width=1.0,alpha=0.5)
    plt.show()

#================================================================================================================
#NSHFAI
#================================================================================================================
def nshffai(building_occsolids, irrad_threshold, epwweatherfile, xdim, ydim,
            rad_folderpath, nshffai_threshold = None, shading_occfaces = []):
    """
    This function calculates the Non-Solar Heated Facade to Floor Area Index (NSHFFAI) which is the ratio of the facade area that 
    receives irradiation below a specified level over the net floor area. For more information refer to: Chen, Kian Wee, and Leslie Norford.
    2017. Evaluating Urban Forms for Comparison Studies in the Massing Design Stage. Sustainability 9 (6). doi:10.3390/su9060987.
    
    Parameters
    ----------
    building_occsolids : list of OCCsolids
        List of buildings occsolids to be analysed.
    
    irrad_threshold : float 
        The solar irradiance threshold value (kwh/m2). For Singapore a tropical climate 364 kwh/m2 is used.
    
    epwweatherfile : string
        The file path of the epw weatherfile.
    
    xdim : int
        The x dimension grid size for the building facades.
    
    ydim : int
        The y dimension grid size
    
    rad_folderpath : string
        The file directory to store all the result files.
    
    nshffai_threshold : float, optional
        The nshffai threshold value for calculating the nshffai percent, default = None. If None, nshffai percent will return None.
        
    shading_occfaces : list of OCCfaces, optional
        The other surfaces to consider when running the Radiance simulation apart from the buildings of interest. e.g. surrounding terrain or buildings.
    
    Returns
    -------
    result dictionary : dictionary
        A dictionary with this keys : {"afi", "ai", "percent", "sensor_surfaces" , 
        "solar_results", "building_solids", "afi_list"}
    
        afi : float
            The nshffai of the urban design.
            
        ai : float
            The Non-Solar Heated Facade Area Index. The ratio of the facade area that receives irradiation below a specified level over the net facade area.
        
        percent : float
            The percentage of the buidings that has nshffai higher than the threshold.
        
        sensor surfaces : list of OCCfaces
            The gridded facade.   
        
        solar_results : list of floats
            The the irradiance results in (kWh/m2), the list corresponds to the sensor surface list.
        
        building_solids : list of OCCsolids
            The OCCsolids of the buildings.
            
        afi_list : list of floats
            The nshffai of each building, the list corresponds to the building solids.
            
    """
    #sort and process the surfaces into radiance ready surfaces
    rad, sensor_ptlist, sensor_dirlist, sensor_srflist, bldgdict_list = initialise_srf_indexes(building_occsolids, 
                                                                                               xdim, ydim, 
                                                                                               rad_folderpath, 
                                                                                               shading_occfaces = shading_occfaces)   
    
    #execute gencumulative sky rtrace
    irrad_ress = execute_cummulative_radiance(rad,1,12, 1,31,0, 24, epwweatherfile)
    
    sorted_bldgdict_list = get_afi_dict(irrad_ress, sensor_srflist, bldgdict_list, surface = "all_surfaces")
    
    #calculate avg shgfavi 
    total_afi,ai, afi_percent, high_perf_area_list, sa_list, shape_factor_list, bsolid_list, afi_list = calculate_afi(sorted_bldgdict_list, irrad_threshold, "nshffai",
                                                                                                                       afi_threshold = nshffai_threshold)
            

    res_dict = {}
    res_dict["afi"] = total_afi
    res_dict["ai"] = ai
    res_dict["percent"] = afi_percent
    res_dict["sensor_surfaces"] = sensor_srflist
    res_dict["solar_results"] = irrad_ress
    res_dict["building_solids"] = bsolid_list
    res_dict["afi_list"] = afi_list
    
    return res_dict
    
def usffai(building_occsolids, lower_irrad_threshold, upper_irrad_threshold, epwweatherfile, xdim, ydim,
            rad_folderpath, usffai_threshold = None, shading_occfaces = []):
    
    """
    This function calculates the Useful-Solar Facade to Floor Area Index (USFFAI) which is the ratio of the facade area that 
    receives irradiation between the lower and upper solar threshold over the net floor area. 

    Parameters
    ----------
    building_occsolids : list of OCCsolids
        List of buildings occsolids to be analysed.
    
    lower_irrad_threshold : float 
        The lower solar irradiance threshold value (kwh/m2). For Singapore a tropical climate 254 kwh/m2 is used.
        
    upper_irrad_threshold : float 
        The upper solar irradiance threshold value (kwh/m2). For Singapore a tropical climate 364 kwh/m2 is used.
    
    epwweatherfile : string
        The file path of the epw weatherfile.
    
    xdim : int
        The x dimension grid size for the building facades.
    
    ydim : int
        The y dimension grid size
    
    rad_folderpath : string
        The file directory to store all the result files.
    
    usffai_threshold : float, optional
        The usffai threshold value for calculating the nshffai percent, default = None. If None, usffai percent will return None.
        
    shading_occfaces : list of OCCfaces, optional
        The other surfaces to consider when running the Radiance simulation apart from the buildings of interest. e.g. surrounding terrain or buildings.
    
    Returns
    -------
    result dictionary : dictionary
        A dictionary with this keys : {"afi", "ai", "percent", "sensor_surfaces" , 
        "solar_results", "building_solids", "afi_list"}
    
        afi : float
            The usffai of the urban design.
            
        ai : float
            The Useful-Solar Facade Area Index. The ratio of the facade area that receives irradiation between the thresholdsover the net facade area.
        
        percent : float
            The percentage of the buidings that has usffai higher than the threshold.
        
        sensor surfaces : list of OCCfaces
            The gridded facade.   
        
        solar_results : list of floats
            The the irradiance results in (kWh/m2), the list corresponds to the sensor surface list.
        
        building_solids : list of OCCsolids
            The OCCsolids of the buildings.
            
        afi_list : list of floats
            The usffai of each building, the list corresponds to the building solids.
            
    """
    #sort and process the surfaces into radiance ready surfaces
    rad, sensor_ptlist, sensor_dirlist, sensor_srflist, bldgdict_list = initialise_srf_indexes(building_occsolids, 
                                                                                               xdim, ydim, 
                                                                                               rad_folderpath, 
                                                                                               shading_occfaces = shading_occfaces)   
    
    #execute gencumulative sky rtrace
    irrad_ress = execute_cummulative_radiance(rad,1,12, 1,31,0, 24, epwweatherfile)
    
    sorted_bldgdict_list = get_afi_dict(irrad_ress, sensor_srflist, bldgdict_list, surface = "all_surfaces")
    
    #calculate avg shgfavi 
    total_afi,ai, afi_percent, high_perf_area_list, sa_list, shape_factor_list, bsolid_list, afi_list = calculate_afi2(sorted_bldgdict_list, lower_irrad_threshold,
                                                                                                                       upper_irrad_threshold, "usffai",
                                                                                                                       afi_threshold = usffai_threshold)
            

    res_dict = {}
    res_dict["afi"] = total_afi
    res_dict["ai"] = ai
    res_dict["percent"] = afi_percent
    res_dict["sensor_surfaces"] = sensor_srflist
    res_dict["solar_results"] = irrad_ress
    res_dict["building_solids"] = bsolid_list
    res_dict["afi_list"] = afi_list
    
    return res_dict

def calculate_epv(sensor_srflist,irrad_ress):
    """
    This function calculates the energy produced by PV (kwh/yr) (epv). 
    epv = apv*fpv*gt*nmod*ninv
    apv is area of pv (m2)
    fpv is faction of surface with active solar cells (ratio)
    gt is total annual solar radiation energy incident on pv (kwh/m2/yr)
    nmod is the pv efficiency (12%)
    ninv is the avg inverter efficiency (90%)
    
    Parameters
    ----------
    sensor_srflist : list of OCCfaces
        The gridded facade.
            
    irrad_ress : list of floats
        The the irradiance results in (kWh/m2), the list corresponds to the sensor surface list.
    
    Returns
    -------
    epv : float
        The energy produced by PV (kwh/yr).
    
    """
    apv = urbangeom.faces_surface_area(sensor_srflist)
    fpv = 0.8
    gt = (sum(irrad_ress))/(float(len(irrad_ress)))
    nmod = 0.12
    ninv = 0.9
    epv = apv*fpv*gt*nmod*ninv
    return epv

#================================================================================================================
#PVAFAI AND PVEFAI
#================================================================================================================
def pvafai(building_occsolids, irrad_threshold, epwweatherfile, xdim, ydim,
            rad_folderpath, mode = "roof", pvafai_threshold = None, shading_occfaces = []):
    
    """
    This function calculates the PhotoVoltaic Area to Floor Area Index (PVAFAI) which is the ratio of the PV area that 
    receives irradiation above a specified level over the net floor area. For more information refer to: Chen, Kian Wee, and Leslie Norford.
    2017. Evaluating Urban Forms for Comparison Studies in the Massing Design Stage. Sustainability 9 (6). doi:10.3390/su9060987.

    Parameters
    ----------
    building_occsolids : list of OCCsolids
        List of buildings occsolids to be analysed.
    
    irrad_threshold : float 
        The solar irradiance threshold value (kwh/m2). For Singapore a tropical climate 512 kwh/m2 is used for the facade and 1280 kWh/m2 is used for the roof.
    
    epwweatherfile : string
        The file path of the epw weatherfile.
    
    xdim : int
        The x dimension grid size for the building facades.
    
    ydim : int
        The y dimension grid size
    
    rad_folderpath : string
        The file directory to store all the result files.
        
    mode : str, optional
        The PV area of the building. Options are either "roof" or "facade", default = "roof".
    
    pvafai_threshold : float, optional
        The pvafai threshold value for calculating the pvafai percent, default = None. If None, nshffai percent will return None.
        
    shading_occfaces : list of OCCfaces, optional
        The other surfaces to consider when running the Radiance simulation apart from the buildings of interest. e.g. surrounding terrain or buildings.
    
    Returns
    -------
    result dictionary : dictionary
        A dictionary with this keys : {"afi", "ai", "percent", "sensor_surfaces" , 
        "solar_results", "building_solids", "afi_list", "epv"}
    
        afi : float
            The pvafai of the urban design.
            
        ai : float
            The PV Area to Facade Area Index. The ratio of the facade area that receives irradiation below a specified level over the net facade area.
        
        percent : float
            The percentage of the buidings that has pvafai higher than the threshold.
        
        sensor surfaces : list of OCCfaces
            The gridded facade.   
        
        solar_results : list of floats
            The the irradiance results in (kWh/m2), the list corresponds to the sensor surface list.
        
        building_solids : list of OCCsolids
            The OCCsolids of the buildings.
            
        afi_list : list of floats
            The pvafai of each building, the list corresponds to the building solids.
            
        epv : float
        The energy produced by PV (kwh/yr).
            
    """
    
    #sort and process the surfaces into radiance ready surfaces
    rad, sensor_ptlist, sensor_dirlist, sensor_srflist, bldgdict_list = initialise_srf_indexes(building_occsolids, 
                                                                                               xdim, ydim, rad_folderpath, 
                                                                                               surface = mode, 
                                                                                               shading_occfaces = shading_occfaces)   
    #execute gencumulative sky rtrace
    irrad_ress = execute_cummulative_radiance(rad,1,12, 1,31,0, 24, epwweatherfile)
    
    sorted_bldgdict_list = get_afi_dict(irrad_ress, sensor_srflist, bldgdict_list, surface = "all_surfaces")    
    
    #calculate avg pvavi 
    total_afi,ai, afi_percent, high_perf_area_list, sa_list, shape_factor_list, bsolid_list, afi_list = calculate_afi(sorted_bldgdict_list, irrad_threshold, "pvefai", afi_threshold = pvafai_threshold)
              
    #calculate the potential energy generated from pv 
    epv = calculate_epv(sensor_srflist,irrad_ress)
    
    res_dict = {}
    res_dict["afi"] = total_afi
    res_dict["ai"] = ai
    res_dict["percent"] = afi_percent
    res_dict["sensor_surfaces"] = sensor_srflist
    res_dict["solar_results"] = irrad_ress
    res_dict["building_solids"] = bsolid_list
    res_dict["afi_list"] = afi_list
    res_dict["epv"] = epv
        
    return res_dict
    
            
def pvefai(building_occsolids, roof_irrad_threshold, facade_irrad_threshold, epwweatherfile, xdim, ydim,
            rad_folderpath, pvrfai_threshold = None, pvffai_threshold = None, pvefai_threshold = None, shading_occfaces = []):
    """
    This function calculates the PhotoVoltaic Envelope to Floor Area Index (PVEFAI) which is the ratio of the PV envelope area (both facade and roof) that 
    receives irradiation above a specified level over the net floor area. For more information refer to: Chen, Kian Wee, and Leslie Norford.
    2017. Evaluating Urban Forms for Comparison Studies in the Massing Design Stage. Sustainability 9 (6). doi:10.3390/su9060987.

    Parameters
    ----------
    building_occsolids : list of OCCsolids
        List of buildings occsolids to be analysed.
    
    roof_irrad_threshold : float 
        The solar irradiance threshold value (kwh/m2). For Singapore a tropical climate 1280 kWh/m2 is used for the roof.
        
    facade_irrad_threshold : float 
        The solar irradiance threshold value (kwh/m2). For Singapore a tropical climate 512 kwh/m2 is used for the facade.
    
    epwweatherfile : string
        The file path of the epw weatherfile.
    
    xdim : int
        The x dimension grid size for the building facades.
    
    ydim : int
        The y dimension grid size
    
    rad_folderpath : string
        The file directory to store all the result files.
    
    pvrfai_threshold : float, optional
        The PV Roof to Floor Area Index (pvrfai) threshold value for calculating the pvrfai percent, default = None. If None, pvrfai percent will return None.
        
    pvffai_threshold : float, optional
        The PV Facade to Floor Area Index (pvffai) threshold value for calculating the pvffai percent, default = None. If None, pvffai percent will return None.
        
    pvefai_threshold : float, optional
        The PV Envelope to Floor Area Index (pvefai) threshold value for calculating the pvefai percent, default = None. If None, pvefai percent will return None.
        
    shading_occfaces : list of OCCfaces, optional
        The other surfaces to consider when running the Radiance simulation apart from the buildings of interest. e.g. surrounding terrain or buildings.
    
    Returns
    -------
    result dictionary : dictionary
        A dictionary with this keys : {"afi", "ai", "percent", "sensor_surfaces" , 
        "solar_results", "building_solids", "afi_list", "epv"}
    
        afi : list of floats
            The pvefai, pvrfai and pvffai of the urban design.
            
        ai : list of floats
            The PV Envelope Area Index, PV Roof Area Index and PV Facade Area Index. The ratio of the envelope, roof or facade area that receives irradiation above a specified level over the 
            net envelope, roof or facade area.
        
        percent : list of floats
            The percentage of the buidings that has pvefai, pvrfai and pvffai higher than the threshold.
        
        sensor surfaces : list of OCCfaces
            The gridded envelope surfaces.   
        
        solar_results : list of floats
            The the irradiance results in (kWh/m2), the list corresponds to the sensor surface list.
        
        building_solids : list of OCCsolids
            The OCCsolids of the buildings.
            
        afi_list : 2d list of floats
            The pvefai, pvrfai and pvffai of each building, the list corresponds to the building solids. e.g. [[envelope_result_list],[roof_result_list], [facade_result_list]]
            
        epv : float
        The energy produced by PV (kwh/yr) if the envelope is installed with PV.
            
    """
    flr2flr_height = 3.0
    
    #sort and process the surfaces into radiance ready surfaces
    rad, sensor_ptlist, sensor_dirlist, sensor_srflist, bldgdict_list = initialise_srf_indexes(building_occsolids,
                                                                                               xdim, ydim, rad_folderpath, 
                                                                                               surface = "envelope",
                                                                                               shading_occfaces = shading_occfaces)   
    #execute gencumulative sky rtrace
    irrad_ress = execute_cummulative_radiance(rad,1,12, 1,31,0, 24, epwweatherfile)
    
    sorted_bldgdict_listr = get_afi_dict(irrad_ress, sensor_srflist, bldgdict_list, surface = "roof")
    sorted_bldgdict_listf = get_afi_dict(irrad_ress, sensor_srflist, bldgdict_list, surface = "facade")
    
    #calculate avg pvavi 
    rtotal_afi,rai, rafi_percent, rhigh_perf_area_list, rsa_list, shape_factor_list, bsolid_list, rafi_list  = calculate_afi(sorted_bldgdict_listr, roof_irrad_threshold,"pvefai",
                                                                                                                      afi_threshold = pvrfai_threshold)
                         
    ftotal_afi,fai, fafi_percent, fhigh_perf_area_list, fsa_list, shape_factor_list, bsolid_list, fafi_list  = calculate_afi(sorted_bldgdict_listf, facade_irrad_threshold, "pvefai",
                                                                                                                     afi_threshold = pvffai_threshold)
    
    total_bld_up_area = urbangeom.calculate_bld_up_area(bsolid_list,flr2flr_height)
    eafi_list = []
    compared_list = []
    for pv_cnt in range(len(bsolid_list)):
        bldg_flr_area = urbangeom.calculate_bldg_flr_area(bsolid_list[pv_cnt], flr2flr_height)
        eafi = ((rhigh_perf_area_list[pv_cnt] + fhigh_perf_area_list[pv_cnt])/bldg_flr_area)
        eafi_list.append(eafi)
        
        if pvefai_threshold != None:
            if eafi >= pvefai_threshold:
                compared_list.append(eafi)
        
    eafi_percent = (float(len(compared_list))/float(len(eafi_list)))*100
    
    etotal_afi = (sum(rhigh_perf_area_list) + sum(fhigh_perf_area_list))/total_bld_up_area
    #calculate pvai
    eai = (sum(rhigh_perf_area_list) + sum(fhigh_perf_area_list))/(sum(rsa_list) + sum(fsa_list))
    #calculate the potential energy generated from pv 
    epv = calculate_epv(sensor_srflist,irrad_ress)
    
    res_dict = {}
    res_dict["afi"] = [etotal_afi, rtotal_afi,ftotal_afi]
    res_dict["ai"] = [eai, rai,fai]
    res_dict["percent"] = [eafi_percent,rafi_percent,fafi_percent]
    res_dict["sensor_surfaces"] = sensor_srflist
    res_dict["solar_results"] = irrad_ress
    res_dict["building_solids"] = bsolid_list
    res_dict["afi_list"] = [eafi_list, rafi_list, fafi_list]
    res_dict["epv"] = epv
    
    return res_dict
    
def dffai(building_occsolids, illum_threshold, epwweatherfile, xdim, ydim,
            rad_folderpath,daysim_folderpath, dffai_threshold = None, shading_occfaces = []):
    """
    This function calculates the Daylight Facade to Floor Area Index (DFFAI) which is the ratio of the facade area that 
    receives illuminance (lx) higher than a threshold over the net floor area. 

    Parameters
    ----------
    building_occsolids : list of OCCsolids
        List of buildings occsolids to be analysed.
    
    illum_threshold : float 
        The illuminance threshold value (lx). For Singapore a tropical climate 10,000lx is used.
    
    epwweatherfile : string
        The file path of the epw weatherfile.
    
    xdim : int
        The x dimension grid size for the building facades.
    
    ydim : int
        The y dimension grid size
    
    rad_folderpath : string
        The file directory to store all the result files.
        
    daysim_folderpath : string 
        The file directory to store all the daysim result files.
    
    dffai_threshold : float, optional
        The dffai threshold value for calculating the dffai percent, default = None. If None, dsffai percent will return None.
        
    shading_occfaces : list of OCCfaces, optional
        The other surfaces to consider when running the Radiance simulation apart from the buildings of interest. e.g. surrounding terrain or buildings.
    
    Returns
    -------
    result dictionary : dictionary
        A dictionary with this keys : {"afi", "ai", "percent", "sensor_surfaces" , 
        "solar_results", "building_solids", "afi_list"}
    
        afi : float
            The dffai of the urban design.
            
        ai : float
            The Daylight Facade Area Index. The ratio of the facade area that receives illuminance above the thresholds over the net facade area.
        
        percent : float
            The percentage of the buidings that has dffai higher than the threshold.
        
        sensor surfaces : list of OCCfaces
            The gridded facade.   
        
        solar_results : list of floats
            The illuminance in (lx), the list corresponds to the sensor surface list.
        
        building_solids : list of OCCsolids
            The OCCsolids of the buildings.
            
        afi_list : list of floats
            The dffai of each building, the list corresponds to the building solids.
            
    """
    
    rad, sensor_ptlist, sensor_dirlist, sensor_srflist, bldgdict_list = initialise_srf_indexes(building_occsolids, 
                                                                                      xdim, ydim, rad_folderpath, 
                                                                                      shading_occfaces = shading_occfaces)   
    
    illum_ress = execute_cummulative_radiance(rad,1,12, 1,31,0, 24, epwweatherfile, mode = "illuminance")
    
    rad.initialise_daysim(daysim_folderpath)
    #a 60min weatherfile is generated
    rad.execute_epw2wea(epwweatherfile)
    sunuphrs = rad.sunuphrs
    #ge the mean_illum_ress
    mean_illum_ress = []
    for illum in illum_ress:
        mean_illum = illum/float(sunuphrs)
        mean_illum_ress.append(mean_illum)
        
    sorted_bldgdict_list = get_afi_dict(mean_illum_ress, sensor_srflist, bldgdict_list, surface = "all_surfaces")
    
    total_afi,ai, afi_percent, high_perf_area_list, sa_list, shape_factor_list, bsolid_list, afi_list = calculate_afi(sorted_bldgdict_list, illum_threshold, "dffai",
                                                                                                                       afi_threshold = dffai_threshold)
    
    res_dict = {}
    res_dict["afi"] = total_afi
    res_dict["ai"] = ai
    res_dict["percent"] = afi_percent
    res_dict["sensor_surfaces"] = sensor_srflist
    res_dict["solar_results"] = mean_illum_ress
    res_dict["building_solids"] = bsolid_list
    res_dict["afi_list"] = afi_list
    
    return res_dict
    
#================================================================================================================
#SOLAR SIM FUNCTIONS
#================================================================================================================
def initialise_srf_indexes(building_occsolids, xdim, ydim, rad_folderpath, surface = "facade", shading_occfaces = []):
    """
    This function sorts all the building geometries and convert them into Radiance ready geometries.

    Parameters
    ----------
    building_occsolids : list of OCCsolids
        List of buildings occsolids to be analysed.
    
    xdim : int
        The x dimension grid size for the building facades.
    
    ydim : int
        The y dimension grid size
    
    rad_folderpath : string
        The file directory to store all the result files.
        
    surface : string, optional
        The string specifying what are the surface types to extract from the OCCsolid for the analysis. Options are: "facade", "roof" and "envelope", default = "facade".
        
    shading_occfaces : list of OCCfaces, optional
        The other surfaces to consider when running the Radiance simulation apart from the buildings of interest. e.g. surrounding terrain or buildings.
    
    Returns
    -------    
    rad : py2radiance Rad class instance
        The class stores all the Radiance ready geometries.
        
    sensor_ptlist : pyptlist
            List of positions for sensing. Pyptlist is a list of tuples of floats. A pypt is a tuple that documents the xyz coordinates of a 
            pt e.g. (x,y,z), thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
    
    sensor_dirlist : pyveclist
        List of normals of the points sensing. Pyveclist is a list of tuples of floats. A pyvec is a tuple that documents the xyz coordinates of a 
        direction e.g. (x,y,z), thus a pyveclist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    sensor_surfacelist : list of OCCfaces
        The gridded facade.
        
    bldg_dictlist : list of dictionaries
        List of dictionaries. Each dictionary documents information on a building. Each dictionary has these keys : {"solid", "surface_index"}
    
        solid : OCCsolid
            The building OCCsolid.
            
        surface_index : list of int
            The integers are index to the sensor_surfacelist. It specifies which surfaces in the sensor_surfacelist belongs to this building. 
            if the parameter surface == "envelope", the bldg_dict["surface_index"] = [envelope_index1, envelope_index2,roof_index1,roof_index2,facade_index1,facade_index2].
            if the parameter surface == "facade" or "roof", bldg_dict["surface_index"] = [surface_index1,surface_index2].        
    """
    #initialise py2radiance 
    rad_base_filepath = os.path.join(os.path.dirname(__file__),'py2radiance','base.rad')
    rad = py2radiance.Rad(rad_base_filepath, rad_folderpath)
    srfmat = "RAL2012"
    
    sensor_ptlist = []
    sensor_dirlist = []
    sensor_surfacelist = []
    
    bldg_dictlist = []
    
    gsrf_index_cnt = 0
    bldg_cnt = 0
    for bsolid in building_occsolids:
        gsrf_cnt = 0
        #separate the solid into facade footprint and roof
        bldg_dict = {}
        facades, roofs, footprints = urbangeom.identify_building_surfaces(bsolid)
        total_surface_list = facades + roofs
        nsrfs = len(total_surface_list)
        bsrflist = facades + roofs + footprints
        bldg_dict["solid"] = bsolid
        #TO DO: NEED TO PROPERLY DEFINE THE CONDITION THIS IS TOO ARBITRARY 
        if nsrfs < 50:
            if surface == "roof" or surface == "envelope":
                for roof in roofs:
                    sensor_surfaces, sensor_pts, sensor_dirs = urbangeom.generate_sensor_surfaces(roof, xdim, ydim)
                    sensor_ptlist.extend(sensor_pts)
                    sensor_dirlist.extend(sensor_dirs)
                    sensor_surfacelist.extend(sensor_surfaces)
                    
                    gsrf_cnt += len(sensor_surfaces)
                    
                if surface == "envelope":
                    roof_index1 = gsrf_index_cnt
                    roof_index2 = gsrf_index_cnt + gsrf_cnt
                 
            if surface == "facade" or surface == "envelope":
                for facade in facades:
                    sensor_surfaces, sensor_pts, sensor_dirs = urbangeom.generate_sensor_surfaces(facade, xdim, ydim)
                    sensor_ptlist.extend(sensor_pts)
                    sensor_dirlist.extend(sensor_dirs)
                    sensor_surfacelist.extend(sensor_surfaces)
                    
                    gsrf_cnt += len(sensor_surfaces)
                    
                if surface == "envelope":
                    facade_index1 = roof_index2
                    facade_index2 = gsrf_index_cnt + gsrf_cnt
        else:
            if surface == "roof" or surface == "envelope":
                for roof in roofs:
                    sensor_surfaces = []
                    area = py3dmodel.calculate.face_area(roof)
                    if area > 0.01:
                        sensor_pt = py3dmodel.calculate.face_midpt(roof)
                        sensor_dir = py3dmodel.calculate.face_normal(roof)
                        sensor_pt = py3dmodel.modify.move_pt(sensor_pt, sensor_dir, 0.05)
                        
                        sensor_ptlist.append(sensor_pt)
                        sensor_dirlist.append(sensor_dir)
                        sensor_surfacelist.append(roof)
                        sensor_surfaces.append(roof)

                    gsrf_cnt += len(sensor_surfaces)
                    
                if surface == "envelope":
                    roof_index1 = gsrf_index_cnt
                    roof_index2 = gsrf_index_cnt + gsrf_cnt
                 
            if surface == "facade" or surface == "envelope":
                for facade in facades:
                    sensor_surfaces = []
                    area = py3dmodel.calculate.face_area(facade)
                    if area > 0.01:
                        sensor_pt = py3dmodel.calculate.face_midpt(facade)
                        sensor_dir = py3dmodel.calculate.face_normal(facade)
                        sensor_pt = py3dmodel.modify.move_pt(sensor_pt, sensor_dir, 0.05)
                        
                        sensor_ptlist.append(sensor_pt)
                        sensor_dirlist.append(sensor_dir)
                        sensor_surfacelist.append(facade)
                        sensor_surfaces.append(facade)
                                            
                    gsrf_cnt += len(sensor_surfaces)
                    
                if surface == "envelope":
                    facade_index1 = roof_index2
                    facade_index2 = gsrf_index_cnt + gsrf_cnt
             
        bsrf_cnt = 0
        for bsrf in bsrflist:
            pypolygon = py3dmodel.fetch.points_frm_occface(bsrf)
            srfname = "srf" + str(bldg_cnt) + str(bsrf_cnt)
            py2radiance.RadSurface(srfname, pypolygon, srfmat, rad)
            bsrf_cnt+=1
            
        gsrf_range1 = gsrf_index_cnt
        gsrf_range2= gsrf_index_cnt + gsrf_cnt
        
        
        if surface == "envelope":
            bldg_dict["surface_index"] = [gsrf_range1, gsrf_range2,roof_index1,roof_index2,facade_index1,facade_index2]
        else:
            bldg_dict["surface_index"] = [gsrf_range1, gsrf_range2]
             
        bldg_dictlist.append(bldg_dict)
        gsrf_index_cnt +=  gsrf_cnt 
        bldg_cnt += 1 
        
    # the shading surfaces
    shade_cnt = 0
    for shade_srf in shading_occfaces:
        pypolygon = py3dmodel.fetch.points_frm_occface(shade_srf)
        srfname = "shade" + str(shade_cnt)
        py2radiance.RadSurface(srfname, pypolygon, srfmat, rad)
        shade_cnt+=1
            
    #get the sensor grid points
    rad.set_sensor_points(sensor_ptlist, sensor_dirlist)
    rad.create_sensor_input_file()
    #create the geometry files
    rad.create_rad_input_file()
    return rad, sensor_ptlist, sensor_dirlist, sensor_surfacelist, bldg_dictlist
    
def execute_cummulative_radiance(rad,start_mth,end_mth, start_date,end_date,start_hr, end_hr, 
                                 epwweatherfile, mode = "irradiance"):
    """
    This function executes Radiance on the buildings.

    Parameters
    ----------
    rad : py2radiance Rad class instance
        The class stores all the Radiance ready geometries.
    
    start_mth : int
        The start month of the simulation e.g. 1. This means the simulation will run from Jan.
        
    end_mth : int
        The end month of the simulation e.g. 12. This means the simulation will end on Dec.
        
    start_date : int
        The start date of the simulation e.g. 1. This means the simulation will start on the 1st of the start mth.
        
    end_date : int
        The start date of the simulation e.g. 31. This means the simulation will end on the 31st of the end mth.
        
    start_hr : int
        The start hour of the simulation e.g. 7. This means the simulation will start on 7 am everyday.
        
    end_hr : int
        The end hour of the simulation e.g. 19. This means the simulation will end on 7 pm everyday.
        
    epwweatherfile : string
        The file path of the epw weatherfile.
        
    mode : string
        The units of the results, "irradiance" (kWh/m2) or "illuminance" (lux), default = "irradiance".
    
    Returns
    -------
    results : list of floats
        List of irradiance results (kWh/m2) or illuminance in (lux) that corresponds to the sensor points depending on the mode parameter.
            
    """
    time = str(start_hr) + " " + str(end_hr)
    date = str(start_mth) + " " + str(start_date) + " " + str(end_mth) + " " + str(end_date)
    
    if mode == "irradiance":
        rad.execute_cumulative_oconv(time, date, epwweatherfile)
        #execute cumulative_rtrace
        rad.execute_cumulative_rtrace(str(2))#EXECUTE!! 
        #retrieve the results
        irrad_ress = rad.eval_cumulative_rad()
        return irrad_ress
    if mode == "illuminance":
        rad.execute_cumulative_oconv(time, date, epwweatherfile, output = "illuminance")
        #execute cumulative_rtrace
        rad.execute_cumulative_rtrace(str(2))#EXECUTE!! 
        #retrieve the results
        illum_ress = rad.eval_cumulative_rad(output = "illuminance")   
        return illum_ress

def get_afi_dict(result_list, sensor_srflist, bldgdict_list, surface = "all_surfaces"):
    """
    This function rearrange the surfaces of a building accordingly for calculate_afi function after the execution of Radiance.
    
    Parameters
    ----------
    result_list : list of floats
        List of irradiance results (kWh/m2) or illuminance in (lux) depending on the intention to cacluate either nshffai, usffai or dffai. The list corresponds to the sensor_surfacelist.
        
    sensor_surfacelist : list of OCCfaces
        The gridded facade.
        
    bldg_dictlist : list of dictionaries
        List of dictionaries generated from the function initialise_srf_indexes(). Each dictionary documents information on a building. Each dictionary has these keys : {"solid", "surface_index"}
        
    surface : string, optional
        The string specifying what are the surface types to extract from the OCCsolid for the analysis. Options are: "all_surfaces", "facade" and "roof", default = "all_surfaces".
        
    Returns
    -------    
    sorted_bldg_dictlist : list of dictionaries
        List of dictionaries. Each dictionary documents information on a building. Each dictionary has these keys : {"solid", "surface", "result"}
    
        solid : OCCsolid
            The building OCCsolid.
            
        surface : list of OCCfaces
            The surfaces that belongs to this building.
        
        result : list of floats
            List of irradiance results (kWh/m2) or illuminance in (lux) depending on the intention to cacluate either nshaffai, usffai, pvefai, pvafai or dffai. The list corresponds to the surface.
    """
    sorted_bldgdict_list = []
    for bldgdict in bldgdict_list:
        sorted_bldgdict = {}
        surface_index = bldgdict["surface_index"]
        bsolid = bldgdict["solid"]
        sorted_bldgdict["solid"] = bsolid
        if surface == "all_surfaces":
            sorted_bldgdict["result"] = result_list[surface_index[0]:surface_index[1]]
            sorted_bldgdict["surface"] = sensor_srflist[surface_index[0]:surface_index[1]]
        if surface == "roof":
            sorted_bldgdict["result"] = result_list[surface_index[2]:surface_index[3]]
            sorted_bldgdict["surface"] = sensor_srflist[surface_index[2]:surface_index[3]]
        if surface == "facade":
            sorted_bldgdict["result"] = result_list[surface_index[4]:surface_index[5]]
            sorted_bldgdict["surface"] = sensor_srflist[surface_index[4]:surface_index[5]]
        sorted_bldgdict_list.append(sorted_bldgdict)
            
    return sorted_bldgdict_list

def calculate_shape_factor(bldg_occsolid_list, flr2flr_height):
    """
    This function calculates the shape factor of all the buildings. The shape factor is the ratio of building envelope surface area over the building floor area.
    
    Parameters
    ----------
    bldg_occsolid_list : list of OCCsolids
        The list of OCCsolids that are buildings to be calculated.
        
    flr2flr_height : float
        The floor to floor height the building.
    
    Returns
    -------        
    total_bldg_shape_factor_list : list of floats
        The list of shape factor of all the buildings.
    """
    shape_factor_list = []
    for bldg_occsolid in bldg_occsolid_list:
        flr_area = urbangeom.calculate_bldg_flr_area(bldg_occsolid, flr2flr_height)
        bldg_occfaces = py3dmodel.fetch.topo_explorer(bldg_occsolid, "face")
        bldg_surface_area = urbangeom.faces_surface_area(bldg_occfaces)
        shape_factor = bldg_surface_area/flr_area
        shape_factor_list.append(shape_factor)
        
    return shape_factor_list

def calculate_afi(bldgdict_list, result_threshold, mode, flr2flr_height = 3.0,  afi_threshold = None):
    """
    This function calculates the x (either envelope, roof or facade) area to floor area index.
    
    Parameters
    ----------
    bldgdict_list : list of dictionaries
        List of dictionaries generated from the function get_afi_dict(). Each dictionary documents information on a building. Each dictionary has these keys : {"solid", "surface", "result"}
        
    result_threshold : float
        The threshold value either irradiance (kWh/m2) or illuminance (lx) depending on the intention to calculate nshaffai, pvefai, pvafai or dffai.
        
    mode : str
        The options are "nshffai", "pvefai" or "dffai". Mode "pvefai" is used form both function pvafai() and pvefai().
        
    flr2flr_height : float, optional
        The floor to floor height the building, default = 3.0.
        
    afi_threshold : float, optional
        The afi threshold value for calculating the afi percent, default = None. If None, afi percent will return None.
        
    Returns
    -------
    afi : float
        The afi of the urban design.
        
    ai : float
        The Facade Area Index. The ratio of the facade area that receives x (illuminance or irradiance) above/below the thresholds over the net facade area.
    
    percent : float
        The percentage of the buidings that has afi higher/lower than the threshold.
        
    high_perf_area_list : list of floats
        The list of the area of the facade/roof/envelope area performing above/below the threshold.
    
    sa_list : list of floats
        The list of the area of the facade/roof/envelope of the building.
    
    shape_factor_list : list of floats
        The list of the shape factor of the buildings.
    
    bsolid_list : list of OCCsolids
        The OCCsolids of the buildings.
        
    afi_list : list of floats
        The afi of each building, the list corresponds to the building solids.
        
    """
    afi_list = []
    compared_afi_list = []
    high_perf_area_list = []
    sa_list = []
    shape_factor_list = []
    total_bld_up = []
    bsolid_list = []
    for bldgdict in bldgdict_list:
        result_list = bldgdict["result"]
        surface_list = bldgdict["surface"]
        high_perf = []
        high_perf_srf = []
        
        bradcnt = 0
        for res in result_list:
            if mode == "nshffai":
                if res <= result_threshold:
                    high_perf.append(res)
                    high_perf_srf.append(surface_list[bradcnt])
            if mode == "pvefai" or mode == "dffai":
                if res >= result_threshold:
                    high_perf.append(res)
                    high_perf_srf.append(surface_list[bradcnt])
                
            bradcnt+=1

        high_perf_area = urbangeom.faces_surface_area(high_perf_srf)
        high_perf_area_list.append(high_perf_area)
        surface_area = urbangeom.faces_surface_area(surface_list)
        sa_list.append(surface_area)
        bldg_occsolid = bldgdict["solid"]
        bsolid_list.append(bldg_occsolid)
        bldg_flr_area = urbangeom.calculate_bldg_flr_area(bldg_occsolid, flr2flr_height)
        total_bld_up.append(bldg_flr_area)
        shape_factor = surface_area/bldg_flr_area
        shape_factor_list.append(shape_factor)
        #the higher the shape factor the less compact
        afi = high_perf_area/bldg_flr_area 
        afi_list.append(afi)

        if afi_threshold != None:
            if afi >= afi_threshold:
                compared_afi_list.append(afi)
    
    total_afi = sum(high_perf_area_list)/sum(total_bld_up)
    if sum(sa_list) !=0:
        ai = sum(high_perf_area_list)/sum(sa_list)
    else:
        ai = 0.0
    
    if afi_threshold != None:
        afi_percent = float(len(compared_afi_list))/float(len(afi_list))
    else:
        afi_percent = None
        
    return total_afi,ai, afi_percent, high_perf_area_list, sa_list, shape_factor_list, bsolid_list, afi_list

def calculate_afi2(bldgdict_list, lower_result_threshold, upper_result_threshold, mode, flr2flr_height = 3.0,  afi_threshold = None):
    """
    This function calculates the x (either envelope, roof or facade) area to floor area index.
    
    Parameters
    ----------
    bldgdict_list : list of dictionaries
        List of dictionaries generated from the function get_afi_dict(). Each dictionary documents information on a building. Each dictionary has these keys : {"solid", "surface", "result"}
        
    lower_result_threshold : float
        The lower threshold value irradiance (kWh/m2).
        
    upper_result_threshold : float
        The upper threshold value irradiance (kWh/m2).
        
    mode : str
        The options are "usffai".
        
    flr2flr_height : float, optional
        The floor to floor height the building, default = 3.0.
        
    afi_threshold : float, optional
        The afi threshold value for calculating the afi percent, default = None. If None, afi percent will return None.
        
    Returns
    -------
    afi : float
        The afi of the urban design.
        
    ai : float
        The Facade Area Index. The ratio of the facade area that receives x (illuminance or irradiance) above/below the thresholds over the net facade area.
    
    percent : float
        The percentage of the buidings that has afi higher/lower than the threshold.
        
    high_perf_area_list : list of floats
        The list of the area of the facade/roof/envelope area performing above/below the threshold.
    
    sa_list : list of floats
        The list of the area of the facade/roof/envelope of the building.
        
    shape_factor_list : list of floats
        The list of the shape factor of the buildings.
        
    bsolid_list : list of OCCsolids
        The OCCsolids of the buildings.
        
    afi_list : list of floats
        The afi of each building, the list corresponds to the building solids.
        
    """
    afi_list = []
    compared_afi_list = []
    high_perf_area_list = []
    sa_list = []
    shape_factor_list = []
    total_bld_up = []
    bsolid_list = []
    for bldgdict in bldgdict_list:
        result_list = bldgdict["result"]
        surface_list = bldgdict["surface"]
        high_perf = []
        high_perf_srf = []
        
        bradcnt = 0
        for res in result_list:
            if mode == "usffai":
                if lower_result_threshold <= res <= upper_result_threshold:
                    high_perf.append(res)
                    high_perf_srf.append(surface_list[bradcnt])                
            bradcnt+=1

        high_perf_area = urbangeom.faces_surface_area(high_perf_srf)
        high_perf_area_list.append(high_perf_area)
        surface_area = urbangeom.faces_surface_area(surface_list)
        sa_list.append(surface_area)
        bldg_occsolid = bldgdict["solid"]
        bsolid_list.append(bldg_occsolid)
        bldg_flr_area = urbangeom.calculate_bldg_flr_area(bldg_occsolid, flr2flr_height)
        total_bld_up.append(bldg_flr_area)
        shape_factor = surface_area/bldg_flr_area
        shape_factor_list.append(shape_factor)
        #the higher the shape factor the less compact
        afi = high_perf_area/bldg_flr_area 
        afi_list.append(afi)

        if afi_threshold != None:
            if afi >= afi_threshold:
                compared_afi_list.append(afi)
                
    total_afi = sum(high_perf_area_list)/sum(total_bld_up)
    ai = sum(high_perf_area_list)/sum(sa_list)
    
    if afi_threshold != None:
        afi_percent = float(len(compared_afi_list))/float(len(afi_list))
    else:
        afi_percent = None
        
    return total_afi,ai, afi_percent, high_perf_area_list, sa_list, shape_factor_list, bsolid_list, afi_list