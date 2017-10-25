#==================================================================================================
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
#    along with Pyliburo.  If not, see <http://www.gnu.org/licenses/>.
#
#   Authors: Patrick Janssen <patrick@janssen.name>
#           Chen Kian Wee <chenkianwee@gmail.com>
# ==================================================================================================


def surface(name, material, points):
    """
    This function writes the surface information into Radiance readable string format.
    
    Parameters
    ----------
    name :  str
        The name of the surface.
        
    material :  str
        The name of the material of the surface. The material name must be in the base.rad file.
        
    points :  pyptlist
        List of points defining the surface. Pyptlist is a list of tuples of floats. A pypt is a tuple that documents the xyz coordinates of a 
        pt e.g. (x,y,z), thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]

    Returns
    -------
    rad surface :  str
        The surface written into radiance readable string.
    """
    surface = material + " polygon " + name + "\n"+\
    "0\n"+\
    "0\n"+\
    str(len(points) * 3) + "\n"
    for point in points:
        surface = surface + "    " + str(point[0]) + "  " + str(point[1]) + "  " + str(point[2]) + "\n"
    surface = surface + "\n"
    return surface

def glow(name, colour):
    """
    This function writes the glow function for Radiance.
 
    Parameters
    ----------
    name: str
        The name of glow. 

    colour: tuple of floats
        A tuple of floats describing the colour. e.g. (1,1,1) for a white sky.
        
    Returns
    -------
    rad glow :  str
        The glow written into radiance readable string.
    """
    glow = "skyfunc glow " + name + "\n"+\
    "0\n"+\
    "0\n"+\
    "4 " +\
    str(colour[0])+ " "  +\
    str(colour[1]) + " " +\
    str(colour[2]) + " 0\n"
    glow = glow + "\n"
    return glow 

def source(name, material, direction):
    """
    This function writes the source function for Radiance.
 
    Parameters
    ----------
    name: str
        The name of source. 
    
    material: str
        The material of the source, can be either "sky_glow" or "ground_glow".

    direction: tuple of floats
        A tuple of floats describing the direction of the source. e.g. (0,0,1) for point up.
        
    Returns
    -------
    rad source :  str
        The source written into radiance readable string.
    """
    source = material + " source " + name + "\n"+\
    "0\n"+\
    "0\n"+\
    "4 " +\
    str(direction[0])+ " "  +\
    str(direction[1]) + " " +\
    str(direction[2]) + " 180\n"
    source = source + "\n"
    return source

def brightfunc(cal_name):
    """
    This function writes the brightfunc function for Radiance.
 
    Parameters
    ----------
    cal_name: str
        The name of cal. 
        
    Returns
    -------
    rad brightfunc :  str
        The brightfunc written into radiance readable string.
    """
    
    brightfunc = "void brightfunc skyfunc\n" +\
                 "2 skybright " + cal_name + "\n"+\
                 "0\n"+\
                 "0\n\n"
                 
    return brightfunc


def material_glass(name, transmission):
    """
    This function writes the Radiance glass material.
 
    Parameters
    ----------
    name: str
        The name of glass. 
    
    transmission: tuple of floats
        A tuple of floats describing the transmission of the glass.
        
    Returns
    -------
    rad glass :  str
        The glass written into radiance readable string.
    """
    
    material_glass = "# Glass material\n"+\
    "void glass " + name + "\n"+\
    "0\n"+\
    "0\n"+\
    "3 " +\
    str(transmission[0])+ " "  +\
    str(transmission[1]) + " " +\
    str(transmission[2]) + "\n\n"
    return material_glass


def material_plastic(name, colour, spec, rough):
    """
    This function writes the Radiance plastic material.
 
    Parameters
    ----------
    name: str
        The name of plastic. 
    
    colour: tuple of floats
        A tuple of floats describing the colour of the glass.
    
    spec: float
        A float describing the specularity of the plastic.
        
    rough: float
        A float describing the roughness of the plastic.
        
    Returns
    -------
    rad plastic :  str
        The plastic written into radiance readable string.
    """
    material_plastic = "# Plastic material\n"+\
    "void plastic " + name + "\n"+\
    "0\n"+\
    "0\n"+\
    "5 " +\
    str(colour[0])+ " "  +\
    str(colour[1]) + " " +\
    str(colour[2]) + " " +\
    str(spec) + " " +\
    str(rough) + "\n\n"
    return material_plastic

def sensor_file(positions, normals):
    """
    This function writes the sensor points and their normals for the Radiance/Daysim simulation.
 
    Parameters
    ----------
    positions: pyptlist
        List of positions for sensing. Pyptlist is a list of tuples of floats. A pypt is a tuple that documents the xyz coordinates of a 
        pt e.g. (x,y,z), thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]

    normals: pyveclist
        List of normals of the points sensing. Pyveclist is a list of tuples of floats. A pyvec is a tuple that documents the xyz coordinates of a 
        direction e.g. (x,y,z), thus a pyveclist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    Returns
    -------
    rad sensors :  str
        The sensors written into radiance readable string.
    """
        
    if not positions or not normals:
        raise Exception
    if len(positions) != len(normals):
        raise Exception
    sensors = ""
    for i in range(len(positions)):
        pos = positions[i]
        nor = normals[i]
        sensors = sensors + str(pos[0]) + " " + str(pos[1]) + " " + str(pos[2]) + " " + str(nor[0]) + " " + str(nor[1]) + " " + str(nor[2]) + "\n"
    return sensors 