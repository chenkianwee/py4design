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
"""
Pyliburo: Python Library for Urban Optimisation
================================================
Documentation is available in the docstrings and online at xxx. 
Contents
--------
Subpackages & Submodules
------------------------
Using any of these subpackages requires an explicit import. For example, import pyliburo.py3dmodel.
::
    
 py2energyplus                --- Python library to write idf file and execute energyplus
 py2radiance                  --- Python library to write rad file and execute radiance/daysim
 py3dmodel                    --- A wrapper of CAD Kernel PythonOCC, dependencies: PythonOCC, OCCUtils, scipy/numpy, pycollada
 pycitygml                    --- Python library to read and write LOD1 Citygml 2.0, dependencies: lxml
 pyoptimise                   --- Optimisation module currently includes NSGAII, dependencies: matplotlib, scikit-learn, pymf, cvxopt
    
Using any of these modules requires an explicit import. For example, import pyliburo.utility.
::
    
 analysisrulepalette          --- Base rules for converting geometrical to CityGML model (LOD1), uses subpackages: py3dmodel
 buildingformeval             --- Functions for evaluating building forms, uses subpackages: py3dmodel, py2radiance, uses modules: utility, gml3dmodel
 citygml2eval                 --- Evaluation of CityGML (LOD1) file, uses subpackages: pycitygml, py3dmodel, uses modules: gml3dmodel, urbanformeval
 gml3dmodel                   --- Funcitons to process 3D geometries CityGML file (LOD1), uses subpackages: py3dmodel, pycitygml, uses modules: utility3d
 gmlparameterise              --- Module for parameterising a CityGML model (LOD1), uses subpackages: pycitygml
 gmlparmpalette               --- Base parameters for parameterisng a CityGML model (LOD1), uses subpackages: pycitygml, py3dmodel, uses modules: gml3dmodel, utility
 massing2citygml              --- Convert a massing model into CityGML model (LOD1), dependencies: pycollada, uses subpackages: py3dmodel, pytcitygml, uses modules: gml3dmodel, shapeattributes
 shapeattributes              --- A class to store attributes in geometries
 shp2citygml                  --- Functions to convert shapefiles to CityGML models, dependencies: shapefile, uses subpackages: pycitygml, py3dmodel, uses modules: gml3dmodel
 skyviewfactor                --- Functions to calculate sky view factor, uses subpackages: py3dmodel
 templaterulepalette          --- Base template rules to convert geometrical to CityGML model (LOD1), uses subpackages: py3dmodel, uses modules: gml3dmodel
 urbanformeval                --- Functions to evaluate urban forms, dependencies: networkx, uses subpackages: py3dmodel, py2radiance, uses modules: gml3dmodel
 urbangeom                    --- Functions to process urban geometries, uses subpackages: py3dmodel
 utility                      --- Utility functions
"""