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
import colorsys

import construct
import calculate
import fetch
import modify
import os

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
        from OCC.Quantity import Quantity_TOC_RGB, Quantity_Color
        compound = construct.make_compound(c_srfs)
        display.DisplayColoredShape(compound, color=Quantity_Color(colour[0], colour[1], colour[2], Quantity_TOC_RGB), update=True)
        
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
    
def write_2_stl(occtopology, stl_filepath, linear_deflection = 0.8, angle_deflection = 0.5):
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
    from OCC.TopoDS import TopoDS_Shape
    # Export to STL
    stl_writer = StlAPI_Writer()
    stl_writer.SetASCIIMode(True)
    occtopology = TopoDS_Shape(occtopology)
    mesh = BRepMesh_IncrementalMesh(occtopology, linear_deflection, True, angle_deflection, True)
    assert mesh.IsDone()
        
    stl_writer.Write(occtopology,stl_filepath)
    
def write_2_stl2(occtopology, stl_filepath, is_meshed = True, linear_deflection = 0.8, angle_deflection = 0.5):
    """
    This function writes a 3D model into STL format. This is different from write2stl as it uses the numpy-stl library.
 
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
    import numpy as np
    from stl import mesh
    
    if is_meshed == False:
        tri_faces = construct.simple_mesh(occtopology, linear_deflection = linear_deflection, angle_deflection = angle_deflection)
        occtopology = construct.make_compound(tri_faces)
        
    face_list = fetch.topo_explorer(occtopology, "face")
    vlist = fetch.topo_explorer(occtopology, "vertex")
    occptlist = modify.occvertex_list_2_occpt_list(vlist)
    pyptlist = modify.occpt_list_2_pyptlist(occptlist)
    pyptlist = modify.rmv_duplicated_pts(pyptlist)
    vertices = np.array(pyptlist)
    
    face_index_2dlsit = []
    for face in face_list:
        f_pyptlist = fetch.points_frm_occface(face)
        f_pyptlist.reverse()            
        if len(f_pyptlist) == 3:
            index_list = []
            for fp in f_pyptlist:
                p_index = pyptlist.index(fp)
                index_list.append(p_index)
            face_index_2dlsit.append(index_list)
        elif len(f_pyptlist) > 3:
            print "THE FACE HAS THE WRONG NUMBER OF VERTICES, IT HAS:", len(f_pyptlist), "VERTICES"
            tri_faces = construct.simple_mesh(face)
            for tri_face in tri_faces:
                tps = fetch.points_frm_occface(tri_face)
                index_list = []
                for tp in tps:
                    p_index = pyptlist.index(tp)
                    index_list.append(p_index)
                face_index_2dlsit.append(index_list)
#        else:
#            print "THE FACE HAS THE WRONG NUMBER OF VERTICES, IT HAS:", len(f_pyptlist), "VERTICES"
        
    faces = np.array(face_index_2dlsit)
    shape_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype = mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            shape_mesh.vectors[i][j] = vertices[f[j],:]
            
    shape_mesh.save(stl_filepath)
    
    
def read_stl(stl_filepath):
    """
    This function reads STL format.
 
    Parameters
    ----------
    stl_filepath : str
        The file path of the STL file. 
        
    Returns
    -------
    occtopology : OCCtopology
        The geometries from an STL file.
    """       
    from OCC.StlAPI import StlAPI_Reader
    from OCC.TopoDS import TopoDS_Shape
    
    stl_reader = StlAPI_Reader()
    the_shape = TopoDS_Shape()
    stl_reader.Read(the_shape, stl_filepath)

    assert not the_shape.IsNull()

    return the_shape

def write_brep(occtopology, brep_filepath):
    """
    This function writes a 3D model into brep format.
 
    Parameters
    ----------
    occtopology : OCCtopology
        Geometries to be written into STL.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    brep_filepath : str
        The file path of the brep file. 
        
    Returns
    -------
    None : None
        The geometries are written to a brep file.
    """       
    from OCC.BRepTools import breptools_Write
    breptools_Write(occtopology, brep_filepath)
    
def read_brep(brep_filepath):
    """
    This function writes a 3D model into brep format.
 
    Parameters
    ----------
    brep_filepath : str
        The file path of the brep file. 
        
    Returns
    -------
    occtopology : OCCtopology
        Geometries read from the brep.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
    """       
    from OCC.BRepTools import breptools_Read
    from OCC.TopoDS import TopoDS_Shape
    from OCC.BRep import BRep_Builder
    
    shape = TopoDS_Shape()
    builder = BRep_Builder()
    breptools_Read(shape, brep_filepath, builder)
    return shape
    
def write_2_stl_gmsh(occtopology, stl_filepath, mesh_dim = 2, min_length = 1, max_length = 5,
                     gmsh_location = "C:\\gmsh\\gmsh.exe"):
    """
    This function mesh an occtopology using gmsh http://gmsh.info/.
 
    Parameters
    ----------
    occtopology : OCCtopology
        Geometries to be written into STL.
        OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        
    stl_filepath : str
        The file path of the STL file. 
        
    mesh_dim : int, optional
        Perform 1D, 2D or 3D mesh generation.
        
    min_length : float, optional
        The minimum edge length of the mesh.
    
    max_length : float, optional
        The max edge length of the mesh.
        
    gmsh_location : str
        The location where the gmsh program is located. We assumed it is isntalled in C:\\gmsh\\gmsh.exe
        
    Returns
    -------
    None : None
        The geometries are meshed and written to a stl file.
    """
    # dump the geometry to a brep file
    from OCC.BRepTools import breptools_Write
    import subprocess
    
    parent_path = os.path.abspath(os.path.join(stl_filepath, os.pardir))
    filename = os.path.splitext(stl_filepath)[0]
    # create the brep file
    brep_file = os.path.join(parent_path, filename +".brep")
    breptools_Write(occtopology,brep_file)
    
    # create the gmesh file
    geo_file = os.path.join(parent_path, "shape.geo")
    set_factory_str = 'SetFactory("OpenCASCADE");\n'
    mesh_min_length = 'Mesh.CharacteristicLengthMin = ' + str(min_length)+';\n'
    mesh_max_length = 'Mesh.CharacteristicLengthMax = ' + str(max_length) + ';\n'
    brep_file_str = 'a() = ShapeFromFile("' + brep_file +'");'
    gmsh_geo_file_content = set_factory_str+mesh_min_length+mesh_max_length+brep_file_str
    gmsh_geo_file = open(geo_file, "w")
    gmsh_geo_file.write(gmsh_geo_file_content)
    gmsh_geo_file.close()

    # call gmsh
    cwd = os.getcwd()
    gmsh_dir = os.path.abspath(os.path.join(gmsh_location, os.pardir))
    os.chdir(gmsh_dir)

    command = "gmsh " +  geo_file + " -" + str(mesh_dim) + " -algo meshadapt -o " + stl_filepath + " -format stl"
    print command
    process = subprocess.call(command)

    
    # load the stl file
    if process == 0 and os.path.isfile(stl_filepath) :
        print "WROTE TO:", stl_filepath
        os.chdir(cwd)
    else:
        print "Be sure gmsh is in your PATH"