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
import abc
import gml3dmodel
import pycitygml
import py3dmodel
import utility

class BaseParm(object):
    """
    The base class for developing new parameters for parameterising a semantic model. For more information please refer to 
    Chen, Kian Wee, Patrick Janssen, and Leslie Norford. 2017. Automatic Parameterisation of Semantic 3D City Models for Urban Design Optimisation. 
    In Future Trajectories of Computation in Design, Proceedings of the 17th International Conference on Computer Aided Architectural Design Futures, pp 84 to 100. Istanbul, Turkey.
    """
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def define_int_range(self, start, stop, step):
        """ 
        The function defines the range of the parameter if the parameter type is integer.
        
        Parameters
        ----------
        start : int
            The starting number of the sequence.
        
        stop : int
            Generate numbers up to, including this number.
        
        step : int
            The difference between each number in the sequence.
        
        Returns
        -------        
        parameter range : list of ints
            List of generated parameters.
        """
        parm_range = range(start, stop+step, step)
        for parm in parm_range:
            if parm > stop:
                parm_range.remove(parm)
        return parm_range
        
    @abc.abstractmethod
    def define_float_range(self, start, stop, step = None):
        """ 
        The function defines the range of the parameter if the parameter type is float.
        
        Parameters
        ----------
        start : float
            The starting number of the sequence.
        
        stop : float
            Generate numbers up to, including this number.
        
        step : float, optional
            The difference between each number in the sequence, default = None. When None the parameter is a continuous parameter, if not None the parameter is a discrete parameter.
        
        Returns
        -------        
        parameter range : list of floats
            List of generated float parameters if step = None, if step != None the parameter range is made up of two numbers the start and the end of the continuous parameter.
        """
        
        if step !=None:
            parm_range = utility.frange(start, stop + step, step)
            for parm in parm_range:
                if parm > stop:
                    parm_range.remove(parm)
        else:
            parm_range = (start, stop)
                    
        return parm_range
        
    @abc.abstractmethod
    def set_parm_range(self, parm_range):
        """ 
        The function defines the range of the parameter .
        
        Parameters
        ----------
        parm_range : list of ints/floats
            The parameter range.
        """
        return 
        
    @abc.abstractmethod
    def define_nparameters(self, pycitygml_reader):
        """ 
        The function determines the total parameters for parameterising the model.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
        """
        return
        
    @abc.abstractmethod
    def map_nrmlise_parms_2_parms(self, nrmlised_parm_list):
        """ 
        The function maps the the normalise parameter list to the real parameter list.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        parameter list : list of int/floats
            List of real parameters.
        """
        parm_range = self.parm_range
        parm_list = []
        if type(parm_range) == tuple and len(parm_range) == 2:
            start =  parm_range[0]
            stop = parm_range[1]
            parm_extent = stop - start
            
            for nrml_parm in nrmlised_parm_list:
                parm = start + (nrml_parm*parm_extent)
                parm_list.append(parm)
                
        else:
            n_parm_range = len(parm_range)-1
            for nrml_parm in nrmlised_parm_list:
                parm_index = int(round(nrml_parm*n_parm_range))
                parm = parm_range[parm_index]
                parm_list.append(parm)
            
        return parm_list
        
    @abc.abstractmethod
    def execute(self,pycitygml_reader, parameters):
        """ 
        This funciton defines the parameterisation process and executes the process.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
        
        parameters : list of ints/floats
            The normalised parameters to be mapped to the real parameters defined, the parameters will be used to generate a design alternative.
        """
        return 
        
class BldgFlrAreaHeightParm(BaseParm):
    """
    An implementation of the BaseParm class for parameterising the massing of buildings (LOD1) in terms of its height while constraint by its floor area.
    
    Attributes
    ----------    
    bldg_class : str
        The string of the gml code for building class.
    
    bldg_function : str
        The string of the gml code for building function.
        
    bldg_usage : str
        The string of the gml code for building usage.
        
    parm_range : list of floats/ints
        The list of possible parameters.
    """
    def __init__(self):
        """Initialise the class"""
        self.bldg_class = None
        self.bldg_function = None
        self.bldg_usage = None
        self.parm_range = None
        
    def apply_2_bldg_class(self, bldg_class):
        """
        This function declares the building class that will have this parameter, buildings which is not this class will not be parameterised.
        
        Parameters
        ----------     
        bldg_class : str
            The string of the gml code for building class.
        """
        self.bldg_class = bldg_class
        
    def apply_2_bldg_function(self, bldg_function):
        """
        This function declares the building function that will have this parameter, buildings which is not this function will not be parameterised.
        
        Parameters
        ----------     
        bldg_function : str
            The string of the gml code for building function.
        """
        self.bldg_function = bldg_function
        
    def apply_2_bldg_usage(self, bldg_usage):
        """
        This function declares the building usage that will have this parameter, buildings which is not this usage will not be parameterised.
        
        Parameters
        ----------     
        bldg_usage : str
            The string of the gml code for building usage.
        """
        self.bldg_usage = bldg_usage
        
    def eligibility_test(self, gml_bldg_list, pycitygml_reader):
        """ 
        The function checks which are the buildings that are eligible to be parameterised.
        
        Parameters
        ----------
        gml_bldg_list : list of lxml.etree Element 
            The GML building to be parameterised.
            
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        eligible_bldg_list : list of lxml.etree Element 
            The GML building to be parameterised.
        
        non_eligible_bldg_list : list of lxml.etree Element 
            The GML building that will not be parameterised.
        """
        eligible_bldg_list = []
        non_eligible_bldg_list = []
        for gml_bldg in gml_bldg_list:
            eligibility = True
            if self.bldg_class != None: 
                bldg_class = pycitygml_reader.get_building_class(gml_bldg)
                if self.bldg_class != bldg_class:
                    eligibility = False
                    
            if self.bldg_function != None:
                bldg_function = pycitygml_reader.get_building_function(gml_bldg)
                if self.bldg_function != bldg_function:
                    eligibility = False
            
            if self.bldg_usage != None:
                bldg_usage = pycitygml_reader.get_building_usage(gml_bldg)
                if self.bldg_usage != bldg_usage:
                    eligibility = False
                    
            if eligibility == True:
                eligible_bldg_list.append(gml_bldg)
                
            if eligibility == False:
                non_eligible_bldg_list.append(gml_bldg)
                
        return eligible_bldg_list, non_eligible_bldg_list
        
    def define_int_range(self, start, stop, step):
        """ 
        The function defines the range of the parameter if the parameter type is integer.
        
        Parameters
        ----------
        start : int
            The starting number of the sequence.
        
        stop : int
            Generate numbers up to, including this number.
        
        step : int
            The difference between each number in the sequence.
        
        Returns
        -------        
        parameter range : list of ints
            List of generated parameters.
        """
        parm_range = super(BldgFlrAreaHeightParm, self).define_int_range(start, stop, step)
        self.parm_range = parm_range
        return parm_range
        
    def define_float_range(self, start, stop, step=None):
        """ 
        The function defines the range of the parameter if the parameter type is float.
        
        Parameters
        ----------
        start : float
            The starting number of the sequence.
        
        stop : float
            Generate numbers up to, including this number.
        
        step : float, optional
            The difference between each number in the sequence, default = None. When None the parameter is a continuous parameter, if not None the parameter is a discrete parameter.
        
        Returns
        -------        
        parameter range : list of floats
            List of generated float parameters if step = None, if step != None the parameter range is made up of two numbers the start and the end of the continuous parameter.
        """
        parm_range = super(BldgFlrAreaHeightParm, self).define_float_range(start, stop, step=step)
        self.parm_range = parm_range
        return parm_range
        
    def set_parm_range(self, parm_range):
        """ 
        The function defines the range of the parameter .
        
        Parameters
        ----------
        parm_range : list of ints/floats
            The parameter range.
        """
        self.parm_range = parm_range
        
    def map_nrmlise_parms_2_parms(self, nrmlised_parm_list):
        """ 
        The function maps the the normalise parameter list to the real parameter list.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        parameter list : list of int/floats
            List of real parameters.
        """
        if self.parm_range == None:
            raise Exception("please define parm range")
        parm_list = super(BldgFlrAreaHeightParm, self).map_nrmlise_parms_2_parms(nrmlised_parm_list)
        return parm_list
        
    def define_nparameters(self,pycitygml_reader):
        """ 
        The function determines the total parameters for parameterising the model.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        nparameters : int
            The number of parameters for the model.
        """
        gml_bldg_list = pycitygml_reader.get_buildings()
        #filter through the eligible buildings
        eligible_bldg_list, non_eligible_bldg_list = self.eligibility_test(gml_bldg_list, pycitygml_reader)
        #because each building has one building height parameter
        nparameters = len(eligible_bldg_list)
        return nparameters
                
    def execute(self, pycitygml_reader, nrmlised_parm_list):
        """ 
        This funciton defines the parameterisation process and executes the process. A design alternative of the parametric model is returned.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
        
        nrmlised_parm_list : list of ints/floats
            The normalised parameters to be mapped to the real parameters defined, the parameters will be used to generate a design alternative.
            
        Returns
        -------        
        new pycitygml_reader : pycitygml.Reader class instance
            The new design alternative generated and documented as a CityGML model.
        """
        parm_list = self.map_nrmlise_parms_2_parms(nrmlised_parm_list)
        citygml_writer = pycitygml.Writer()
        gml_landuses = pycitygml_reader.get_landuses()
        gml_bldg_list = pycitygml_reader.get_buildings()
        bcnt = 0
        for gml_landuse in gml_landuses:
            #echeck which buildings are on this plot
            gml_bldg_on_luse = gml3dmodel.buildings_on_landuse(gml_landuse,gml_bldg_list, pycitygml_reader)
            
            #check which buildings should this parameter be applied to
            eligibility_bldg_list, non_eligible_bldg_list = self.eligibility_test(gml_bldg_on_luse, pycitygml_reader)
            n_eligibility_bldgs = len(eligibility_bldg_list)
            
            #calculate the total landuse floor area
            luse_flr_area = 0
            for eligible_gml_bldg in eligibility_bldg_list:
                height, nstorey, storey_height = gml3dmodel.get_building_height_storey(eligible_gml_bldg, pycitygml_reader)
                bldg_flr_area, flrplates = gml3dmodel.get_bulding_floor_area(eligible_gml_bldg, nstorey, storey_height, pycitygml_reader)
                luse_flr_area += bldg_flr_area
               
            #get the parameters for this landuse plot
            parms_4_luse = parm_list[bcnt:bcnt+n_eligibility_bldgs]
            total_prop = float(sum(parms_4_luse))
            
            #redistribute the flr area
            new_bldg_flr_area_list = []
            for parm in parms_4_luse:
                new_bldg_flr_area = float(parm)/total_prop * luse_flr_area
                new_bldg_flr_area_list.append(new_bldg_flr_area)
                
            #reconstuct the buildings according to the new distribuition
            for cnt in range(n_eligibility_bldgs):
                gml_bldg = eligibility_bldg_list[cnt]
                bldg_occsolid = gml3dmodel.get_building_occsolid(gml_bldg,pycitygml_reader)
                height, nstorey, storey_height = gml3dmodel.get_building_height_storey(gml_bldg, pycitygml_reader)
                new_bldg_flr_area = new_bldg_flr_area_list[cnt]
                new_building_solid = gml3dmodel.construct_building_through_floorplates(bldg_occsolid,new_bldg_flr_area,storey_height)
                new_height, new_n_storey = gml3dmodel.calculate_bldg_height_n_nstorey(new_building_solid, storey_height)
                gml3dmodel.update_gml_building(gml_bldg,new_building_solid, pycitygml_reader, 
                                               citygml_writer, new_height = new_height, new_nstorey = new_n_storey)
                
            bcnt += n_eligibility_bldgs
        
        non_bldg_cityobjs = pycitygml_reader.get_non_xtype_cityobject("bldg:Building")
        gml3dmodel.write_citygml(non_bldg_cityobjs, citygml_writer)
        gml3dmodel.write_non_eligible_bldgs(non_eligible_bldg_list, citygml_writer)
        citymodel_node = citygml_writer.citymodelnode
        reader = pycitygml.Reader()
        reader.load_citymodel_node(citymodel_node)
        return reader
    
class BldgHeightParm(BaseParm):
    """
    An implementation of the BaseParm class for parameterising the massing of buildings (LOD1) in terms of its height.
    
    Attributes
    ----------    
    bldg_class : str
        The string of the gml code for building class.
    
    bldg_function : str
        The string of the gml code for building function.
        
    bldg_usage : str
        The string of the gml code for building usage.
        
    parm_range : list of floats/ints
        The list of possible parameters.
    """
    def __init__(self):
        """Initialise the class"""
        self.bldg_class = None
        self.bldg_function = None
        self.bldg_usage = None
        self.parm_range = None
        
    def apply_2_bldg_class(self, bldg_class):
        """
        This function declares the building class that will have this parameter, buildings which is not this class will not be parameterised.
        
        Parameters
        ----------     
        bldg_class : str
            The string of the gml code for building class.
        """
        self.bldg_class = bldg_class
        
    def apply_2_bldg_function(self, bldg_function):
        """
        This function declares the building function that will have this parameter, buildings which is not this function will not be parameterised.
        
        Parameters
        ----------     
        bldg_function : str
            The string of the gml code for building function.
        """
        self.bldg_function = bldg_function
        
    def apply_2_bldg_usage(self, bldg_usage):
        """
        This function declares the building usage that will have this parameter, buildings which is not this usage will not be parameterised.
        
        Parameters
        ----------     
        bldg_usage : str
            The string of the gml code for building usage.
        """
        self.bldg_usage = bldg_usage
        
    def eligibility_test(self, gml_bldg_list, pycitygml_reader):
        """ 
        The function checks which are the buildings that are eligible to be parameterised.
        
        Parameters
        ----------
        gml_bldg_list : list of lxml.etree Element 
            The GML building to be parameterised.
            
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        eligible_bldg_list : list of lxml.etree Element 
            The GML building to be parameterised.
        
        non_eligible_bldg_list : list of lxml.etree Element 
            The GML building that will not be parameterised.
        """
        eligible_bldg_list = []
        non_eligible_bldg_list = []
        for gml_bldg in gml_bldg_list:
            eligibility = True
            if self.bldg_class != None: 
                bldg_class = pycitygml_reader.get_building_class(gml_bldg)
                if self.bldg_class != bldg_class:
                    eligibility = False
                    
            if self.bldg_function != None:
                bldg_function = pycitygml_reader.get_building_function(gml_bldg)
                if self.bldg_function != bldg_function:
                    eligibility = False
            
            if self.bldg_usage != None:
                bldg_usage = pycitygml_reader.get_building_usage(gml_bldg)
                if self.bldg_usage != bldg_usage:
                    eligibility = False
                    
            if eligibility == True:
                eligible_bldg_list.append(gml_bldg)
                
            if eligibility == False:
                non_eligible_bldg_list.append(gml_bldg)
                
        return eligible_bldg_list, non_eligible_bldg_list
        
    def define_int_range(self, start, stop, step):
        """ 
        The function defines the range of the parameter if the parameter type is integer.
        
        Parameters
        ----------
        start : int
            The starting number of the sequence.
        
        stop : int
            Generate numbers up to, including this number.
        
        step : int
            The difference between each number in the sequence.
        
        Returns
        -------        
        parameter range : list of ints
            List of generated parameters.
        """
        parm_range = super(BldgHeightParm, self).define_int_range(start, stop, step)
        self.parm_range = parm_range
        return parm_range
        
    def define_float_range(self, start, stop, step=None):
        """ 
        The function defines the range of the parameter if the parameter type is float.
        
        Parameters
        ----------
        start : float
            The starting number of the sequence.
        
        stop : float
            Generate numbers up to, including this number.
        
        step : float, optional
            The difference between each number in the sequence, default = None. When None the parameter is a continuous parameter, if not None the parameter is a discrete parameter.
        
        Returns
        -------        
        parameter range : list of floats
            List of generated float parameters if step = None, if step != None the parameter range is made up of two numbers the start and the end of the continuous parameter.
        """
        parm_range = super(BldgHeightParm, self).define_float_range(start, stop, step=step)
        self.parm_range = parm_range
        return parm_range
        
    def set_parm_range(self, parm_range):
        """ 
        The function defines the range of the parameter .
        
        Parameters
        ----------
        parm_range : list of ints/floats
            The parameter range.
        """
        self.parm_range = parm_range
        
    def map_nrmlise_parms_2_parms(self, nrmlised_parm_list):
        """ 
        The function maps the the normalise parameter list to the real parameter list.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        parameter list : list of int/floats
            List of real parameters.
        """
        if self.parm_range == None:
            raise Exception("please define parm range")
        parm_list = super(BldgHeightParm, self).map_nrmlise_parms_2_parms(nrmlised_parm_list)
        return parm_list
        
    def define_nparameters(self,pycitygml_reader):
        """ 
        The function determines the total parameters for parameterising the model.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        nparameters : int
            The number of parameters for the model.
        """
        gml_bldg_list = pycitygml_reader.get_buildings()
        #filter through the eligible buildings
        eligible_bldg_list, non_eligible_bldg_list = self.eligibility_test(gml_bldg_list, pycitygml_reader)
        #because each building has one building height parameter
        nparameters = len(eligible_bldg_list)
        return nparameters
                
    def execute(self, pycitygml_reader, nrmlised_parm_list):
        """ 
        This funciton defines the parameterisation process and executes the process. A design alternative of the parametric model is returned.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
        
        nrmlised_parm_list : list of ints/floats
            The normalised parameters to be mapped to the real parameters defined, the parameters will be used to generate a design alternative.
            
        Returns
        -------        
        new pycitygml_reader : pycitygml.Reader class instance
            The new design alternative generated and documented as a CityGML model.
        """
        parm_list = self.map_nrmlise_parms_2_parms(nrmlised_parm_list)
        citygml_writer = pycitygml.Writer()
        gml_landuses = pycitygml_reader.get_landuses()
        gml_bldg_list = pycitygml_reader.get_buildings()
        bcnt = 0
        for gml_landuse in gml_landuses:
            #echeck which buildings are on this plot
            gml_bldg_on_luse = gml3dmodel.buildings_on_landuse(gml_landuse,gml_bldg_list, pycitygml_reader)
            
            #check which buildings should this parameter be applied to
            eligibility_bldg_list, non_eligible_bldg_list = self.eligibility_test(gml_bldg_on_luse, pycitygml_reader)
            n_eligibility_bldgs = len(eligibility_bldg_list)
            
            #get the parameters for this landuse plot
            parms_4_luse = parm_list[bcnt:bcnt+n_eligibility_bldgs]
            
            #change the bldgs height 
            bcnt = 0
            for eligible_gml_bldg in eligibility_bldg_list:
                #get the height parm for the bldg
                height_parm = parms_4_luse[bcnt]
                
                #extract the bldg solid
                bldg_solid = gml3dmodel.get_building_occsolid(eligible_gml_bldg, pycitygml_reader)
                print 'OCCSOLID', bldg_solid
                #change the height of each bldg according to the parameter
                height, nstorey, storey_height = gml3dmodel.get_building_height_storey(eligible_gml_bldg, pycitygml_reader)
                bldg_bounding_footprint =  gml3dmodel.get_building_bounding_footprint(bldg_solid)
                midpt = py3dmodel.calculate.face_midpt(bldg_bounding_footprint)
                height_ratio = float(height_parm)/height
                scaled_bldg = py3dmodel.modify.uniform_scale(bldg_solid,1,1,height_ratio,midpt)
                new_bldg_occsolid = py3dmodel.fetch.geom_explorer(scaled_bldg, "solid")[0]
                #py3dmodel.construct.visualise([[new_bldg_occsolid]], ["WHITE"])
                
                new_height, new_n_storey = gml3dmodel.calculate_bldg_height_n_nstorey(new_bldg_occsolid, storey_height)
                
                gml3dmodel.update_gml_building(eligible_gml_bldg,new_bldg_occsolid, pycitygml_reader, 
                                               citygml_writer, new_height = new_height, new_nstorey = new_n_storey)
                
                bcnt+=1
                
        non_bldg_cityobjs = pycitygml_reader.get_non_xtype_cityobject("bldg:Building")
        gml3dmodel.write_citygml(non_bldg_cityobjs, citygml_writer)
        gml3dmodel.write_non_eligible_bldgs(non_eligible_bldg_list, citygml_writer)
        citymodel_node = citygml_writer.citymodelnode
        reader = pycitygml.Reader()
        reader.load_citymodel_node(citymodel_node)
        return reader
        
class BldgOrientationParm(BaseParm):
    """
    An implementation of the BaseParm class for parameterising the massing of buildings (LOD1) in terms of its orientation.
    
    Attributes
    ----------    
    bldg_class : str
        The string of the gml code for building class.
    
    bldg_function : str
        The string of the gml code for building function.
        
    bldg_usage : str
        The string of the gml code for building usage.
        
    parm_range : list of floats/ints
        The list of possible parameters.
        
    clash_detection : bool
        True or False, if True the design alternative is not allowed to clash with any other buildings, if clashes occur the original building is returned.
        
    boundary_detection : bool
        True or False, if True the design alternative is not allowed to be outside the plot boundary, if outside the original building is returned.
    """
    def __init__(self):
        """Initialise the class"""
        self.bldg_class = None
        self.bldg_function = None
        self.bldg_usage = None
        self.parm_range = None
        self.clash_detection = True
        self.boundary_detection = True
        
    def apply_2_bldg_class(self, bldg_class):
        """
        This function declares the building class that will have this parameter, buildings which is not this class will not be parameterised.
        
        Parameters
        ----------     
        bldg_class : str
            The string of the gml code for building class.
        """
        self.bldg_class = bldg_class
        
    def apply_2_bldg_function(self, bldg_function):
        """
        This function declares the building function that will have this parameter, buildings which is not this function will not be parameterised.
        
        Parameters
        ----------     
        bldg_function : str
            The string of the gml code for building function.
        """
        self.bldg_function = bldg_function
        
    def apply_2_bldg_usage(self, bldg_usage):
        """
        This function declares the building usage that will have this parameter, buildings which is not this usage will not be parameterised.
        
        Parameters
        ----------     
        bldg_usage : str
            The string of the gml code for building usage.
        """
        self.bldg_usage = bldg_usage
        
    def eligibility_test(self, gml_bldg_list, pycitygml_reader):
        """ 
        The function checks which are the buildings that are eligible to be parameterised.
        
        Parameters
        ----------
        gml_bldg_list : list of lxml.etree Element 
            The GML building to be parameterised.
            
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        eligible_bldg_list : list of lxml.etree Element 
            The GML building to be parameterised.
        
        non_eligible_bldg_list : list of lxml.etree Element 
            The GML building that will not be parameterised.
        """
        eligible_bldg_list = []
        non_eligible_bldg_list = []
        for gml_bldg in gml_bldg_list:
            eligibility = True
            if self.bldg_class != None: 
                bldg_class = pycitygml_reader.get_building_class(gml_bldg)
                if self.bldg_class != bldg_class:
                    eligibility = False
                    
            if self.bldg_function != None:
                bldg_function = pycitygml_reader.get_building_function(gml_bldg)
                if self.bldg_function != bldg_function:
                    eligibility = False
            
            if self.bldg_usage != None:
                bldg_usage = pycitygml_reader.get_building_usage(gml_bldg)
                if self.bldg_usage != bldg_usage:
                    eligibility = False
                    
            if eligibility == True:
                eligible_bldg_list.append(gml_bldg)
                
            if eligibility == False:
                non_eligible_bldg_list.append(gml_bldg)
                
        return eligible_bldg_list, non_eligible_bldg_list
        
    def set_clash_detection(self, true_or_false):
        """ 
        The function declares the clash detection to be True or False.
        
        Parameters
        ----------
        true_or_false : bool
            True or False, if True the design alternative is not allowed to clash with any other buildings, if clashes occur the original building is returned.
        """
        self.clash_detection = true_or_false
        
    def set_boundary_detection(self, true_or_false):
        """ 
        The function declares the boundary detection to be True or False.
        
        Parameters
        ----------
        true_or_false : bool
            True or False, if True the design alternative is not allowed to be outside the plot boundary, if outside the original building is returned.
        """
        self.boundary_detection = true_or_false
        
    def define_int_range(self, start, stop, step):
        """ 
        The function defines the range of the parameter if the parameter type is integer.
        
        Parameters
        ----------
        start : int
            The starting number of the sequence.
        
        stop : int
            Generate numbers up to, including this number.
        
        step : int
            The difference between each number in the sequence.
        
        Returns
        -------        
        parameter range : list of ints
            List of generated parameters.
        """
        parm_range = super(BldgOrientationParm, self).define_int_range(start, stop, step)
        self.parm_range = parm_range
        return parm_range
        
    def define_float_range(self, start, stop, step=None):
        """ 
        The function defines the range of the parameter if the parameter type is float.
        
        Parameters
        ----------
        start : float
            The starting number of the sequence.
        
        stop : float
            Generate numbers up to, including this number.
        
        step : float, optional
            The difference between each number in the sequence, default = None. When None the parameter is a continuous parameter, if not None the parameter is a discrete parameter.
        
        Returns
        -------        
        parameter range : list of floats
            List of generated float parameters if step = None, if step != None the parameter range is made up of two numbers the start and the end of the continuous parameter.
        """
        parm_range = super(BldgOrientationParm, self).define_float_range(start, stop, step=step)
        self.parm_range = parm_range
        return parm_range
        
    def set_parm_range(self, parm_range):
        """ 
        The function defines the range of the parameter .
        
        Parameters
        ----------
        parm_range : list of ints/floats
            The parameter range.
        """
        self.parm_range = parm_range
        
    def map_nrmlise_parms_2_parms(self, nrmlised_parm_list):
        """ 
        The function maps the the normalise parameter list to the real parameter list.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        parameter list : list of int/floats
            List of real parameters.
        """
        if self.parm_range == None:
            raise Exception("please define parm range")
        parm_list = super(BldgOrientationParm, self).map_nrmlise_parms_2_parms(nrmlised_parm_list)
        return parm_list
        
    def define_nparameters(self,pycitygml_reader):
        """ 
        The function determines the total parameters for parameterising the model.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        nparameters : int
            The number of parameters for the model.
        """
        gml_bldg_list = pycitygml_reader.get_buildings()
        #filter through the eligible buildings
        eligible_bldg_list, non_eligible_bldg_list = self.eligibility_test(gml_bldg_list, pycitygml_reader)
        #because each building has one building height parameter
        nparameters = len(eligible_bldg_list)
        return nparameters
                
    def execute(self, pycitygml_reader, nrmlised_parm_list):
        """ 
        This funciton defines the parameterisation process and executes the process. A design alternative of the parametric model is returned.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
        
        nrmlised_parm_list : list of ints/floats
            The normalised parameters to be mapped to the real parameters defined, the parameters will be used to generate a design alternative.
            
        Returns
        -------        
        new pycitygml_reader : pycitygml.Reader class instance
            The new design alternative generated and documented as a CityGML model.
        """
        parm_list = self.map_nrmlise_parms_2_parms(nrmlised_parm_list)
        citygml_writer = pycitygml.Writer()
        gml_landuses = pycitygml_reader.get_landuses()
        gml_bldg_list = pycitygml_reader.get_buildings()
        bcnt = 0
        for gml_landuse in gml_landuses:
            #echeck which buildings are on this plot
            gml_bldg_on_luse = gml3dmodel.buildings_on_landuse(gml_landuse,gml_bldg_list, pycitygml_reader)
            
            #check which buildings should this parameter be applied to
            eligibility_bldg_list, non_eligible_bldg_list = self.eligibility_test(gml_bldg_on_luse, pycitygml_reader)
            n_eligibility_bldgs = len(eligibility_bldg_list)
            
            #get the parameters for this landuse plot
            parms_4_luse = parm_list[bcnt:bcnt+n_eligibility_bldgs]
            luse_occface = gml3dmodel.gml_landuse_2_occface(gml_landuse, pycitygml_reader)
            #get all the bldg_occsolid 
            roting_bldg_occsolid_list = []
            for gml_bldg in eligibility_bldg_list:
                bldg_occsolid = gml3dmodel.get_building_occsolid(gml_bldg, pycitygml_reader)
                roting_bldg_occsolid_list.append(bldg_occsolid)
             
            non_roting_bldg_occsolid_list = []
            for non_gml_bldg in non_eligible_bldg_list:
                non_bldg_occsolid = gml3dmodel.get_building_occsolid(non_gml_bldg, pycitygml_reader)
                non_roting_bldg_occsolid_list.append(non_bldg_occsolid)
                
            #rotate the buildings
            for cnt in range(n_eligibility_bldgs):
                eligible_gml_bldg = eligibility_bldg_list[cnt]
                rot_angle = parms_4_luse[cnt]
                rot_bldg_occsolid = gml3dmodel.rotate_bldg(eligible_gml_bldg, rot_angle, pycitygml_reader)
                roting_bldg_occsolid_list2 = roting_bldg_occsolid_list[:]
                del roting_bldg_occsolid_list2[cnt]
                roting_bldg_occsolid_list2.extend(non_roting_bldg_occsolid_list)
                
                
                if self.clash_detection == True and self.boundary_detection == False:
                    clash_detected = gml3dmodel.detect_clash(rot_bldg_occsolid, roting_bldg_occsolid_list2)
                    if not clash_detected:
                        #there is no clash
                        roting_bldg_occsolid_list[cnt] = rot_bldg_occsolid
                        
                elif self.boundary_detection == True and self.clash_detection == False:
                    is_in_boundary = gml3dmodel.detect_in_boundary(rot_bldg_occsolid, luse_occface)
                    if is_in_boundary:
                        #it is within the boundary
                        roting_bldg_occsolid_list[cnt] = rot_bldg_occsolid
                
                elif self.boundary_detection == True and self.clash_detection == True:
                    clash_detected = gml3dmodel.detect_clash(rot_bldg_occsolid, roting_bldg_occsolid_list2)
                    is_in_boundary = gml3dmodel.detect_in_boundary(rot_bldg_occsolid, luse_occface)
                    if not clash_detected and is_in_boundary:
                        roting_bldg_occsolid_list[cnt] = rot_bldg_occsolid
                        
                elif self.clash_detection == False and self.boundary_detection == False:
                    roting_bldg_occsolid_list[cnt] = rot_bldg_occsolid
            
            for up_cnt in range(n_eligibility_bldgs):
                gml_bldg = eligibility_bldg_list[up_cnt]
                new_building_solid = roting_bldg_occsolid_list[up_cnt]
                gml3dmodel.update_gml_building(gml_bldg,new_building_solid, pycitygml_reader, 
                                               citygml_writer)

            bcnt += n_eligibility_bldgs
        
        non_bldg_cityobjs = pycitygml_reader.get_non_xtype_cityobject("bldg:Building")
        gml3dmodel.write_citygml(non_bldg_cityobjs, citygml_writer)
        gml3dmodel.write_non_eligible_bldgs(non_eligible_bldg_list, citygml_writer)
        citymodel_node = citygml_writer.citymodelnode
        reader = pycitygml.Reader()
        reader.load_citymodel_node(citymodel_node)
        return reader
        
class BldgPositionParm(BaseParm):
    """
    An implementation of the BaseParm class for parameterising the massing of buildings (LOD1) in terms of its position.
    
    Attributes
    ----------    
    bldg_class : str
        The string of the gml code for building class.
    
    bldg_function : str
        The string of the gml code for building function.
        
    bldg_usage : str
        The string of the gml code for building usage.
        
    parm_range : list of floats/ints
        The list of possible parameters.
        
    clash_detection : bool
        True or False, if True the design alternative is not allowed to clash with any other buildings, if clashes occur the original building is returned.
        
    boundary_detection : bool
        True or False, if True the design alternative is not allowed to be outside the plot boundary, if outside the original building is returned.
    
    xdim : int
        The x-dimension of the gridded plot. The higher the dimension the more positions there are for the building.
        
    ydim : int
        The y-dimension of the gridded plot. The higher the dimension the more positions there are for the building.
    """
    def __init__(self):
        """Initialise the class"""
        self.bldg_class = None
        self.bldg_function = None
        self.bldg_usage = None
        self.parm_range = None
        self.clash_detection = True
        self.boundary_detection = True
        self.xdim = 10
        self.ydim = 10
        
    def apply_2_bldg_class(self, bldg_class):
        """
        This function declares the building class that will have this parameter, buildings which is not this class will not be parameterised.
        
        Parameters
        ----------     
        bldg_class : str
            The string of the gml code for building class.
        """
        self.bldg_class = bldg_class
        
    def apply_2_bldg_function(self, bldg_function):
        """
        This function declares the building function that will have this parameter, buildings which is not this function will not be parameterised.
        
        Parameters
        ----------     
        bldg_function : str
            The string of the gml code for building function.
        """
        self.bldg_function = bldg_function
        
    def apply_2_bldg_usage(self, bldg_usage):
        """
        This function declares the building usage that will have this parameter, buildings which is not this usage will not be parameterised.
        
        Parameters
        ----------     
        bldg_usage : str
            The string of the gml code for building usage.
        """
        self.bldg_usage = bldg_usage
        
    def eligibility_test(self, gml_bldg_list, pycitygml_reader):
        """ 
        The function checks which are the buildings that are eligible to be parameterised.
        
        Parameters
        ----------
        gml_bldg_list : list of lxml.etree Element 
            The GML building to be parameterised.
            
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        eligible_bldg_list : list of lxml.etree Element 
            The GML building to be parameterised.
        
        non_eligible_bldg_list : list of lxml.etree Element 
            The GML building that will not be parameterised.
        """
        eligible_bldg_list = []
        non_eligible_bldg_list = []
        for gml_bldg in gml_bldg_list:
            eligibility = True
            if self.bldg_class != None: 
                bldg_class = pycitygml_reader.get_building_class(gml_bldg)
                if self.bldg_class != bldg_class:
                    eligibility = False
                    
            if self.bldg_function != None:
                bldg_function = pycitygml_reader.get_building_function(gml_bldg)
                if self.bldg_function != bldg_function:
                    eligibility = False
            
            if self.bldg_usage != None:
                bldg_usage = pycitygml_reader.get_building_usage(gml_bldg)
                if self.bldg_usage != bldg_usage:
                    eligibility = False
                    
            if eligibility == True:
                eligible_bldg_list.append(gml_bldg)
                
            if eligibility == False:
                non_eligible_bldg_list.append(gml_bldg)
                
        return eligible_bldg_list, non_eligible_bldg_list
        
    def set_clash_detection(self, true_or_false):
        """ 
        The function declares the clash detection to be True or False.
        
        Parameters
        ----------
        true_or_false : bool
            True or False, if True the design alternative is not allowed to clash with any other buildings, if clashes occur the original building is returned.
        """
        self.clash_detection = true_or_false
        
    def set_boundary_detection(self, true_or_false):
        """ 
        The function declares the boundary detection to be True or False.
        
        Parameters
        ----------
        true_or_false : bool
            True or False, if True the design alternative is not allowed to be outside the plot boundary, if outside the original building is returned.
        """
        self.boundary_detection = true_or_false
        
    def set_xdim_ydim(self, xdim, ydim):
        """ 
        The function sets the xdim and ydim of the gridded plot the building is on.
        
        Parameters
        ----------
        xdim : int
            The x-dimension of the gridded plot. The higher the dimension the more positions there are for the building.
        
        ydim : int
            The y-dimension of the gridded plot. The higher the dimension the more positions there are for the building.
        """
        self.xdim = xdim
        self.ydim = ydim
        
    def define_int_range(self, start, stop, step):
        """ 
        The function defines the range of the parameter if the parameter type is integer.
        
        Parameters
        ----------
        start : int
            The starting number of the sequence.
        
        stop : int
            Generate numbers up to, including this number.
        
        step : int
            The difference between each number in the sequence.
        
        Returns
        -------        
        parameter range : list of ints
            List of generated parameters.
        """
        parm_range = super(BldgPositionParm, self).define_int_range(start, stop, step)
        self.parm_range = parm_range
        return parm_range
        
    def define_float_range(self, start, stop, step=None):
        """ 
        The function defines the range of the parameter if the parameter type is float.
        
        Parameters
        ----------
        start : float
            The starting number of the sequence.
        
        stop : float
            Generate numbers up to, including this number.
        
        step : float, optional
            The difference between each number in the sequence, default = None. When None the parameter is a continuous parameter, if not None the parameter is a discrete parameter.
        
        Returns
        -------        
        parameter range : list of floats
            List of generated float parameters if step = None, if step != None the parameter range is made up of two numbers the start and the end of the continuous parameter.
        """
        parm_range = super(BldgPositionParm, self).define_float_range(start, stop, step=step)
        self.parm_range = parm_range
        return parm_range
        
    def set_parm_range(self, parm_range):
        """ 
        The function defines the range of the parameter .
        
        Parameters
        ----------
        parm_range : list of ints/floats
            The parameter range.
        """
        self.parm_range = parm_range
        
    def map_nrmlise_parms_2_parms(self, nrmlised_parm_list):
        """ 
        The function maps the the normalise parameter list to the real parameter list.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        parameter list : list of int/floats
            List of real parameters.
        """
        if self.parm_range == None:
            raise Exception("please define parm range")
        parm_list = super(BldgPositionParm, self).map_nrmlise_parms_2_parms(nrmlised_parm_list)
        return parm_list
        
    def define_nparameters(self,pycitygml_reader):
        """ 
        The function determines the total parameters for parameterising the model.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        nparameters : int
            The number of parameters for the model.
        """
        gml_bldg_list = pycitygml_reader.get_buildings()
        #filter through the eligible buildings
        eligible_bldg_list, non_eligible_bldg_list = self.eligibility_test(gml_bldg_list, pycitygml_reader)
        #because each building has one building height parameter
        nparameters = len(eligible_bldg_list)
        return nparameters
                
    def execute(self, pycitygml_reader, nrmlised_parm_list):
        """ 
        This funciton defines the parameterisation process and executes the process. A design alternative of the parametric model is returned.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
        
        nrmlised_parm_list : list of ints/floats
            The normalised parameters to be mapped to the real parameters defined, the parameters will be used to generate a design alternative.
            
        Returns
        -------        
        new pycitygml_reader : pycitygml.Reader class instance
            The new design alternative generated and documented as a CityGML model.
        """
        citygml_writer = pycitygml.Writer()
        gml_landuses = pycitygml_reader.get_landuses()
        gml_bldg_list = pycitygml_reader.get_buildings()
        bcnt = 0
        for gml_landuse in gml_landuses:
            #echeck which buildings are on this plot
            gml_bldg_on_luse = gml3dmodel.buildings_on_landuse(gml_landuse,gml_bldg_list, pycitygml_reader)
            
            #check which buildings should this parameter be applied to
            eligibility_bldg_list, non_eligible_bldg_list  = self.eligibility_test(gml_bldg_on_luse, pycitygml_reader)
            n_eligibility_bldgs = len(eligibility_bldg_list)
            
            #grid the plot
            luse_occface = gml3dmodel.gml_landuse_2_occface(gml_landuse, pycitygml_reader)
            pypt_list, grid_faces = gml3dmodel.landuse_2_grid(luse_occface, self.xdim, self.ydim)
            npypt_list = len(pypt_list)
            self.define_int_range(0, npypt_list-1, 1)
            
            #get the parameters for this landuse plot
            nrmlised_parms_4_luse = nrmlised_parm_list[bcnt:bcnt+n_eligibility_bldgs]
            parms_4_luse = self.map_nrmlise_parms_2_parms(nrmlised_parms_4_luse)
            
            bldg_occsolid_list = []
            #get all the occsolid of the buildings
            for eligible_gml_bldg in eligibility_bldg_list:
                bldg_occsolid = gml3dmodel.get_building_occsolid(eligible_gml_bldg, pycitygml_reader)
                bldg_occsolid_list.append(bldg_occsolid)
            
            non_bldg_occsolid_list = []
            for non_eligible_gml_bldg in non_eligible_bldg_list:
                non_bldg_occsolid = gml3dmodel.get_building_occsolid(non_eligible_gml_bldg, pycitygml_reader)
                non_bldg_occsolid_list.append(non_bldg_occsolid)
                
            posed_bldg_occsolid_list = gml3dmodel.rearrange_building_position(bldg_occsolid_list, pypt_list, luse_occface, parms_4_luse,
                                                                              other_occsolids = non_bldg_occsolid_list, 
                                                                              clash_detection = self.clash_detection, 
                                                                              boundary_detection = self.boundary_detection)
            
            for up_cnt in range(n_eligibility_bldgs):
                gml_bldg = eligibility_bldg_list[up_cnt]
                new_building_solid = posed_bldg_occsolid_list[up_cnt]
                gml3dmodel.update_gml_building(gml_bldg,new_building_solid, pycitygml_reader, 
                                               citygml_writer)

            bcnt += n_eligibility_bldgs
        
        non_bldg_cityobjs = pycitygml_reader.get_non_xtype_cityobject("bldg:Building")
        gml3dmodel.write_citygml(non_bldg_cityobjs, citygml_writer)
        gml3dmodel.write_non_eligible_bldgs(non_eligible_bldg_list, citygml_writer)
        citymodel_node = citygml_writer.citymodelnode
        reader = pycitygml.Reader()
        reader.load_citymodel_node(citymodel_node)
        return reader
    
class BldgTwistParm(BaseParm):
    """
    An implementation of the BaseParm class for parameterising the massing of buildings (LOD1) in terms of its geometry. This parameter will gradually twist the building solid according to the 
    twist parameter.
    
    Attributes
    ----------    
    bldg_class : str
        The string of the gml code for building class.
    
    bldg_function : str
        The string of the gml code for building function.
        
    bldg_usage : str
        The string of the gml code for building usage.
        
    parm_range : list of floats/ints
        The list of possible parameters.
    
    flr2flr_height : float
        The assumed floor to floor height of the building, default = 3m.
    """
    def __init__(self):
        """Initialise the class"""
        self.bldg_class = None
        self.bldg_function = None
        self.bldg_usage = None
        self.parm_range = None
        self.flr2flr_height = 3
        
    def define_flr2flr_height(self, flr2flr_height):
        """ 
        The function define the floor to floor height of the buildings to be parameterised.
        
        Parameters
        ----------
        flr2flr_height : float
            The assumed floor to floor height of the building.
        """
        self.flr2flr_height = flr2flr_height
        
    def apply_2_bldg_class(self, bldg_class):
        """
        This function declares the building class that will have this parameter, buildings which is not this class will not be parameterised.
        
        Parameters
        ----------     
        bldg_class : str
            The string of the gml code for building class.
        """
        self.bldg_class = bldg_class
        
    def apply_2_bldg_function(self, bldg_function):
        """
        This function declares the building function that will have this parameter, buildings which is not this function will not be parameterised.
        
        Parameters
        ----------     
        bldg_function : str
            The string of the gml code for building function.
        """
        self.bldg_function = bldg_function
        
    def apply_2_bldg_usage(self, bldg_usage):
        """
        This function declares the building usage that will have this parameter, buildings which is not this usage will not be parameterised.
        
        Parameters
        ----------     
        bldg_usage : str
            The string of the gml code for building usage.
        """
        self.bldg_usage = bldg_usage
        
    def eligibility_test(self, gml_bldg_list, pycitygml_reader):
        """ 
        The function checks which are the buildings that are eligible to be parameterised.
        
        Parameters
        ----------
        gml_bldg_list : list of lxml.etree Element 
            The GML building to be parameterised.
            
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        eligible_bldg_list : list of lxml.etree Element 
            The GML building to be parameterised.
        
        non_eligible_bldg_list : list of lxml.etree Element 
            The GML building that will not be parameterised.
        """
        eligible_bldg_list = []
        non_eligible_bldg_list = []
        for gml_bldg in gml_bldg_list:
            eligibility = True
            if self.bldg_class != None: 
                bldg_class = pycitygml_reader.get_building_class(gml_bldg)
                if self.bldg_class != bldg_class:
                    eligibility = False
                    
            if self.bldg_function != None:
                bldg_function = pycitygml_reader.get_building_function(gml_bldg)
                if self.bldg_function != bldg_function:
                    eligibility = False
            
            if self.bldg_usage != None:
                bldg_usage = pycitygml_reader.get_building_usage(gml_bldg)
                if self.bldg_usage != bldg_usage:
                    eligibility = False
                    
            if eligibility == True:
                eligible_bldg_list.append(gml_bldg)
                
            if eligibility == False:
                non_eligible_bldg_list.append(gml_bldg)
                
        return eligible_bldg_list, non_eligible_bldg_list
        
    def define_int_range(self, start, stop, step):
        """ 
        The function defines the range of the parameter if the parameter type is integer.
        
        Parameters
        ----------
        start : int
            The starting number of the sequence.
        
        stop : int
            Generate numbers up to, including this number.
        
        step : int
            The difference between each number in the sequence.
        
        Returns
        -------        
        parameter range : list of ints
            List of generated parameters.
        """
        parm_range = super(BldgTwistParm, self).define_int_range(start, stop, step)
        self.parm_range = parm_range
        return parm_range
        
    def define_float_range(self, start, stop, step=None):
        """ 
        The function defines the range of the parameter if the parameter type is float.
        
        Parameters
        ----------
        start : float
            The starting number of the sequence.
        
        stop : float
            Generate numbers up to, including this number.
        
        step : float, optional
            The difference between each number in the sequence, default = None. When None the parameter is a continuous parameter, if not None the parameter is a discrete parameter.
        
        Returns
        -------        
        parameter range : list of floats
            List of generated float parameters if step = None, if step != None the parameter range is made up of two numbers the start and the end of the continuous parameter.
        """
        parm_range = super(BldgTwistParm, self).define_float_range(start, stop, step=step)
        self.parm_range = parm_range
        return parm_range
        
    def set_parm_range(self, parm_range):
        """ 
        The function defines the range of the parameter .
        
        Parameters
        ----------
        parm_range : list of ints/floats
            The parameter range.
        """
        self.parm_range = parm_range
        
    def map_nrmlise_parms_2_parms(self, nrmlised_parm_list):
        """ 
        The function maps the the normalise parameter list to the real parameter list.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        parameter list : list of int/floats
            List of real parameters.
        """
        if self.parm_range == None:
            raise Exception("please define parm range")
        parm_list = super(BldgTwistParm, self).map_nrmlise_parms_2_parms(nrmlised_parm_list)
        return parm_list
        
    def define_nparameters(self,pycitygml_reader):
        """ 
        The function determines the total parameters for parameterising the model.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        nparameters : int
            The number of parameters for the model.
        """
        gml_bldg_list = pycitygml_reader.get_buildings()
        #filter through the eligible buildings
        eligible_bldg_list, non_eligible_bldg_list = self.eligibility_test(gml_bldg_list, pycitygml_reader)
        #because each building has one building height parameter
        nparameters = len(eligible_bldg_list)
        return nparameters
                
    def execute(self, pycitygml_reader, nrmlised_parm_list):
        """ 
        This funciton defines the parameterisation process and executes the process. A design alternative of the parametric model is returned.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
        
        nrmlised_parm_list : list of ints/floats
            The normalised parameters to be mapped to the real parameters defined, the parameters will be used to generate a design alternative.
            
        Returns
        -------        
        new pycitygml_reader : pycitygml.Reader class instance
            The new design alternative generated and documented as a CityGML model.
        """
        parm_list = self.map_nrmlise_parms_2_parms(nrmlised_parm_list)
        citygml_writer = pycitygml.Writer()
        gml_landuses = pycitygml_reader.get_landuses()
        gml_bldg_list = pycitygml_reader.get_buildings()
        flr2flr_height = self.flr2flr_height
        bcnt = 0
        for gml_landuse in gml_landuses:
            #check which buildings are on this plot
            gml_bldg_on_luse = gml3dmodel.buildings_on_landuse(gml_landuse,gml_bldg_list, pycitygml_reader)
            
            #check which buildings should this parameter be applied to
            eligibility_bldg_list, non_eligible_bldg_list = self.eligibility_test(gml_bldg_on_luse, pycitygml_reader)
            n_eligibility_bldgs = len(eligibility_bldg_list)
            
            #get the parameters for this landuse plot
            parms_4_luse = parm_list[bcnt:bcnt+n_eligibility_bldgs]
            
            #twist the bldg
            bcnt = 0
            for eligible_gml_bldg in eligibility_bldg_list:
                #get the twist parm for the bldg
                twist_parm = parms_4_luse[bcnt]
                
                #extract the bldg solid
                bldg_solid = gml3dmodel.get_building_occsolid(eligible_gml_bldg, pycitygml_reader)
                bldg_solid_centre = py3dmodel.calculate.get_centre_bbox(bldg_solid)
                #twist each bldg according to the parameter
                #first get all the floorplates 
                height, nstorey, storey_height = gml3dmodel.get_building_height_storey(eligible_gml_bldg, pycitygml_reader, 
                                                                                       flr2flr_height = flr2flr_height)

                plates_occface_2dlist = gml3dmodel.get_building_plates_by_level(bldg_solid, nstorey, storey_height, 
                                                                                roundndigit = 4, distance = 0.2)
                #plates_occface_list = reduce(lambda x,y :x+y ,plates_occface_2dlist)
                #py3dmodel.construct.visualise([plates_occface_list], ["BLUE"])
                nlvl = len(plates_occface_2dlist)
                twist_interval = float(twist_parm)/float(nlvl)
                
                lvl_shell_list = []
                external_horz_plate_list = []
                external_horz_plate_list1 = []
                for pcnt in range(nlvl-1):
                    twist_angle = twist_interval*(pcnt+1)
                    if pcnt == 0:
                        cur_plate_list = plates_occface_2dlist[pcnt]
                        external_horz_plate_list.extend(cur_plate_list)
                        
                    nxt_plate_list = plates_occface_2dlist[pcnt+1]
                    plate_cmpd = py3dmodel.construct.make_compound(nxt_plate_list)
                    rot_plate_shape = py3dmodel.modify.rotate(plate_cmpd, bldg_solid_centre, (0,0,1), twist_angle)
                    rot_nxt_plate_list = py3dmodel.fetch.geom_explorer(rot_plate_shape, "face")
                    n_cur_plates = len(cur_plate_list)
                    n_nxt_plates = len(rot_nxt_plate_list)
                    
                    #twist the next plates
                    if n_cur_plates == n_nxt_plates:
                        for pcnt2 in range(n_cur_plates):
                            cur_plate = cur_plate_list[pcnt2]
                            
                            #find the nearest face to loft 
                            if len(rot_nxt_plate_list) > 1:
                                min_dist_list = []
                                for rot_nxt_plate in rot_nxt_plate_list:
                                    min_dist = py3dmodel.calculate.minimum_distance(cur_plate, rot_nxt_plate)
                                    min_dist_list.append(min_dist)
                                    
                                min_min_dist = min(min_dist_list)
                                min_index = min_dist_list.index(min_min_dist)
                                nxt_plate = rot_nxt_plate_list[min_index]
                            else:
                                nxt_plate = rot_nxt_plate_list[pcnt2]
                                
                            cur_plate_area = py3dmodel.calculate.face_area(cur_plate)
                            nxt_plate_area = py3dmodel.calculate.face_area(nxt_plate)
                            diff_area = abs(nxt_plate_area-cur_plate_area)
                            
                            if diff_area/cur_plate_area >= 0.5:
                                cur_midpt = py3dmodel.calculate.face_midpt(cur_plate)
                                m_cur_midpt = py3dmodel.modify.move_pt(cur_midpt, (0,0,1), flr2flr_height)
                                m_cur_plate = py3dmodel.modify.move(cur_midpt, m_cur_midpt, cur_plate)
                                rot_plate_shape = py3dmodel.modify.rotate(m_cur_plate, bldg_solid_centre, (0,0,1), twist_interval)
                                rot_cur_plate= py3dmodel.fetch.geom_explorer(rot_plate_shape, "face")[0]
                                plates2loft = [cur_plate, rot_cur_plate]
                                lvl_shell = py3dmodel.construct.make_loft(plates2loft, rule_face = False)
                                lvl_shell_list.append(lvl_shell)
                                #the last level append the roof
                                if pcnt == nlvl-2:
                                    external_horz_plate_list.append(rot_cur_plate)
                                else:
                                    external_horz_plate_list1.append([])
                                    external_horz_plate_list1[-1].append(nxt_plate)
                                    external_horz_plate_list1[-1].append(rot_cur_plate)
                            else:
                                plates2loft = [cur_plate, nxt_plate]
                                lvl_shell = py3dmodel.construct.make_loft(plates2loft, rule_face = False)
                                lvl_shell_list.append(lvl_shell)
                                #the last level append the roof
                                if pcnt == nlvl-2:
                                    external_horz_plate_list.append(nxt_plate)
                            
                    if n_cur_plates != n_nxt_plates:
                        #move the cur plate up and rotate them 
                        if pcnt!=nlvl-2:
                            external_horz_plate_list1.append([])
                            external_horz_plate_list1[-1].extend(rot_nxt_plate_list)
                            
                        for cur_plate in cur_plate_list:
                            cur_midpt = py3dmodel.calculate.face_midpt(cur_plate)
                            m_cur_midpt = py3dmodel.modify.move_pt(cur_midpt, (0,0,1), flr2flr_height)
                            m_cur_plate = py3dmodel.modify.move(cur_midpt, m_cur_midpt, cur_plate)
                            #if there is a boolean it means it is connected to the upper floor in some way
                            common_plate = py3dmodel.construct.boolean_common(m_cur_plate, plate_cmpd)
                            if common_plate:
                                rot_plate_shape = py3dmodel.modify.rotate(m_cur_plate, bldg_solid_centre, (0,0,1), twist_interval)
                                rot_cur_plate= py3dmodel.fetch.geom_explorer(rot_plate_shape, "face")[0]
                                plates2loft = [cur_plate, rot_cur_plate]
                                lvl_shell = py3dmodel.construct.make_loft(plates2loft, rule_face = False)
                                lvl_shell_list.append(lvl_shell)
                                #the last level append the roof
                                if pcnt == nlvl-2:
                                    external_horz_plate_list.append(rot_cur_plate)
                                else:
                                    external_horz_plate_list1[-1].append(rot_cur_plate)
                            else:
                                external_horz_plate_list.append(cur_plate)
                                
                    cur_plate_list = rot_nxt_plate_list
                    
                #need to union all the volumes
                diff_list = []
                
                for horz_plate_list in external_horz_plate_list1:
                    hcnt = 0
                    for lvl in horz_plate_list:
                        external_horz_plate_list2 = horz_plate_list[:]
                        del external_horz_plate_list2[hcnt]
                        external_horz_plate_extruded_list = gml3dmodel.extrude_move_down_occ_faces(external_horz_plate_list2)
                        hplate2_cmpd = py3dmodel.construct.make_compound(external_horz_plate_extruded_list)
                        diff_cmpd = py3dmodel.construct.boolean_difference(lvl, hplate2_cmpd)
                        diff_face_list = py3dmodel.construct.simple_mesh(diff_cmpd)
                        #py3dmodel.construct.visualise([[lvl], [hplate2_cmpd], diff_face_list],['RED','GREEN', 'BLUE'])
                        
                        if diff_face_list:
                            diff_list.extend(diff_face_list)
                        hcnt+=1
                
                lvl_shell_cmpd = py3dmodel.construct.make_compound(lvl_shell_list)
                #py3dmodel.construct.visualise([[lvl_shell_cmpd]],['RED'])
                lvl_faces = py3dmodel.construct.simple_mesh(lvl_shell_cmpd)
                
                external_horz_plate_cmpd = py3dmodel.construct.make_compound(external_horz_plate_list)
                external_horz_plate_list = py3dmodel.construct.simple_mesh(external_horz_plate_cmpd)
                new_bldg_face_list = lvl_faces + external_horz_plate_list + diff_list
                new_building_shell_list = py3dmodel.construct.make_shell_frm_faces(new_bldg_face_list)
                
                
                if len(new_building_shell_list)>1:
                    print "NUMBER OF SOLIDS:", len(new_building_shell_list)
                    if external_horz_plate_list1:
                        external_horz_plate_list2 = reduce(lambda x,y :x+y ,external_horz_plate_list1)
                        new_bldg_face_list = lvl_faces + external_horz_plate_list + external_horz_plate_list2
                    else:
                        new_bldg_face_list = lvl_faces + external_horz_plate_list
                        
                    new_building_shell_list = py3dmodel.construct.make_shell_frm_faces(new_bldg_face_list)
                    if len(new_building_shell_list) == 1:
                        new_bldg_occsolid = py3dmodel.construct.make_solid(new_building_shell_list[0])
                        new_bldg_occsolid = py3dmodel.modify.fix_close_solid(new_bldg_occsolid)
                    else:
                        vol_list = []
                        for shell in new_building_shell_list:
                            bldg_solid = py3dmodel.construct.make_solid(shell)
                            bldg_solid = py3dmodel.modify.fix_close_solid(bldg_solid)
                            solid_vol = py3dmodel.calculate.solid_volume(bldg_solid)
                            vol_list.append(solid_vol)
                            
                        max_vol = max(vol_list)
                        max_index = vol_list.index(max_vol)
                        new_bldg_shell = new_building_shell_list[max_index]
                        new_bldg_occsolid = py3dmodel.construct.make_solid(new_bldg_shell)
                        new_bldg_occsolid = py3dmodel.modify.fix_close_solid(new_bldg_occsolid)
                    
                else:
                    new_building_shell =new_building_shell_list[0]
                    new_bldg_occsolid = py3dmodel.construct.make_solid(new_building_shell)
                    new_bldg_occsolid = py3dmodel.modify.fix_close_solid(new_bldg_occsolid)
                   
                #py3dmodel.construct.visualise([[new_bldg_occsolid]], ["RED"])
                new_height, new_n_storey = gml3dmodel.calculate_bldg_height_n_nstorey(new_bldg_occsolid, storey_height)
                gml3dmodel.update_gml_building(eligible_gml_bldg,new_bldg_occsolid, pycitygml_reader, 
                                               citygml_writer, new_height = new_height, new_nstorey = new_n_storey)
                
                bcnt+=1
                
        non_bldg_cityobjs = pycitygml_reader.get_non_xtype_cityobject("bldg:Building")
        gml3dmodel.write_citygml(non_bldg_cityobjs, citygml_writer)
        gml3dmodel.write_non_eligible_bldgs(non_eligible_bldg_list, citygml_writer)
        citymodel_node = citygml_writer.citymodelnode
        reader = pycitygml.Reader()
        reader.load_citymodel_node(citymodel_node)
        return reader
    
class BldgBendParm(BaseParm):
    """
    An implementation of the BaseParm class for parameterising the massing of buildings (LOD1) in terms of its geometry. This parameter will gradually bend the building solid according to the 
    parameter.
    
    Attributes
    ----------    
    bldg_class : str
        The string of the gml code for building class.
    
    bldg_function : str
        The string of the gml code for building function.
        
    bldg_usage : str
        The string of the gml code for building usage.
        
    parm_range : list of floats/ints
        The list of possible parameters.
    
    flr2flr_height : float
        The assumed floor to floor height of the building, default = 3m.
    """
    def __init__(self):
        """Initialise the class"""
        self.bldg_class = None
        self.bldg_function = None
        self.bldg_usage = None
        self.parm_range = None
        self.flr2flr_height = 3
        
    def define_flr2flr_height(self, flr2flr_height):
        """ 
        The function define the floor to floor height of the buildings to be parameterised.
        
        Parameters
        ----------
        flr2flr_height : float
            The assumed floor to floor height of the building.
        """
        self.flr2flr_height = flr2flr_height
        
    def apply_2_bldg_class(self, bldg_class):
        """
        This function declares the building class that will have this parameter, buildings which is not this class will not be parameterised.
        
        Parameters
        ----------     
        bldg_class : str
            The string of the gml code for building class.
        """
        self.bldg_class = bldg_class
        
    def apply_2_bldg_function(self, bldg_function):
        """
        This function declares the building function that will have this parameter, buildings which is not this function will not be parameterised.
        
        Parameters
        ----------     
        bldg_function : str
            The string of the gml code for building function.
        """
        self.bldg_function = bldg_function
        
    def apply_2_bldg_usage(self, bldg_usage):
        """
        This function declares the building usage that will have this parameter, buildings which is not this usage will not be parameterised.
        
        Parameters
        ----------     
        bldg_usage : str
            The string of the gml code for building usage.
        """
        self.bldg_usage = bldg_usage
        
    def eligibility_test(self, gml_bldg_list, pycitygml_reader):
        """ 
        The function checks which are the buildings that are eligible to be parameterised.
        
        Parameters
        ----------
        gml_bldg_list : list of lxml.etree Element 
            The GML building to be parameterised.
            
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        eligible_bldg_list : list of lxml.etree Element 
            The GML building to be parameterised.
        
        non_eligible_bldg_list : list of lxml.etree Element 
            The GML building that will not be parameterised.
        """
        eligible_bldg_list = []
        non_eligible_bldg_list = []
        for gml_bldg in gml_bldg_list:
            eligibility = True
            if self.bldg_class != None: 
                bldg_class = pycitygml_reader.get_building_class(gml_bldg)
                if self.bldg_class != bldg_class:
                    eligibility = False
                    
            if self.bldg_function != None:
                bldg_function = pycitygml_reader.get_building_function(gml_bldg)
                if self.bldg_function != bldg_function:
                    eligibility = False
            
            if self.bldg_usage != None:
                bldg_usage = pycitygml_reader.get_building_usage(gml_bldg)
                if self.bldg_usage != bldg_usage:
                    eligibility = False
                    
            if eligibility == True:
                eligible_bldg_list.append(gml_bldg)
                
            if eligibility == False:
                non_eligible_bldg_list.append(gml_bldg)
                
        return eligible_bldg_list, non_eligible_bldg_list
        
    def define_int_range(self, start, stop, step):
        """ 
        The function defines the range of the parameter if the parameter type is integer.
        
        Parameters
        ----------
        start : int
            The starting number of the sequence.
        
        stop : int
            Generate numbers up to, including this number.
        
        step : int
            The difference between each number in the sequence.
        
        Returns
        -------        
        parameter range : list of ints
            List of generated parameters.
        """
        parm_range = super(BldgBendParm, self).define_int_range(start, stop, step)
        self.parm_range = parm_range
        return parm_range
        
    def define_float_range(self, start, stop, step=None):
        """ 
        The function defines the range of the parameter if the parameter type is float.
        
        Parameters
        ----------
        start : float
            The starting number of the sequence.
        
        stop : float
            Generate numbers up to, including this number.
        
        step : float, optional
            The difference between each number in the sequence, default = None. When None the parameter is a continuous parameter, if not None the parameter is a discrete parameter.
        
        Returns
        -------        
        parameter range : list of floats
            List of generated float parameters if step = None, if step != None the parameter range is made up of two numbers the start and the end of the continuous parameter.
        """
        parm_range = super(BldgBendParm, self).define_float_range(start, stop, step=step)
        self.parm_range = parm_range
        return parm_range
        
    def set_parm_range(self, parm_range):
        """ 
        The function defines the range of the parameter .
        
        Parameters
        ----------
        parm_range : list of ints/floats
            The parameter range.
        """
        self.parm_range = parm_range
        
    def map_nrmlise_parms_2_parms(self, nrmlised_parm_list):
        """ 
        The function maps the the normalise parameter list to the real parameter list.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        parameter list : list of int/floats
            List of real parameters.
        """
        if self.parm_range == None:
            raise Exception("please define parm range")
        parm_list = super(BldgBendParm, self).map_nrmlise_parms_2_parms(nrmlised_parm_list)
        return parm_list
        
    def define_nparameters(self,pycitygml_reader):
        """ 
        The function determines the total parameters for parameterising the model.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        nparameters : int
            The number of parameters for the model.
        """
        gml_bldg_list = pycitygml_reader.get_buildings()
        #filter through the eligible buildings
        eligible_bldg_list, non_eligible_bldg_list = self.eligibility_test(gml_bldg_list, pycitygml_reader)
        #because each building has one building height parameter
        nparameters = len(eligible_bldg_list)
        return nparameters
                
    def execute(self, pycitygml_reader, nrmlised_parm_list):
        """ 
        This funciton defines the parameterisation process and executes the process. A design alternative of the parametric model is returned.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
        
        nrmlised_parm_list : list of ints/floats
            The normalised parameters to be mapped to the real parameters defined, the parameters will be used to generate a design alternative.
            
        Returns
        -------        
        new pycitygml_reader : pycitygml.Reader class instance
            The new design alternative generated and documented as a CityGML model.
        """
        parm_list = self.map_nrmlise_parms_2_parms(nrmlised_parm_list)
        citygml_writer = pycitygml.Writer()
        gml_landuses = pycitygml_reader.get_landuses()
        gml_bldg_list = pycitygml_reader.get_buildings()
        flr2flr_height = self.flr2flr_height
        bcnt = 0
        for gml_landuse in gml_landuses:
            #check which buildings are on this plot
            gml_bldg_on_luse = gml3dmodel.buildings_on_landuse(gml_landuse,gml_bldg_list, pycitygml_reader)
            
            #check which buildings should this parameter be applied to
            eligibility_bldg_list, non_eligible_bldg_list = self.eligibility_test(gml_bldg_on_luse, pycitygml_reader)
            n_eligibility_bldgs = len(eligibility_bldg_list)
            
            #get the parameters for this landuse plot
            parms_4_luse = parm_list[bcnt:bcnt+n_eligibility_bldgs]
            
            #twist the bldg
            bcnt = 0
            for eligible_gml_bldg in eligibility_bldg_list:
                #get the twist parm for the bldg
                bend_parm = parms_4_luse[bcnt]
                
                #extract the bldg solid
                bldg_solid = gml3dmodel.get_building_occsolid(eligible_gml_bldg, pycitygml_reader)
                
                xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(bldg_solid)
                #bend each bldg according to the parameter
                #first get all the floorplates 
                height, nstorey, storey_height = gml3dmodel.get_building_height_storey(eligible_gml_bldg, pycitygml_reader, 
                                                                                       flr2flr_height = flr2flr_height)

                plates_occface_2dlist = gml3dmodel.get_building_plates_by_level(bldg_solid, nstorey, storey_height, 
                                                                                roundndigit = 4, distance = 0.2)
                
                #plates_occface_list = reduce(lambda x,y :x+y ,plates_occface_2dlist)
                #py3dmodel.construct.visualise([plates_occface_list], ["BLUE"])

                nlvl = len(plates_occface_2dlist)
                bend_interval = float(bend_parm)/float(nlvl)
                
                lvl_shell_list = []
                external_horz_plate_list = []
                external_horz_plate_list1 = []
                #print "NUM OF LEVELS", nlvl
                for pcnt in range(nlvl-1):                    
                    bend_angle = bend_interval*(pcnt+1)
                    if pcnt == 0:
                        cur_plate_list = plates_occface_2dlist[pcnt]
                        external_horz_plate_list.extend(cur_plate_list)
                        
                    nxt_plate_list = plates_occface_2dlist[pcnt+1]
                    plate_cmpd = py3dmodel.construct.make_compound(nxt_plate_list)
                    plate_midpt = py3dmodel.calculate.get_centre_bbox(plate_cmpd)
                    #bend towards the right
                    edge_pt = (xmax,ymax,plate_midpt[2])
                    
                    rot_plate_shape = py3dmodel.modify.rotate(plate_cmpd, edge_pt, (0,1,0), bend_angle)
                    rot_nxt_plate_list = py3dmodel.fetch.geom_explorer(rot_plate_shape, "face")
                    n_cur_plates = len(cur_plate_list)
                    n_nxt_plates = len(rot_nxt_plate_list)
                    
                    #twist the next plates
                    if n_cur_plates == n_nxt_plates:
                        for pcnt2 in range(n_cur_plates):
                            cur_plate = cur_plate_list[pcnt2]
                            #find the nearest face to loft 
                            if len(rot_nxt_plate_list) > 1:
                                min_dist_list = []
                                for rot_nxt_plate in rot_nxt_plate_list:
                                    min_dist = py3dmodel.calculate.minimum_distance(cur_plate, rot_nxt_plate)
                                    min_dist_list.append(min_dist)
                                    
                                min_min_dist = min(min_dist_list)
                                min_index = min_dist_list.index(min_min_dist)
                                nxt_plate = rot_nxt_plate_list[min_index]
                            else:
                                nxt_plate = rot_nxt_plate_list[pcnt2]
                            
                            cur_plate_area = py3dmodel.calculate.face_area(cur_plate)
                            nxt_plate_area = py3dmodel.calculate.face_area(nxt_plate)
                            diff_area = abs(nxt_plate_area-cur_plate_area)
                            
                            if diff_area/cur_plate_area >= 0.5:
                                cur_midpt = py3dmodel.calculate.face_midpt(cur_plate)
                                m_cur_midpt = py3dmodel.modify.move_pt(cur_midpt, (0,0,1), flr2flr_height)
                                m_cur_plate = py3dmodel.modify.move(cur_midpt, m_cur_midpt, cur_plate)
                                rot_plate_shape = py3dmodel.modify.rotate(m_cur_plate, edge_pt, (0,1,0), bend_interval)
                                rot_cur_plate= py3dmodel.fetch.geom_explorer(rot_plate_shape, "face")[0]
                                
                                plates2loft = [cur_plate, rot_cur_plate]
                                lvl_shell = py3dmodel.construct.make_loft(plates2loft, rule_face = False)
                                lvl_shell_list.append(lvl_shell)
                                #the last level append the roof
                                if pcnt == nlvl-2:
                                    external_horz_plate_list.append(rot_cur_plate)
                                else:
                                    external_horz_plate_list1.append([])
                                    external_horz_plate_list1[-1].append(nxt_plate)
                                    external_horz_plate_list1[-1].append(rot_cur_plate)
                            else:
                                plates2loft = [cur_plate, nxt_plate]
                                lvl_shell = py3dmodel.construct.make_loft(plates2loft, rule_face = False)
                                lvl_shell_list.append(lvl_shell)
                                #the last level append the roof
                                if pcnt == nlvl-2:
                                    external_horz_plate_list.append(nxt_plate)
                            
                    if n_cur_plates != n_nxt_plates:
                        #move the cur plate up and rotate them 
                        if pcnt!=nlvl-2:
                            external_horz_plate_list1.append([])
                            external_horz_plate_list1[-1].extend(rot_nxt_plate_list)
                        for cur_plate in cur_plate_list:
                            cur_midpt = py3dmodel.calculate.face_midpt(cur_plate)
                            m_cur_midpt = py3dmodel.modify.move_pt(cur_midpt, (0,0,1), flr2flr_height)
                            m_cur_plate = py3dmodel.modify.move(cur_midpt, m_cur_midpt, cur_plate)
                            #if there is a boolean it means it is connected to the upper floor in some way
                            common_plate = py3dmodel.construct.boolean_common(m_cur_plate, plate_cmpd)
                            if common_plate:
                                rot_plate_shape = py3dmodel.modify.rotate(m_cur_plate, edge_pt, (0,1,0), bend_interval)
                                rot_cur_plate= py3dmodel.fetch.geom_explorer(rot_plate_shape, "face")[0]
                                plates2loft = [cur_plate, rot_cur_plate]
                                lvl_shell = py3dmodel.construct.make_loft(plates2loft, rule_face = False)
                                lvl_shell_list.append(lvl_shell)
                                #the last level append the roof
                                if pcnt == nlvl-2:
                                    external_horz_plate_list.append(rot_cur_plate)
                                else:
                                    external_horz_plate_list1[-1].append(rot_cur_plate)
                            else:
                                external_horz_plate_list.append(cur_plate)
                                
                    cur_plate_list = rot_nxt_plate_list
                
                #need to union all the volumes
                diff_list = []
                for horz_plate_list in external_horz_plate_list1:
                    hcnt = 0
                    for lvl in horz_plate_list:
                        external_horz_plate_list2 = horz_plate_list[:]
                        del external_horz_plate_list2[hcnt]
                        external_horz_plate_extruded_list = gml3dmodel.extrude_move_down_occ_faces(external_horz_plate_list2)
                        hplate2_cmpd = py3dmodel.construct.make_compound(external_horz_plate_extruded_list)
                        diff_cmpd = py3dmodel.construct.boolean_difference(lvl, hplate2_cmpd)
                        diff_face_list = py3dmodel.construct.simple_mesh(diff_cmpd)
                        if diff_face_list:
                            diff_list.extend(diff_face_list)
                        hcnt+=1
                
                lvl_shell_cmpd = py3dmodel.construct.make_compound(lvl_shell_list)
                lvl_faces = py3dmodel.construct.simple_mesh(lvl_shell_cmpd)
                
                external_horz_plate_cmpd = py3dmodel.construct.make_compound(external_horz_plate_list)
                external_horz_plate_list = py3dmodel.construct.simple_mesh(external_horz_plate_cmpd)
                new_bldg_face_list = lvl_faces + external_horz_plate_list + diff_list
                new_building_shell_list = py3dmodel.construct.make_shell_frm_faces(new_bldg_face_list)
                
                if len(new_building_shell_list)>1:
                    print "NUMBER OF SOLIDS:", len(new_building_shell_list)
                    if external_horz_plate_list1:
                        external_horz_plate_list2 = reduce(lambda x,y :x+y ,external_horz_plate_list1)
                        new_bldg_face_list = lvl_faces + external_horz_plate_list + external_horz_plate_list2
                    else:
                        new_bldg_face_list = lvl_faces + external_horz_plate_list
                        
                    new_building_shell_list = py3dmodel.construct.make_shell_frm_faces(new_bldg_face_list)
                    if len(new_building_shell_list) == 1:
                        new_bldg_occsolid = py3dmodel.construct.make_solid(new_building_shell_list[0])
                        new_bldg_occsolid = py3dmodel.modify.fix_close_solid(new_bldg_occsolid)
                    else:
                        vol_list = []
                        for shell in new_building_shell_list:
                            bldg_solid = py3dmodel.construct.make_solid(shell)
                            bldg_solid = py3dmodel.modify.fix_close_solid(bldg_solid)
                            solid_vol = py3dmodel.calculate.solid_volume(bldg_solid)
                            vol_list.append(solid_vol)
                            
                        max_vol = max(vol_list)
                        max_index = vol_list.index(max_vol)
                        new_bldg_shell = new_building_shell_list[max_index]
                        new_bldg_occsolid = py3dmodel.construct.make_solid(new_bldg_shell)
                        new_bldg_occsolid = py3dmodel.modify.fix_close_solid(new_bldg_occsolid)
                    
                else:
                    new_building_shell =new_building_shell_list[0]
                    new_bldg_occsolid = py3dmodel.construct.make_solid(new_building_shell)
                    new_bldg_occsolid = py3dmodel.modify.fix_close_solid(new_bldg_occsolid)
                    
                #py3dmodel.construct.visualise([[new_bldg_occsolid]], ["RED"])
                new_height, new_n_storey = gml3dmodel.calculate_bldg_height_n_nstorey(new_bldg_occsolid, storey_height)
                gml3dmodel.update_gml_building(eligible_gml_bldg,new_bldg_occsolid, pycitygml_reader, 
                                               citygml_writer, new_height = new_height, new_nstorey = new_n_storey)
                
                bcnt+=1
                
        non_bldg_cityobjs = pycitygml_reader.get_non_xtype_cityobject("bldg:Building")
        gml3dmodel.write_citygml(non_bldg_cityobjs, citygml_writer)
        gml3dmodel.write_non_eligible_bldgs(non_eligible_bldg_list, citygml_writer)
        citymodel_node = citygml_writer.citymodelnode
        reader = pycitygml.Reader()
        reader.load_citymodel_node(citymodel_node)
        return reader
    
class BldgSlantParm(BaseParm):
    """
    An implementation of the BaseParm class for parameterising the massing of buildings (LOD1) in terms of its geometry. This parameter will gradually slant the building solid according to the 
    parameter.
    
    Attributes
    ----------    
    bldg_class : str
        The string of the gml code for building class.
    
    bldg_function : str
        The string of the gml code for building function.
        
    bldg_usage : str
        The string of the gml code for building usage.
        
    parm_range : list of floats/ints
        The list of possible parameters.
    
    flr2flr_height : float
        The assumed floor to floor height of the building, default = 3m.
    """
    def __init__(self):
        """Initialise the class"""
        self.bldg_class = None
        self.bldg_function = None
        self.bldg_usage = None
        self.parm_range = None
        self.flr2flr_height = 3
        
    def define_flr2flr_height(self, flr2flr_height):
        """ 
        The function define the floor to floor height of the buildings to be parameterised.
        
        Parameters
        ----------
        flr2flr_height : float
            The assumed floor to floor height of the building.
        """
        self.flr2flr_height = flr2flr_height
        
    def apply_2_bldg_class(self, bldg_class):
        """
        This function declares the building class that will have this parameter, buildings which is not this class will not be parameterised.
        
        Parameters
        ----------     
        bldg_class : str
            The string of the gml code for building class.
        """
        self.bldg_class = bldg_class
        
    def apply_2_bldg_function(self, bldg_function):
        """
        This function declares the building function that will have this parameter, buildings which is not this function will not be parameterised.
        
        Parameters
        ----------     
        bldg_function : str
            The string of the gml code for building function.
        """
        self.bldg_function = bldg_function
        
    def apply_2_bldg_usage(self, bldg_usage):
        """
        This function declares the building usage that will have this parameter, buildings which is not this usage will not be parameterised.
        
        Parameters
        ----------     
        bldg_usage : str
            The string of the gml code for building usage.
        """
        self.bldg_usage = bldg_usage
        
    def eligibility_test(self, gml_bldg_list, pycitygml_reader):
        """ 
        The function checks which are the buildings that are eligible to be parameterised.
        
        Parameters
        ----------
        gml_bldg_list : list of lxml.etree Element 
            The GML building to be parameterised.
            
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        eligible_bldg_list : list of lxml.etree Element 
            The GML building to be parameterised.
        
        non_eligible_bldg_list : list of lxml.etree Element 
            The GML building that will not be parameterised.
        """
        eligible_bldg_list = []
        non_eligible_bldg_list = []
        for gml_bldg in gml_bldg_list:
            eligibility = True
            if self.bldg_class != None: 
                bldg_class = pycitygml_reader.get_building_class(gml_bldg)
                if self.bldg_class != bldg_class:
                    eligibility = False
                    
            if self.bldg_function != None:
                bldg_function = pycitygml_reader.get_building_function(gml_bldg)
                if self.bldg_function != bldg_function:
                    eligibility = False
            
            if self.bldg_usage != None:
                bldg_usage = pycitygml_reader.get_building_usage(gml_bldg)
                if self.bldg_usage != bldg_usage:
                    eligibility = False
                    
            if eligibility == True:
                eligible_bldg_list.append(gml_bldg)
                
            if eligibility == False:
                non_eligible_bldg_list.append(gml_bldg)
                
        return eligible_bldg_list, non_eligible_bldg_list
        
    def define_int_range(self, start, stop, step):
        """ 
        The function defines the range of the parameter if the parameter type is integer.
        
        Parameters
        ----------
        start : int
            The starting number of the sequence.
        
        stop : int
            Generate numbers up to, including this number.
        
        step : int
            The difference between each number in the sequence.
        
        Returns
        -------        
        parameter range : list of ints
            List of generated parameters.
        """
        parm_range = super(BldgSlantParm, self).define_int_range(start, stop, step)
        self.parm_range = parm_range
        return parm_range
        
    def define_float_range(self, start, stop, step=None):
        """ 
        The function defines the range of the parameter if the parameter type is float.
        
        Parameters
        ----------
        start : float
            The starting number of the sequence.
        
        stop : float
            Generate numbers up to, including this number.
        
        step : float, optional
            The difference between each number in the sequence, default = None. When None the parameter is a continuous parameter, if not None the parameter is a discrete parameter.
        
        Returns
        -------        
        parameter range : list of floats
            List of generated float parameters if step = None, if step != None the parameter range is made up of two numbers the start and the end of the continuous parameter.
        """
        parm_range = super(BldgSlantParm, self).define_float_range(start, stop, step=step)
        self.parm_range = parm_range
        return parm_range
        
    def set_parm_range(self, parm_range):
        """ 
        The function defines the range of the parameter .
        
        Parameters
        ----------
        parm_range : list of ints/floats
            The parameter range.
        """
        self.parm_range = parm_range
        
    def map_nrmlise_parms_2_parms(self, nrmlised_parm_list):
        """ 
        The function maps the the normalise parameter list to the real parameter list.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        parameter list : list of int/floats
            List of real parameters.
        """
        if self.parm_range == None:
            raise Exception("please define parm range")
        parm_list = super(BldgSlantParm, self).map_nrmlise_parms_2_parms(nrmlised_parm_list)
        return parm_list
        
    def define_nparameters(self,pycitygml_reader):
        """ 
        The function determines the total parameters for parameterising the model.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        nparameters : int
            The number of parameters for the model.
        """
        gml_bldg_list = pycitygml_reader.get_buildings()
        #filter through the eligible buildings
        eligible_bldg_list, non_eligible_bldg_list = self.eligibility_test(gml_bldg_list, pycitygml_reader)
        #because each building has one building height parameter
        nparameters = len(eligible_bldg_list)
        return nparameters
                
    def execute(self, pycitygml_reader, nrmlised_parm_list):
        """ 
        This funciton defines the parameterisation process and executes the process. A design alternative of the parametric model is returned.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
        
        nrmlised_parm_list : list of ints/floats
            The normalised parameters to be mapped to the real parameters defined, the parameters will be used to generate a design alternative.
            
        Returns
        -------        
        new pycitygml_reader : pycitygml.Reader class instance
            The new design alternative generated and documented as a CityGML model.
        """
        parm_list = self.map_nrmlise_parms_2_parms(nrmlised_parm_list)
        citygml_writer = pycitygml.Writer()
        gml_landuses = pycitygml_reader.get_landuses()
        gml_bldg_list = pycitygml_reader.get_buildings()
        flr2flr_height = self.flr2flr_height
        bcnt = 0
        for gml_landuse in gml_landuses:
            #check which buildings are on this plot
            gml_bldg_on_luse = gml3dmodel.buildings_on_landuse(gml_landuse,gml_bldg_list, pycitygml_reader)
            
            #check which buildings should this parameter be applied to
            eligibility_bldg_list, non_eligible_bldg_list = self.eligibility_test(gml_bldg_on_luse, pycitygml_reader)
            n_eligibility_bldgs = len(eligibility_bldg_list)
            
            #get the parameters for this landuse plot
            parms_4_luse = parm_list[bcnt:bcnt+n_eligibility_bldgs]
            
            #twist the bldg
            bcnt = 0
            for eligible_gml_bldg in eligibility_bldg_list:
                #get the twist parm for the bldg
                parm = parms_4_luse[bcnt]
                
                #extract the bldg solid
                bldg_solid = gml3dmodel.get_building_occsolid(eligible_gml_bldg, pycitygml_reader)
                bldg_bf = gml3dmodel.get_building_bounding_footprint(bldg_solid)
                bf_midpt = py3dmodel.calculate.face_midpt(bldg_bf)
                #bend each bldg according to the parameter
                #first get all the floorplates 
                height, nstorey, storey_height = gml3dmodel.get_building_height_storey(eligible_gml_bldg, pycitygml_reader, 
                                                                                       flr2flr_height = flr2flr_height)

                plates_occface_2dlist = gml3dmodel.get_building_plates_by_level(bldg_solid, nstorey, storey_height, 
                                                                                roundndigit = 4, distance = 0.2)
                
                #plates_occface_list = reduce(lambda x,y :x+y ,plates_occface_2dlist)
                #print "NUM OF FLOOR PLATES", len(plates_occface_list)
                #py3dmodel.construct.visualise([plates_occface_list], ["BLUE"])

                nlvl = len(plates_occface_2dlist)
                interval = float(parm)/float(nlvl)
                
                lvl_shell_list = []
                external_horz_plate_list = []
                external_horz_plate_list1 = []
                #print "NUM OF LEVELS", nlvl
                for pcnt in range(nlvl-1):                    
                    magnitude = interval*(pcnt+1)
                    if pcnt == 0:
                        cur_plate_list = plates_occface_2dlist[pcnt]
                        external_horz_plate_list.extend(cur_plate_list)
                        
                    nxt_plate_list = plates_occface_2dlist[pcnt+1]
                    plate_cmpd = py3dmodel.construct.make_compound(nxt_plate_list)
                    level_midpt = py3dmodel.calculate.get_centre_bbox(plate_cmpd)
                    plate_midpt = (bf_midpt[0],bf_midpt[1],level_midpt[2])
                    #slant towards the right
                    m_plate_midpt = py3dmodel.modify.move_pt(plate_midpt, (1,0,0), magnitude)
                    
                    trsf_plate_shape = py3dmodel.modify.move(plate_midpt, m_plate_midpt, plate_cmpd)
                    trsf_nxt_plate_list = py3dmodel.fetch.geom_explorer(trsf_plate_shape, "face")
                    n_cur_plates = len(cur_plate_list)
                    n_nxt_plates = len(trsf_nxt_plate_list)
                    
                    #slant the next plates
                    if n_cur_plates == n_nxt_plates:
                        for pcnt2 in range(n_cur_plates):
                            cur_plate = cur_plate_list[pcnt2]
                            #find the nearest face to loft 
                            if len(trsf_nxt_plate_list) > 1:
                                min_dist_list = []
                                for trsf_nxt_plate in trsf_nxt_plate_list:
                                    min_dist = py3dmodel.calculate.minimum_distance(cur_plate, trsf_nxt_plate)
                                    min_dist_list.append(min_dist)
                                    
                                min_min_dist = min(min_dist_list)
                                min_index = min_dist_list.index(min_min_dist)
                                nxt_plate = trsf_nxt_plate_list[min_index]
                            else:
                                nxt_plate = trsf_nxt_plate_list[pcnt2]
                            
                            cur_plate_area = py3dmodel.calculate.face_area(cur_plate)
                            nxt_plate_area = py3dmodel.calculate.face_area(nxt_plate)
                            diff_area = abs(nxt_plate_area-cur_plate_area)
                            
                            if diff_area/cur_plate_area >= 0.5:
                                cur_midpt = py3dmodel.calculate.face_midpt(cur_plate)
                                m_cur_midpt = py3dmodel.modify.move_pt(cur_midpt, (0,0,1), flr2flr_height)
                                m_cur_plate = py3dmodel.modify.move(cur_midpt, m_cur_midpt, cur_plate)
                                
                                m_cur_midpt2 = py3dmodel.modify.move_pt(plate_midpt, (1,0,0), interval)
                                
                                trsf_plate_shape = py3dmodel.modify.move(plate_midpt, m_cur_midpt2, m_cur_plate)
                                trsf_cur_plate= py3dmodel.fetch.geom_explorer(trsf_plate_shape, "face")[0]
                                
                                plates2loft = [cur_plate, trsf_cur_plate]
                                lvl_shell = py3dmodel.construct.make_loft(plates2loft, rule_face = False)
                                lvl_shell_list.append(lvl_shell)
                                #the last level append the roof
                                if pcnt == nlvl-2:
                                    external_horz_plate_list.append(trsf_cur_plate)
                                else:
                                    external_horz_plate_list1.append([])
                                    external_horz_plate_list1[-1].append(nxt_plate)
                                    external_horz_plate_list1[-1].append(trsf_cur_plate)
                            else:
                                plates2loft = [cur_plate, nxt_plate]
                                lvl_shell = py3dmodel.construct.make_loft(plates2loft, rule_face = False)
                                lvl_shell_list.append(lvl_shell)
                                #the last level append the roof
                                if pcnt == nlvl-2:
                                    external_horz_plate_list.append(nxt_plate)
                            
                    if n_cur_plates != n_nxt_plates:
                        #move the cur plate up and rotate them 
                        if pcnt!=nlvl-2:
                            external_horz_plate_list1.append([])
                            external_horz_plate_list1[-1].extend(trsf_nxt_plate_list)
                        for cur_plate in cur_plate_list:
                            cur_midpt = py3dmodel.calculate.face_midpt(cur_plate)
                            m_cur_midpt = py3dmodel.modify.move_pt(cur_midpt, (0,0,1), flr2flr_height)
                            m_cur_plate = py3dmodel.modify.move(cur_midpt, m_cur_midpt, cur_plate)
                            #if there is a boolean it means it is connected to the upper floor in some way
                            common_plate = py3dmodel.construct.boolean_common(m_cur_plate, plate_cmpd)
                            if common_plate:
                                m_cur_midpt2 = py3dmodel.modify.move_pt(plate_midpt, (1,0,0), interval)
                                
                                trsf_plate_shape = py3dmodel.modify.move(plate_midpt, m_cur_midpt2, m_cur_plate)
                                trsf_cur_plate= py3dmodel.fetch.geom_explorer(trsf_plate_shape, "face")[0]
                                
                                plates2loft = [cur_plate, trsf_cur_plate]
                                lvl_shell = py3dmodel.construct.make_loft(plates2loft, rule_face = False)
                                lvl_shell_list.append(lvl_shell)
                                #the last level append the roof
                                if pcnt == nlvl-2:
                                    external_horz_plate_list.append(trsf_cur_plate)
                                else:
                                    external_horz_plate_list1[-1].append(trsf_cur_plate)
                            else:
                                external_horz_plate_list.append(cur_plate)
                                
                    cur_plate_list = trsf_nxt_plate_list
                
                #need to union all the volumes
                diff_list = []
                for horz_plate_list in external_horz_plate_list1:
                    hcnt = 0
                    for lvl in horz_plate_list:
                        external_horz_plate_list2 = horz_plate_list[:]
                        del external_horz_plate_list2[hcnt]
                        external_horz_plate_extruded_list = gml3dmodel.extrude_move_down_occ_faces(external_horz_plate_list2)
                        hplate2_cmpd = py3dmodel.construct.make_compound(external_horz_plate_extruded_list)
                        diff_cmpd = py3dmodel.construct.boolean_difference(lvl, hplate2_cmpd)
                        diff_face_list = py3dmodel.construct.simple_mesh(diff_cmpd)
                        if diff_face_list:
                            diff_list.extend(diff_face_list)
                        hcnt+=1
                
                lvl_shell_cmpd = py3dmodel.construct.make_compound(lvl_shell_list)
                lvl_faces = py3dmodel.construct.simple_mesh(lvl_shell_cmpd)
                
                external_horz_plate_cmpd = py3dmodel.construct.make_compound(external_horz_plate_list)
                external_horz_plate_list = py3dmodel.construct.simple_mesh(external_horz_plate_cmpd)
                new_bldg_face_list = lvl_faces + external_horz_plate_list + diff_list
                new_building_shell_list = py3dmodel.construct.make_shell_frm_faces(new_bldg_face_list)
                
                if len(new_building_shell_list)>1:
                    print "NUMBER OF SOLIDS:", len(new_building_shell_list)
                    #py3dmodel.construct.visualise([new_building_shell_list], ["RED"])
                    if external_horz_plate_list1:
                        external_horz_plate_list2 = reduce(lambda x,y :x+y ,external_horz_plate_list1)
                        new_bldg_face_list = lvl_faces + external_horz_plate_list + external_horz_plate_list2
                    else:
                        new_bldg_face_list = lvl_faces + external_horz_plate_list
                        
                    new_building_shell_list = py3dmodel.construct.make_shell_frm_faces(new_bldg_face_list)
                    if len(new_building_shell_list) == 1:
                        new_bldg_occsolid = py3dmodel.construct.make_solid(new_building_shell_list[0])
                        new_bldg_occsolid = py3dmodel.modify.fix_close_solid(new_bldg_occsolid)
                    else:
                        vol_list = []
                        for shell in new_building_shell_list:
                            bldg_solid = py3dmodel.construct.make_solid(shell)
                            bldg_solid = py3dmodel.modify.fix_close_solid(bldg_solid)
                            solid_vol = py3dmodel.calculate.solid_volume(bldg_solid)
                            vol_list.append(solid_vol)
                            
                        max_vol = max(vol_list)
                        max_index = vol_list.index(max_vol)
                        new_bldg_shell = new_building_shell_list[max_index]
                        new_bldg_occsolid = py3dmodel.construct.make_solid(new_bldg_shell)
                        new_bldg_occsolid = py3dmodel.modify.fix_close_solid(new_bldg_occsolid)
                        #py3dmodel.construct.visualise([[new_bldg_occsolid]], ["RED"])
                    
                else:
                    new_building_shell =new_building_shell_list[0]
                    new_bldg_occsolid = py3dmodel.construct.make_solid(new_building_shell)
                    new_bldg_occsolid = py3dmodel.modify.fix_close_solid(new_bldg_occsolid)
                    
                #py3dmodel.construct.visualise([[new_bldg_occsolid]], ["RED"])
                new_height, new_n_storey = gml3dmodel.calculate_bldg_height_n_nstorey(new_bldg_occsolid, storey_height)
                gml3dmodel.update_gml_building(eligible_gml_bldg,new_bldg_occsolid, pycitygml_reader, 
                                               citygml_writer, new_height = new_height, new_nstorey = new_n_storey)
                
                bcnt+=1
                
        non_bldg_cityobjs = pycitygml_reader.get_non_xtype_cityobject("bldg:Building")
        gml3dmodel.write_citygml(non_bldg_cityobjs, citygml_writer)
        gml3dmodel.write_non_eligible_bldgs(non_eligible_bldg_list, citygml_writer)
        citymodel_node = citygml_writer.citymodelnode
        reader = pycitygml.Reader()
        reader.load_citymodel_node(citymodel_node)
        return reader
    
class BldgTaperParm(BaseParm):
    """
    An implementation of the BaseParm class for parameterising the massing of buildings (LOD1) in terms of its geometry. This parameter will gradually taper the building solid according to the 
    parameter.
    
    Attributes
    ----------    
    bldg_class : str
        The string of the gml code for building class.
    
    bldg_function : str
        The string of the gml code for building function.
        
    bldg_usage : str
        The string of the gml code for building usage.
        
    parm_range : list of floats/ints
        The list of possible parameters.
    
    flr2flr_height : float
        The assumed floor to floor height of the building, default = 3m.
    """
    def __init__(self):
        """Initialise the class"""
        self.bldg_class = None
        self.bldg_function = None
        self.bldg_usage = None
        self.parm_range = None
        self.flr2flr_height = 3
        
    def define_flr2flr_height(self, flr2flr_height):
        """ 
        The function define the floor to floor height of the buildings to be parameterised.
        
        Parameters
        ----------
        flr2flr_height : float
            The assumed floor to floor height of the building.
        """
        self.flr2flr_height = flr2flr_height
        
    def apply_2_bldg_class(self, bldg_class):
        """
        This function declares the building class that will have this parameter, buildings which is not this class will not be parameterised.
        
        Parameters
        ----------     
        bldg_class : str
            The string of the gml code for building class.
        """
        self.bldg_class = bldg_class
        
    def apply_2_bldg_function(self, bldg_function):
        """
        This function declares the building function that will have this parameter, buildings which is not this function will not be parameterised.
        
        Parameters
        ----------     
        bldg_function : str
            The string of the gml code for building function.
        """
        self.bldg_function = bldg_function
        
    def apply_2_bldg_usage(self, bldg_usage):
        """
        This function declares the building usage that will have this parameter, buildings which is not this usage will not be parameterised.
        
        Parameters
        ----------     
        bldg_usage : str
            The string of the gml code for building usage.
        """
        self.bldg_usage = bldg_usage
        
    def eligibility_test(self, gml_bldg_list, pycitygml_reader):
        """ 
        The function checks which are the buildings that are eligible to be parameterised.
        
        Parameters
        ----------
        gml_bldg_list : list of lxml.etree Element 
            The GML building to be parameterised.
            
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        eligible_bldg_list : list of lxml.etree Element 
            The GML building to be parameterised.
        
        non_eligible_bldg_list : list of lxml.etree Element 
            The GML building that will not be parameterised.
        """
        eligible_bldg_list = []
        non_eligible_bldg_list = []
        for gml_bldg in gml_bldg_list:
            eligibility = True
            if self.bldg_class != None: 
                bldg_class = pycitygml_reader.get_building_class(gml_bldg)
                if self.bldg_class != bldg_class:
                    eligibility = False
                    
            if self.bldg_function != None:
                bldg_function = pycitygml_reader.get_building_function(gml_bldg)
                if self.bldg_function != bldg_function:
                    eligibility = False
            
            if self.bldg_usage != None:
                bldg_usage = pycitygml_reader.get_building_usage(gml_bldg)
                if self.bldg_usage != bldg_usage:
                    eligibility = False
                    
            if eligibility == True:
                eligible_bldg_list.append(gml_bldg)
                
            if eligibility == False:
                non_eligible_bldg_list.append(gml_bldg)
                
        return eligible_bldg_list, non_eligible_bldg_list
        
    def define_int_range(self, start, stop, step):
        """ 
        The function defines the range of the parameter if the parameter type is integer.
        
        Parameters
        ----------
        start : int
            The starting number of the sequence.
        
        stop : int
            Generate numbers up to, including this number.
        
        step : int
            The difference between each number in the sequence.
        
        Returns
        -------        
        parameter range : list of ints
            List of generated parameters.
        """
        parm_range = super(BldgTaperParm, self).define_int_range(start, stop, step)
        self.parm_range = parm_range
        return parm_range
        
    def define_float_range(self, start, stop, step=None):
        """ 
        The function defines the range of the parameter if the parameter type is float.
        
        Parameters
        ----------
        start : float
            The starting number of the sequence.
        
        stop : float
            Generate numbers up to, including this number.
        
        step : float, optional
            The difference between each number in the sequence, default = None. When None the parameter is a continuous parameter, if not None the parameter is a discrete parameter.
        
        Returns
        -------        
        parameter range : list of floats
            List of generated float parameters if step = None, if step != None the parameter range is made up of two numbers the start and the end of the continuous parameter.
        """
        parm_range = super(BldgTaperParm, self).define_float_range(start, stop, step=step)
        self.parm_range = parm_range
        return parm_range
        
    def set_parm_range(self, parm_range):
        """ 
        The function defines the range of the parameter .
        
        Parameters
        ----------
        parm_range : list of ints/floats
            The parameter range.
        """
        self.parm_range = parm_range
        
    def map_nrmlise_parms_2_parms(self, nrmlised_parm_list):
        """ 
        The function maps the the normalise parameter list to the real parameter list.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        parameter list : list of int/floats
            List of real parameters.
        """
        if self.parm_range == None:
            raise Exception("please define parm range")
        parm_list = super(BldgTaperParm, self).map_nrmlise_parms_2_parms(nrmlised_parm_list)
        return parm_list
        
    def define_nparameters(self,pycitygml_reader):
        """ 
        The function determines the total parameters for parameterising the model.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
            
        Returns
        -------        
        nparameters : int
            The number of parameters for the model.
        """
        gml_bldg_list = pycitygml_reader.get_buildings()
        #filter through the eligible buildings
        eligible_bldg_list, non_eligible_bldg_list = self.eligibility_test(gml_bldg_list, pycitygml_reader)
        #because each building has one building height parameter
        nparameters = len(eligible_bldg_list)
        return nparameters
                
    def execute(self, pycitygml_reader, nrmlised_parm_list):
        """ 
        This funciton defines the parameterisation process and executes the process. A design alternative of the parametric model is returned.
        
        Parameters
        ----------
        pycitygml_reader : pycitygml.Reader class instance
            The reader to read the CityGML file to be parameterised.
        
        nrmlised_parm_list : list of ints/floats
            The normalised parameters to be mapped to the real parameters defined, the parameters will be used to generate a design alternative.
            
        Returns
        -------        
        new pycitygml_reader : pycitygml.Reader class instance
            The new design alternative generated and documented as a CityGML model.
        """
        parm_list = self.map_nrmlise_parms_2_parms(nrmlised_parm_list)
        citygml_writer = pycitygml.Writer()
        gml_landuses = pycitygml_reader.get_landuses()
        gml_bldg_list = pycitygml_reader.get_buildings()
        flr2flr_height = self.flr2flr_height
        bcnt = 0
        for gml_landuse in gml_landuses:
            #check which buildings are on this plot
            gml_bldg_on_luse = gml3dmodel.buildings_on_landuse(gml_landuse,gml_bldg_list, pycitygml_reader)
            
            #check which buildings should this parameter be applied to
            eligibility_bldg_list, non_eligible_bldg_list = self.eligibility_test(gml_bldg_on_luse, pycitygml_reader)
            n_eligibility_bldgs = len(eligibility_bldg_list)
            
            #get the parameters for this landuse plot
            parms_4_luse = parm_list[bcnt:bcnt+n_eligibility_bldgs]
            
            #twist the bldg
            bcnt = 0
            for eligible_gml_bldg in eligibility_bldg_list:
                #get the twist parm for the bldg
                parm = parms_4_luse[bcnt]
                parm = parm-1.0
                
                #extract the bldg solid
                bldg_solid = gml3dmodel.get_building_occsolid(eligible_gml_bldg, pycitygml_reader)
                bldg_solid_midpt = py3dmodel.calculate.get_centre_bbox(bldg_solid)
                xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(bldg_solid)
                #bend each bldg according to the parameter
                #first get all the floorplates 
                height, nstorey, storey_height = gml3dmodel.get_building_height_storey(eligible_gml_bldg, pycitygml_reader, 
                                                                                       flr2flr_height = flr2flr_height)

                plates_occface_2dlist = gml3dmodel.get_building_plates_by_level(bldg_solid, nstorey, storey_height, 
                                                                                roundndigit = 4, distance = 0.2)
                
                #plates_occface_list = reduce(lambda x,y :x+y ,plates_occface_2dlist)
                #print "NUM OF FLOOR PLATES", len(plates_occface_list)
                #py3dmodel.construct.visualise([plates_occface_list], ["BLUE"])

                nlvl = len(plates_occface_2dlist)
                interval = float(parm)/float(nlvl)
                
                lvl_shell_list = []
                external_horz_plate_list = []
                external_horz_plate_list1 = []
                #print "NUM OF LEVELS", nlvl
                for pcnt in range(nlvl-1):                    
                    magnitude = interval*(pcnt+1)
                    magnitude = 1.0 + magnitude
                    if pcnt == 0:
                        cur_plate_list = plates_occface_2dlist[pcnt]
                        external_horz_plate_list.extend(cur_plate_list)
                        
                    nxt_plate_list = plates_occface_2dlist[pcnt+1]
                    plate_cmpd = py3dmodel.construct.make_compound(nxt_plate_list)
                    #plate_midpt = py3dmodel.calculate.get_centre_bbox(plate_cmpd)
                    #taper
                    trsf_plate_shape = py3dmodel.modify.scale(plate_cmpd, magnitude, bldg_solid_midpt)
                    trsf_nxt_plate_list = py3dmodel.fetch.geom_explorer(trsf_plate_shape, "face")
                    
                    n_cur_plates = len(cur_plate_list)
                    n_nxt_plates = len(trsf_nxt_plate_list)
                    
                    #taper the next plates
                    if n_cur_plates == n_nxt_plates:
                        for pcnt2 in range(n_cur_plates):
                            cur_plate = cur_plate_list[pcnt2]
                            #find the nearest face to loft 
                            if len(trsf_nxt_plate_list) > 1:
                                min_dist_list = []
                                for trsf_nxt_plate in trsf_nxt_plate_list:
                                    min_dist = py3dmodel.calculate.minimum_distance(cur_plate, trsf_nxt_plate)
                                    min_dist_list.append(min_dist)
                                    
                                min_min_dist = min(min_dist_list)
                                min_index = min_dist_list.index(min_min_dist)
                                nxt_plate = trsf_nxt_plate_list[min_index]
                            else:
                                nxt_plate = trsf_nxt_plate_list[pcnt2]
                            
                            cur_plate_area = py3dmodel.calculate.face_area(cur_plate)
                            nxt_plate_area = py3dmodel.calculate.face_area(nxt_plate)
                            diff_area = abs(nxt_plate_area-cur_plate_area)
                            
                            if diff_area/cur_plate_area >= 0.5:
                                cur_midpt = py3dmodel.calculate.face_midpt(cur_plate)
                                m_cur_midpt = py3dmodel.modify.move_pt(cur_midpt, (0,0,1), flr2flr_height)
                                m_cur_plate = py3dmodel.modify.move(cur_midpt, m_cur_midpt, cur_plate)
                                trsf_plate_shape = py3dmodel.modify.scale(m_cur_plate, 1+interval, bldg_solid_midpt)
                                trsf_cur_plate= py3dmodel.fetch.geom_explorer(trsf_plate_shape, "face")[0]
                                
                                plates2loft = [cur_plate, trsf_cur_plate]
                                lvl_shell = py3dmodel.construct.make_loft(plates2loft, rule_face = True)
                                lvl_shell_list.append(lvl_shell)
                                #the last level append the roof
                                if pcnt == nlvl-2:
                                    external_horz_plate_list.append(trsf_cur_plate)
                                else:
                                    external_horz_plate_list1.append([])
                                    external_horz_plate_list1[-1].append(nxt_plate)
                                    external_horz_plate_list1[-1].append(trsf_cur_plate)
                            else:
                                plates2loft = [cur_plate, nxt_plate]
                                lvl_shell = py3dmodel.construct.make_loft(plates2loft, rule_face = True)
                                lvl_shell_list.append(lvl_shell)
                                #the last level append the roof
                                if pcnt == nlvl-2:
                                    external_horz_plate_list.append(nxt_plate)
                            
                    if n_cur_plates != n_nxt_plates:
                        #move the cur plate up and rotate them 
                        if pcnt!=nlvl-2:
                            external_horz_plate_list1.append([])
                            external_horz_plate_list1[-1].extend(trsf_nxt_plate_list)
                        for cur_plate in cur_plate_list:
                            cur_midpt = py3dmodel.calculate.face_midpt(cur_plate)
                            m_cur_midpt = py3dmodel.modify.move_pt(cur_midpt, (0,0,1), flr2flr_height)
                            m_cur_plate = py3dmodel.modify.move(cur_midpt, m_cur_midpt, cur_plate)
                            #if there is a boolean it means it is connected to the upper floor in some way
                            common_plate = py3dmodel.construct.boolean_common(m_cur_plate, plate_cmpd)
                            if common_plate:
                                m_cur_midpt2 = py3dmodel.modify.move_pt(m_cur_midpt, (1,0,0), interval)
                                trsf_plate_shape = py3dmodel.modify.move(cur_midpt, m_cur_midpt2, cur_plate)
                                trsf_plate_shape = py3dmodel.modify.scale(m_cur_plate, 1+interval, bldg_solid_midpt)
                                trsf_cur_plate= py3dmodel.fetch.geom_explorer(trsf_plate_shape, "face")[0]
                                
                                plates2loft = [cur_plate, trsf_cur_plate]
                                lvl_shell = py3dmodel.construct.make_loft(plates2loft, rule_face = True)
                                lvl_shell_list.append(lvl_shell)
                                #the last level append the roof
                                if pcnt == nlvl-2:
                                    external_horz_plate_list.append(trsf_cur_plate)
                                else:
                                    external_horz_plate_list1[-1].append(trsf_cur_plate)
                            else:
                                external_horz_plate_list.append(cur_plate)
                                
                    cur_plate_list = trsf_nxt_plate_list
                
                #need to union all the volumes
                diff_list = []
                for horz_plate_list in external_horz_plate_list1:
                    hcnt = 0
                    for lvl in horz_plate_list:
                        external_horz_plate_list2 = horz_plate_list[:]
                        del external_horz_plate_list2[hcnt]
                        external_horz_plate_extruded_list = gml3dmodel.extrude_move_down_occ_faces(external_horz_plate_list2)
                        hplate2_cmpd = py3dmodel.construct.make_compound(external_horz_plate_extruded_list)
                        diff_cmpd = py3dmodel.construct.boolean_difference(lvl, hplate2_cmpd)
                        diff_face_list = py3dmodel.construct.simple_mesh(diff_cmpd)
                        if diff_face_list:
                            diff_list.extend(diff_face_list)
                        hcnt+=1
                
                lvl_shell_cmpd = py3dmodel.construct.make_compound(lvl_shell_list)
                lvl_faces = py3dmodel.construct.simple_mesh(lvl_shell_cmpd)
                #py3dmodel.construct.visualise([lvl_faces], ["RED"])
                external_horz_plate_cmpd = py3dmodel.construct.make_compound(external_horz_plate_list)
                external_horz_plate_list = py3dmodel.construct.simple_mesh(external_horz_plate_cmpd)
                new_bldg_face_list = lvl_faces + external_horz_plate_list + diff_list
                new_building_shell_list = py3dmodel.construct.make_shell_frm_faces(new_bldg_face_list)
                
                if len(new_building_shell_list)>1:
                    print "NUMBER OF SOLIDS:", len(new_building_shell_list)
                    
                    if external_horz_plate_list1:
                        external_horz_plate_list2 = reduce(lambda x,y :x+y ,external_horz_plate_list1)
                        new_bldg_face_list = lvl_faces + external_horz_plate_list + external_horz_plate_list2
                    else:
                        new_bldg_face_list = lvl_faces + external_horz_plate_list
                        
                    new_building_shell_list = py3dmodel.construct.make_shell_frm_faces(new_bldg_face_list)
                    if len(new_building_shell_list) == 1:
                        new_bldg_occsolid = py3dmodel.construct.make_solid(new_building_shell_list[0])
                        new_bldg_occsolid = py3dmodel.modify.fix_close_solid(new_bldg_occsolid)
                    else:
                        vol_list = []
                        for shell in new_building_shell_list:
                            bldg_solid = py3dmodel.construct.make_solid(shell)
                            bldg_solid = py3dmodel.modify.fix_close_solid(bldg_solid)
                            solid_vol = py3dmodel.calculate.solid_volume(bldg_solid)
                            vol_list.append(solid_vol)
                            
                        max_vol = max(vol_list)
                        max_index = vol_list.index(max_vol)
                        new_bldg_shell = new_building_shell_list[max_index]
                        new_bldg_occsolid = py3dmodel.construct.make_solid(new_bldg_shell)
                        new_bldg_occsolid = py3dmodel.modify.fix_close_solid(new_bldg_occsolid)
                    
                else:
                    new_building_shell =new_building_shell_list[0]
                    new_bldg_occsolid = py3dmodel.construct.make_solid(new_building_shell)
                    new_bldg_occsolid = py3dmodel.modify.fix_close_solid(new_bldg_occsolid)
                    
                #py3dmodel.construct.visualise([[new_bldg_occsolid]], ["RED"])
                new_height, new_n_storey = gml3dmodel.calculate_bldg_height_n_nstorey(new_bldg_occsolid, storey_height)
                gml3dmodel.update_gml_building(eligible_gml_bldg,new_bldg_occsolid, pycitygml_reader, 
                                               citygml_writer, new_height = new_height, new_nstorey = new_n_storey)
                
                bcnt+=1
                
        non_bldg_cityobjs = pycitygml_reader.get_non_xtype_cityobject("bldg:Building")
        gml3dmodel.write_citygml(non_bldg_cityobjs, citygml_writer)
        gml3dmodel.write_non_eligible_bldgs(non_eligible_bldg_list, citygml_writer)
        citymodel_node = citygml_writer.citymodelnode
        reader = pycitygml.Reader()
        reader.load_citymodel_node(citymodel_node)
        return reader