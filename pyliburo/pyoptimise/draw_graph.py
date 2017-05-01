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
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def scatter_plot(pts2plotlist, colourlist, pt_arealist, label_size = 16, labellist = [], xlabel = "", ylabel = "", title = "", 
                 savefile = ""):
    x =[]
    y = []

    cnt = 0
    for pt in pts2plotlist:
        x.append(pt[0])
        y.append(pt[1])
        cnt +=1
    
    plt.scatter(x, y, s = pt_arealist , c=colourlist, alpha=0.5)
    
    if labellist:
        for i, txt in enumerate(labellist):
            #print i, txt, len(x), len(y)
            plt.annotate(txt, (x[i],y[i]))
    
    if xlabel:
        plt.xlabel(xlabel, fontsize=label_size)
    if ylabel:
        plt.ylabel(ylabel, fontsize=label_size)
    if title:
        plt.title(title, fontsize=label_size )
    if savefile:
        plt.savefig(savefile, dpi = 300,transparent=True,papertype="a3")
        
    plt.tick_params(axis='both', which='major', labelsize=label_size)
    plt.show()
    
def scatter_plot3d(pt3d_list, colour_list, pt_arealist, labellist = [], xlabel = "", ylabel = "", zlabel = "", title = "", 
                 savefile = "", elev=30, azim = -45, surface_pts = None):
    
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    x =[]
    y = []
    z=[]

    cnt = 0
    for pt in pt3d_list:
        x.append(pt[0])
        y.append(pt[1])
        z.append(pt[2])
        cnt +=1
        
    ax.scatter(x, y, z, c=colour_list)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    plt.title(title )
    ax.view_init(elev=elev, azim=-azim)
    plt.savefig(savefile, dpi = 300,transparent=True,papertype="a3")
    
def scatter_plot_surface3d(pt3d_list, colour_list, pt_arealist, labellist = [], xlabel = "", ylabel = "", zlabel = "", title = "", 
                 savefile = "", elev=30, azim = -45):
    
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    x =[]
    y = []
    z=[]

    cnt = 0
    for pt in pt3d_list:
        x.append(pt[0])
        y.append(pt[1])
        z.append(pt[2])
        cnt +=1
        
    ax.plot_trisurf(x, y, z, linewidth=0.2, antialiased=True)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    plt.title(title )
    ax.view_init(elev=elev, azim=-azim)
    plt.savefig(savefile, dpi = 300,transparent=True,papertype="a3")
    
    