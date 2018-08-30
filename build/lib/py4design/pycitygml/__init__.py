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

from lxml import etree
from lxml.etree import ElementTree, Element

import write_gml

class Writer(object):
    """
    lxml.etree Element object that contains the CityGML information. Currently all methods only work with lod1 CityGML models.

    ...

    Attributes
    ----------
    citymodel_node :  lxml.etree Element
        The Element class that contains all the CityGML information.
    """
    def __init__(self):
        """
        This function creates a lxml.etree Element.           
        """
        self.citymodel_node = write_gml.write_root()
        
    def create_cityobjectmember(self):
        """
        This function creates a cityObjectMember.           
        """
        cityObjectMember = Element('cityObjectMember')
        return cityObjectMember
            
    def add_landuse(self, lod, name, geometry_list, function = None, generic_attrib_dict = None):
        """
        This function adds a landuse object into the CityGML model. Currently, only works for lod1 landuse.
     
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
        landuse = write_gml.write_landuse(lod, name, geometry_list, function = function, generic_attrib_dict = generic_attrib_dict)
        self.citymodel_node.append(landuse)

    def add_transportation(self, trpt_type, lod, name, geometry_list, rd_class = None, function = None, generic_attrib_dict= None):
        """
        This function adds a transportation object into the CityGML model. Transportation object includes road, railway, track and square.
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
        transportation = write_gml.write_transportation(trpt_type, lod, name, geometry_list, rd_class = rd_class, function = function, generic_attrib_dict= generic_attrib_dict)
        self.citymodel_node.append(transportation)

    def add_building(self, lod, name, geometry_list, bldg_class = None,function = None, usage = None,yr_constr  = None,
                   rooftype = None,height = None,stry_abv_grd = None, stry_blw_grd = None, generic_attrib_dict=None ):
        """
        This function adds a building object into the CityGML model. Currently, only works for lod1 building.
     
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
        
        bldg = write_gml.write_building(lod, name, geometry_list, bldg_class = bldg_class ,function = function ,
                                        usage = usage, yr_constr = yr_constr, rooftype = rooftype , height= height ,
                                        stry_abv_grd = stry_abv_grd, stry_blw_grd = stry_blw_grd, 
                                        generic_attrib_dict = generic_attrib_dict )
        
        self.citymodel_node.append(bldg)
        
    def add_cityfurniture(self,lod, name, geometry_list, furn_class = None,function = None, generic_attrib_dict = None):
        """
        This function adds a city furniture object into the CityGML model. Currently, only works for lod1.
     
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
        city_frn = write_gml.write_cityfurniture(lod, name, geometry_list, furn_class = furn_class,function = function, generic_attrib_dict = generic_attrib_dict)
        self.citymodel_node.append(city_frn)
        
    def add_tin_relief(self, lod, name, geometry_list):
        """
        This function adds a TIN relief object into the CityGML model. Currently, only works for lod1.
     
        Parameters
        ----------
        lod : str
            The level of detail of the geometry of the tin relief. The string should be in this form: "lod1". 
            
        name : str
            The name of the relief feature.
            
        geometry_list : list of Triangle
            The geometry of the relief.
        """
        tin_relief = write_gml.write_tin_relief(lod,name,geometry_list)
        self.citymodel_node.append(tin_relief)
        
    def add_bounded_by(self, epsg, lower_bound, upper_bound):
        """
        This function adds a bounded by object into the CityGML model.
     
        Parameters
        ----------
        epsg : str
            The epsg of the coordinate system.
            
        lower_bound : tuple of floats
            A tuple of floats that is specifying the xyz coordinate of the lower bound.
            
        upper_bound : tuple of floats
            A tuple of floats that is specifying the xyz coordinate of the upper bound.
        """
        write_gml.write_boundedby(self.citymodel_node, epsg, lower_bound, upper_bound)

    def write2string(self):
        """
        This function prints all the information into a string.           
        """
        print etree.tostring(self.citymodel_node, pretty_print=True)
        
    def write(self, filepath):
        """
        This function writes all the information into a CityGML file.
     
        Parameters
        ----------
        filepath : str
            The file path of the CityGML file.
        """
        outFile = open(filepath, 'w')
        ElementTree(self.citymodel_node).write(outFile,pretty_print = True, xml_declaration = True, encoding="UTF-8", standalone="yes")
        outFile.close()

class Reader(object):
    """
    Reads a CityGML file and stores it in a lxml.etree Element object that contains the CityGML information.

    ...

    Attributes
    ----------
    citymodel_node :  lxml.etree Element
        The Element class that contains all the CityGML information.
        
    cityobjectmembers : list of lxml.etree Element
        A list of Element class of all the cityobjectmembers in the CityGML file.
        
    namespaces : dictionary of XMLNamespaces from write_gml module
       A dictionary of XMLNamespaces.
        
    """
    def __init__(self):
        """
        Initialises the Reader class.           
        """
        self.citymodel_node = None
        self.cityobjectmembers = None
        self.namespaces = {"citygml":write_gml.XMLNamespaces.citygml,
                           "core": write_gml.XMLNamespaces.core,
                           "xsi": write_gml.XMLNamespaces.xsi,
                           "trans": write_gml.XMLNamespaces.trans,
                           "wtr": write_gml.XMLNamespaces.wtr,
                           "gml": write_gml.XMLNamespaces.gml,
                           "smil20lang": write_gml.XMLNamespaces.smil20lang,
                           "xlink": write_gml.XMLNamespaces.xlink,
                           "grp": write_gml.XMLNamespaces.grp,
                           "luse": write_gml.XMLNamespaces.luse,
                           "frn": write_gml.XMLNamespaces.frn,
                           "app": write_gml.XMLNamespaces.app,
                           "tex": write_gml.XMLNamespaces.tex,
                           "smil20": write_gml.XMLNamespaces.smil20,
                           "xAL": write_gml.XMLNamespaces.xAL,
                           "bldg": write_gml.XMLNamespaces.bldg,
                           "dem": write_gml.XMLNamespaces.dem,
                           "veg": write_gml.XMLNamespaces.veg,
                           "gen": write_gml.XMLNamespaces.gen} 
        
    def load_filepath(self, filepath):
        """
        This function loads the CityGML file and all the information into the citymodelnode and populate the cityobjectmembers.
     
        Parameters
        ----------
        filepath : str
            The file path of the CityGML file.
        """
        if self.citymodel_node != None:
            raise Exception("you have already loaded a citygml file")
        tree = etree.parse(filepath)
        self.citymodel_node = tree.getroot()
        self.cityobjectmembers = tree.findall("citygml:cityObjectMember", namespaces=self.namespaces)
        
    def load_citymodel_node(self, citymodel_node):
        """
        This function loads a citymodel_node and populate the cityobjectmembers.
     
        Parameters
        ----------
        filepath : str
            The file path of the CityGML file.
            
        Raises
        ------
        Exception
            when a CityGML file has already been loaded.
        """
        if self.citymodel_node != None:
            raise Exception("you have already loaded a citygml file")
            
        tree = etree.fromstring(etree.tostring(citymodel_node, pretty_print=True))        
        self.citymodel_node = tree
        self.cityobjectmembers = tree.findall("citygml:cityObjectMember", namespaces=self.namespaces)
        
    def get_buildings(self):
        """
        This function gets all the buildings from the loaded CityGML file.
        
        Returns
        -------
        buildings : list of lxml Elements
            A list of lxml Elements buildings.
        """
        buildings = []
        cityobjectmembers = self.cityobjectmembers
        for cityobject in cityobjectmembers:
            building = cityobject.find("bldg:Building", namespaces=self.namespaces)
            if building is not None:
                buildings.append(building)
        return buildings
    
    def get_relief_feature(self):
        """
        This function gets the relief feature cityobject.
        
        Returns
        -------
        relief features: list of lxml Elements
            List of relief feature lxml Element.
        """
        relief_features = []
        cityobjectmembers = self.cityobjectmembers
        for cityobject in cityobjectmembers:
            relief_feature = cityobject.find("dem:ReliefFeature", namespaces=self.namespaces)
            if relief_feature is not None:
                relief_features.append(relief_feature)
        return relief_features
                
    def get_landuses(self):
        """
        This function gets the landuse cityobject.
        
        Returns
        -------
        landuses : list of lxml Elements
            List of landuses lxml Element.
        """
        landuses = []
        cityobjectmembers = self.cityobjectmembers
        for cityobject in cityobjectmembers:
            landuse = cityobject.find("luse:LandUse", namespaces=self.namespaces)
            if landuse is not None:
                landuses.append(landuse)
        return landuses
    
    def get_roads(self):
        """
        This function gets the roads cityobject.
        
        Returns
        -------
        roads : list of lxml Elements
            List of roads lxml Element.
        """
        roads = []
        cityobjectmembers = self.cityobjectmembers
        for cityobject in cityobjectmembers:
            road = cityobject.find("trans:Road", namespaces=self.namespaces)
            if road is not None:
                roads.append(road)
        return roads

    def get_railways(self):
        """
        This function gets the railway cityobject.
        
        Returns
        -------
        railways : list of lxml Elements
            List of railway lxml Elements.
        """
        rails = []
        cityobjectmembers = self.cityobjectmembers
        for cityobject in cityobjectmembers:
            rail = cityobject.find("trans:Railway", namespaces=self.namespaces)
            if rail is not None:
                rails.append(rail)
        return rails
    
    def get_non_xtype_cityobject(self, xtype):
        """
        This function find all cityobject that is not of xtype.
        
        Parameters
        ----------
        xtype : str
            A cityobject type, e.g. "bldg:Building"
        
        Returns
        -------
        non-xtype cityobject : list of lxml Elements
            A list of lxml Elements non-xtype cityobjects.
        """
        non_xtype_cityobject = []
        cityobjectmembers = self.cityobjectmembers
        for cityobject in cityobjectmembers:
            xtype_cityobj = cityobject.find(xtype, namespaces=self.namespaces)
            if xtype_cityobj is None:
                non_xtype_cityobject.append(cityobject)
        return non_xtype_cityobject
    
    def get_building_height(self, lxmlbuilding):
        """
        This function gets the height of the building.
        
        Parameters
        ----------
        lxmlbuilding : lxml Element
            A lxml building object.
        
        Returns
        -------
        building height : float
            The building height, if attribute is not available return None.
        """
        height = lxmlbuilding.find("bldg:measuredHeight", namespaces=self.namespaces)
        if height != None:
            return float(height.text)
        else:
            return None
        
    def get_building_storey(self, lxmlbuilding):
        """
        This function gets the number of building storey above ground of the building.
        
        Parameters
        ----------
        lxmlbuilding : lxml Element
            A lxml building object.
        
        Returns
        -------
        building storey above ground : int
            The building storey above ground, if attribute is not available return None.
        """
        storey = lxmlbuilding.find("bldg:storeysAboveGround", namespaces=self.namespaces)
        if storey != None:
            return int(storey.text)
        else:
            return None
        
    def get_building_function(self,lxmlbuilding):
        """
        This function gets the function of the building.
        
        Parameters
        ----------
        lxmlbuilding : lxml Element
            A lxml building object.
        
        Returns
        -------
        building function code : str
            The building function in gml code, if attribute is not available return None.
        """
        function = lxmlbuilding.find("bldg:function", namespaces=self.namespaces)
        if function != None:
            return function.text
        else:
            return None
        
    def get_building_usage(self, lxmlbuilding):
        """
        This function gets the function of the building.
        
        Parameters
        ----------
        lxmlbuilding : lxml Element
            A lxml building object.
        
        Returns
        -------
        building usage code : str
            The building usage in gml code, if attribute is not available return None.
        """
        usage = lxmlbuilding.find("bldg:usage", namespaces=self.namespaces)
        if usage != None:
            return usage.text
        else:
            return None
        
    def get_building_class(self,lxmlbuilding):
        """
        This function gets the class of the building.
        
        Parameters
        ----------
        lxmlbuilding : lxml Element
            A lxml building object.
        
        Returns
        -------
        building class code : str
            The building class in gml code, if attribute is not available return None.
        """
        bclass =  lxmlbuilding.find("bldg:class", namespaces=self.namespaces)
        if bclass != None:
            return bclass.text
        else:
            return None
    
    def get_building_yr_constr(self, lxmlbuilding):
        """
        This function gets year of construction of the building.
        
        Parameters
        ----------
        lxmlbuilding : lxml Element
            A lxml building object.
        
        Returns
        -------
        building year of construction : str
            The building year of construction, if attribute is not available return None.
        """
        constr = lxmlbuilding.find("bldg:yearOfConstruction", namespaces=self.namespaces)
        if constr != None:
            return constr.text
        else:
            return None
        
    def get_building_rooftype(self, lxmlbuilding):
        """
        This function gets year of construction of the building.
        
        Parameters
        ----------
        lxmlbuilding : lxml Element
            A lxml building object.
        
        Returns
        -------
        building rooftype : str
            The building rooftype in gml code, if attribute is not available return None.
        """
        rooftype = lxmlbuilding.find("bldg:roofType", namespaces=self.namespaces)
        if rooftype != None:
            return rooftype.text
        else:
            return None
        
    def get_building_epsg(self, lxmlbuilding):
        """
        This function gets the coordinate system epsg of the building.
        
        Parameters
        ----------
        lxmlbuilding : lxml Element
            A lxml building object.
        
        Returns
        -------
        building epsg : str
            The building epsg, if attribute is not available return None.
        """
        envelope = lxmlbuilding.find("gml:boundedBy//gml:Envelope", namespaces=self.namespaces)
        epsg = envelope.attrib["srsName"]
        if epsg!=None:
            return epsg
        else:
            return None
    
    def get_building_storey_blw_grd(self, lxmlbuilding):
        """
        This function gets the number of building storey below ground of the building.
        
        Parameters
        ----------
        lxmlbuilding : lxml Element
            A lxml building object.
        
        Returns
        -------
        building storey below ground : int
            The building storey below ground, if attribute is not available return None.
        """
        sbg = lxmlbuilding.find("bldg:storeysBelowGround", namespaces=self.namespaces)
        if sbg != None:
            if sbg.text != "None":
                return int(sbg.text)
            else:
                return None
        else:
            return None
        
    def get_generic_attribs(self, cityobject):
        """
        This function gets the generic attribute of the cityobject.
        
        Parameters
        ----------
        cityobject : lxml Element
            A lxml cityobject.
        
        Returns
        -------
        dictionary generic attributes : dictionary
            The dictionary have a string key which will be the name of the generic attributes, and either an int, float or str value.
        """
        generic_attrib_dict = {}
        string_attribs = cityobject.findall("gen:stringAttribute", namespaces=self.namespaces )
        if string_attribs:
            for s_att in string_attribs:
                name = s_att.attrib["name"]
                value = s_att.find("gen:value",namespaces=self.namespaces).text
                generic_attrib_dict[name] = value
                
        int_attribs = cityobject.findall("gen:intAttribute", namespaces=self.namespaces )
        if int_attribs:
            for i_att in int_attribs:
                name = i_att.attrib["name"]
                value = i_att.find("gen:value",namespaces=self.namespaces).text
                generic_attrib_dict[name] = int(value)
                
        double_attribs = cityobject.findall("gen:doubleAttribute", namespaces=self.namespaces )
        if double_attribs:
            for d_att in double_attribs:
                name = d_att.attrib["name"]
                value = d_att.find("gen:value",namespaces=self.namespaces).text
                generic_attrib_dict[name] = float(value)
                
        return generic_attrib_dict
    
        
    def get_landuse_name(self, lxmllanduse):
        """
        This function gets the name of the landuse.
        
        Parameters
        ----------
        lxmllanduse : lxml Element
            A lxml landuse object.
        
        Returns
        -------
        landuse name : str
            The name of the landuse.
        """
        name = lxmllanduse.find("gml:name", namespaces=self.namespaces)
        if name !=None:
            return name.text
        else:
            return None
        
    def get_landuse_function(self, lxmllanduse):
        """
        This function gets the function of the landuse.
        
        Parameters
        ----------
        lxmllanduse : lxml Element
            A lxml landuse object.
        
        Returns
        -------
        landuse function : str
            The function of the landuse.
        """
        lfunction = lxmllanduse.find("luse:function", namespaces=self.namespaces)
        if lfunction != None:
            return lfunction.text
        else:
            return None
        
    def get_bus_stops(self):
        """
        This function gets the busstop cityobject.
        
        Returns
        -------
        bus stops : list of lxml Elements
            List of bus stops lxml Element.
        """
        stops = []
        cityobjectmembers = self.cityobjectmembers
        for cityobject in cityobjectmembers:
            frn = cityobject.find("frn:CityFurniture", namespaces=self.namespaces)
            if frn is not None:
                fclass = frn.find("frn:class", namespaces=self.namespaces).text
                ffunction = frn.find("frn:function", namespaces=self.namespaces).text
                if fclass == "1000" and ffunction == "1110":
                    stops.append(frn)
        return stops
        
    def get_epsg(self, cityobject):
        """
        This function gets the coordinate system epsg of the cityobject.
        
        Parameters
        ----------
        cityobject : lxml Element
            A lxml cityobject.
        
        Returns
        -------
        epsg : str
            The cityobject epsg, if attribute is not available return None.
        """
        envelope = cityobject.find("gml:boundedBy//gml:Envelope", namespaces=self.namespaces)
        if envelope != None:
            epsg = envelope.attrib["srsName"]
            if epsg !=None:
                return epsg
            else:
                return None
        
    def get_gml_id(self, cityobject):
        """
        This function gets the id of the cityobject.
        
        Parameters
        ----------
        cityobject : lxml Element
            A lxml cityobject.
        
        Returns
        -------
        id : str
            The cityobject id, if attribute is not available return None.
        """
        name = cityobject.attrib["{%s}id"% self.namespaces['gml']]
        if name !=None:
            return name
        else:
            return None
        
    def get_triangles(self,cityobject):
        """
        This function gets the triangles geometry of the cityobject.
        
        Parameters
        ----------
        cityobject : lxml Element
            A lxml cityobject.
        
        Returns
        -------
        triangles : list of lxml triangles
            List of lxml triangles.
        """
        triangles = cityobject.findall(".//gml:Triangle", namespaces=self.namespaces)
        return triangles
    
    def get_polygons(self,cityobject):
        """
        This function gets the polygon geometry of the cityobject.
        
        Parameters
        ----------
        cityobject : lxml Element
            A lxml cityobject.
        
        Returns
        -------
        polygons : list of lxml polygons
            List of lxml polygons.
        """
        polygons = cityobject.findall(".//gml:Polygon", namespaces=self.namespaces)
        return polygons
        
    def get_polygon_pt_list(self, lxmlpolygon):
        """
        This function gets the list of points that defines the polygon.
        
        Parameters
        ----------
        lxmlpolygon : lxml Element
            A lxml polygon object.
        
        Returns
        -------
        list of polygon points : list of polygon point lxml Elements
            The list of polygon point lxml elements. Each element is a polygon.
        """
        rings = lxmlpolygon.findall("gml:exterior//gml:LinearRing", namespaces=self.namespaces)
        poly_poslist = []
        if rings is not None:
            for ring in rings:
                poslist = ring.find("gml:posList", namespaces=self.namespaces)
                poly_poslist.append(poslist)
                
        return poly_poslist
        
    def get_polygon_pt_list_2_pyptlist(self, lxmlpolygon_pt_list):
        """
        This function gets the list of points that defines the polygon.
        
        Parameters
        ----------
        lxmlpolygon_pt_list : list of lxml Elements
            A list of lxml polygon point object.
        
        Returns
        -------
        list of points : pyptlist
            A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
            thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        """
        pos_list_str = lxmlpolygon_pt_list.text
        splitted_pt_list_str = pos_list_str.split(" ")
        srsdim = int(lxmlpolygon_pt_list.attrib["srsDimension"])
        npts = len(splitted_pt_list_str)/srsdim
                
        pt_list = []
        for c_cnt in range(npts):
            x = float(splitted_pt_list_str[c_cnt*srsdim])
            y = float(splitted_pt_list_str[(c_cnt*srsdim) + 1])
            z = float(splitted_pt_list_str[(c_cnt*srsdim) + 2])
            pt = (x,y,z)
            pt_list.append(pt)
            
        return pt_list
        
    def polygon_2_pyptlist(self, lxmlpolygon):
        """
        This function gets the list of points that defines the polygon.
        
        Parameters
        ----------
        lxmlpolygon : list of lxml Elements
            A list of lxml polygon object.
        
        Returns
        -------
        list of points : pyptlist
            A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
            thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        """
        poslist = self.get_polygon_pt_list(lxmlpolygon)[0]

        #poslist = poslist[0]
        pt_list = self.get_polygon_pt_list_2_pyptlist(poslist)
            
        return pt_list
        
    def get_pypolygon_list(self, cityobject):
        """
        This function gets a 2d list of points that defines the polygon. Pypolygon_list is a 2d list of tuples.
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z). 
        A pypolygon is a list of pypt that forms a polygon e.g. [(x1,y1,z1), (x2,y2,z2), ...].
        A pypolygon_list is a 2d list of tuples e.g. [[(x11,y11,z11), (x12,y12,z12), ...], [(x21,y21,z21), (x22,y22,z22), ...], ...]
        
        Parameters
        ----------
        cityobject : lxml Elements
            A cityobject lxml Element.
        
        Returns
        -------
        2d list of points : pypolygon_list
            A 2d list that defines a list of polygons.
        """
        polygons = self.get_polygons(cityobject)
        pypolygon_list = []
        for polygon in polygons:
            pyptlist = self.polygon_2_pyptlist(polygon)
            pypolygon_list.append(pyptlist)
        return pypolygon_list
        
    def get_pytriangle_list(self, cityobject):
        """
        This function gets a 2d list of points that defines the triangle. Pytriangle_list is a 2d list of tuples.
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z). 
        A pytriangle is a list of pypt that forms a polygon e.g. [(x1,y1,z1), (x2,y2,z2), ...].
        A pytriangle_list is a 2d list of tuples e.g. [[(x11,y11,z11), (x12,y12,z12), ...], [(x21,y21,z21), (x22,y22,z22), ...], ...]
        
        Parameters
        ----------
        cityobject : lxml Elements
            A cityobject lxml Element.
        
        Returns
        -------
        2d list of points : pytriangle_list
            A 2d list that defines a list of triangles.
        """
        triangles = self.get_triangles(cityobject)
        pytriangle_list = []
        for triangle in triangles:
            pyptlist = self.polygon_2_pyptlist(triangle)
            pytriangle_list.append(pyptlist)
        return pytriangle_list
        
    def get_linestring(self, cityobject):
        """
        This function gets the linestring (polyline) geometry of the cityobject. Currently, this method only works with lod0Network
        
        Parameters
        ----------
        cityobject : lxml Element
            A lxml cityobject.
        
        Returns
        -------
        polylines : list of lxml polylines
            List of lxml polylines.
        """
        lod0networks = cityobject.findall("trans:lod0Network", namespaces=self.namespaces)
        polylines = []
        for lod0 in lod0networks:
            linestrings = lod0.findall(".//gml:GeometricComplex//gml:LineString", namespaces=self.namespaces)
            if linestrings is not None:
                for lstring in linestrings:
                    poslist = lstring.find("gml:posList", namespaces=self.namespaces)
                    polylines.append(poslist)
                    
        return polylines
        
    def get_pylinestring_list(self, cityobject):
        """
        This function gets a 2d list of points that defines the polylines. Pypolyline_list is a 2d list of tuples.
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z). 
        A pypolyline is a list of pypt that forms a polyline e.g. [(x1,y1,z1), (x2,y2,z2), ...].
        A pypolyline_list is a 2d list of tuples e.g. [[(x11,y11,z11), (x12,y12,z12), ...], [(x21,y21,z21), (x22,y22,z22), ...], ...]
        
        Parameters
        ----------
        cityobject : lxml Elements
            A cityobject lxml Element.
        
        Returns
        -------
        2d list of points : pypolyline_list
            A 2d list that defines a list of polylines.
        """
        polylines = self.get_linestring(cityobject)
        pylinestring_list = []
        for polyline in polylines:
            pt_list = self.get_polygon_pt_list_2_pyptlist(polyline)
            pylinestring_list.append(pt_list)
            
        return pylinestring_list

class SurfaceMember(object):
    """
    Writes a surface member object instance.
    
    Parameters
    ----------
    pyptlist :  list of tuples of floats
        List of points to be written. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]

    Attributes
    ----------
    pos_list :  pyptlist
        List of points to be written. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    """
    def __init__(self, pyptlist):
        self.pos_list = pyptlist
        
    def construct(self):
        """
        This function writes a GML surface member.
        
        Returns
        -------
        surface member :  lxml Element
            lxml surface member element.
        """
        surface = write_gml.write_surface_member(self.pos_list)
        return surface
        
class Triangle(object):
    """
    Writes a triangle object instance.
    
    Parameters
    ----------
    pyptlist :  list of tuples of floats
        List of points to be written. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]

    Attributes
    ----------
    pos_list :  pyptlist
        List of points to be written. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    """
    def __init__(self, pyptlist):
        """
        This function initialises the surface member class.
        
        Parameters
        ----------
        pyptlist :  list of tuples of floats
            List of points to be written. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
            thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        """
        self.pos_list = pyptlist
        
    def construct(self):
        """
        This function writes a GML triangle.
        
        Returns
        -------
        triangle :  lxml Element
            lxml triangle element.
        """
        triangle = write_gml.write_triangle(self.pos_list)
        return triangle

class LineString(object):
    """
    Writes a linestring object instance.
    
    Parameters
    ----------
    pyptlist :  list of tuples of floats
        List of points to be written. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]

    Attributes
    ----------
    pos_list :  pyptlist
        List of points to be written. A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z), 
        thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    """
    def __init__(self, pyptlist):
        """
        This function initialises the linestring class.
        """
        self.pos_list = pyptlist
        
    def construct(self):
        """
        This function writes a GML linestring.
        
        Returns
        -------
        linestring :  lxml Element
            lxml linestring element.
        """
        line = write_gml.write_linestring(self.pos_list)
        return line
    
class Point(object):
    """
    Writes a point object instance.
    
    Parameters
    ----------
    pypt :  tuple of floats
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z).

    Attributes
    ----------
    pos_list :  pypt
        A pypt is a tuple that documents the xyz coordinates of a pt e.g. (x,y,z).
        
    """
    def __init__(self, pypt):
        """
        This function initialises the point class.
        """
        self.pos = pypt
        
    def construct(self):
        """
        This function writes a GML point.
        
        Returns
        -------
        point :  lxml Element
            lxml point element.
        """
        pt = write_gml.write_pt(self.pos)
        return pt