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
import colorsys

import construct
import calculate
import fetch
import modify

from OCC.Display.SimpleGui import init_display
from OCCUtils import Topology

def generate_falsecolour_bar(minval, maxval, unit_str, bar_length, description_str = None, bar_pos = (0,0,0)):
    import numpy
    interval = 10.0
    xdim = bar_length/interval
    ydim = bar_length
    rectangle = construct.make_rectangle(xdim, ydim)
    rec_mid_pt = calculate.face_midpt(rectangle)
    moved_rectangle = fetch.shape2shapetype(modify.move(rec_mid_pt, bar_pos, rectangle))
    
    grid_srfs = construct.grid_face(moved_rectangle, xdim, xdim)

    #generate uniform results between max and min
    inc1 = (maxval-minval)/(interval)
    value_range = list(numpy.arange(minval, maxval+0.1, inc1))
    inc2 = inc1/2.0
    value_range_midpts = list(numpy.arange(minval+inc2, maxval, inc1))
    bar_colour = falsecolour(value_range_midpts, minval, maxval)
    grid_srfs2 = []
    moved_str_face_list = []
    srf_cnt = 0
    for srf in grid_srfs:
        reversed_srf = modify.reverse_face(srf)
        grid_srfs2.append(reversed_srf)
        res_label = round(value_range[srf_cnt],2)
        brep_str = fetch.shape2shapetype(construct.make_brep_text(str(res_label), xdim/2))
        orig_pt = calculate.get_centre_bbox(brep_str)
        loc_pt = calculate.face_midpt(srf)
        loc_pt = modify.move_pt(loc_pt, (1,-0.3,0), xdim*1.2)
        moved_str = modify.move(orig_pt, loc_pt, brep_str)
        moved_str_face_list.append(moved_str)
        
        if srf_cnt == len(grid_srfs)-1:
            res_label = round(value_range[srf_cnt+1],2)
            brep_str = fetch.shape2shapetype(construct.make_brep_text(str(res_label), xdim/2))
            orig_pt = calculate.get_centre_bbox(brep_str)
            loc_pt3 = modify.move_pt(loc_pt, (0,1,0), xdim)
            moved_str = modify.move(orig_pt, loc_pt3, brep_str)
            moved_str_face_list.append(moved_str)
        
            brep_str_unit = construct.make_brep_text(str(unit_str), xdim)
            orig_pt2 = calculate.get_centre_bbox(brep_str_unit)
            loc_pt2 = modify.move_pt(loc_pt, (0,1,0), xdim*2)
            moved_str = modify.move(orig_pt2, loc_pt2, brep_str_unit)
            moved_str_face_list.append(moved_str)
            
        if description_str !=None:    
            if srf_cnt == 0:
                d_str = fetch.shape2shapetype(construct.make_brep_text(description_str, xdim/2))
                orig_pt2 = calculate.get_centre_bbox(d_str)
                loc_pt2 = modify.move_pt(loc_pt, (0,-1,0), xdim*5)
                moved_str = modify.move(orig_pt2, loc_pt2, d_str)
                moved_str_face_list.append(moved_str)
            

        srf_cnt+=1
        
    cmpd = construct.make_compound(moved_str_face_list)
    face_list = fetch.geom_explorer(cmpd, "face")
    meshed_list = []
    for face in face_list:    
        meshed_face_list = construct.simple_mesh(face)
        mface = construct.make_shell(meshed_face_list)
        face_mid_pt =  calculate.face_midpt(face)
        str_mid_pt = calculate.get_centre_bbox(mface)
        moved_mface = modify.move(str_mid_pt,face_mid_pt,mface)
        meshed_list.append(moved_mface)
        
    meshed_str_cmpd =construct.make_compound(meshed_list)
    str_colour_list = [(0,0,0)]
    return grid_srfs2, bar_colour, meshed_str_cmpd, str_colour_list, value_range_midpts

def pseudocolor(val, minval, maxval):
    # convert val in range minval..maxval to the range 0..120 degrees which
    # correspond to the colors red..green in the HSV colorspace
    if val <= minval:
        h = 250.0
    elif val>=maxval:
        h = 0.0
    else:
        h = 250 - (((float(val-minval)) / (float(maxval-minval)))*250)
    # convert hsv color (h,1,1) to its rgb equivalent
    # note: the hsv_to_rgb() function expects h to be in the range 0..1 not 0..360
    r, g, b = colorsys.hsv_to_rgb(h/360, 1., 1.)
    return r, g, b
    
def falsecolour(results, minval, maxval):
    res_colours = []
    for result in results:
        r,g,b = pseudocolor(result, minval, maxval)
        colour = (r, g, b)
        res_colours.append(colour)
    return res_colours

def rgb2val(rgb, minval, maxval):
    hsv = colorsys.rgb_to_hsv(rgb[0],rgb[1],rgb[2])
    y = hsv[0]*360
    orig_val_part1 = ((-1*y) + 250)/250.0
    orig_val_part2 = maxval-minval
    orig_val = (orig_val_part1*orig_val_part2)+minval
    return orig_val

def visualise_falsecolour_topo(results, occtopo_list, other_topo2dlist = None, other_colourlist = None, 
                               minval_range = None, maxval_range = None, backend = "qt-pyqt5"):
                                   
    display, start_display, add_menu, add_function_to_menu = init_display(backend_str = backend)
    
    if minval_range == None: 
        minval = min(results)
    elif minval_range != None:
        minval = minval_range
    
    if maxval_range == None: 
        maxval = max(results)
    elif maxval_range != None: 
        maxval = maxval_range
        
    res_colours = falsecolour(results, minval, maxval)

    colour_list = []
    c_srf_list = []
    for r_cnt in range(len(res_colours)):
        fcolour = res_colours[r_cnt]
        rf = occtopo_list[r_cnt]
        if fcolour not in colour_list:
            colour_list.append(fcolour)
            c_srf_list.append([rf])
            
        elif fcolour in colour_list:
            c_index = colour_list.index(fcolour)
            c_srf_list[c_index].append(rf)
        
    for c_cnt in range(len(c_srf_list)):
        c_srfs = c_srf_list[c_cnt]
        colour = colour_list[c_cnt]
        compound = construct.make_compound(c_srfs)
        display.DisplayColoredShape(compound, color=colour, update=True)
        
    #display the edges of the grid
    tedges = []
    for t in occtopo_list:
        edge = list(Topology.Topo(t).edges())
        tedges.extend(edge)
        
    edgecompound = construct.make_compound(tedges)
    display.DisplayColoredShape(edgecompound, color="BLACK", update=True)
            
    if other_topo2dlist != None:
        tc_cnt = 0
        for other_topolist in other_topo2dlist:
            other_compound = construct.make_compound(other_topolist)
            other_colour = other_colourlist[tc_cnt]
            display.DisplayColoredShape(other_compound, color=other_colour, update=True)
            tc_cnt +=1
    
    display.set_bg_gradient_color(0, 0, 0, 0, 0, 0)
    display.View_Iso()
    display.FitAll()
    start_display()
    
def visualise(shape2dlist, colour_list, backend = "qt-pyqt5"):
    display, start_display, add_menu, add_function_to_menu = init_display(backend_str = backend)
    sc_cnt = 0
    for shape_list in shape2dlist:
        compound = construct.make_compound(shape_list)
        colour = colour_list[sc_cnt]
        display.DisplayColoredShape(compound, color = colour, update=True)
        sc_cnt+=1
        
    display.set_bg_gradient_color(250, 250, 250, 250, 250, 250)
    display.View_Iso()
    display.FitAll()
    start_display()
    
def write_2_stl(occshape, stl_filepath, mesh_incremental_float = 0.8):
    from OCC.StlAPI import StlAPI_Writer
    from OCC.BRepMesh import BRepMesh_IncrementalMesh
    # Export to STL
    stl_writer = StlAPI_Writer()
    stl_writer.SetASCIIMode(True)
    mesh = BRepMesh_IncrementalMesh(occshape, mesh_incremental_float)
    mesh.Perform()
    assert mesh.IsDone()
    stl_writer.Write(occshape,stl_filepath)