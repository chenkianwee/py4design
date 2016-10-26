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
import numpy as np
import matplotlib.pyplot as plt

def scatter_plot(pts2plot_2dlist, colour_list):
    x =[]
    y = []
    colours = []
    area = []
    #nclrs = len(pts2plot_2dlist)
    #step = 1.0/float(nclrs)
    cnt = 0
    colors = np.random.rand(10)
    print colors
    for pts2plot in pts2plot_2dlist:
        for pt in pts2plot:
            x.append(pt[0])
            y.append(pt[1])
            colours.append(colour_list[cnt])
            area.append(15)
            
        cnt +=1
        
    print x, y
    plt.scatter(x, y,s = area , c=colours, alpha=0.5)
    plt.show()