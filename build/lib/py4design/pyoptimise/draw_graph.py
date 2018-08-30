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
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def scatter_plot(pts2plotlist, colourlist, pt_arealist, label_size = 16, labellist = [], xlabel = "", ylabel = "", title = "", 
                 savefile = ""):
    """
    This function plots a scatter plot.
    
    Parameters
    ----------
    pts2plotlist : 2d list of floats
        The pts2plotlist is in this format: [point1, point2, pointx], pointx = [x,y]
        
    colourlist : list of str
        List of string describing the colours, e.g. "red", "blue", "yellow".
        
    pt_arealist : list of floats
        List of floats describing the size of each point.
        
    label_size : int, optional
        The font size of the labels, Default = 16.
        
    labellist : list of str
        List of string describing the points.
        
    xlabel : str, optional
        String describing the x-axis, Default = "".
        
    ylabel : str, optional
        String describing the y-axis, Default = "".
        
    title : str, optional
        String describing the graph, Default = "".
        
    savefile : str, optional
        The filepath to save the generated graph image, Default = "".
    """
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
                 savefile = "", elev=30, azim = -45):
    """
    This function plots a 3d scatter plot.
    
    Parameters
    ----------
    pt3d_list : 2d list of floats
        The pts2plotlist is in this format: [point1, point2, pointx], pointx = [x,y,z]
        
    colourlist : list of str
        List of string describing the colours, e.g. "red", "blue", "yellow".
        
    pt_arealist : list of floats
        List of floats describing the size of each point.
        
    label_size : int, optional
        The font size of the labels, Default = 16.
        
    labellist : list of str
        List of string describing the points.
        
    xlabel : str, optional
        String describing the x-axis, Default = "".
        
    ylabel : str, optional
        String describing the y-axis, Default = "".
        
    zlabel : str, optional
        String describing the z-axis, Default = "".
        
    title : str, optional
        String describing the graph, Default = "".
        
    savefile : str, optional
        The filepath to save the generated graph image, Default = "".
        
    elev : float, optional
        The elevation of the view, Default = 30.
        
    azim : float, optional
        The angle of the view, Default = -45.
    """
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()
    ax = Axes3D(fig)
    #ax = fig.gca(projection='3d')
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
    """
    This function plots a 3d surface scatter plot.
    
    Parameters
    ----------
    pt3d_list : 2d list of floats
        The pts2plotlist is in this format: [point1, point2, pointx], pointx = [x,y,z]
        
    colourlist : list of str
        List of string describing the colours, e.g. "red", "blue", "yellow".
        
    pt_arealist : list of floats
        List of floats describing the size of each point.
        
    label_size : int, optional
        The font size of the labels, Default = 16.
        
    labellist : list of str
        List of string describing the points.
        
    xlabel : str, optional
        String describing the x-axis, Default = "".
        
    ylabel : str, optional
        String describing the y-axis, Default = "".
        
    zlabel : str, optional
        String describing the z-axis, Default = "".
        
    title : str, optional
        String describing the graph, Default = "".
        
    savefile : str, optional
        The filepath to save the generated graph image, Default = "".
        
    elev : float, optional
        The elevation of the view, Default = 30.
        
    azim : float, optional
        The angle of the view, Default = -45.
    """
    from mpl_toolkits.mplot3d import Axes3D
    
    fig = plt.figure()
    ax = Axes3D(fig)
    #fig.gca(projection='3d')
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
    
def parallel_coordinates(data_sets, parmlabels, savefile = "", style=None):
    """
    This function plots a parallel coordinate plot.
    
    Parameters
    ----------
    data_sets : 2d list of floats
        Each list in the 2d list is a line on the PCP.
        
    parmlabels : list of str
        List of string describing each axis of the PCP.
    
    savefile : str, optional
        The filepath to save the generated graph image, Default = "".
        
    style : list of str, optional
        List of string describing the colours, e.g. "red", "blue", "yellow". If None all the lines are black.
        
    """
    dims = len(data_sets[0])
    x    = range(dims)
    fig, axes = plt.subplots(1, dims-1, sharey=False)

    if style is None:
        style = ['black']*len(data_sets)

    # Calculate the limits on the data
    min_max_range = list()
    for m in zip(*data_sets):
        #check if the data are whole numbers or float
        num_d = len(m)
        is_integer = []
        is_int_data = False
        for d in m:
            if d.is_integer():
                is_integer.append(1)

        if is_integer.count(1) == num_d:
            is_int_data = True
        
        mn = min(m)
        mx = max(m)
        if mn == mx:
            mn -= 0.5
            mx = mn + 1.
        r  = float(mx - mn)
        min_max_range.append((mn, mx, r, is_int_data))

    # Normalize the data sets
    norm_data_sets = list()
    for ds in data_sets:
        nds = [(value - min_max_range[dimension][0]) / 
                min_max_range[dimension][2] 
                for dimension,value in enumerate(ds)]
        norm_data_sets.append(nds)
    data_sets = norm_data_sets
    # Plot the datasets on all the subplots
    for i, ax in enumerate(axes):
        for dsi, d in enumerate(data_sets):
            ax.plot(x, d, style[dsi])
        ax.set_xlim([x[i], x[i+1]])
        #set the x tick labels for first few dimensions 
        ax.set_xticks([0])
        ax.set_xticklabels([parmlabels[i]])

    # Set the x axis ticks 
    for dimension, (axx,xx) in enumerate(zip(axes, x[:-1])):
        axx.xaxis.set_major_locator(ticker.FixedLocator([xx]))
        ticks = len(axx.get_yticklabels())
        labels = list()
        data_range = min_max_range[dimension][2]
        is_it_int = min_max_range[dimension][3]
        if is_it_int:
            if data_range <=25:
                axx.set_yticks(create_int_normalise(data_range))
                ticks = len(axx.get_yticklabels())
                
        step = min_max_range[dimension][2] / (ticks - 1)
        mn   = min_max_range[dimension][0]
        if is_it_int:
            if data_range <=25:
                for i in xrange(ticks):
                    v = int(mn + i*step)
                    labels.append('%4.0f' % v)
            else:
                for i in xrange(ticks):
                    v = mn + i*step
                    labels.append('%4.2f' % v)
        else:
            for i in xrange(ticks):
                v = mn + i*step
                labels.append('%4.2f' % v)
        axx.set_yticklabels(labels)
        for yticklabel in axx.get_yticklabels():
            yticklabel.set_fontsize(16)
        for xticklabel in axx.get_xticklabels():
            xticklabel.set_fontsize(14)
            xticklabel.set_y(-0.01)
        
    # Move the final axis' ticks to the right-hand side
    axx = plt.twinx(axes[-1])
    dimension += 1
    axx.xaxis.set_major_locator(ticker.FixedLocator([x[-2], x[-1]]))
    #set the x tick labels for last 2 dimension 
    ax.set_xticklabels([parmlabels[-2],parmlabels[-1]])
    ticks = len(axx.get_yticklabels())
    data_range = min_max_range[dimension][2]
    is_it_int = min_max_range[dimension][3]
    if is_it_int:
            if data_range <=25:
                axx.set_yticks(create_int_normalise(data_range))
                ticks = len(axx.get_yticklabels())
                
    step = min_max_range[dimension][2] / (ticks - 1)
    mn   = min_max_range[dimension][0]
    if is_it_int:
        if data_range <=25:
            labels = ['%4.0f' % (int(mn + i*step)) for i in xrange(ticks)]
        else:
            labels = ['%4.2f' % (mn + i*step) for i in xrange(ticks)]
    else:
        labels = ['%4.2f' % (mn + i*step) for i in xrange(ticks)]
        
    axx.set_yticklabels(labels)
    for yticklabel in axx.get_yticklabels():
        yticklabel.set_fontsize(16)

    for xticklabel in ax.get_xticklabels():
        xticklabel.set_fontsize(14)
        xticklabel.set_y(-0.01)


    # Stack the subplots 
    plt.subplots_adjust(wspace=0)
    if savefile:
        plt.savefig(savefile, dpi = 300,transparent=True,papertype="a3")
    plt.show()

def create_int_normalise(r):
    """
    This function creates a list of normalise integers within the specified range.
    
    Parameters
    ----------
    r : float
       The range.
    
    Returns
    -------
    normalised list : list of integers
        List of normalised integers.
    """
    step = 1/r
    norm_list = []
    for i in range(int(r+1)):
        norm_list.append(i*step)
    return norm_list