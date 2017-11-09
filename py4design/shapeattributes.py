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
class ShapeAttributes(object):
    """
    An object that allows the documentation of topology objects and append attributes to them.
    
    Attributes
    ----------    
    dictionary : dictionary
        The dictionary of attributes appended to the object.
    """
    def __init__(self):
        """Initialises the class"""
        self.dictionary = {}
        
    def set_shape(self, occtopo):
        """
        Appends the geometry as the "shape" attribute to the object
        
        Parameters
        ----------
        occtopo : OCCtopology
            The OCCtopology to be documented and append with attributes.
            OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        """
        self.dictionary["shape"] = occtopo
        
    @property
    def shape(self):
        """
        Retrieve the the geometry from the object.
        
        Parameters
        ----------
        occtopo : OCCtopology
            The OCCtopology to be documented and append with attributes.
            OCCtopology includes: OCCshape, OCCcompound, OCCcompsolid, OCCsolid, OCCshell, OCCface, OCCwire, OCCedge, OCCvertex 
        """
        return self.dictionary["shape"]
    
    def set_analysis_rule_item(self, key, val):
        """
        Sets analysis rule condition for the BaseAnalysisRule base class.
        
        Parameters
        ----------
        key : str
            The name of the base analysis rule.
        
        val : bool
            The value of the base analysis rule, True or False.
        """
        if not isinstance(key, str):
            raise ValueError("key must be a str")
        if not isinstance(val, bool):
            raise ValueError("val must be a bool (True or False)")
        self.dictionary[key] = val
        
    def get_value(self, key):
        """
        Retrieve the value of the attribute specified.
        
        Parameters
        ----------
        key : str
            The name of the attribute value to retrieve.
        """
        return self.dictionary[key]
    
    def set_key_value(self, key, value):
        """
        Sets an attribute for the object.
        
        Parameters
        ----------
        key : str
            The name of the attribute.
        
        val : str, float, int, bool
            The value of the attribute.
        """
        self.dictionary[key] = value