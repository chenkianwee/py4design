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
import uuid
import datetime

from lxml.etree import Element, SubElement

class XMLNamespaces:
    """
    Contains all the XML namespaces of the CityGML schema.        
    """
    citygml = "http://www.opengis.net/citygml/1.0"
    core = "http://www.opengis.net/citygml/base/1.0"
    xsi = "http://www.w3.org/2001/XMLSchema-instance"
    trans="http://www.opengis.net/citygml/transportation/1.0"
    wtr = "http://www.opengis.net/citygml/waterbody/1.0"
    gml = "http://www.opengis.net/gml"
    smil20lang = "http://www.w3.org/2001/SMIL20/Language"
    xlink = "http://www.w3.org/1999/xlink"
    grp = "http://www.opengis.net/citygml/cityobjectgroup/1.0"
    luse = "http://www.opengis.net/citygml/landuse/1.0"
    frn="http://www.opengis.net/citygml/cityfurniture/1.0"
    app="http://www.opengis.net/citygml/appearance/1.0"
    tex="http://www.opengis.net/citygml/texturedsurface/1.0"
    smil20="http://www.w3.org/2001/SMIL20/"
    xAL="urn:oasis:names:tc:ciq:xsdschema:xAL:2.0"
    bldg="http://www.opengis.net/citygml/building/1.0"
    dem="http://www.opengis.net/citygml/relief/1.0"
    veg="http://www.opengis.net/citygml/vegetation/1.0"
    gen="http://www.opengis.net/citygml/generics/1.0"

def write_root():
    """
    This function writes the root node of a CityGML model.
        
    Returns
    -------
    root node : lxml Element
        The root node of a CityGML file.
    """
    schemaLocation="http://www.opengis.net/citygml/landuse/1.0\
    http://schemas.opengis.net/citygml/landuse/1.0/landUse.xsd http://www.opengis.net/citygml/cityfurniture/1.0\
    http://schemas.opengis.net/citygml/cityfurniture/1.0/cityFurniture.xsd http://www.opengis.net/citygml/appearance/1.0\
    http://schemas.opengis.net/citygml/appearance/1.0/appearance.xsd http://www.opengis.net/citygml/texturedsurface/1.0\
    http://schemas.opengis.net/citygml/texturedsurface/1.0/texturedSurface.xsd http://www.opengis.net/citygml/transportation/1.0\
    http://schemas.opengis.net/citygml/transportation/1.0/transportation.xsd http://www.opengis.net/citygml/waterbody/1.0\
    http://schemas.opengis.net/citygml/waterbody/1.0/waterBody.xsd http://www.opengis.net/citygml/building/1.0\
    http://schemas.opengis.net/citygml/building/1.0/building.xsd http://www.opengis.net/citygml/relief/1.0\
    http://schemas.opengis.net/citygml/relief/1.0/relief.xsd http://www.opengis.net/citygml/vegetation/1.0\
    http://schemas.opengis.net/citygml/vegetation/1.0/vegetation.xsd http://www.opengis.net/citygml/cityobjectgroup/1.0\
    http://schemas.opengis.net/citygml/cityobjectgroup/1.0/cityObjectGroup.xsd http://www.opengis.net/citygml/generics/1.0\
    http://schemas.opengis.net/citygml/generics/1.0/generics.xsd"
   
    root = Element("CityModel",
                   attrib={"{" + XMLNamespaces.xsi + "}schemaLocation" : schemaLocation},
                   nsmap={None:"http://www.opengis.net/citygml/1.0",
                          'core': XMLNamespaces.core,
                          'xsi':XMLNamespaces.xsi,
                          'trans':XMLNamespaces.trans,
                          'wtr': XMLNamespaces.wtr,
                          'gml': XMLNamespaces.gml,
                          'smil20lang': XMLNamespaces.smil20lang,
                          'xlink': XMLNamespaces.xlink,
                          'grp': XMLNamespaces.grp,
                          'luse': XMLNamespaces.luse,
                          'frn': XMLNamespaces.frn,
                          'app': XMLNamespaces.app,
                          'tex': XMLNamespaces.tex,
                          'smil20': XMLNamespaces.smil20,
                          'xAL': XMLNamespaces.xAL,
                          'bldg': XMLNamespaces.bldg,
                          'dem': XMLNamespaces.dem,
                          'veg': XMLNamespaces.veg,
                          'gen': XMLNamespaces.gen})
    return root

def write_boundedby(parent_node, epsg, lower_bound, upper_bound):
    """
    This function writes the boundedby node of a CityGML model.
 
    Parameters
    ----------
    parent_node : lxml Element
        The parent node of the boundedby node.
        
    epsg : str
        The epsg of the coordinate system.
    
    lower_bound : tuple of floats
            A tuple of floats that is specifying the xyz coordinate of the lower bound.
            
    upper_bound : tuple of floats
        A tuple of floats that is specifying the xyz coordinate of the upper bound.
    """
    gml_boundedBy = SubElement(parent_node, "{" + XMLNamespaces.gml+ "}" + 'boundedBy')
    #TO DO: implement geometry operattions to find the boundary
    gml_Envelope = SubElement(gml_boundedBy, "{" + XMLNamespaces.gml+ "}" + 'Envelope')
    gml_Envelope.attrib['srsDimension'] = '3'
    gml_Envelope.attrib['srsName'] = epsg
    gml_lowerCorner = SubElement(gml_Envelope, "{" + XMLNamespaces.gml+ "}" + 'lowerCorner')
    gml_lowerCorner.attrib['srsDimension'] = '3'
    gml_lowerCorner.text = str(lower_bound[0]) + " " +  str(lower_bound[1]) + " " + str(lower_bound[2]) 
    gml_upperCorner = SubElement(gml_Envelope, "{" + XMLNamespaces.gml+ "}" + 'upperCorner')
    gml_upperCorner.attrib['srsDimension'] = '3'
    gml_upperCorner.text = str(upper_bound[0]) + " " + str(upper_bound[1]) + " " + str(upper_bound[2]) 
   

def write_gen_attribute(parent_node, generic_attrib_dict):
    """
    This function writes generic attributes for a cityobject member.
 
    Parameters
    ----------
    parent_node : lxml Element
        The parent node of the generic attributes node, usually a cityobject member.
        
    generic_attrib_dict : dictionary, optional
            Extra attributes to be appended to the object.
            The dictionary must have a string key which will be the name of the generic attributes, and either an int, float or str value.
            
    """
    for name in generic_attrib_dict:
        attrib = generic_attrib_dict[name]
        if type(attrib) == int: 
            gen_intAttribute = SubElement(parent_node, "{" + XMLNamespaces.gen + "}" +'intAttribute')
            gen_intAttribute.attrib['name'] = name
            gen_value = SubElement(gen_intAttribute, "{" + XMLNamespaces.gen + "}" +'value')
            gen_value.text = str(attrib)
  
        if type(attrib) == float:
            gen_doubleAttribute = SubElement(parent_node, "{" + XMLNamespaces.gen + "}" +'doubleAttribute')
            gen_doubleAttribute.attrib['name'] = name
            gen_value = SubElement(gen_doubleAttribute, "{" + XMLNamespaces.gen + "}" +'value')
            gen_value.text = str(attrib)
     
        if type(attrib) == str:
            gen_stringAttribute = SubElement(parent_node, "{" + XMLNamespaces.gen + "}" +'stringAttribute')
            gen_stringAttribute.attrib['name'] = name
            gen_value = SubElement(gen_stringAttribute, "{" + XMLNamespaces.gen + "}" +'value')
            gen_value.text = str(attrib)

def write_landuse(lod, name, geometry_list, function = None, generic_attrib_dict = None):
    """
    This function writes the landuse cityobject member. Currently, only works for lod1.
 
    Parameters
    ----------
    lod : str
        The level of detail of the geometry of the landuse. The string should be in this form: "lod1". 
        
    name : str
        The name of the landuse.
        
    geometry_list : list of SurfaceMember
        The geometry of the landuse.
    
    function : str, optional
        The function of the landuse in gml code, e.g. for residential specify "1010", Default = None. Refer to CityGML 
        documentation for more information. https://www.citygml.org/
        
    generic_attrib_dict : dictionary, optional
        Extra attributes to be appended to the object, Default = None.
        The dictionary must have a string key which will be the name of the generic attributes, and either an int, float or str value.
            
    """
    cityObjectMember = Element('cityObjectMember')

    luse = SubElement(cityObjectMember, "{" + XMLNamespaces.luse+ "}" +'LandUse')
    # luse.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = name

    gml_name = SubElement(luse, "{" + XMLNamespaces.gml+ "}" + 'name')
    gml_name.text = name
   
    #=======================================================================================================
    #attribs
    #=======================================================================================================
    if function != None:
        luse_function = SubElement(luse, "{" + XMLNamespaces.luse+ "}" +'function')
        luse_function.text = function
       
    if generic_attrib_dict != None:
        write_gen_attribute(luse, generic_attrib_dict)

    #=======================================================================================================
    #geometries
    #=======================================================================================================
    if lod == "lod1":
        luse_lod1MultiSurface = SubElement(luse, "{" + XMLNamespaces.luse+ "}" + 'lod1MultiSurface')

        gml_MultiSurface = SubElement(luse_lod1MultiSurface, "{" + XMLNamespaces.gml+ "}" + 'MultiSurface')
        gml_MultiSurface.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = 'UUID_' + str(uuid.uuid1())

        for geometry in geometry_list:
            gml_MultiSurface.append(geometry.construct())
      
    return cityObjectMember
   
def write_tin_relief(lod, name, geometry_list):
    """
    This function writes the TIN relief cityobject member. Currently, only works for lod1.
 
    Parameters
    ----------
    lod : str
        The level of detail of the geometry of the tin relief. The string should be in this form: "lod1". 
        
    name : str
        The name of the relief feature.
        
    geometry_list : list of Triangle
        The geometry of the tin relief.
    """
    cityObjectMember = Element('cityObjectMember')
    
    relief_feature = SubElement(cityObjectMember, "{" + XMLNamespaces.dem+ "}" +'ReliefFeature')
    relief_feature.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = name
    
    gml_name = SubElement(relief_feature, "{" + XMLNamespaces.gml+ "}" + 'name')
    gml_name.text = name
    
    #=======================================================================================================
    #geometries
    #=======================================================================================================
    if lod == "lod1":
        dem_lod = SubElement(relief_feature, "{" + XMLNamespaces.dem+ "}" + 'lod')
        dem_lod.text = "1"
        dem_reliefComponent = SubElement(relief_feature, "{" + XMLNamespaces.dem+ "}" + 'reliefComponent')
        
        dem_TINRelief = SubElement(dem_reliefComponent, "{" + XMLNamespaces.dem+ "}" + 'TINRelief')
        dem_TINRelief.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = name+"dem"
        
        gml_name = SubElement(dem_TINRelief, "{" + XMLNamespaces.gml+ "}" + 'name')
        gml_name.text = "ground"
        dem_lod = SubElement(dem_TINRelief, "{" + XMLNamespaces.dem+ "}" + 'lod')
        dem_lod.text = "1"
        dem_tin =  SubElement(dem_TINRelief, "{" + XMLNamespaces.dem+ "}" + 'tin')
        
        gml_TriangulatedSurface = SubElement(dem_tin, "{" + XMLNamespaces.gml+ "}" + 'TriangulatedSurface')
        
        gml_trianglePatches = SubElement(gml_TriangulatedSurface, "{" + XMLNamespaces.gml+ "}" + 'trianglePatches')
        
        for geometry in geometry_list:
            gml_trianglePatches.append(geometry.construct())
            
    return cityObjectMember
   
   
def write_transportation(trpt_type, lod, name, geometry_list, rd_class = None, function = None, generic_attrib_dict= None):
    """
    This function writes the transportation cityobject member. Transportation object includes road, railway, track and square.
    Currently only works for lod0 transportation network.
 
    Parameters
    ----------
    trpt_type : str
        The transportation type. The options are: "Road", "Railway", "Track", "Square".
        
    lod : str
        The level of detail of the geometry of the transportation. The string should be in this form: "lod0". 
        
    name : str
        The name of the transportation object.
        
    geometry_list : list of Linestring
        The geometry of the landuse.
    
    rd_class : str, optional
        The class of the transportation gml code, e.g. for road specify "1000", Default = None. Refer to CityGML 
        documentation for more information. https://www.citygml.org/
        
    function : str, optional
        The function of the transportation gml code, e.g. for road specify "1000", Default = None. Refer to CityGML 
        documentation for more information. https://www.citygml.org/
        
    generic_attrib_dict : dictionary, optional
        Extra attributes to be appended to the object, Default = None.
        The dictionary must have a string key which will be the name of the generic attributes, and either an int, float or str value.
    """
    cityObjectMember = Element('cityObjectMember')
    tran_trpt_type = SubElement(cityObjectMember, "{" + XMLNamespaces.trans+ "}" + trpt_type)
    # tran_trpt_type.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = name
    
    gml_name = SubElement(tran_trpt_type, "{" + XMLNamespaces.gml+ "}" + 'name')
    gml_name.text = name
    
    #=======================================================================================================
    #attrib
    #=======================================================================================================
    if rd_class !=None:
        tran_class = SubElement(tran_trpt_type,"{" + XMLNamespaces.trans+ "}" + 'class')
        tran_class.text = rd_class
    if function != None:
        tran_function = SubElement(tran_trpt_type,"{" + XMLNamespaces.trans+ "}" + 'function')
        tran_function.text = function
    if generic_attrib_dict != None:
        write_gen_attribute(tran_trpt_type, generic_attrib_dict)
       
    #=======================================================================================================
    #geometries
    #=======================================================================================================
    if lod == "lod0":
        tran_lod0Network = SubElement(tran_trpt_type, "{" + XMLNamespaces.trans+ "}" + 'lod0Network')
        gml_GeometricComplex = SubElement(tran_lod0Network, "{" + XMLNamespaces.gml+ "}" + 'GeometricComplex')
        
        for geometry in geometry_list:
            gml_element = SubElement(gml_GeometricComplex, "{" + XMLNamespaces.gml+ "}" + 'element')
            gml_element.append(geometry.construct())
            gml_GeometricComplex.append(gml_element)
    
    if lod == 'lod1':
        tran_lod1MultiSurface = SubElement(tran_trpt_type, "{" + XMLNamespaces.trans+ "}" + 'lod1MultiSurface')
        gml_MultiSurface = SubElement(tran_lod1MultiSurface, "{" + XMLNamespaces.gml+ "}" + 'MultiSurface')
        gml_MultiSurface.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = 'UUID_' + str(uuid.uuid1())

        for geometry in geometry_list:
            gml_MultiSurface.append(geometry.construct())
        
    return cityObjectMember

def write_building(lod, name, geometry_list, bldg_class = None,function = None, usage = None,
                   yr_constr  = None, rooftype = None,height = None,stry_abv_grd = None, 
                   stry_blw_grd = None, generic_attrib_dict=None ):
    """
    This function writes the building cityobject member. Currently, only works for lod1 building.
     
    Parameters
    ----------
    lod : str
        The level of detail of the geometry of the building. The string should be in this form: "lod1". 
        
    name : str
        The name of the building.
        
    geometry_list : list of SurfaceMember
        The geometry of the building.
    
    bldg_class : str, optional
        The building class of the building in gml code e.g. for habitation specify "1000", Default = None. Refer to CityGML 
        documentation for more information. https://www.citygml.org/
        
    function : str, optional
        The function of the building in gml code e.g. for residential specify "1000", Default = None. Refer to CityGML 
        documentation for more information. https://www.citygml.org/
        
    usage : str, optional
        The usage of the building in gml code e.g. for residential specify "1000", Default = None. Refer to CityGML 
        documentation for more information. https://www.citygml.org/
        
    yr_constr : str, optional
        The year the building is constructed e.g. "2017", Default = None.
        
    rooftype : str, optional
        The rooftype of the building in gml code e.g. for flat roof specify "1000", Default = None. Refer to CityGML 
        documentation for more information. https://www.citygml.org/
        
    height : str, optional
        The height of the building, e.g. "48", Default = None.
        
    stry_abv_grd : str, optional
        The number of storey of the building above ground, e.g. "12", Default = None.
        
    stry_blw_grd : str, optional
        The number of storey of the building below ground, e.g. "2", Default = None.
        
    generic_attrib_dict : dictionary, optional
        Extra attributes to be appended to the object, Default = None.
        The dictionary must have a string key which will be the name of the generic attributes, and either an int, float or str value.
    """
    cityObjectMember = Element('cityObjectMember')
    bldg_Building = SubElement(cityObjectMember, "{" + XMLNamespaces.bldg + "}" + "Building")
    # bldg_Building.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = id  
    #=======================================================================================================
    #attrib
    #=======================================================================================================
    
    b_name = SubElement(bldg_Building,"{" + XMLNamespaces.gml+ "}" + 'name')
    b_name.text = name
        
    if bldg_class != None:
        b_class = SubElement(bldg_Building,"{" + XMLNamespaces.bldg+ "}" + 'class')
        b_class.text = bldg_class
        
    if function!=None:
        bldg_function = SubElement(bldg_Building,"{" + XMLNamespaces.bldg+ "}" + 'function')
        bldg_function.text = function
        
    if usage != None:
        bldg_usage = SubElement(bldg_Building,"{" + XMLNamespaces.bldg+ "}" + 'usage')
        bldg_usage.text = usage
        
    if yr_constr != None:
        bldg_yearOfConstruction = SubElement(bldg_Building,"{" + XMLNamespaces.bldg+ "}" + 'yearOfConstruction')
        bldg_yearOfConstruction.text = yr_constr
        
    if rooftype != None:
        bldg_roofType = SubElement(bldg_Building,"{" + XMLNamespaces.bldg+ "}" + 'roofType')
        bldg_roofType.text = rooftype
        
    if height!=None:
        bldg_measuredHeight = SubElement(bldg_Building,"{" + XMLNamespaces.bldg+ "}" + 'measuredHeight')
        bldg_measuredHeight.attrib['uom'] = "m"
        bldg_measuredHeight.text = height
        
    if stry_abv_grd != None:
        bldg_storeysAboveGround = SubElement(bldg_Building,"{" + XMLNamespaces.bldg+ "}" + 'storeysAboveGround')
        bldg_storeysAboveGround.text = stry_abv_grd
        
    if stry_blw_grd != None:
        bldg_storeysBelowGround = SubElement(bldg_Building,"{" + XMLNamespaces.bldg+ "}" + 'storeysBelowGround')
        bldg_storeysBelowGround.text = stry_blw_grd
       
    if generic_attrib_dict != None:
        write_gen_attribute(bldg_Building, generic_attrib_dict)
   
    #=======================================================================================================
    #geometries
    #=======================================================================================================
    if lod == "lod1":
        bldg_lod1Solid = SubElement(bldg_Building, "{" + XMLNamespaces.bldg+ "}" + 'lod1Solid')
        gml_Solid = SubElement(bldg_lod1Solid, "{" + XMLNamespaces.gml+ "}" + 'Solid')
        gml_exterior = SubElement(gml_Solid, "{" + XMLNamespaces.gml+ "}" + 'exterior')
        gml_CompositeSurface = SubElement(gml_exterior, "{" + XMLNamespaces.gml+ "}" + 'CompositeSurface')
        for geometry in geometry_list:
            gml_CompositeSurface.append(geometry.construct())
   
    return cityObjectMember

def write_cityfurniture(lod, name, geometry_list, furn_class = None,function = None, 
                        generic_attrib_dict = None ):
    """
    This function writes the city furniture cityobjectmemeber. Currently, only works for lod1.
 
    Parameters
    ----------
    lod : str
        The level of detail of the geometry of the furniture. The string should be in this form: "lod1". 
        
    name : str
        The name of the furniture.
        
    geometry_list : list of SurfaceMember
        The geometry of the furniture.
    
    furn_class : str, optional
        The furniture class of the city furniture in gml code, for traffic specify "1000", Default = None. Refer to CityGML 
        documentation for more information. https://www.citygml.org/
        
    function : str, optional
        The function of the city furniture in gml code, for bus stop specify "1110",Default = None. Refer to CityGML 
        documentation for more information. https://www.citygml.org/
        
    generic_attrib_dict : dictionary, optional
        Extra attributes to be appended to the object, Default = None.
        The dictionary must have a string key which will be the name of the generic attributes, and either an int, float or str value.
    """
    cityObjectMember = Element('cityObjectMember')
    frn_CityFurniture = SubElement(cityObjectMember,"{" + XMLNamespaces.frn+ "}" + 'CityFurniture')
    frn_CityFurniture.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = name
    
    creationDate = SubElement(frn_CityFurniture, 'creationDate')
    creationDate.text = str(datetime.datetime.now())
    
    #=======================================================================================================
    #attrib
    #=======================================================================================================
    if furn_class !=None:
        frn_class = SubElement(frn_CityFurniture,"{" + XMLNamespaces.frn+ "}" + 'class')
        frn_class.text = furn_class
    if function != None:
        frn_function = SubElement(frn_CityFurniture,"{" + XMLNamespaces.frn+ "}" + 'function')
        frn_function.text = function
    if generic_attrib_dict != None:
        write_gen_attribute(frn_CityFurniture, generic_attrib_dict)
   
    #=======================================================================================================
    #geometries
    #=======================================================================================================
    if lod == "lod1":
        lod1Geometry = SubElement(frn_CityFurniture, "{" + XMLNamespaces.frn+ "}" + 'lod1Geometry')
        gml_Solid = SubElement(lod1Geometry, "{" + XMLNamespaces.gml+ "}" + 'Solid')
        gml_exterior = SubElement(gml_Solid, "{" + XMLNamespaces.gml+ "}" + 'exterior')
        gml_CompositeSurface = SubElement(gml_exterior, "{" + XMLNamespaces.gml+ "}" + 'CompositeSurface')
        for geometry in geometry_list:
            gml_CompositeSurface.append(geometry.construct())

    '''
    #==================================================================
    #reference geometries script TODO: Make it work 
    #==================================================================
    frn_lod1ImplicitRepresentation = SubElement(frn_CityFurniture,"{" + XMLNamespaces.frn+ "}" + 'lod1ImplicitRepresentation')
    ImplicitGeometry = SubElement(frn_lod1ImplicitRepresentation,'ImplicitGeometry')
    mimeType = SubElement(ImplicitGeometry,'mimeType')
    mimeType.text = geometry_type
    libraryObject = SubElement(ImplicitGeometry,'libraryObject')
    libraryObject.text = ref_geometry
    referencePoint = SubElement(ImplicitGeometry,'referencePoint')
    referencePoint.append(ref_pt.construct())
    '''
    return cityObjectMember

def write_tree(lod, name, geometry_list=None, tree_class = None, tree_species = None,
               function = None,tree_height = None, trunk_diameter = None, 
               crown_diameter=None, generic_attrib_dict = None, implicit_geom = None,
               trsf_matrix = None, ref_pt = None):
    
    """
    This function writes the city vegetaton cityobjectmemeber. Currently, only works for lod1.
 
    Parameters
    ----------
    lod : str
        The level of detail of the geometry of the tree. The string should be in this form: "lod1". 
        
    name : str
        The name of the tree.
        
    geometry_list : list of SurfaceMember, optional
        The geometry of the tree, default=None.
    
    tree_class : str, optional
        The class of the tree in gml code, Default = None. Refer to CityGML 
        documentation for more information. https://www.citygml.org/
        
    tree_species : str, optional
        The species of the tree in gml code, Default = None. Refer to CityGML 
        documentation for more information. https://www.citygml.org/
        
    function : str, optional
        The function of the tree in gml code, Default = None. Refer to CityGML 
        documentation for more information. https://www.citygml.org/
    
    tree_height : float, optional
        The height of the tree, Default = None.
        
    trunk_diameter : float, optional
        The diatmeter of the tree trunk, Default = None.
    
    crown_diameter : float, optional
        The diameter of the tree crown, Default = None..
        
    generic_attrib_dict : dictionary, optional
        Extra attributes to be appended to the object, Default = None.
        The dictionary must have a string key which will be the name of the generic attributes, and either an int, float or str value.
    
    implicit_geom : str or lxml element, optional
        The id of the implicit geom, Default = None. If true the geometry is referenced.
        if a str of the gml id is given, will just reference the id. If the lxml element is given, will write the geom.
        
    trsf_matrix : 2d list, optional
        The transformation matrix 4x4, Default = None.
        
    ref_pt : pypt, optional
        the reference point, Default = None.
    """
    
    cityObjectMember = Element('cityObjectMember')
    veg_svo = SubElement(cityObjectMember,"{" + XMLNamespaces.veg+ "}" + 'SolitaryVegetationObject')
    # veg_svo.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = name
    
    t_name = SubElement(veg_svo,"{" + XMLNamespaces.gml+ "}" + 'name')
    t_name.text = name
    
    #=======================================================================================================
    #attrib
    #=======================================================================================================
    if tree_class !=None:
        svo_class = SubElement(veg_svo,"{" + XMLNamespaces.veg+ "}" + 'class')
        svo_class.text = tree_class
        
    if tree_species !=None:
        svo_species = SubElement(veg_svo,"{" + XMLNamespaces.veg+ "}" + 'species')
        svo_species.text = tree_species
    
    if function !=None:
        svo_function = SubElement(veg_svo,"{" + XMLNamespaces.veg+ "}" + 'function')
        svo_function.text = function
        
    if tree_height !=None:
        svo_height = SubElement(veg_svo,"{" + XMLNamespaces.veg+ "}" + 'height')
        svo_height.attrib['uom'] = "m"
        svo_height.text = str(tree_height)
        
    if trunk_diameter !=None:
        svo_tdia = SubElement(veg_svo,"{" + XMLNamespaces.veg+ "}" + 'trunkDiameter')
        svo_tdia.attrib['uom'] = "m"
        svo_tdia.text = str(trunk_diameter)
        
    if crown_diameter !=None:
        svo_cdia = SubElement(veg_svo,"{" + XMLNamespaces.veg+ "}" + 'crownDiameter')
        svo_cdia.attrib['uom'] = "m"
        svo_cdia.text = str(crown_diameter)
        
    if generic_attrib_dict != None:
        write_gen_attribute(veg_svo, generic_attrib_dict)
   
    #=======================================================================================================
    #geometries
    #=======================================================================================================
    if lod == "lod1" and implicit_geom == None:
        lod1Geometry = SubElement(veg_svo, "{" + XMLNamespaces.veg+ "}" + 'lod1Geometry')
        gml_MultiSurface = SubElement(lod1Geometry, "{" + XMLNamespaces.gml+ "}" + 'MultiSurface')
        gml_MultiSurface.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = 'UUID_' + str(uuid.uuid1())
        for geometry in geometry_list:
            gml_MultiSurface.append(geometry.construct())
    
    elif lod == "lod1" and implicit_geom != None:
        lod1impgeo = SubElement(veg_svo, "{" + XMLNamespaces.veg+ "}" + 'lod1ImplicitRepresentation')
        impgeo = SubElement(lod1impgeo, 'ImplicitGeometry')
        trsf_mat = SubElement(impgeo, 'transformationMatrix')
        trsf_matrix = pytrsf_mat2str_mat(trsf_matrix)
        trsf_mat.text = trsf_matrix
        
        if type(implicit_geom) == str: 
            rel_geom = SubElement(impgeo, 'relativeGMLGeometry')
            rel_geom.attrib["{" + XMLNamespaces.xlink+ "}" +'href'] = implicit_geom
            
        else:
            rel_geom = SubElement(impgeo, 'relativeGMLGeometry')
            rel_geom.append(implicit_geom)
        
        rpt = SubElement(impgeo, 'referencePoint')
        gml_pt = write_pt(ref_pt)
        rpt.append(gml_pt)
        
    return cityObjectMember
        
def pytrsf_mat2str_mat(pytrsf):
    """
    Converts the pytrsf into text form for CityGML.
 
    Parameters
    ----------
    pytrsf : 2d list
        The transformation matrix 4x4.
        
    Returns
    -------
    str_mat : str
        The pytrsf converted into string form.
    """
    s_trsf = []
    for m in pytrsf:    
        str_m = list(map(str, m))
        s_trsf.append(str_m)
        
    str_mat = s_trsf[0][0]+' '+s_trsf[0][1]+' '+s_trsf[0][2]+' '+s_trsf[0][3]+' '+\
              s_trsf[1][0]+' '+s_trsf[1][1]+' '+s_trsf[1][2]+' '+s_trsf[1][3]+' '+\
              s_trsf[2][0]+' '+s_trsf[2][1]+' '+s_trsf[2][2]+' '+s_trsf[2][3]+' '+\
              s_trsf[3][0]+' '+s_trsf[3][1]+' '+s_trsf[3][2]+' '+s_trsf[3][3]
    
    return str_mat 

def write_gml_multisrf(geometry_list, unique_id = None):
    """
    Writes a geometry list to GML multisurfaces.
 
    Parameters
    ----------
    geometry_list : list of lxml surfaces
        List of lxml surfaces to be written.
        
    Returns
    -------
    multisurface : instance of the 
        multisurface etree element.
        
    """
    gml_MultiSurface = Element("{" + XMLNamespaces.gml+ "}" + 'MultiSurface')
    if unique_id != None:
        gml_MultiSurface.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = unique_id
    else:
        gml_MultiSurface.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = 'UUID_' + str(uuid.uuid1())
        
    for geometry in geometry_list:
        gml_MultiSurface.append(geometry.construct())
    return gml_MultiSurface
            
def pos_list2text(pyptlist):
    """
    This function converts the pyptlist into text form for CityGML.
 
    Parameters
    ----------
    pyptlist : a list of tuples
        List of points to be converted. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    Returns
    -------
    converted list of points : str
        The pyptlist converted into string form.
    """
    pos_text = ""
    num_pos = len(pyptlist)
    pos_cnt = 0
    for pos in pyptlist:
        if pos_cnt == num_pos-1:
            pos_text = pos_text + str(pos[0]) + " " + str(pos[1]) + " " + str(pos[2])
        else:
            pos_text = pos_text + str(pos[0]) + " " + str(pos[1]) + " " + str(pos[2]) + " "
        pos_cnt += 1

    return pos_text

def write_surface_member(pyptlist, holes = None):
    """
    This function writes a GML surface member.
 
    Parameters
    ----------
    pyptlist : a list of tuples
        List of points to be converted. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    Returns
    -------
    surface member : lxml Element
        The lxml surface member.
    """
    gml_surfaceMember = Element("{" + XMLNamespaces.gml+ "}" + 'surfaceMember')
    gml_Polygon = SubElement(gml_surfaceMember,"{" + XMLNamespaces.gml+ "}" + 'Polygon')
    gml_Polygon.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = 'UUID_' + str(uuid.uuid1())

    gml_exterior = SubElement(gml_Polygon, "{" + XMLNamespaces.gml+ "}" + 'exterior')
    
    gml_LinearRing = SubElement(gml_exterior, "{" + XMLNamespaces.gml+ "}" + 'LinearRing')
    gml_LinearRing.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = 'UUID_' + str(uuid.uuid1())

    gml_posList = SubElement(gml_LinearRing, "{" + XMLNamespaces.gml+ "}" + 'posList')
    gml_posList.attrib['srsDimension'] = '3'
    gml_posList.text = pos_list2text(pyptlist)
    
    if holes !=None:
        for hole in holes:
            gml_interior = SubElement(gml_Polygon, "{" + XMLNamespaces.gml+ "}" + 'interior')
    
            gml_LinearRing = SubElement(gml_interior, "{" + XMLNamespaces.gml+ "}" + 'LinearRing')
            gml_LinearRing.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = 'UUID_' + str(uuid.uuid1())

            gml_posList = SubElement(gml_LinearRing, "{" + XMLNamespaces.gml+ "}" + 'posList')
            gml_posList.attrib['srsDimension'] = '3'
    
            gml_posList.text = pos_list2text(hole)

    return gml_surfaceMember
    
def write_triangle(pyptlist):
    """
    This function writes a GML triangle member.
 
    Parameters
    ----------
    pyptlist : a list of tuples
        List of points to be converted. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    Returns
    -------
    triangle member : lxml Element
        The lxml triangle member.
    """
    gml_Triangle = Element("{" + XMLNamespaces.gml+ "}" + 'Triangle')
    #gml_Triangle.attrib["{" + write_gml.XMLNamespaces.gml+ "}" +'id'] = 'UUID_' + str(uuid.uuid1())
    gml_exterior = SubElement(gml_Triangle, "{" + XMLNamespaces.gml+ "}" + 'exterior')

    gml_LinearRing = SubElement(gml_exterior, "{" + XMLNamespaces.gml+ "}" + 'LinearRing')
    gml_LinearRing.attrib["{" + XMLNamespaces.gml+ "}" +'id'] = 'UUID_' + str(uuid.uuid1())

    gml_posList = SubElement(gml_LinearRing, "{" + XMLNamespaces.gml+ "}" + 'posList')
    gml_posList.attrib['srsDimension'] = '3'
    
    gml_posList.text = pos_list2text(pyptlist)

    return gml_Triangle

def write_linestring(pyptlist):
    """
    This function writes a GML linestring member.
 
    Parameters
    ----------
    pyptlist : a list of tuples
        List of points to be converted. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    Returns
    -------
    linestring member : lxml Element
        The lxml linestring member.
    """
    gml_LineString = Element("{" + XMLNamespaces.gml+ "}" + 'LineString')
    gml_posList = SubElement(gml_LineString, "{" + XMLNamespaces.gml+ "}" + 'posList')
    gml_posList.attrib['srsDimension'] = '3'
    gml_posList.text = pos_list2text(pyptlist)
    return gml_LineString

def write_pt(pypt):
    """
    This function writes a GML point member.
 
    Parameters
    ----------
    pypt : tuple of floats
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z).
        
    Returns
    -------
    point member : lxml Element
        The lxml point member.
    """
    gml_Point = Element("{" + XMLNamespaces.gml+ "}" + 'Point')
    gml_pos = SubElement(gml_Point,"{" + XMLNamespaces.gml+ "}" + 'pos')
    gml_pos.attrib['srsDimension'] = "3"
    gml_pos.text = str(pypt[0]) + " " + str(pypt[1]) + " " + str(pypt[2])
    return gml_Point