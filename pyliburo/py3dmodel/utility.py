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

#========================================================================================================
#NUMERIC & TEXT INPUTS
#========================================================================================================
def generate_falsecolour_bar(minval, maxval, unit_str, bar_length, description_str = None, bar_pos = (0,0,0)):
    """
    This function constructs a falsecolour diagram.
 
    Parameters
    ----------
    minval : float
        The minimum value of the falsecolour bar.
        
    maxval : float
        The maximum value of the falsecolour bar.
        
    unit_str : str
        The string of the unit to be displayed on the bar.
        
    bar_length : float
        The length of the falsecolour bar.
        
    description_str : str, optional
        Description for the falsecolour bar, Default = None.
        
    bar_pos : tuple of floats, optional
        The position of the bar, Default = (0,0,0).
        
    Returns
    -------
    falsecolour bar : list of OCCfaces
        The falsecolor bar which is a list of OCCfaces. 
        
    bar colour : list of tuple of floats
        Each tuple is a r,g,b that is specifying the colour of the bar.
        
    geometries of text: OCCcompound
        The geometries of the text.
        
    str_colour_list : list of tuple of floats
        Each tuple is a r,g,b that is specifying the colour of the string.
        
    value of each falsecolour : list of floats
        The value of each falsecolour.
    """
    import numpy
    interval = 10.0
    xdim = bar_length/interval
    ydim = bar_length
    rectangle = construct.make_rectangle(xdim, ydim)
    rec_mid_pt = calculate.face_midpt(rectangle)
    moved_rectangle = fetch.topo2topotype(modify.move(rec_mid_pt, bar_pos, rectangle))
    
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
        brep_str = fetch.topo2topotype(construct.make_brep_text(str(res_label), xdim/2))
        orig_pt = calculate.get_centre_bbox(brep_str)
        loc_pt = calculate.face_midpt(srf)
        loc_pt = modify.move_pt(loc_pt, (1,-0.3,0), xdim*1.2)
        moved_str = modify.move(orig_pt, loc_pt, brep_str)
        moved_str_face_list.append(moved_str)
        
        if srf_cnt == len(grid_srfs)-1:
            res_label = round(value_range[srf_cnt+1],2)
            brep_str = fetch.topo2topotype(construct.make_brep_text(str(res_label), xdim/2))
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
                d_str = fetch.topo2topotype(construct.make_brep_text(description_str, xdim/2))
                orig_pt2 = calculate.get_centre_bbox(d_str)
                loc_pt2 = modify.move_pt(loc_pt, (0,-1,0), xdim*5)
                moved_str = modify.move(orig_pt2, loc_pt2, d_str)
                moved_str_face_list.append(moved_str)
            

        srf_cnt+=1
        
    cmpd = construct.make_compound(moved_str_face_list)
    face_list = fetch.topo_explorer(cmpd, "face")
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
    """
    This function converts a value into a rgb value with reference to the minimum and maximum value.
 
    Parameters
    ----------
    val : float
        The value to be converted into rgb.
        
    minval : float
        The minimum value of the falsecolour rgb.
        
    maxval : float
        The maximum value of the falsecolour rgb.
        
    Returns
    -------
    rgb value : tuple of floats
        The converted rgb value.
    """
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
    
def falsecolour(vals, minval, maxval):
    """
    This function converts a list of values into a list of rgb values with reference to the minimum and maximum value.
 
    Parameters
    ----------
    vals : list of float
        A list of values to be converted into rgb.
        
    minval : float
        The minimum value of the falsecolour rgb.
        
    maxval : float
        The maximum value of the falsecolour rgb.
        
    Returns
    -------
    rgb value : list of tuple of floats
        The converted list of rgb value.
    """
    res_colours = []
    for result in vals:
        r,g,b = pseudocolor(result, minval, maxval)
        colour = (r, g, b)
        res_colours.append(colour)
    return res_colours

def rgb2val(rgb, minval, maxval):
    """
    This function converts a rgb of value into its original value with reference to the minimum and maximum value.
 
    Parameters
    ----------
    rgb : tuple of floats
        The rgb value to be converted.
        
    minval : float
        The minimum value of the falsecolour rgb.
        
    maxval : float
        The maximum value of the falsecolour rgb.
        
    Returns
    -------
    original value : float
        The orignal float value.
    """
    hsv = colorsys.rgb_to_hsv(rgb[0],rgb[1],rgb[2])
    y = hsv[0]*360
    orig_val_part1 = ((-1*y) + 250)/250.0
    orig_val_part2 = maxval-minval
    orig_val = (orig_val_part1*orig_val_part2)+minval
    return orig_val

#========================================================================================================
#OCCTOPOLOGY INPUTS
#========================================================================================================
def visualise_falsecolour_topo(occtopo_list, results, other_occtopo_2dlist = None, other_colour_list = None, 
                               minval = None, maxval = None, backend = "qt-pyqt5"):
    """
    This function visualise a falsecolour 3D model using the PythonOCC viewer.
 
    Parameters
    ----------
    occtopo_list : list of OCCtopologies
        The geometries to be visualised with the results. The list of geometries must correspond to the list of results.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    results : list of floats
        The results to be visualised. The list of results must correspond to the occtopo_list.
        
    other_occtopo_2dlist : 2d list of OCCtopologies, optional
        Other geometries to be visualised together with the results, Default = None.
        
    other_colour_list : list of str, optional
        The colours of the other_topo2dlist, Default = None. The colour strings include: "WHITE", "BLUE", "RED", "GREEN", "YELLOW", "CYAN",
        "BLACK", "ORANGE". The number of colours must correspond to the number of list in the other_topo2dlist. 
        
    minval : float, optional
        The minimum value of the falsecolour rgb, Default = None. If None the maximum value is equal to the maximum value from the results.
        
    maxval : float, optional
        The maximum value of the falsecolour rgb, Default = None. If None the maximum value is equal to the minimum value from the results.
        
    backend : str, optional
        The graphic interface to use for visualisation, Default = qt-pyqt5. Other options include:"qt-pyqt4", "qt-pyside", "wx"
        
    Returns
    -------
    None : None
        A qt window pops up displaying the geometries.
    """                          
    display, start_display, add_menu, add_function_to_menu = init_display(backend_str = backend)
    
    if minval == None: 
        minval1 = min(results)
    elif minval != None:
        minval1 = minval
    
    if maxval == None: 
        maxval1 = max(results)
    elif maxval != None: 
        maxval1 = maxval
        
    res_colours = falsecolour(results, minval1, maxval1)

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
            
    if other_occtopo_2dlist != None:
        tc_cnt = 0
        for other_topolist in other_occtopo_2dlist:
            other_compound = construct.make_compound(other_topolist)
            other_colour = other_colour_list[tc_cnt]
            display.DisplayColoredShape(other_compound, color=other_colour, update=True)
            tc_cnt +=1
    
    display.set_bg_gradient_color(0, 0, 0, 0, 0, 0)
    display.View_Iso()
    display.FitAll()
    start_display()
    
def visualise(occtopo_2dlist, colour_list = None, backend = "qt-pyqt5"):
    """
    This function visualise a 3D model using the PythonOCC viewer.
 
    Parameters
    ----------
    occtopo_2dlist : 2d list of OCCtopologies
        Geometries to be visualised together with the results.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    colour_list : list of str, optional
        The colours of the occtopo_2dlist, Default = None. If None all the geometries are displayed in white.
        The colour strings include: "WHITE", "BLUE", "RED", "GREEN", "YELLOW", "CYAN", "BLACK", "ORANGE". 
        The number of colours must correspond to the number of list in the other_topo2dlist. 
        
    backend : str, optional
        The graphic interface to use for visualisation, Default = qt-pyqt5. Other options include:"qt-pyqt4", "qt-pyside", "wx"
        
    Returns
    -------
    None : None
        A qt window pops up displaying the geometries.
    """       
    display, start_display, add_menu, add_function_to_menu = init_display(backend_str = backend)
    
    if colour_list == None:
        colour_list = []
        for _ in range(len(occtopo_2dlist)):
            colour_list.append("WHITE")
            
    sc_cnt = 0
    for shape_list in occtopo_2dlist:
        compound = construct.make_compound(shape_list)
        colour = colour_list[sc_cnt]
        display.DisplayColoredShape(compound, color = colour, update=True)
        sc_cnt+=1
        
    display.set_bg_gradient_color(250, 250, 250, 250, 250, 250)
    display.View_Iso()
    display.FitAll()
    start_display()
    
def write_2_stl(occtopology, stl_filepath, mesh_incremental_float = 0.8):
    """
    This function writes a 3D model into STL format.
 
    Parameters
    ----------
    occtopology : OCCtopology
        Geometries to be written into STL.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    stl_filepath : str
        The file path of the STL file. 
        
    mesh_incremental_float : float, optional
        Default = 0.8.
        
    Returns
    -------
    None : None
        The geometries are written to a STL file.
    """       
    from OCC.StlAPI import StlAPI_Writer
    from OCC.BRepMesh import BRepMesh_IncrementalMesh
    # Export to STL
    stl_writer = StlAPI_Writer()
    stl_writer.SetASCIIMode(True)
    mesh = BRepMesh_IncrementalMesh(occtopology, mesh_incremental_float)
    mesh.Perform()
    assert mesh.IsDone()
    stl_writer.Write(occtopology,stl_filepath)