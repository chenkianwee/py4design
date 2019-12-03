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
import math
from functools import reduce

from . import py3dmodel

#========================================================================================================
#FACE INPUTS
#========================================================================================================
def generate_sensor_surfaces(occface, xdim, ydim, distance_offset = 0.01):
    """
    This function generates a gridded face from an OCCface, the gridded faces are not on the OCCface but moved in the face normal 
    direction.
 
    Parameters
    ----------
    occface : OCCface
        OCCface to be gridded
        
    xdim : float
        The x-dimension of each grid.
        
    ydim : float
        The y-dimension of each grid.
        
    distance_offset : float, optional
        The distance moved in the direction of the face normal, Default = 0.01.
        
    Returns
    -------
    sensor faces : list of OCCfaces
        List of OCCfaces of the grid.
    
    sensor points : pyptlist
        The mid point of each grid. Pyptlist is a list of tuples of floats. A pypt is a tuple that documents the xyz coordinates of a 
        pt e.g. (x,y,z), thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    sensor directions : pyveclist
        Pyveclist is a list of tuples of floats. A pyvec is a tuple that documents the xyz coordinates of a direction e.g. (x,y,z), 
        thus a pyveclist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
    
    """
    normal = py3dmodel.calculate.face_normal(occface)
    mid_pt = py3dmodel.calculate.face_midpt(occface)
    location_pt = py3dmodel.modify.move_pt(mid_pt, normal, 0.01)
    moved_oface = py3dmodel.fetch.topo2topotype(py3dmodel.modify.move(mid_pt, location_pt, occface))
    #put it into occ and subdivide surfaces 
    sensor_surfaces = py3dmodel.construct.grid_face(moved_oface, xdim, ydim)
    sensor_pts = []
    sensor_dirs = []
    for sface in sensor_surfaces:
        smidpt = py3dmodel.calculate.face_midpt(sface)
        sensor_pts.append(smidpt)
        sensor_dirs.append(normal)
    
    return sensor_surfaces, sensor_pts, sensor_dirs

def landuse_2_grid(landuse_occface, xdim, ydim):
    """
    This function generates a gridded face from an OCCface.
 
    Parameters
    ----------
    occface : OCCface
        OCCface to be gridded
        
    xdim : float
        The x-dimension of each grid.
        
    ydim : float
        The y-dimension of each grid.
        
    Returns
    -------
    grid points : pyptlist
        The mid point of each grid. Pyptlist is a list of tuples of floats. A pypt is a tuple that documents the xyz coordinates of a 
        pt e.g. (x,y,z), thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    grid faces : list of OCCfaces
        List of OCCfaces of the grid.
    
    """
    pt_list = []
    grid_faces = py3dmodel.construct.grid_face(landuse_occface, xdim, ydim)
    for f in grid_faces:
        pt = py3dmodel.calculate.face_midpt(f)
        pt_list.append(pt)
        
    return pt_list, grid_faces
        
def identify_srfs_according_2_angle(occface_list):
    """
    This function identify if a OCCface is a roof, wall, or floor depending on the angle of its normal.
 
    Parameters
    ----------
    occface_list : a list of OCCfaces
        List of OCCfaces that will be analysed.
        
    Returns
    -------
    facades : list of OCCfaces
        List of OCCfaces identified as facade, angle of normal between 45 < n < 170, with reference to the up direction (0,0,1).
        
    roofs : list of OCCfaces
        List of OCCfaces identified as roof, angle of normal between n<=45 , with reference to the up direction (0,0,1).
        
    floors : list of OCCfaces
        List of OCCfaces identified as floors, angle of normal between n>=170 , with reference to the up direction (0,0,1).
    
    """
    roof_list = []
    facade_list = []
    footprint_list = []
    vec1 = (0,0,1)
    for f in occface_list:
        #get the normal of each face
        n = py3dmodel.calculate.face_normal(f)
        angle = py3dmodel.calculate.angle_bw_2_vecs(vec1, n)
        #means its a facade
        if angle>45 and angle<170:
            facade_list.append(f)
        elif angle<=45:
            roof_list.append(f)
        elif angle>=170:
            footprint_list.append(f)
    return facade_list, roof_list, footprint_list

def identify_surface_direction(occface_list):
    """
    This function identify if a OCCface is facing north, south, east and west depending on the angle of its normal. The y-direction is
    assumed as north.
 
    Parameters
    ----------
    occface_list : a list of OCCfaces
        List of OCCfaces that will be analysed.
        
    Returns
    -------
    north facades : list of OCCfaces
        List of OCCfaces identified as facing north, angle of normal between 0 <= n <= 45 and n >= 315, 
        with reference to the y direction (0,1,0).
        
    south facades : list of OCCfaces
        List of OCCfaces identified as facing south, angle of normal between 135 <= n <= 225, with reference to the y direction (0,1,0).
        
    east facades : list of OCCfaces
        List of OCCfaces identified as facing east, angle of normal between 225 < n < 315, with reference to the y direction (0,1,0).
        
    west facades : list of OCCfaces
        List of OCCfaces identified as facing west, angle of normal between 45 < n < 135, with reference to the y direction (0,1,0).
    
    """
    vec1 = (0,1,0)
    pyref_vec = (0,0,1)
    north_list = []
    south_list = []
    east_list = []
    west_list = []
    
    for f in occface_list:
        #get the normal of each face
        n = py3dmodel.calculate.face_normal(f)
        n = (n[0],n[1],0.0)
        angle = py3dmodel.calculate.angle_bw_2_vecs_w_ref(vec1, n, pyref_vec)
        if angle>=0 and angle<=45:
            north_list.append(f)
        elif angle>=315:
            north_list.append(f)
        elif angle>45 and angle<135:
            west_list.append(f)
        elif angle>=135 and angle<=225:
            south_list.append(f)
        elif angle>225 and angle<315:
            east_list.append(f)
    return north_list, south_list, east_list, west_list

def faces_surface_area(occface_list):
    """
    This function measures the total surface area of the list of OCCfaces.
 
    Parameters
    ----------
    occface_list : a list of OCCfaces
        List of OCCfaces that will be analysed.
        
    Returns
    -------
    total surface area : float
        The total surface area of all the OCCfaces summed up.
    
    """
    total_sa = 0
    for occface in occface_list:
        sa = py3dmodel.calculate.face_area(occface)
        total_sa = total_sa + sa
    return total_sa
            
def extrude_move_down_occ_faces(occface_list, distance = 1):
    """
    This function moves the OCCfaces down a distance from its original position and extrude the OCCfaces.
 
    Parameters
    ----------
    occface_list : a list of OCCfaces
        List of OCCfaces that will be analysed.
        
    distance : float
        The distance moved by the OCCface.
        
    Returns
    -------
    list of extruded solids : list of OCCsolids
        The list of extruded OCCsolids.
    
    """
    extrude_list = []
    for occface in occface_list:
        midpt = py3dmodel.calculate.face_midpt(occface)
        loc_pt = py3dmodel.modify.move_pt(midpt, (0,0,-1),1)
        #move the face down
        m_occface = py3dmodel.modify.move(midpt, loc_pt, occface)
        m_occface = py3dmodel.fetch.topo2topotype(m_occface)
        #extrude the face
        extrude = py3dmodel.construct.extrude(m_occface, (0,0,1), 2)
        extrude_list.append(extrude)
    return extrude_list
    
def redraw_occfaces(occface_list):
    """
    This function redraws all the OCCfaces.
 
    Parameters
    ----------
    occface_list : a list of OCCfaces
        List of OCCfaces to be redrawed.
        
    Returns
    -------
    list of redrawn faces : list of OCCfaces
        The list of redrawn OCCfaces.
    
    """
    recon_faces = []
    for occface in occface_list:
        pyptlist = py3dmodel.fetch.points_frm_occface(occface)
        recon_face = py3dmodel.construct.make_polygon(pyptlist)
        recon_faces.append(recon_face)
    return recon_faces

#========================================================================================================
#SHELL INPUTS
#========================================================================================================  
def reconstruct_bldg_shell(bldg_occshell):
    """
    This function reconstructs the OCCshell.
 
    Parameters
    ----------
    occshell : OCCshell
        OCCshell to be reconstructed.
        
    Returns
    -------
    reconstructed shell : OCCshell
        The reconstructed OCCshell.
    
    """
    bldg_occsolid = py3dmodel.construct.make_solid(bldg_occshell)
    bldg_occsolid = py3dmodel.modify.fix_close_solid(bldg_occsolid)
    intersection_list = []
    bounding_list = []
    loc_pt  = get_building_location_pt(bldg_occsolid)
    bounding_footprint = get_building_bounding_footprint(bldg_occsolid)
    
    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(bldg_occsolid)
    height = zmax-zmin
    flr_height = 3.0
    remainder = height%flr_height
    division = int(height/flr_height)
    if remainder >0:
        division = int(math.ceil(division))
        flr_height = height/math.ceil(division)
    
    for scnt in range(division):
        if scnt==0:
            moved_pt = (loc_pt[0], loc_pt[1], loc_pt[2]-0.1)
            moved_bldg_occsolid = py3dmodel.modify.move(loc_pt,moved_pt, bldg_occsolid)
            #intersection_list.append(moved_bldg_occsolid)
            flr1_list = py3dmodel.construct.boolean_common(moved_bldg_occsolid,bounding_footprint)
            flr1_list = py3dmodel.fetch.topo_explorer(flr1_list, "face")
            nflr1 = len(flr1_list)
            if nflr1 > 1:
                break
            flr1 = flr1_list[0]
            
        if scnt !=0 or scnt !=division-1:
            z = loc_pt[2]+((scnt)*flr_height)
            moved_pt = (loc_pt[0], loc_pt[1], z)
            moved_f = py3dmodel.modify.move(loc_pt, moved_pt, bounding_footprint)
            bounding_list.append(py3dmodel.fetch.topo2topotype(moved_f))
            
        if scnt == division-1:
            z = loc_pt[2]+((scnt)*flr_height)
            moved_pt = (loc_pt[0], loc_pt[1], z)
            moved_f = py3dmodel.modify.move(loc_pt, moved_pt, bounding_footprint)
            
            moved_pt = (loc_pt[0], loc_pt[1], loc_pt[2]+0.1)
            moved_bldg_occsolid = py3dmodel.modify.move(loc_pt,moved_pt, bldg_occsolid)
            flr_last = py3dmodel.construct.boolean_common(moved_bldg_occsolid,moved_f )
            flr_last = py3dmodel.fetch.topo_explorer(flr_last, "face")[0]
        
    if nflr1 ==1:
        bounding_cmpd = py3dmodel.construct.make_compound(bounding_list)
        floors = py3dmodel.construct.boolean_common(bounding_cmpd, bldg_occsolid)
        floors = py3dmodel.fetch.topo_explorer(floors, "face")
        intersection_list.append(flr1)
        intersection_list.extend(floors)
        intersection_list.append(flr_last)
    
        loft = py3dmodel.construct.make_loft(intersection_list)
        loft = py3dmodel.fetch.topo2topotype(loft)
        lface_list = py3dmodel.fetch.topo_explorer(loft, "face")
        
        recon_faces = []
        recon_faces.append(flr1)
        recon_faces.extend(lface_list)
        recon_faces.append(flr_last)
        recon_shell = py3dmodel.construct.sew_faces(recon_faces)[0]
        recon_shell = py3dmodel.modify.fix_shell_orientation(recon_shell)
        r_loft_faces = py3dmodel.construct.simple_mesh(recon_shell)
        recon_shell = py3dmodel.construct.sew_faces(r_loft_faces)[0]
        recon_shell = py3dmodel.modify.fix_shell_orientation(recon_shell)
        return recon_shell
    else:
        return bldg_occshell
        
def is_shell_faces_planar(occshell):
    """
    This function identify if all OCCfaces in the OCCshell are planar.
 
    Parameters
    ----------
    occshell : OCCshell
        OCCshell to be analysed.
        
    Returns
    -------
    is planar : bool
        True or False, if True OCCshell is planar, if False OCCshell not planar.
    
    """
    face_list = py3dmodel.fetch.topo_explorer(occshell, "face")
    for face in face_list:
        is_face_planar = py3dmodel.calculate.is_face_planar(face, 1e-06)
        if not is_face_planar:
            return False
    return True
    
def is_shell_simple(occshell):
    """
    This function check if the OCCshell is simple. Simple is defined as having less than 6 surfaces.
 
    Parameters
    ----------
    occshell : OCCshell
        OCCshell to be analysed.
        
    Returns
    -------
    is planar : bool
        True or False, if True OCCshell is simple, if False OCCshell not simple.
    
    """
    #if the shell has more than triangle polygon and has more than 6 faces
    #it is not simple
    face_list = py3dmodel.fetch.topo_explorer(occshell, "face")
    nface = len(face_list)
    for face in face_list:
        pypt_list = py3dmodel.fetch.points_frm_occface(face)
        npypt = len(pypt_list)
        if npypt == 3 and nface>6:
            return False
    return True

def identify_open_close_shells(occshell_list):
    """
    This function identify if the OCCshells are open or closed.
 
    Parameters
    ----------
    occshell_list : a list of OCCshells
        List of OCCshells to be analysed.
        
    Returns
    -------
    list of closed shell : list of OCCshells
        The list of closed OCCshells.
    
    list of open shell : list of OCCshells
        The list of open OCCshells.
    
    """
    close_shell_list = []
    open_shell_list = []
    for shell in occshell_list:
        is_closed = py3dmodel.calculate.is_shell_closed(shell)
        if is_closed:
            close_shell_list.append(shell)
        else:
            open_shell_list.append(shell)
            
    return close_shell_list, open_shell_list
    
def reconstruct_open_close_shells(occshell_list):
    """
    This function recombines all the OCCfaces in the OCCshells , and rearrange the OCCfaces into new OCCshells. This is to check if there 
    are e.g. two open shells that can be recombined to form a closed shell.
 
    Parameters
    ----------
    occshell_list : a list of OCCshells
        List of OCCshells to be analysed and recombined.
        
    Returns
    -------
    list of recombined shell : list of OCCshells
        The list of recombined OCCshells.
    
    """
    close_shell_list, open_shell_list = identify_open_close_shells(occshell_list)
    if open_shell_list:
        open_shell_compound = py3dmodel.construct.make_compound(open_shell_list)
        open_shell_faces = py3dmodel.fetch.topo_explorer(open_shell_compound, "face")
        #sew all the open shell faces together to check if there are solids among the open shells
        recon_shell_list = py3dmodel.construct.sew_faces(open_shell_faces)
        recon_close_shell_list, recon_open_shell_list = identify_open_close_shells(recon_shell_list)
        if recon_close_shell_list:
            open_shell_list2 = []
            open_shell_rmv_index = []
            #boolean difference the close shells from the open shells 
            for recon_close_shell in recon_close_shell_list:
                os_cnt = 0
                for open_shell in open_shell_list:
                    #common_cmpd = py3dmodel.construct.boolean_common(recon_close_shell, open_shell)
                    difference_cmpd = py3dmodel.construct.boolean_difference(open_shell, recon_close_shell)
                    is_diff_null = py3dmodel.fetch.is_compound_null(difference_cmpd)
                    if is_diff_null:
                        open_shell_rmv_index.append(os_cnt)
                    os_cnt+=1
                    
            for os_cnt2 in range(len(open_shell_list)):
                if os_cnt2 not in open_shell_rmv_index:
                    open_shell2 = open_shell_list[os_cnt2]
                    open_shell_list2.append(open_shell2)
                    
            return close_shell_list + recon_close_shell_list + open_shell_list2
        else:
            return occshell_list
    else:
        return occshell_list

#========================================================================================================
#SOLID INPUTS
#========================================================================================================
def identify_building_surfaces(bldg_occsolid):
    """
    This function identifies all the OCCfaces in a OCCsolid as a roof, wall, or floor depending on the angle of its normal.
 
    Parameters
    ----------
    bldg_occsolid : OCCsolid
        The OCCsolid that is a building to be analysed.
        
    Returns
    -------
    facades : list of OCCfaces
        List of OCCfaces identified as facade, angle of normal between 45 < n < 170, with reference to the up direction (0,0,1).
        
    roofs : list of OCCfaces
        List of OCCfaces identified as roof, angle of normal between n<=45 , with reference to the up direction (0,0,1).
        
    floors : list of OCCfaces
        List of OCCfaces identified as floors, angle of normal between n>=170 , with reference to the up direction (0,0,1).
    
    """
    face_list = py3dmodel.fetch.faces_frm_solid(bldg_occsolid)
    facade_list, roof_list, footprint_list = identify_srfs_according_2_angle(face_list)     
    return facade_list, roof_list, footprint_list
    
def get_bldg_footprint_frm_bldg_occsolid(bldg_occsolid, tolerance = 1e-05, roundndigit = 6, distance = 0.1):
    """
    This function gets the footprint of a building.
 
    Parameters
    ----------
    bldg_occsolid : OCCsolid
        The OCCsolid that is a building to be analysed.
        
    tolearnce : float, optional
        The tolerance used for the analysis, the smaller the float it is more precise. Default = 1e-05.
    
    roundndigit : int, optional
        The number of decimal places of the xyz of the points for the boolean section function, Default = 6. The higher the number the more precise are the points.
        Depending on the precision of the points, it will decide whether the edges are connected.
        
    distance : float, optional
        The smallest distance between two points from the edges for boolean section function, Default = 0.01. 
        The further the distance the less precise is the resultant faces.
        
    Returns
    -------        
    footprints : list of OCCfaces
        List of OCCfaces identified as footprints.
    
    """
    bounding_footprint = get_building_bounding_footprint(bldg_occsolid)
    b_midpt = py3dmodel.calculate.face_midpt(bounding_footprint)
    loc_pt = (b_midpt[0], b_midpt[1], b_midpt[2]+tolerance)
    bounding_footprint = py3dmodel.fetch.topo2topotype(py3dmodel.modify.move(b_midpt, loc_pt, bounding_footprint))
    bldg_footprint_cmpd = py3dmodel.construct.boolean_section(bldg_occsolid, bounding_footprint, roundndigit = roundndigit, distance = distance)
    bldg_footprint_cmpd = py3dmodel.fetch.topo2topotype(py3dmodel.modify.move(loc_pt, b_midpt, bldg_footprint_cmpd))
    bldg_footprint_list = py3dmodel.fetch.topo_explorer(bldg_footprint_cmpd, "face")
    return bldg_footprint_list

def get_building_roofplates(bldg_occsolid, nstorey, storey_height, tolerance = 1e-05, roundndigit = 6, distance = 0.1):
    """
    This function gets the roof plate of a building, roof plates in this function is defined as the plates at the very top of the building.
 
    Parameters
    ----------
    bldg_occsolid : OCCsolid
        The OCCsolid that is a building to be analysed.
        
    nstorey : int
        The number of storey of the building.
    
    storey_height : float
        The floor to floor height the building.
        
    tolearnce : float, optional
        The tolerance used for the analysis, the smaller the float it is more precise. Default = 1e-05.
        
    tolearnce : float, optional
        The tolerance used for the analysis, the smaller the float it is more precise. Default = 1e-05.
    
    roundndigit : int, optional
        The number of decimal places of the xyz of the points for the boolean section function, Default = 6. The higher the number the more precise are the points.
        Depending on the precision of the points, it will decide whether the edges are connected.
        
    distance : float, optional
        The smallest distance between two points from the edges for boolean section function, Default = 0.01. 
        The further the distance the less precise is the resultant faces.
        
    Returns
    -------        
    roof plates : list of OCCfaces
        List of OCCfaces identified as roofs.
    
    """
    loc_pt = get_building_location_pt(bldg_occsolid)
    bounding_footprint = get_building_bounding_footprint(bldg_occsolid)
    z = loc_pt[2]+(nstorey*storey_height)
    moved_pt = (loc_pt[0], loc_pt[1], z)
    moved_f = py3dmodel.modify.move(loc_pt, moved_pt, bounding_footprint)
           
    moved_pt2 = (loc_pt[0], loc_pt[1], loc_pt[2] + tolerance)
    moved_occsolid = py3dmodel.modify.move(loc_pt, moved_pt2, bldg_occsolid)
    floors = py3dmodel.construct.boolean_section(moved_f, moved_occsolid, roundndigit = roundndigit, distance = distance)
    inter_face_list = py3dmodel.fetch.topo_explorer(floors, "face")
    return inter_face_list#, bounding_list
    
def get_building_flrplates(bldg_occsolid, nstorey, storey_height):
    """
    This function gets the floor plates of a building.
    
    Parameters
    ----------
    bldg_occsolid : OCCsolid
        The OCCsolid that is a building to be analysed.
        
    nstorey : int
        The number of storey of the building.
    
    storey_height : float
        The floor to floor height the building.
        
    Returns
    -------        
    floor plates : list of OCCfaces
        List of OCCfaces that are floors.
    
    """
    intersection_list = []
    bounding_list = []
    loc_pt = get_building_location_pt(bldg_occsolid)
    bounding_footprint = get_building_bounding_footprint(bldg_occsolid)
    bldg_footprint_list = get_bldg_footprint_frm_bldg_occsolid(bldg_occsolid)
    intersection_list.extend(bldg_footprint_list)
    for scnt in range(nstorey):
        z = loc_pt[2]+(scnt*storey_height)
        moved_pt = (loc_pt[0], loc_pt[1], z)
        moved_f = py3dmodel.modify.move(loc_pt, moved_pt, bounding_footprint)
        bounding_list.append(moved_f)
           
    bounding_compound = py3dmodel.construct.make_compound(bounding_list)
    floors = py3dmodel.construct.boolean_common(bldg_occsolid, bounding_compound)
    common_compound = py3dmodel.fetch.topo2topotype(floors)
    inter_face_list = py3dmodel.fetch.topo_explorer(common_compound, "face")
    if inter_face_list:
        for inter_face in inter_face_list:
            intersection_list.append(inter_face)
    return intersection_list#, bounding_list

def get_building_plates_by_level(bldg_occsolid, nstorey, storey_height, roundndigit = 6, distance = 0.1):
    """
    This function gets the floor plates of a building and return a 2d list instead of a list of the OCCfaces.
    
    Parameters
    ----------
    bldg_occsolid : OCCsolid
        The OCCsolid that is a building to be analysed.
        
    nstorey : int
        The number of storey of the building.
    
    storey_height : float
        The floor to floor height the building.
    
    roundndigit : int, optional
        The number of decimal places of the xyz of the points for the boolean section function, Default = 6. The higher the number the more precise are the points.
        Depending on the precision of the points, it will decide whether the edges are connected.
        
    distance : float, optional
        The smallest distance between two points from the edges for boolean section function, Default = 0.01. 
        The further the distance the less precise is the resultant faces.
        
    Returns
    -------        
    floor plates : 2dlist of OCCfaces
        2d List of OCCfaces that are floors. The 2d list is in such format:
        [floorplates on level 1, floorplates on level 2, floorplates on level x}, floorplates on level x = [face1,face2,facex]
    
    """
    intersection_2dlist = []
    bounding_list = []
    
    loc_pt = get_building_location_pt(bldg_occsolid)
    bounding_footprint = get_building_bounding_footprint(bldg_occsolid)
    bldg_footprint_list = get_bldg_footprint_frm_bldg_occsolid(bldg_occsolid, roundndigit = roundndigit, distance = distance)
    intersection_2dlist.append(bldg_footprint_list)
    
    for scnt in range(nstorey):
        z = loc_pt[2]+((scnt+1)*storey_height)
        moved_pt = (loc_pt[0], loc_pt[1], z)
        moved_f = py3dmodel.modify.move(loc_pt, moved_pt, bounding_footprint)
        floor_cmpd = py3dmodel.construct.boolean_section(moved_f, bldg_occsolid, roundndigit = roundndigit, distance = distance)
        floor_list = py3dmodel.fetch.topo_explorer(floor_cmpd, "face")
        if floor_list:
            intersection_2dlist.append(floor_list)
        bounding_list.append(moved_f)
            

    new_2d_list = []
    for intersection_list in intersection_2dlist:
        new_flr_list = []
        for floor in intersection_list:
            wire_list = py3dmodel.fetch.topo_explorer(floor, "wire")
            to_be_cut_list = []
            cutting_list = []
            for wire in wire_list:
                bspline_edge = py3dmodel.modify.wire_2_bsplinecurve_edge(wire)
                lbound, ubound = py3dmodel.fetch.edge_domain(bspline_edge)
                bound = ubound - lbound
                n_interval = 30
                b_interval = bound/float(n_interval)
                pyptlist = []
                for i in range(n_interval):
                    u = lbound + (i*b_interval)
                    e_pypt = py3dmodel.calculate.edgeparameter2pt(u, bspline_edge)
                    pyptlist.append(e_pypt)
                
                #pyref_vec = (0,0,1)
                pyref_vec = py3dmodel.calculate.face_normal(floor)
                is_anticlockwise = py3dmodel.calculate.is_anticlockwise(pyptlist, pyref_vec)
                new_floor = py3dmodel.construct.make_polygon(pyptlist)
                if is_anticlockwise:
                    to_be_cut_list.append(new_floor)
                else:
                    cutting_list.append(new_floor) 
                    
            if len(cutting_list) !=0:
                extrude_list = []
                for cut in cutting_list:
                    midpt = py3dmodel.calculate.face_midpt(cut)
                    loc_pt = py3dmodel.modify.move_pt(midpt, (0,0,-1),0.3)
                    #move the face down
                    m_occface = py3dmodel.modify.move(midpt, loc_pt, cut)
                    m_occface = py3dmodel.fetch.topo2topotype(m_occface)
                    #extrude the face
                    extrude_solid = py3dmodel.construct.extrude(m_occface, (0,0,1), 0.6)
                    extrude_list.append(extrude_solid)
                    
                cmpd = py3dmodel.construct.make_compound(extrude_list)
        
                for tbc in to_be_cut_list:
                    diff_cmpd = py3dmodel.construct.boolean_difference(tbc, cmpd)
                    cut_new_flr_list = py3dmodel.fetch.topo_explorer(diff_cmpd, "face")
                    new_flr_list.extend(cut_new_flr_list)
            else:
                new_flr_list.extend(to_be_cut_list)
        new_2d_list.append(new_flr_list)
            
    return new_2d_list

def detect_clash(bldg_occsolid, other_occsolids):
    """
    This function detects if this building OCCsolid clashes with the other OCCsolids.
    
    Parameters
    ----------
    bldg_occsolid : OCCsolid
        The OCCsolid that is a building to be analysed.
        
    other_occsolids : list of OCCsolid
        The list of other OCCsolid to be analysed.
        
    Returns
    -------        
    clash : bool
        True or False, if True there is a clash, if False there is no clash.
    """
    compound = py3dmodel.construct.make_compound(other_occsolids)
    #extract all the faces as the boolean dun work well with just the solid
    bldg_faces = py3dmodel.fetch.topo_explorer(bldg_occsolid, "face")
    face_cmpd = py3dmodel.construct.make_compound(bldg_faces)
    common_compound = py3dmodel.construct.boolean_common(bldg_occsolid, compound)
    common_compound2 = py3dmodel.construct.boolean_common(face_cmpd, compound)
    is_cmpd_null = py3dmodel.fetch.is_compound_null(common_compound)
    is_cmpd_null2 = py3dmodel.fetch.is_compound_null(common_compound2)
    if is_cmpd_null == True and is_cmpd_null2 == True:
        return False
    else:
        return True
    
def detect_in_boundary(bldg_occsolid, luse_occface):
    """
    This function detects if this building OCCsolid is inside the boundary of the landuse OCCface.
    
    Parameters
    ----------
    bldg_occsolid : OCCsolid
        The OCCsolid that is a building to be analysed.
        
    luse_occface : OCCface
        The boundary landuse OCCface.
        
    Returns
    -------        
    in boundary : bool
        True or False, if True in boundary, if False not in boundary.
    """
    luse_occsolid = py3dmodel.construct.extrude(luse_occface,(0,0,1), 10000)
    diff_cmpd = py3dmodel.construct.boolean_difference(bldg_occsolid, luse_occsolid)
    is_cmpd_null = py3dmodel.fetch.is_compound_null(diff_cmpd)
    return is_cmpd_null

def calculate_bldg_height(bldg_occsolid):
    """
    This function calculates the building height of this building OCCsolid.
    
    Parameters
    ----------
    bldg_occsolid : OCCsolid
        The OCCsolid that is a building to be analysed.
        
    Returns
    -------        
    height : float
        The building height.
    """
    xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(bldg_occsolid)
    height = zmax - zmin
    return round(height,2)
    
def calculate_bldg_height_n_nstorey(bldg_occsolid, storey_height):
    """
    This function calculates the building height and the number of storeys of this building OCCsolid.
    
    Parameters
    ----------
    bldg_occsolid : OCCsolid
        The OCCsolid that is a building to be analysed.
        
    storey_height : float
        The floor to floor height the building.
        
    Returns
    -------        
    height : float
        The building height.
    
    storey : int
        The the number of storeys of the building.
    """
    height = calculate_bldg_height(bldg_occsolid)
    nstorey = int(math.floor(float(height)/float(storey_height)))
    return height,nstorey
    
def get_building_bounding_footprint(bldg_occsolid):
    """
    This function calculates the building's bounding footprint (the footprint of the bounding box of the OCCsolid).
    
    Parameters
    ----------
    bldg_occsolid : OCCsolid
        The OCCsolid that is a building to be analysed.
        
    Returns
    -------        
    bounding footprint : OCCface
        The bounding footprint of the OCCface.
    """
    xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(bldg_occsolid)
    bounding_footprint = py3dmodel.construct.make_polygon([(xmin,ymin,zmin),(xmin,ymax,zmin),(xmax, ymax, zmin),(xmax, ymin, zmin)])
    return bounding_footprint
    
def get_building_location_pt(bldg_occsolid):
    """
    This function calculates the building's location point (the mid point of the building's bounding footprint).
    
    Parameters
    ----------
    bldg_occsolid : OCCsolid
        The OCCsolid that is a building to be analysed.
        
    Returns
    -------        
    location point : pypt
        Tuple of floats. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z)
    """
    bounding_footprint = get_building_bounding_footprint(bldg_occsolid)
    loc_pt = py3dmodel.calculate.face_midpt(bounding_footprint)
    return loc_pt

def reconstruct_building_through_floorplates(bldg_occsolid, bldg_flr_area, storey_height):
    """
    This function reconstructs the building OCCsolid according to the given floor area.
    
    Parameters
    ----------
    bldg_occsolid : OCCsolid
        The OCCsolid that is a building to be reconstructed.
        
    bldg_flr_area : float
        The floor area of the reconstructed building.
    
    storey_height : float
        The floor to floor height the building.
    
    Returns
    -------        
    reconstructed building : OCCsolid
        The reconstructed building OCCsolid.
    """
    intersection_list = []
    bounding_list = []
    loc_pt  = get_building_location_pt(bldg_occsolid)
    bounding_footprint = get_building_bounding_footprint(bldg_occsolid)
    bldg_footprint_list = get_bldg_footprint_frm_bldg_occsolid(bldg_occsolid)
    intersection_list.extend(bldg_footprint_list)
    scnt = 0
    while bldg_flr_area > 0:
        if scnt == 0:
            for bldg_footprint in bldg_footprint_list:
                flr_area = py3dmodel.calculate.face_area(bldg_footprint)
                bldg_flr_area = bldg_flr_area - flr_area
        else:
            z = loc_pt[2]+((scnt)*storey_height)
            moved_pt = (loc_pt[0], loc_pt[1], z)
            moved_f = py3dmodel.modify.move(loc_pt, moved_pt, bounding_footprint)
            bounding_list.append(py3dmodel.fetch.topo2topotype(moved_f))
            floors = py3dmodel.construct.boolean_common(bldg_occsolid, moved_f)
            #py3dmodel.construct.visualise([[moved_f,building_solid]], ["WHITE"])
            compound = py3dmodel.fetch.topo2topotype(floors)
            inter_face_list = py3dmodel.fetch.topo_explorer(compound,"face")
            if inter_face_list:
                for inter_face in inter_face_list:
                    flr_area = py3dmodel.calculate.face_area(inter_face)
                    bldg_flr_area = bldg_flr_area - flr_area
                    intersection_list.append(inter_face)
            else:
                #it means the original solid is not so tall
                #need to move a storey up 
                loc_pt2 = (moved_pt[0], moved_pt[1], (moved_pt[2]-storey_height))
                previous_flr = intersection_list[-1]
                moved_f2 = py3dmodel.fetch.topo2topotype(py3dmodel.modify.move(loc_pt2, moved_pt, previous_flr))
                flr_area = py3dmodel.calculate.face_area(moved_f2)
                bldg_flr_area = bldg_flr_area - flr_area
                intersection_list.append(moved_f2)

        scnt += 1
            
    last_flr = intersection_list[-1]
    rs_midpt = py3dmodel.calculate.face_midpt(last_flr)
    moved_pt = (rs_midpt[0], rs_midpt[1], (rs_midpt[2]+storey_height))
    roof_srf = py3dmodel.fetch.topo2topotype(py3dmodel.modify.move(rs_midpt, moved_pt, last_flr))

    intersection_list.append(roof_srf)
    flr_srf = intersection_list[0]
    
    new_building_shell = py3dmodel.construct.make_loft(intersection_list, rule_face = False)
    
    face_list = py3dmodel.fetch.faces_frm_shell(new_building_shell) 
    face_list.append(roof_srf)
    face_list.append(flr_srf)
    closed_shell = py3dmodel.construct.sew_faces(face_list)[0]
    shell_list = py3dmodel.fetch.topos_frm_compound(closed_shell)["shell"]
    new_bldg_occsolid = py3dmodel.construct.make_solid(shell_list[0])
    
    return new_bldg_occsolid#, intersection_list, bounding_list

def calculate_bldg_flr_area(bldg_occsolid, flr2flr_height):
    """
    This function calculates the building floor area.
    
    Parameters
    ----------
    bldg_occsolid : OCCsolid
        The OCCsolid that is a building to be calculated.
        
    flr2flr_height : float
        The floor to floor height the building.
    
    Returns
    -------        
    bldg_flr_area : float
        The floor area of the building.
    """
    bldg_height, nstorey = calculate_bldg_height_n_nstorey(bldg_occsolid, flr2flr_height)
    bldg_flr_plates = get_building_plates_by_level(bldg_occsolid, nstorey, flr2flr_height)
    bldg_flr_plates = reduce(lambda x,y :x+y ,bldg_flr_plates)
    #py3dmodel.construct.visualise([bldg_flr_plates], ["RED"])
    flr_area = 0
    for flr in bldg_flr_plates:
        flr_area = flr_area + py3dmodel.calculate.face_area(flr)
    return flr_area

def calculate_bld_up_area(bldg_occsolid_list, flr2flr_height):
    """
    This function calculates the total floor area of all the buildings.
    
    Parameters
    ----------
    bldg_occsolid_list : list of OCCsolids
        The list of OCCsolids that are buildings to be calculated.
        
    flr2flr_height : float
        The floor to floor height the building.
    
    Returns
    -------        
    total_bldg_flr_area : float
        The total floor area of all the buildings.
    """
    flr_area_list = []
    for bldg_occsolid in bldg_occsolid_list:
        flr_area = calculate_bldg_flr_area(bldg_occsolid, flr2flr_height)
        flr_area_list.append(flr_area)
        
    return sum(flr_area_list)

def calculate_urban_vol(bldg_occsolid_list):
    """
    This function calculates the total volume of all the buildings.
    
    Parameters
    ----------
    bldg_occsolid_list : list of OCCsolids
        The list of OCCsolids that are buildings to be calculated.
    
    Returns
    -------        
    total_bldg_volume_list : list of floats
        The list of volumes of all the buildings.
    """
    bvol_list = []
    for bldg_occsolid in bldg_occsolid_list:
        bvol = py3dmodel.calculate.solid_volume(bldg_occsolid)
        bvol_list.append(bvol)
        
    return bvol_list

def rearrange_building_position(bldg_occsolid_list, luse_gridded_pyptlist, luse_occface, parameters, other_occsolids = [], clash_detection = True, 
                                boundary_detection = True):
    """
    This function rearranged the building OCCsolids positions on a land use plot according to the given parameters.
    
    Parameters
    ----------
    bldg_occsolid_list : list of OCCsolids
        The list of OCCsolids that are buildings to be positioned.
        
    luse_gridded_pyptlist : pyptlist
        All the possible positions on the landuse plot. A list of tuples of floats. A pypt is a tuple that documents the xyz coordinates of a pt 
        e.g. (x,y,z), thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
    
    luse_occface : OCCface
        The landuse OCCface.
    
    parameters : list of int.
        The index of the points in luse_gridded_pyptlist. If parameter is 5, the building will be placed on the 5th point of the pyptlist.
        
    other_occsolids : list of OCCsolids
        The other OCCsolids on the landuse plot.
    
    clash_detection : bool
        True or False, if True while rearranging ensures does not clash with other OCCsolid, if False does not.
    
    boundary_detection : bool
        True or False, if True while rearranging ensures stays within land use boundary, if False does not.
        
    Returns
    -------        
    repositioned buildings : list of OCCsolids
        The repositioned building OCCsolids.
    """
    moved_buildings = []
    n_other_occsolid = len(other_occsolids)
    moved_buildings.extend(other_occsolids)
    npypt_list = len(luse_gridded_pyptlist)
    nbldgs = len(bldg_occsolid_list)
    for cnt in range(nbldgs):      
        bldg_occsolid = bldg_occsolid_list[cnt]
        pos_parm = parameters[cnt]
        loc_pt = get_building_location_pt(bldg_occsolid)
        
        isclash = True
        for clash_cnt in range(npypt_list):
            #print "clash_cnt", clash_cnt
            #map the location point to the grid points
            mpt_index = pos_parm+clash_cnt
            if mpt_index >= npypt_list:
                mpt_index = mpt_index-(npypt_list-1) 
                
            moved_pt = luse_gridded_pyptlist[mpt_index]
            moved_solid = py3dmodel.fetch.topo2topotype(py3dmodel.modify.move(loc_pt, moved_pt, bldg_occsolid))
            #shell = py3dmodel.fetch.topo_explorer(moved_solid,"shell")[0]
            moved_solid = py3dmodel.modify.fix_close_solid(moved_solid)
            #=======================================================================================
            if clash_detection == True and boundary_detection == False:
                if moved_buildings:
                    clash_detected = detect_clash(moved_solid, moved_buildings)                    
                    if not clash_detected:
                        #means there is no intersection and there is no clash
                        #print "I am not clashing onto anyone!!!"
                        isclash = False
                        break
                
                else:
                    isclash = False
                    break
                
            #=======================================================================================
            elif boundary_detection == True and clash_detection == False:
                is_in_boundary = detect_in_boundary(moved_solid, luse_occface)
                if is_in_boundary:
                    isclash = False
                    break
            #=======================================================================================
            elif boundary_detection == True and clash_detection == True:
                #need to check if the moved building is within the boundaries of the landuse 
                is_in_boundary = detect_in_boundary(moved_solid, luse_occface)
                    
                if is_in_boundary:
                    #test if it clashes with the other buildings 
                    if moved_buildings:
                        clash_detected = detect_clash(moved_solid, moved_buildings)                    
                        if not clash_detected:
                            #print "I am not clashing onto anyone!!!"
                            isclash = False
                            break
                    
                    else:
                        isclash = False
                        break
            #=======================================================================================  
            elif clash_detection == False and boundary_detection == False:
                isclash = False
                break
            
        if isclash == True:
            print("it is not feasible with these parameters to create a design variant")
            #just append the original arrangements into the list
            return bldg_occsolid_list
        
        if isclash == False:
            #print "successfully positioned the building"
            moved_buildings.append(moved_solid)
            
    if other_occsolids:
        moved_buildings = moved_buildings[n_other_occsolid:]
    print("successfully positioned the buildings")
    return moved_buildings

#========================================================================================================
#COMPOUND INPUTS
#========================================================================================================      
def redraw_occshell(occcompound, tolerance):
    """
    This function redraws and recombine all OCCshells in the OCCcompound.
 
    Parameters
    ----------
    occcompound : OCCcompound
        OCCcompound to be redrawed.
        
    tolerance : float
        The precision of the recombination operation.
        
    Returns
    -------
    reconstructed shells : OCCcompound of OCCshells
        The reconstructed shells.
    
    """
    recon_shelllist = []
    shells = py3dmodel.fetch.topo_explorer(occcompound, "shell")
    for shell in shells:
        faces = py3dmodel.fetch.topo_explorer(shell, "face")
        recon_faces = []
        for face in faces:
            pyptlist = py3dmodel.fetch.points_frm_occface(face)
            recon_face = py3dmodel.construct.make_polygon(pyptlist)
            recon_faces.append(recon_face)
        nrecon_faces = len(recon_faces)
        if nrecon_faces == 1:
            recon_shell = py3dmodel.construct.make_shell(recon_faces)
        if nrecon_faces > 1:
            #py3dmodel.construct.visualise([recon_faces], ['WHITE'])
            recon_shell = py3dmodel.construct.sew_faces(recon_faces, tolerance = tolerance )[0]
        recon_shelllist.append(recon_shell)    
        
    recon_compound = py3dmodel.construct.make_compound(recon_shelllist)
    return recon_compound
    
def redraw_occedge(occcompound, tolerance):
    """
    This function redraws all OCCedges in the OCCcompound.
 
    Parameters
    ----------
    occcompound : OCCcompound
        OCCcompound to be redrawed.
        
    tolerance : float
        The precision of the recombination operation.
        
    Returns
    -------
    reconstructed edges : OCCcompound of OCCedges
        The reconstructed edges.
    
    """
    edges = py3dmodel.fetch.topo_explorer(occcompound, "edge")
    recon_edgelist = []
    for edge in edges:
        epyptlist = py3dmodel.fetch.points_frm_edge(edge)
        if len(epyptlist) >= 2:
            recon_edgelist.append(py3dmodel.construct.make_edge(epyptlist[0], epyptlist[1]))
        
    recon_compound = py3dmodel.construct.make_compound(recon_edgelist)
    return recon_compound