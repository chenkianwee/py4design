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
import math

def frange(start, end=None, inc=None):
    """
    A range function, that does accept float increments.
    
    Parameters
    ----------
    start : float
        The starting number of the sequence.
        
    end : float, optional
        Generate numbers up to, but not including this number, Default = None. When None, end == start and start = 0.0.
        
    inc : float, optional
        The difference between each number in the sequence, Default = None. When None, inc = 1.0.
        
    Returns
    -------
    sequence of floats : list of floats
        A list of float.
    """
    if end == None:
        end = start + 0.0
        start = 0.0
    else: start += 0.0 # force it to be a float

    if inc == None:
        inc = 1.0
    count = int(math.ceil((end - start) / inc))

    L = [None,] * count

    L[0] = start
    for i in xrange(1,count):
        L[i] = L[i-1] + inc
    return L
    
def findmedian(lst):
    """
    This function finds the median.
    
    Parameters
    ----------
    lst : list of ints/floats
        The list to be analysed.
        
    Returns
    -------
    median : int/float
        The median of the list.
    """
    sortedLst = sorted(lst)
    lstLen = len(lst)
    index = (lstLen - 1) // 2

    if (lstLen % 2):
        return sortedLst[index]
    else:
        return (sortedLst[index] + sortedLst[index + 1])/2.0
    
def round2nearest_base(x, base=5):
    """
    This function rounds the int/float to the nearest base.
    
    Parameters
    ----------
    x : int/float
        The number to be rounded.
        
    base : int, optional
        The base to round x to, if 5 will round to the nearest multiple of 5, if 10 will round to the nearest 10.
        
    Returns
    -------
    rounded number : int/float
        The rounded number.
    """
    return int(base * round(float(x)/base))