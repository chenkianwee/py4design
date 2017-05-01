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
class ShapeAttributes(object):
    def __init__(self):
        self.dictionary = {}
        
    def set_shape(self, occshape):
        self.dictionary["shape"] = occshape
        
    @property
    def shape(self):
        return self.dictionary["shape"]
    
    def set_analysis_rule_item(self, key, val):
        if not isinstance(key, str):
            raise ValueError("key must be a str")
        if not isinstance(val, bool):
            raise ValueError("val must be a bool (True or False)")
        self.dictionary[key] = val
        
    def get_value(self, key):
        return self.dictionary[key]