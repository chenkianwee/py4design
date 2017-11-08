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
#    along with Pyliburo.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================
import os

import pycitygml
import py3dmodel
import urbangeom
import gml3dmodel
import urbanformeval

class Evals(object):
    """
    An object that extracts all the neccessary information from a CityGML file for calculating Non-Solar Heated Facade to Floor Area Index,
    Useful Solar Facade to Floor Area Index, Daylight Facade to Floor Area Index, Frontal Area Index, Route Directness Index. Currently,
    the module only works for LOD1 CityGML models. 
    
    Parameters
    ----------
    citygmlfile : str
        The file path of the CityGML file to be analysed.
    
    Attributes
    ----------    
    citygml : pycitygml.Reader() class instance 
        The Reader class that reads and store all the CityGML information for the analysis.
    
    citygmlfilepath : str
        See Parameters.
    
    buildings : list of lxml Elements
            A list of lxml Elements buildings.
    
    landuses : list of lxml Elements
            List of landuses lxml Element.
            
    stops : list of lxml Elements
            List of bus stops lxml Element.
    
    roads : list of lxml Elements
            List of roads lxml Element.
    
    railways : list of lxml Elements
            List of railway lxml Elements.
            
    relief_features : list of lxml Elements
            List of relief feature lxml Element.
    
    building_occsolids : list of OCCsolids
        The geometry (OCCsolid) of the buildings.
        
    roof_occfaces : list of OCCfaces
        Faces of all the roofof all buildings.
    
    facade_occfaces : list of OCCfaces
        Faces of all the facades of all buildings.
    
    footprint_occfaces : list of OCCfaces
        Faces of all the footprints of all buildings.
        
    building_dictlist : list of dictionaries
        Each dictionary has these keys : {"facade", "footprint", "roof", "solid"}
        
        facade : list of OCCfaces
            Faces of all the facades.
        
        footprint : OCCface
            Face of the footprint.
        
        roof : list of OCCfaces
            Faces of all the roofs.
            
        solid : OCCsolid
            The massing of the building (LOD1).
            
    buildings_on_plot_2dlist : 2d list of dictionaries 
        2d list of building dictionaries according to the plot they belong to, e.g. [[bldg_dict1, bldg_dict2, bldg_dict3],[bldg_dict4,bldg_dict5],[bldg_dict6, bldg_dict7]].
    
    landuse_occpolygons : list of OCCfaces
        Faces of all the landuse plots.
    
    relief_feature_occshells : list of OCCshells
        Shells of the terrains.
    
    relief_feature_occfaces : list of OCCfaces
        Faces of the terrains.
        
    road_occedges : list of OCCedges
        The edges defining the road network (LOD0).
    
    shading_faces : list of OCCfaces
        The faces of the surrounding shading objects and faces.
        
    rad_base_filepath : str
        The file path of the base.rad file for Radiance simulation.
    
    nshffai_folderpath : str
        The file directory to store all the result files of nshffai simulation.
    
    dffai_folderpath : str
        The file directory to store all the result files of dffai simulation.
    
    pvefai_folderpath : str
        The file directory to store all the result files of pvefai simulation.
        
    daysim_folderpath : str
        The file directory to store all the result files of daysim simulation.
        
    solarxdim : int
        The x dimension grid size for the building envelope for solar simulation.
    
    solarydim : int
        The y dimension grid size for the building envelope for solar simulation.
    
    rad : py2radiance.Rad class instance
        The rad object documenting all the information for Radiance/Daysim simulation.
    
    irrad_results : list of floats
        The the irradiance results in (kWh/m2), the list corresponds to the sensor surface list.
    
    illum_results : list of floats
        The illuminance in (lx), the list corresponds to the sensor surface list.
    
    facade_grid_srfs : list of OCCfaces
        The gridded facades.   
    
    roof_grid_srfs : list of OCCfaces
        The gridded roofs.
    
    """
    def __init__(self, citygmlfile):
        """Initialises the Evals class"""
        reader = pycitygml.Reader()
        reader.load_filepath(citygmlfile)
        self.citygml = reader
        self.citygmlfilepath = citygmlfile
        self.buildings = self.citygml.get_buildings()
        self.landuses = self.citygml.get_landuses()
        self.stops = self.citygml.get_bus_stops()
        self.roads = self.citygml.get_roads()
        self.railways = self.citygml.get_railways()
        self.relief_features = self.citygml.get_relief_feature()
        #occ geometries
        self.building_occsolids = None
        self.roof_occfaces = None
        self.facade_occfaces = None
        self.footprint_occfaces = None
        self.building_dictlist = None
        self.buildings_on_plot_2dlist = None #2d list of building dictlist according to the plot they belong to 
        self.landuse_occpolygons = None
        self.relief_feature_occshells = None
        self.relief_feature_occfaces = None
        self.road_occedges = None
        self.shading_faces = None
        #radiance parameters
        self.rad_base_filepath = os.path.join(os.path.dirname(__file__),'py2radiance','base.rad')
        self.nshffai_folderpath = os.path.join(os.path.dirname(self.citygmlfilepath), 'nshffai_data')
        self.dffai_folderpath = os.path.join(os.path.dirname(self.citygmlfilepath), 'dffai_data')
        self.pvefai_folderpath = os.path.join(os.path.dirname(self.citygmlfilepath), 'pvefai_data')
        self.daysim_folderpath = os.path.join(os.path.dirname(self.citygmlfilepath), 'daysim_data')
        self.solarxdim = None
        self.solarydim = None
        self.rad = None
        #rad results 
        self.irrad_results = None
        self.illum_results = None
        self.facade_grid_srfs = None
        self.roof_grid_srfs = None
        
    def initialise_occgeom(self):
        """This function extracts all the geometrical information in the CityGML file and documents them in the attributes"""
        buildings = self.buildings
        bsolid_list = []
        roof_list = []
        facade_list = []
        footprint_list = []
        building_dictlist = []
        for building in buildings:
            building_dict ={}
            #get all the polygons from the building 
            pypolygonlist = self.citygml.get_pypolygon_list(building) 
            bsolid = py3dmodel.construct.make_occsolid_frm_pypolygons(pypolygonlist)
            #extract the polygons from the building and separate them into facade, roof, footprint
            facades, roofs, footprints = urbangeom.identify_building_surfaces(bsolid)
            building_dict["facade"] = facades
            building_dict["footprint"] = footprints[0]
            building_dict["roof"] = roofs
            building_dict["solid"] = bsolid
            building_dictlist.append(building_dict)
            bsolid_list.append(bsolid)
            facade_list.extend(facades)
            roof_list.extend(roofs)
            footprint_list.extend(footprints)
            
        self.building_dictlist = building_dictlist
        self.building_occsolids = bsolid_list
        self.facade_occfaces = facade_list
        self.roof_occfaces = roof_list
        self.footprint_occfaces = footprint_list
        
        #get the relief feature
        relief_features = self.relief_features
        rf_occtriangle_list = []
        rf_shell_list = []
        for rf in relief_features:
            pytrianglelist = self.citygml.get_pytriangle_list(rf)
            occtriangle_list = []
            for pytriangle in pytrianglelist:
                occtriangle = py3dmodel.construct.make_polygon(pytriangle)
                rf_occtriangle_list.append(occtriangle)
                occtriangle_list.append(occtriangle)
            rf_shell = py3dmodel.construct.sew_faces(occtriangle_list)[0]
            rf_shell_list.append(rf_shell)
            
        self.relief_feature_occfaces = rf_occtriangle_list
        self.relief_feature_occshells = rf_shell_list
        
        #get the roads
        roads = self.roads
        road_occedges = []
        for road in roads:
            polylines = self.citygml.get_pylinestring_list(road)
            
            for polyline in polylines:
                occ_wire = py3dmodel.construct.make_wire(polyline)
                edge_list = py3dmodel.fetch.topo_explorer(occ_wire, "edge")
                road_occedges.extend(edge_list)
                
        self.road_occedges = road_occedges
        
        #get the land-use plot
        landuses = self.landuses
        lface_list = []
        for landuse in landuses:
            lpolygons = self.citygml.get_polygons(landuse)
            if lpolygons:
                lfaces = []
                if len(lpolygons)>1:
                    for lpolygon in lpolygons:
                        landuse_pts = self.citygml.polygon_2_pyptlist(lpolygon)
                        lface = py3dmodel.construct.make_polygon(landuse_pts)
                        lfaces.append(lface)
                    merged_face = py3dmodel.construct.merge_faces(lfaces)[0]
                if len(lpolygons)==1:
                    landuse_pts = self.citygml.polygon_2_pyptlist(lpolygons[0])
                    lface = py3dmodel.construct.make_polygon(landuse_pts)
                    merged_face = lface
                    
                lface_list.append(merged_face)
                
        self.landuse_occpolygons = lface_list
        
    def add_shadings_4_solar_analysis(self, shading_citygml_file):
        """
        This function adds the CityGML file that is the context/shading of the CityGML file of interest.
    
        Parameters
        ----------        
        shading_citygml_file : str
            The file path of the shading CityGML.
                
        """
        shading_faces = []
        reader = pycitygml.Reader()
        reader.load_filepath(shading_citygml_file)
        gml_bldgs = reader.get_buildings()
        for gml_bldg in gml_bldgs:
            pypolygonlist = reader.get_pypolygon_list(gml_bldg) 
            bsolid = py3dmodel.construct.make_occsolid_frm_pypolygons(pypolygonlist)
            bldg_face_list = py3dmodel.fetch.topo_explorer(bsolid, "face")
            shading_faces.extend(bldg_face_list)
            
        reliefs = reader.get_relief_feature()
        for rf in reliefs:
            pytrianglelist = reader.get_pytriangle_list(rf)
            for pytriangle in pytrianglelist:
                occtriangle = py3dmodel.construct.make_polygon(pytriangle)
                shading_faces.append(occtriangle)
                
        self.shading_faces = shading_faces
        
    def calculate_far(self, flr2flr_height):
        """
        This function calculates the FAR of each landuse plot.
        
        Parameters
        ----------
        flr2flr_height : float
            The floor to floor height of the buildings.
            
        Returns
        -------
        far list : list of floats
            List of FAR for each landuse plot.
            
        """
        if self.building_occsolids == None:
            self.initialise_occgeom()
            
        reader = self.citygml
        luse_polygons = self.landuse_occpolygons
        gmlluses = self.landuses
        gmlbldgs = self.buildings
        nluse = len(gmlluses)
        far_list = []
        for gcnt in range(nluse):
            gmlluse = gmlluses[gcnt]
            luse = luse_polygons[gcnt]
            luse_area = py3dmodel.calculate.face_area(luse)
            gmlbldg_on_luse = gml3dmodel.buildings_on_landuse(gmlluse, gmlbldgs, reader)
            flr_area_list = []
            for gmlbldg in gmlbldg_on_luse:
                pypolygon = reader.get_pypolygon_list(gmlbldg)
                bsolid = py3dmodel.construct.make_occsolid_frm_pypolygons(pypolygon)
                b_flr_area = urbangeom.calculate_bldg_flr_area(bsolid, flr2flr_height)
                flr_area_list.append(b_flr_area)
                
            far = sum(flr_area_list)/luse_area
            far_list.append(far)
        return far_list
        
    def nshffai(self, irrad_threshold, epwweatherfile, xdim, ydim, nshffai_threshold=None):
        """
        This function calculates the Non-Solar Heated Facade to Floor Area Index (NSHFFAI) which is the ratio of the facade area that 
        receives irradiation below a specified level over the net floor area. For more information refer to: Chen, Kian Wee, and Leslie Norford.
        2017. Evaluating Urban Forms for Comparison Studies in the Massing Design Stage. Sustainability 9 (6). doi:10.3390/su9060987.
        
        Parameters
        ----------        
        irrad_threshold : float 
            The solar irradiance threshold value (kwh/m2). For Singapore a tropical climate 364 kwh/m2 is used.
        
        epwweatherfile : string
            The file path of the epw weatherfile.
        
        xdim : int
            The x dimension grid size for the building facades.
        
        ydim : int
            The y dimension grid size
        
        nshffai_threshold : float, optional
            The nshffai threshold value for calculating the nshffai percent, default = None. If None, nshffai percent will return None.
        
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
        if self.building_occsolids == None:
            self.initialise_occgeom()
            
        rf_occfaces = self.relief_feature_occfaces
        #get all the shading srfs
        if self.shading_faces !=None:
            shading_faces = self.shading_faces
            shading_faces = shading_faces + rf_occfaces
        else:
            shading_faces = rf_occfaces
        
        
        bsolid_list = self.building_occsolids
        result_dict = urbanformeval.nshffai(bsolid_list, irrad_threshold, epwweatherfile, xdim, ydim, self.nshffai_folderpath, 
                                            nshffai_threshold = nshffai_threshold, shading_occfaces = shading_faces)
        
        self.irrad_results = result_dict["solar_results"]
        return result_dict
        
    def usffai(self, lower_irrad_threshold, upper_irrad_threshold, epwweatherfile, xdim, ydim, usffai_threshold=None):
        """
        This function calculates the Useful-Solar Facade to Floor Area Index (USFFAI) which is the ratio of the facade area that 
        receives irradiation between the lower and upper solar threshold over the net floor area. 
    
        Parameters
        ----------
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
        
        usffai_threshold : float, optional
            The usffai threshold value for calculating the nshffai percent, default = None. If None, usffai percent will return None.
        
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
        if self.building_occsolids == None:
            self.initialise_occgeom()
            
        rf_occfaces = self.relief_feature_occfaces
        if self.building_occsolids == None:
            self.initialise_occgeom()
            
        rf_occfaces = self.relief_feature_occfaces
        #get all the shading srfs
        if self.shading_faces !=None:
            shading_faces = self.shading_faces
            shading_faces = shading_faces + rf_occfaces
        else:
            shading_faces = rf_occfaces
            
        bsolid_list = self.building_occsolids
        result_dict = urbanformeval.usffai(bsolid_list, lower_irrad_threshold, upper_irrad_threshold, epwweatherfile, 
                                             xdim, ydim, self.nshffai_folderpath, usffai_threshold = usffai_threshold, 
                                             shading_occfaces = shading_faces)
        
        self.irrad_results = result_dict["solar_results"]
        return result_dict
    
    def dffai(self, illum_threshold, epwweatherfile, xdim, ydim, dffai_threshold=None):
        """
        This function calculates the Daylight Facade to Floor Area Index (DFFAI) which is the ratio of the facade area that 
        receives illuminance (lx) higher than a threshold over the net floor area. 
    
        Parameters
        ----------
        illum_threshold : float 
            The illuminance threshold value (lx). For Singapore a tropical climate 10,000lx is used.
        
        epwweatherfile : string
            The file path of the epw weatherfile.
        
        xdim : int
            The x dimension grid size for the building facades.
        
        ydim : int
            The y dimension grid size
        
        dffai_threshold : float, optional
            The dffai threshold value for calculating the dffai percent, default = None. If None, dsffai percent will return None.
        
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
        if self.building_occsolids == None:
            self.initialise_occgeom()
            
        rf_occfaces = self.relief_feature_occfaces
        #get all the shading srfs
        if self.shading_faces !=None:
            shading_faces = self.shading_faces
            shading_faces = shading_faces + rf_occfaces
        else:
            shading_faces = rf_occfaces
            
        bsolid_list = self.building_occsolids
        result_dict = urbanformeval.dffai(bsolid_list, illum_threshold, epwweatherfile, xdim,ydim, self.dffai_folderpath, 
                                          self.daysim_folderpath, dffai_threshold = dffai_threshold, 
                                          shading_occfaces = shading_faces)

        self.illum_results = result_dict["solar_results"]
        return result_dict
        
    def pvafai(self, irrad_threshold, epwweatherfile, xdim, ydim, surface = "roof", pvafai_threshold = None):
        """
        This function calculates the PhotoVoltaic Area to Floor Area Index (PVAFAI) which is the ratio of the PV area that 
        receives irradiation above a specified level over the net floor area. For more information refer to: Chen, Kian Wee, and Leslie Norford.
        2017. Evaluating Urban Forms for Comparison Studies in the Massing Design Stage. Sustainability 9 (6). doi:10.3390/su9060987.
    
        Parameters
        ----------
        irrad_threshold : float 
            The solar irradiance threshold value (kwh/m2). For Singapore a tropical climate 512 kwh/m2 is used for the facade and 1280 kWh/m2 is used for the roof.
        
        epwweatherfile : string
            The file path of the epw weatherfile.
        
        xdim : int
            The x dimension grid size for the building facades.
        
        ydim : int
            The y dimension grid size
            
        surface : str, optional
            The PV area of the building. Options are either "roof" or "facade", default = "roof".
        
        pvafai_threshold : float, optional
            The pvafai threshold value for calculating the pvafai percent, default = None. If None, nshffai percent will return None.
        
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
        if self.building_occsolids == None:
            self.initialise_occgeom()
            
        rf_occfaces = self.relief_feature_occfaces
        #get all the shading srfs
        if self.shading_faces !=None:
            shading_faces = self.shading_faces
            shading_faces = shading_faces + rf_occfaces
        else:
            shading_faces = rf_occfaces
            
        
        bsolid_list = self.building_occsolids
        result_dict = urbanformeval.pvafai(bsolid_list, irrad_threshold, epwweatherfile, xdim, ydim, self.pvefai_folderpath, 
                                          mode = surface, pvafai_threshold = pvafai_threshold, shading_occfaces = shading_faces )

        return result_dict
    
    def pvefai(self, roof_irrad_threshold, facade_irrad_threshold, epwweatherfile, xdim, ydim, 
               pvrfai_threshold = None, pvffai_threshold = None, pvefai_threshold = None):
        """
        This function calculates the PhotoVoltaic Envelope to Floor Area Index (PVEFAI) which is the ratio of the PV envelope area (both facade and roof) that 
        receives irradiation above a specified level over the net floor area. For more information refer to: Chen, Kian Wee, and Leslie Norford.
        2017. Evaluating Urban Forms for Comparison Studies in the Massing Design Stage. Sustainability 9 (6). doi:10.3390/su9060987.
    
        Parameters
        ----------
        roof_irrad_threshold : float 
            The solar irradiance threshold value (kwh/m2). For Singapore a tropical climate 1280 kWh/m2 is used for the roof.
            
        facade_irrad_threshold : float 
            The solar irradiance threshold value (kwh/m2). For Singapore a tropical climate 512 kwh/m2 is used for the facade.
        
        epwweatherfile : str
            The file path of the epw weatherfile.
        
        xdim : int
            The x dimension grid size for the building facades.
        
        ydim : int
            The y dimension grid size
        
        pvrfai_threshold : float, optional
            The PV Roof to Floor Area Index (pvrfai) threshold value for calculating the pvrfai percent, default = None. If None, pvrfai percent will return None.
            
        pvffai_threshold : float, optional
            The PV Facade to Floor Area Index (pvffai) threshold value for calculating the pvffai percent, default = None. If None, pvffai percent will return None.
            
        pvefai_threshold : float, optional
            The PV Envelope to Floor Area Index (pvefai) threshold value for calculating the pvefai percent, default = None. If None, pvefai percent will return None.
        
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
        if self.building_occsolids == None:
            self.initialise_occgeom()
            
        rf_occfaces = self.relief_feature_occfaces
        #get all the shading srfs
        if self.shading_faces !=None:
            shading_faces = self.shading_faces
            shading_faces = shading_faces + rf_occfaces
        else:
            shading_faces = rf_occfaces
            
        bsolid_list = self.building_occsolids
        result_dict = urbanformeval.pvefai(bsolid_list, roof_irrad_threshold, facade_irrad_threshold, epwweatherfile, xdim, ydim, 
                                           self.pvefai_folderpath, pvrfai_threshold = pvrfai_threshold,
                                           pvffai_threshold = pvffai_threshold, pvefai_threshold = pvefai_threshold,
                                           shading_occfaces = shading_faces)
                                                                                             
        return result_dict

    def fai(self, wind_dir, boundary_occface = None, xdim = 100, ydim = 100):
        """
        This function calculates the frontal area index of an urban massing.
        
        Parameters
        ----------
        wind_dir : pyvec
            Pyvec is a tuple of floats that documents the xyz vector of a dir e.g. (x,y,z)
            
        boundary_occface : OCCface, optional
            The boundary of the FAI analysis. This face will be gridded. If None will process the terrain and use the terrain bounding box as the boundary face.
        
        xdim : int
            The x dimension grid size for the boundary.
        
        ydim : int
            The y dimension grid size for the boundary.
            
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
        
        if self.relief_feature_occshells == None:
            self.initialise_occgeom()
            
        
        if boundary_occface == None:
            rf_shells = self.relief_feature_occshells
            rf_compound = py3dmodel.construct.make_compound(rf_shells)
            xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(rf_compound)
            
            all_flatten_rf_faces = []
            for rfshell in rf_shells:
                rffaces = py3dmodel.fetch.topo_explorer(rfshell, "face")
                for rfface in rffaces:
                    flatten_face_z = py3dmodel.modify.flatten_face_z_value(rfface, z = zmin)
                    all_flatten_rf_faces.append(flatten_face_z)         
            boundary_occface = py3dmodel.construct.merge_faces(all_flatten_rf_faces)[0]
            
        bsolid_list = self.building_occsolids
        print "ANALYSING FAI ..."
        res_dict = urbanformeval.frontal_area_index(bsolid_list, boundary_occface,wind_dir,xdim = xdim, ydim = ydim)
                                                                                                         
        return res_dict
        
    def rdi(self, boundary_occface = None, obstruction_occfacelist = [], rdi_threshold = 0.6):
        """
        This function measures the connectivity of street network in a neighbourhood by measuring route 
        directness for each parcel to a series of points around the periphery of the study area. It
        identifies the percentage of good plots that exceed a rdi of 0.8 (urban area) and 0.6 (suburban). 
        Algorithm for Route Directness Test, Stangl, P.. 2012 the pedestrian route directness test: A new level of service model.
        urban design international 17, 228-238.
        
        Parameters
        ----------
        boundary_occface : OCCface
            The boundary of the analysed area. If None will process the terrain and use the terrain bounding box as the boundary face.
        
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
        if self.road_occedges == None:
            self.initialise_occgeom()
            
        #TODO: currently the function only works on flat terrain
        road_occedges = self.road_occedges
        plot_occfacelist = self.landuse_occpolygons
        if boundary_occface == None:
            rf_faces = self.relief_feature_occfaces
            compound_list = rf_faces + road_occedges + plot_occfacelist + obstruction_occfacelist
            compound = py3dmodel.construct.make_compound(compound_list)
            xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(compound)
            
            f_rf_face_list = []
            for rf_face in rf_faces:
                f_rf_face = py3dmodel.modify.flatten_face_z_value(rf_face, z = zmin)
                f_rf_face_list.append(f_rf_face)
                
            boundary_occface = py3dmodel.construct.merge_faces(f_rf_face_list)[0]
            
        if boundary_occface != None:
            compound_list = [boundary_occface] + road_occedges + plot_occfacelist + obstruction_occfacelist
            compound = py3dmodel.construct.make_compound(compound_list)
            xmin,ymin,zmin,xmax,ymax,zmax = py3dmodel.calculate.get_bounding_box(compound)
            
            boundary_occface = py3dmodel.modify.flatten_face_z_value(boundary_occface, z = zmin)
            
        f_redge_list = []
        road_length_list = []
        for redge in road_occedges:
            f_redge = py3dmodel.modify.flatten_edge_z_value(redge, z = zmin)
            lbound, ubound = py3dmodel.fetch.edge_domain(f_redge)
            edge_length = py3dmodel.calculate.edgelength(lbound, ubound, f_redge)
            road_length_list.append(edge_length)
            f_redge_list.append(f_redge)
            
        road_length = sum(road_length_list)
            
        f_p_face_list = []
        for p_face in plot_occfacelist:
            f_p_face = py3dmodel.modify.flatten_face_z_value(p_face, z = zmin)
            f_p_face_list.append(f_p_face)
            
        f_o_face_list = []
        for o_face in obstruction_occfacelist:
            f_o_face = py3dmodel.modify.flatten_face_z_value(o_face, z = zmin)
            f_o_face_list.append(f_o_face)
                
        res_dict = urbanformeval.route_directness(f_redge_list, f_p_face_list, boundary_occface,
                                                  obstruction_occfacelist = f_o_face_list,rdi_threshold = rdi_threshold)
        
        res_dict["road_length"] = road_length
                                                                                                        
        return res_dict