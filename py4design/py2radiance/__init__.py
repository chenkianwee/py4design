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

import os
import subprocess
import shutil

import write_rad


class Rad(object):
    """
    An object that contains all the neccessary information for running a Radiance/Daysim simulation.
    
    Parameters
    ----------
    base_file_path :  str
        The file path of the base.rad file. The base.rad file documents all the basic information of the simulation e.g. materials, constructions ... It is distributed together with py2radiance.
        
    data_folder_path :  str
        The directory to write all the results file to.

    Attributes
    ----------
    base_file_path :  str
        The file path of the base.rad file.
    
    data_folder_path :  str
        The directory to write all the results file to.
        
    command_file: str
        The file path of the command.txt. The command file documents all the executed Radiance/Daysim commands.
    
    surfaces: list of Surface class instances
        The list of surfaces that will be analysed by Radiance/Daysim.
        
    sensor_positions: pyptlist
        List of positions for sensing. Pyptlist is a list of tuples of floats. A pypt is a tuple that documents the xyz coordinates of a 
        pt e.g. (x,y,z), thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
    
    sensor_normals: pyveclist
        List of normals of the points sensing. Pyveclist is a list of tuples of floats. A pyvec is a tuple that documents the xyz coordinates of a 
        direction e.g. (x,y,z), thus a pyveclist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    sensor_file_path :  str
        The file path of the sensor file.
        
    rad_file_path :  str
        The file path of the rad file.
        
    sky_file_path :  str
        The file path of the sky file.
        
    oconv_file_path :  str
        The file path of the oconv file.
        
    cumulative_sky_file_path :  str
        The file path of the cumulative sky file.
        
    cumulative_oconv_file_path :  str
        The file path of the cumulative sky oconv file.
        
    result_file :  str
        The file path of the result file.
        
    cumulative_result_file_path :  str
        The file path of the cumulative result file.
        
    daysimdir_ies :  str
        The daysim ies directory path.
        
    daysimdir_pts :  str
        The daysim points directory path.
        
    daysimdir_rad :  str
        The daysim rad directory path.
        
    daysimdir_res :  str
        The daysim res directory path.
        
    daysimdir_tmp :  str
        The daysim tmp directory path.
        
    daysimdir_wea :  str
        The daysim wea directory path.
        
    hea_file :  str
        The file path of the hea header daysim file.
        
    hea_filename :  str
        The name of the hea header daysim file.
        
    sunuphrs :  int
        The number of daylight hours in the weather file.
        
    Examples
    --------
    #initialise the rad class
        >>> rad = Rad("C:\\base.rad", "C:\\rad_results")
    #append surfaces for the simulation
        >>> RadSurface("srfname1", [(0,0,0), (0,1,0), (1,1,0), (0,1,0)], "srfmat", rad)
    #set sensor points
        >>> rad.set_sensor_points([(0,0.2,0), (0,0.5,0)],[(0,0,1), (0,0,1)] )
    #set the sky
        >>> rad.set_sky( "!gensky 1 31 15 -c -a 1.3 -o -103.9 -m -120", (1,1,1), (0.2.0.2.0.2))
        >>> rad.execute_oconv()
        >>> dict_parm = {"ab": 2, "aa": 0.15, "ar": 128, "ad": 512, "as":256}
        >>> rad.execute_rtrace(dict_parm)
    #evaluate the result
        >>> rad.eval_rad()
    #for rpict rvu and falsecolor
        >>> vp = (0,0,0)
        >>> vd = (1,0,0)
        >>> rad.execute_rvu(vp, vd, dict_parm)
        >>> rad.execute_rpict("pict1", "640", "480", vp, vd, dict_parm)
        >>> rad.execute_falsecolor("C:\\i_pict.tif", "C:\\l_pict.tif", "falsecolor_pict", "1000", "10", illuminance = True)
    #FOR GENCUMULATIVE SKY MODULE
        >>> rad = Rad("C:\\base.rad", "C:\\rad_results")
        >>> RadSurface("srfname1", [(0,0,0), (0,1,0), (1,1,0), (0,1,0)], "srfmat", rad)
        >>> rad.set_sensor_points([(0,0.2,0), (0,0.5,0)],[(0,0,1), (0,0,1)] )
    #the gencumulative sky
        >>> rad.execute_cumulative_oconv("7 19", "1 1 12 31", "c:\\weatherfile.epw", output = "irradiance")
        >>> rad.execute_cumulative_rtrace("2")
    #FOR DAYSIM MODULE
        >>> rad = Rad("C:\\base.rad", "C:\\rad_results")
        >>> RadSurface("srfname1", [(0,0,0), (0,1,0), (1,1,0), (0,1,0)], "srfmat", rad)
    #for daysim you need to create the sensor files
        >>> rad.set_sensor_points([(0,0.2,0), (0,0.5,0)],[(0,0,1), (0,0,1)] )
        >>> rad.create_sensor_input_file()
    #initialise the daysim module
        >>> rad.initialise_daysim("c:\\daysim_dir")
    #convert the epw to wea
        >>> rad.execute_epw2wea(weatherfilepath)
    #convert the rad files to daysim files
        >>> rad.create_rad_input_file()
        >>> rad.execute_radfiles2daysim()
    #write the default radiance parameters
        >>> rad.write_default_radiance_parameters()
    #execute the gen_dc and ds_illum
        >>> rad.execute_gen_dc("w/m2")
        >>> rad.execute_ds_illum()
    #evaluate the result
        >>> res_dict = rad.eval_ill().
            
    """

    def __init__(self, base_file_path, data_folder_path):
        """
        This function initialises the Rad class.
        """
        # paths
        self.base_file_path = base_file_path
        self.data_folder_path = data_folder_path
        self.command_file = os.path.join(data_folder_path, "command.txt")
        if os.path.exists(self.command_file):
            open(self.command_file, "w").close()
        if not os.path.isdir(data_folder_path):
            os.mkdir(data_folder_path)
            # data
        self.surfaces = []
        self.sensor_positions = None
        self.sensor_normals = None
        # input files
        self.sensor_file_path = None
        self.rad_file_path = None
        self.sky_file_path = None
        self.oconv_file_path = None
        self.cumulative_sky_file_path = None
        self.cumulative_oconv_file_path = None
        # output files
        self.result_file = None
        self.cumulative_result_file_path = None
        # daysim stuff
        self.daysimdir_ies = None
        self.daysimdir_pts = None
        self.daysimdir_rad = None
        self.daysimdir_res = None
        self.daysimdir_tmp = None
        self.daysimdir_wea = None
        self.hea_file = None
        self.hea_filename = None
        self.sunuphrs = None

    def set_sensor_points(self, sensor_positions, sensor_normals):
        """
        This function sets the sensor points and their normals for the Radiance/Daysim simulation.
     
        Parameters
        ----------
        sensor_positions: pyptlist
            List of positions for sensing. Pyptlist is a list of tuples of floats. A pypt is a tuple that documents the xyz coordinates of a 
            pt e.g. (x,y,z), thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
    
        sensor_normals: pyveclist
            List of normals of the points sensing. Pyveclist is a list of tuples of floats. A pyvec is a tuple that documents the xyz coordinates of a 
            direction e.g. (x,y,z), thus a pyveclist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        """
        self.sensor_positions = sensor_positions
        self.sensor_normals = sensor_normals

    def create_sensor_input_file(self):
        """
        This function creates the sensor file. It requires the set_sensor_points() function to be executed prior to this function.
        """
        sensor_file_path = os.path.join(self.data_folder_path, "sensor_points.pts")
        sensor_file = open(sensor_file_path, "w")
        sensor_pts_data = write_rad.sensor_file(self.sensor_positions, self.sensor_normals)
        sensor_file.write(sensor_pts_data)
        sensor_file.close()
        self.sensor_file_path = sensor_file_path

    def set_sky(self, gensky_command, sky_colour, ground_colour):
        """
        This function sets the gensky command and parameters.
     
        Parameters
        ----------
        gensky_command: str
            The gensky command, e.g. "!gensky 1 31 15 -c -a 1.3 -o -103.9 -m -120". The command is constructing a sky model for:
            Jan 31st at 15hr cloudy sky (-c) at latitude 1.3 and longitude -103.9 (to the east)  and standard meridian -120 (to the east). 
            The different sky models are -s sunny without sun, +s sunny with sun, -c cloudy sky, -i intermediate sky without sun,  
            +i intermediate with sun, -u uniform cloudy sky.
            For more information visit: https://www.radiance-online.org/learning/documentation/manual-pages/pdfs/gensky.pdf/view 
    
        sky_colour: tuple of floats
            A tuple of floats describing the sky colour. e.g. (1,1,1) for a white sky.
            
        ground_colour: tuple of floats
            A tuple of floats describing the ground colour. e.g. (0.2,0.2,0.2) for a grey ground.
        """
        self.gensky_command = gensky_command
        self.sky_colour = sky_colour
        self.ground_colour = ground_colour

    def create_sky_input_file(self):
        """
        This function creates the sky file. It requires the set_sky() function to be executed prior to this function.
        """
        sky_file_path = os.path.join(self.data_folder_path, "sky.rad")
        sky_file = open(sky_file_path, "w")
        sky_glow = write_rad.glow("sky_glow", self.sky_colour)
        grd_glow = write_rad.glow("ground_glow", self.ground_colour)
        sky_source = write_rad.source("sky", "sky_glow", (0, 0, 1))
        grd_source = write_rad.source("ground", "ground_glow", (0, 0, -1))
        sky_data = self.gensky_command + "\n\n" + sky_glow + "\n\n" + grd_glow + "\n\n" + sky_source + "\n\n" + grd_source
        sky_file.write(sky_data)
        sky_file.close()
        self.sky_file_path = sky_file_path

    def create_rad_input_file(self):
        """
        This function creates the geometry rad file. It requires self.surfaces to be populated.
        """
        rad_file_path = os.path.join(self.data_folder_path, "geometry.rad")
        rad_building_data = []
        rad_file = open(rad_file_path, "w")
        for surface in self.surfaces:
            rad_data = surface.rad()
            rad_building_data.append(rad_data)

        for data in rad_building_data:
            rad_file.write(data)
        rad_file.close()
        self.rad_file_path = rad_file_path

    def execute_oconv(self):
        """
        This function creates the geometry oconv file. It requires set_sky() to be executed prior and self.surfaces to be populated.
        """
        self.create_sky_input_file()
        self.create_rad_input_file()  # what about interior??
        oconv_file_path = os.path.join(self.data_folder_path, "input.oconv")
        command = "oconv " + self.sky_file_path + " " + self.base_file_path + " " \
            .rad_file_path + \
                  " " + ">" + " " + oconv_file_path
        # process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # result = process.communicate()
        # print result
        f = open(self.command_file, "a")
        f.write(command)
        f.write("\n")
        f.close()
        os.system(command)  # EXECUTE!!
        self.oconv_file_path = oconv_file_path

    def execute_rtrace(self, dict_parm):
        """
        This function executes the rtrace Radiance program and simulates the Irradiance. It requires the execute _oconv() to be executed prior.
     
        Parameters
        ----------
        dict_parm: dictionary
            The dictionary needs to have the following keys and values: e.g. {"ab": 2, "aa": 0.15, "ar": 128, "ad": 512, "as":256}. The 
            parameters specify the parameters for the ray-tracing simulation. For more information visit:
            https://www.radiance-online.org/learning/documentation/manual-pages/pdfs/rtrace.pdf/view. 
        """

        if self.oconv_file_path == None:
            raise Exception
        # execute rtrace
        self.create_sensor_input_file()
        result_file_path = os.path.join(self.data_folder_path, "results.txt")
        command = "rtrace -h -w -I+ -ab " + dict_parm["ab"] + " -aa " + dict_parm["aa"] + \
                  " -ar " + dict_parm["ar"] + " -ad " + dict_parm["ad"] + " -as " + dict_parm["as"] + \
                  " " + self.oconv_file_path + " " + " < " + self.sensor_file_path + \
                  " " + " > " + " " + result_file_path

        f = open(self.command_file, "a")
        f.write(command)
        f.write("\n")
        f.close()
        # os.system(command)#EXECUTE!!
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        result = process.communicate()
        print result
        self.result_file_path = result_file_path

    def execute_rvu(self, vp, vd, dict_parm):
        """
        This function executes the rvu Radiance program and renders the scene. It requires the execute _oconv() to be executed prior.
     
        Parameters
        ----------
        vp: str
            The focal point of a perspective view or the center of a parallel projection. e.g. "0 0 0"
            
        vd: str
             the view direction vector. The length of this vector indicates the focal distance. e.g. "1 0 0"
            
        dict_parm: dictionary
            The dictionary needs to have the following keys and values: e.g. {"ab": 2, "aa": 0.15, "ar": 128, "ad": 512, "as":256}. The 
            parameters specify the parameters for the ray-tracing simulation. For more information visit:
            https://www.radiance-online.org/learning/documentation/manual-pages/pdfs/rtrace.pdf/view. 
        """
        if self.oconv_file_path == None:
            raise Exception
        # execute rvu
        operating_sys = os.name
        if operating_sys == "posix":
            command = "rvu -vp " + vp + " -vd " + vd + \
                      " -ab " + dict_parm["ab"] + " -aa " + dict_parm["aa"] + \
                      " -ar " + dict_parm["ar"] + " -ad " + dict_parm["ad"] + " -as " + dict_parm["as"] + \
                      " -pe " + dict_parm["exp"] + " " + self.oconv_file_path + " &"
        elif operating_sys == "nt":
            command = "rvu -vp " + vp + " -vd " + vd + \
                      " -ab " + dict_parm["ab"] + " -aa " + dict_parm["aa"] + \
                      " -ar " + dict_parm["ar"] + " -ad " + dict_parm["ad"] + " -as " + dict_parm["as"] + \
                      " -pe " + dict_parm["exp"] + " " + self.oconv_file_path + " &"

        f = open(self.command_file, "a")
        f.write(command)
        f.write("\n")
        f.close()
        os.system(command)  # EXECUTE!!

    def execute_rpict(self, filename, x_resolution, y_resolution, vp, vd, dict_parm):
        """
        This function executes the rpict Radiance program and renders the scene. It requires the execute _oconv() to be executed prior.
     
        Parameters
        ----------
        filename: str
            The name of generated tif picture. e.g. "pict1". The picture will be saved to the data_folder_path. The tif file is a 
            will have an angular fisheye distortion.
            
        x_resolution: str
            The x-resolution of the generated tif picture. e.g. "640".
            
        y_resolution: str
            The y-resolution of the generated tif picture. e.g. "480".
            
        vp: str
            The focal point of a perspective view or the center of a parallel projection. e.g. "0 0 0".
            
        vd: str
             the view direction vector. The length of this vector indicates the focal distance. e.g. "1 0 0".
            
        dict_parm: dictionary
            The dictionary needs to have the following keys and values: e.g. {"ab": 2, "aa": 0.15, "ar": 128, "ad": 512, "as":256}. The 
            parameters specify the parameters for the ray-tracing simulation. For more information visit:
            https://www.radiance-online.org/learning/documentation/manual-pages/pdfs/rtrace.pdf/view. 
        """
        if self.oconv_file_path == None:
            raise Exception("oconv file is missing")
        # execute rpict
        image_folder_path = os.path.join(self.data_folder_path, "images")
        if not os.path.isdir(image_folder_path):
            os.mkdir(image_folder_path)
        image_file_path = os.path.join(image_folder_path, filename)

        command1 = "rpict -x " + x_resolution + " -y " + y_resolution + " -vp " + vp + \
                   " -vd " + vd + \
                   " -vh 200 -vv 100 -vta" + \
                   " -ab " + dict_parm["ab"] + " -aa " + dict_parm["aa"] + \
                   " -ar " + dict_parm["ar"] + " -ad " + dict_parm["ad"] + " -as " + dict_parm["as"] + \
                   " -i " + self.oconv_file_path + " > " + image_file_path + "out_i.hdr"

        command2 = "rpict -x " + x_resolution + " -y " + y_resolution + " -vp " + \
                   vp + " -vd " + vd + \
                   " -vh 200 -vv 100 -vta" + \
                   " -ab " + dict_parm["ab"] + " -aa " + dict_parm["aa"] + \
                   " -ar " + dict_parm["ar"] + " -ad " + dict_parm["ad"] + " -as " + dict_parm["as"] + \
                   " " + self.oconv_file_path + " > " + image_file_path + "out.hdr"

        command3 = "pfilt -e " + dict_parm["exp"] + " " + image_file_path + "out_i.hdr" + " > " + \
                   image_file_path + "out_i_filt.hdr"
        command4 = "pfilt -e " + dict_parm["exp"] + " " + image_file_path + "out.hdr" + " > " + \
                   image_file_path + "out_filt.hdr"

        command5 = "ra_tiff " + image_file_path + "out.hdr" + " " + image_file_path + "out.tif"
        command6 = "ra_tiff " + image_file_path + "out_i.hdr" + " " + image_file_path + "out_i.tif"
        command7 = "ra_tiff " + image_file_path + "out_filt.hdr" + " " + image_file_path + "out_filt.tif"
        command8 = "ra_tiff " + image_file_path + "out_i_filt.hdr" + " " + image_file_path + "out_i_filt.tif"

        f = open(self.command_file, "a")
        f.write(command1)
        f.write("\n")
        f.write(command2)
        f.write("\n")
        f.write(command3)
        f.write("\n")
        f.write(command4)
        f.write("\n")
        f.write(command5)
        f.write("\n")
        f.write(command6)
        f.write("\n")
        f.write(command7)
        f.write("\n")
        f.write(command8)
        f.write("\n")
        os.system(command1)  # EXECUTE!!
        os.system(command2)  # EXECUTE!!
        os.system(command3)  # EXECUTE!!
        os.system(command4)  # EXECUTE!!
        os.system(command5)  # EXECUTE!!
        os.system(command6)  # EXECUTE!!
        os.system(command7)  # EXECUTE!!
        os.system(command8)  # EXECUTE!!

    def execute_falsecolour(self, i_basefile_path, l_basefile_path, filename, range_max,
                            range_division, illuminance=True):
        """
        This function executes the rpict Radiance program and renders the scene. It requires the execute _oconv() to be executed prior.
     
        Parameters
        ----------
        i_basefile_path : str
            The path of the illuminance tif picture. This tif picture can be generated using the execute_rpict)() function.
        
        l_basefile_path : str
            The path of the luminance tif picture. This tif picture can be generated using the execute_rpict)() function.
            
        filename : str
            The name of generated tif picture. e.g. "pict1". The picture will be saved to the data_folder_path. The tif file is a 
            will have an angular fisheye distortion.
            
        range_max : str
            The maximum value of the falsecolour. e.g. "1200".
            
        range_division : str
            The division of the falsecolour. e.g. "10".
            
        illuminance : bool
            True or False. If True will generate a falsecolour image of the illuminance value. If False will generate a falsecolour image
            of the luminance value.
        
        """
        image_folder_path = os.path.join(self.data_folder_path, "images")
        if not os.path.isdir(image_folder_path):
            os.mkdir(image_folder_path)
        i_base_image_path = i_basefile_path
        l_base_image_path = l_basefile_path
        falsecolour_folder_path = os.path.join(image_folder_path, "falsecolour")
        if not os.path.isdir(falsecolour_folder_path):
            os.mkdir(falsecolour_folder_path)
        falsecolour_file_path = os.path.join(falsecolour_folder_path, filename)
        if illuminance == True:
            # command = "falsecolor -i " + i_base_image_path + " -p " +\
            # l_base_image_path + " -n " + range_division + " -s " + range_max +\
            # " -l lux > " + falsecolour_file_path + "_illum.hdr"

            command = "falsecolor2 -i " + i_base_image_path + " -p " + \
                      l_base_image_path + " -cl -n " + range_division + " -s " + range_max + \
                      " -l lux > " + falsecolour_file_path + "_illum.hdr"

            command2 = "ra_tiff " + falsecolour_file_path + "_illum.hdr" + " " + falsecolour_file_path + "illum.tif"

        else:
            command = "falsecolor2 -ip " + l_base_image_path + \
                      " -n " + range_division + " -s " + range_max + \
                      " -l cd/m2 > " + falsecolour_file_path + "_luminance.hdr"

            # command = "falsecolor2 -ip " + l_base_image_path +\
            # " -cl -n " + range_division + " -s " + range_max +\
            # " -l cd/m2 > " + falsecolour_file_path + "_luminance.hdr"

            command2 = "ra_tiff " + falsecolour_file_path + "_luminance.hdr" + " " + falsecolour_file_path + "luminance.tif"

        f = open(self.command_file, "a")
        f.write(command)
        f.write("\n")
        f.write(command2)
        f.write("\n")
        f.close()
        os.system(command)  # EXECUTE!!
        os.system(command2)  # EXECUTE!!

    def render(self, filename, x_resolution, y_resolution, vp, vd, dict_parm):
        """
        This function executes the rpict Radiance program and renders the scene. It requires the execute _oconv() to be executed prior.
        The difference between render() and execute_rpict() is that this function do not produce illuminance and luminance tif.
     
        Parameters
        ----------
        filename: str
            The name of generated tif picture. e.g. "pict1". The picture will be saved to the data_folder_path. The tif file is a 
            will have an angular fisheye distortion.
            
        x_resolution: str
            The x-resolution of the generated tif picture. e.g. "640".
            
        y_resolution: str
            The y-resolution of the generated tif picture. e.g. "480".
            
        vp: str
            The focal point of a perspective view or the center of a parallel projection. e.g. "0 0 0".
            
        vd: str
             the view direction vector. The length of this vector indicates the focal distance. e.g. "1 0 0".
            
        dict_parm: dictionary
            The dictionary needs to have the following keys and values: e.g. {"ab": 2, "aa": 0.15, "ar": 128, "ad": 512, "as":256}. The 
            parameters specify the parameters for the ray-tracing simulation. For more information visit:
            https://www.radiance-online.org/learning/documentation/manual-pages/pdfs/rtrace.pdf/view. 
        """

        if self.oconv_file_path == None:
            raise Exception("oconv file is missing")
        # execute rpict
        image_folder_path = os.path.join(self.data_folder_path, "render")
        if not os.path.isdir(image_folder_path):
            os.mkdir(image_folder_path)
        image_file_path = os.path.join(image_folder_path, filename)

        command1 = "rpict -x " + x_resolution + " -y " + y_resolution + " -vp " + \
                   vp + " -vd " + vd + \
                   " -ab " + dict_parm["ab"] + " -aa " + dict_parm["aa"] + \
                   " -ar " + dict_parm["ar"] + " -ad " + dict_parm["ad"] + " -as " + dict_parm["as"] + \
                   " " + self.oconv_file_path + " > " + image_file_path + "out.hdr"

        command2 = "pfilt -e " + dict_parm["exp"] + " " + image_file_path + "out.hdr" + " > " + \
                   image_file_path + "out_filt.hdr"

        command3 = "ra_tiff " + image_file_path + "out_filt.hdr" + " " + image_file_path + "out_filt.tif"

        f = open(self.command_file, "a")
        f.write(command1)
        f.write("\n")
        f.write(command2)
        f.write("\n")
        f.write(command3)
        f.write("\n")
        f.close()
        os.system(command1)  # EXECUTE!!
        os.system(command2)  # EXECUTE!!
        os.system(command3)  # EXECUTE!!

    def eval_rad(self):
        """
        This function reads the result file from the simulation and returns the results as a list.
        
        Returns
        --------
        irradiance: list of floats
            List of irradiance results (Wh/m2) that corresponds to the sensor points.
            
        illuminance: list of floats
            List of illuminance in (lux) results that corresponds to the sensor points.
        """

        if self.result_file_path == None:
            raise Exception
        results = open(self.result_file_path, "r")
        irradiance_list = []
        illuminance_list = []
        for result in results:
            words = result.split()
            numbers = map(float, words)
            # IRRADIANCE RESULTS
            irradiance = round((0.265 * numbers[0]) + (0.670 * numbers[1]) + (0.065 * numbers[2]), 1)
            irradiance_list.append(irradiance)
            # ILLUMINANCE RESULTS
            illuminance = irradiance * 179
            illuminance_list.append(illuminance)
        return irradiance_list, illuminance_list

    def create_cumulative_sky_input_file(self, time, date, weatherfile_path, output="irradiance"):
        """
        This function sets the gencummulative sky command and parameters.
     
        Parameters
        ----------
        time: str
            The time duration of the simulation e.g. "7 19". This means the simulation will run from 7am to 7pm.
            
        date: str
            The dates of the simulation e.g. "1 1 12 31". This means the simulation will run from Jan 1st to Dec 31st.
            
        weatherfile_path: str
            The file path of the weather file.
            
        output: str, optional
            The units of the results, "irradiance" (kWh/m2) or "illuminance" (lux), Default = "irradiance".
        """
        # execute epw2wea
        head, tail = os.path.split(weatherfile_path)
        wfilename_no_extension = tail.replace(".epw", "")
        weaweatherfilename = wfilename_no_extension + "_60min.wea"
        weaweatherfile = os.path.join(self.data_folder_path, weaweatherfilename)
        command1 = "epw2wea" + " " + weatherfile_path + " " + weaweatherfile
        proc = subprocess.Popen(command1, stdout=subprocess.PIPE, shell=True)
        site_headers = proc.stdout.read()
        site_headers_list = site_headers.split("\r\n")
        latitude = site_headers_list[1].split(" ")[1]
        longtitude = site_headers_list[2].split(" ")[1]
        meridian = site_headers_list[3].split(" ")[1]
        if output == "irradiance":
            # gencumulative sky command
            cumulative_cal_file_name = "input_cumulative_sky.cal"
            cumulative_cal_file_path = os.path.join(self.data_folder_path, cumulative_cal_file_name)
            # with -p command the output is in kwh, without -p the output is in wh
            cumulative_sky_command = "GenCumulativeSky +s1 -a " + latitude + " -o " + longtitude + " -m " + meridian + " -p -E -time " + \
                                     time + " -date " + date + " " + weatherfile_path + " > " + cumulative_cal_file_path

        elif output == "illuminance":
            # gencumulative sky command
            cumulative_cal_file_name = "input_cumulative_sky.cal"
            cumulative_cal_file_path = os.path.join(self.data_folder_path, cumulative_cal_file_name)
            cumulative_sky_command = "GenCumulativeSky +s1 -a " + latitude + " -o " + longtitude + " -m " + meridian + " -E -time " + \
                                     time + " -date " + date + " " + weatherfile_path + " > " + cumulative_cal_file_path

        f = open(self.command_file, "a")
        f.write(cumulative_sky_command)
        f.write("\n")
        f.close()
        # os.system(cumulative_sky_command)#EXECUTE
        subprocess.call(cumulative_sky_command, shell=True)
        # create the sky file using the .cal file created
        cumulative_sky_file_path = os.path.join(self.data_folder_path, "cumulative_sky.rad")
        cumulative_sky_file = open(cumulative_sky_file_path, "w")
        csky_brightfunc = write_rad.brightfunc(cumulative_cal_file_name)
        csky_glow = write_rad.glow("sky_glow", (1, 1, 1))
        csky_source = write_rad.source("sky", "sky_glow", (0, 0, 1))
        cumulative_sky_data = "# cumulative sky file\n\n" + csky_brightfunc + "\n\n" + csky_glow + "\n\n" + csky_source
        cumulative_sky_file.write(cumulative_sky_data)
        cumulative_sky_file.close()
        self.cumulative_sky_file_path = cumulative_sky_file_path

    def execute_cumulative_oconv(self, time, date, weatherfile_path, output="irradiance"):
        """
        This function executes the gencummulative oconv command and parameters.
     
        Parameters
        ----------
        time: str
            The time duration of the simulation e.g. "7 19". This means the simulation will run from 7am to 7pm.
            
        date: str
            The dates of the simulation e.g. "1 1 12 31". This means the simulation will run from Jan 1st to Dec 31st.
            
        weatherfile_path: str
            The file path of the weather file.
            
        output: str, optional
            The units of the results, "irradiance" (kWh/m2) or "illuminance" (lux), Default = "irradiance".
        """
        if output == "irradiance":
            self.create_cumulative_sky_input_file(time, date, weatherfile_path)
        if output == "illuminance":
            self.create_cumulative_sky_input_file(time, date, weatherfile_path, output="illuminance")

        self.create_rad_input_file()  # what about interior??
        cumulative_oconv_file_path = os.path.join(self.data_folder_path, "cumulative_input.oconv")
        # make sure the dir is at where the .cal file is
        cur_dir = os.getcwd()
        os.chdir(self.data_folder_path)
        command2 = "oconv -f " + self.base_file_path + " " \
                   + self.cumulative_sky_file_path + " " + self.rad_file_path + \
                   " " + ">" + " " + cumulative_oconv_file_path
        f = open(self.command_file, "a")
        f.write(command2)
        f.write("\n")
        f.close()

        os.chdir(cur_dir)
        subprocess.call(command2, shell=True)
        # os.system(command2) #EXECUTE!!
        self.cumulative_oconv_file_path = cumulative_oconv_file_path

    def execute_cumulative_rtrace(self, ab):
        """
        This function executes the rtrace with the cummulative sky. This function requires the execution of execute_cumulative_oconv() prior.
        
        Parameters
        ----------
        ab: str
            The number of ambient bounces for the ray-tracing. e.g. "2".
        """
        if self.cumulative_oconv_file_path == None:
            raise Exception
        # execute rtrace
        cur_dir = os.getcwd()
        os.chdir(self.data_folder_path)
        self.create_sensor_input_file()
        cumulative_result_file_path = os.path.join(self.data_folder_path, "cumulative_radmap_results.txt")
        command = "rtrace -I -h -dp 2048 -ms 0.063 -ds .2 -dt .05 -dc .75 -dr 3 -st .01 -lr 12 -lw .0005 -ab " + ab + " -ad 1000 -as 20 -ar 300 -aa 0.1   " + \
                  self.cumulative_oconv_file_path + " " + " < " + self.sensor_file_path + \
                  " " + " > " + " " + cumulative_result_file_path
        f = open(self.command_file, "a")
        f.write(command)
        f.write("\n")
        f.close()
        subprocess.call(command, shell=True)
        # os.system(command)#EXECUTE!!
        os.chdir(cur_dir)
        self.cumulative_result_file_path = cumulative_result_file_path

    def eval_cumulative_rad(self, output="irradiance"):
        """
        This function reads the cummulative result file from the simulation and returns the results as a list.
        
        Parameters
        ----------
        output: str, optional
            The units of the results, "irradiance" (Wh/m2) or "illuminance" (lux), Default = "irradiance".
            
        Returns
        ------
        results: list of floats
            List of irradiance results (kWh/m2) or illuminance in (lux) that corresponds to the sensor points depending on the output parameter.
        
        """
        if self.cumulative_result_file_path == None:
            raise Exception
        results = open(self.cumulative_result_file_path)
        results_read = results.read()
        lines = results_read.split("\n")
        del lines[-1]
        result_list = []
        for line in lines:
            words = line.split("\t")
            words.remove("")
            numbers = map(float, words)
            # IRRADIANCE RESULTS
            irradiance = round((0.265 * numbers[0]) + (0.670 * numbers[1]) + (0.065 * numbers[2]), 1)
            if output == "irradiance":
                result_list.append(irradiance)
            if output == "illuminance":
                # ILLUMINANCE RESULTS
                illuminance = irradiance * 179
                result_list.append(illuminance)

        return result_list

    def initialise_daysim(self, daysim_dir):
        """
        Run this method prior to running any Daysim simulation. This function creates the base .hea header file and all the neccessary 
        folders for the Daysim simulation.
        
        Parameters
        ----------            
        daysim_dir :  str
            The directory to write all the daysim results file to.
        """
        # create the directory if its not existing
        if not os.path.isdir(daysim_dir):
            os.mkdir(daysim_dir)

        head, tail = os.path.split(daysim_dir)
        # create an empty .hea file
        hea_filepath = os.path.join(daysim_dir, tail + ".hea")
        hea_file = open(hea_filepath, "w")
        # the project name will take the name of the folder
        hea_file.write("project_name" + " " + tail + "\n")
        # write the project directory
        hea_file.write("project_directory" + " " + os.path.join(daysim_dir, "") + "\n")
        # bin directory, assumes daysim is always installed at the default c drive
        hea_file.write("bin_directory" + " " + os.path.join("c:/daysim", "bin", "") + "\n")
        # write tmp directory
        hea_file.write("tmp_directory" + " " + os.path.join("tmp", "") + "\n")
        # write material directory
        hea_file.write("material_directory" + " " + os.path.join("c:/daysim", "") + "\n")
        # write ies directory
        hea_file.write("ies_directory" + " " + os.path.join("c:/daysim", "") + "\n")
        hea_file.close()
        self.hea_file = hea_filepath

        # create all the subdirectory
        sub_hea_folders = ["ies", "pts", "rad", "res", "tmp", "wea"]
        for folder in range(len(sub_hea_folders)):
            sub_hea_folder = sub_hea_folders[folder]
            sub_hea_folders_path = os.path.join(daysim_dir, sub_hea_folder)
            if folder == 0:
                self.daysimdir_ies = sub_hea_folders_path
            if folder == 1:
                self.daysimdir_pts = sub_hea_folders_path
            if folder == 2:
                self.daysimdir_rad = sub_hea_folders_path
            if folder == 3:
                self.daysimdir_res = sub_hea_folders_path
            if folder == 4:
                self.daysimdir_tmp = sub_hea_folders_path
            if folder == 5:
                self.daysimdir_wea = sub_hea_folders_path

            # if the directories are not existing create them
            if not os.path.isdir(sub_hea_folders_path):
                os.mkdir(sub_hea_folders_path)

            # if they are existing delete all of the files
            if os.path.isdir(sub_hea_folders_path):
                files_in_dir = os.listdir(sub_hea_folders_path)
                for filename in files_in_dir:
                    rmv_path = os.path.join(sub_hea_folders_path, filename)
                    os.remove(rmv_path)

    def execute_epw2wea(self, epwweatherfile, ground_reflectance=0.2):
        """
        This function executes the epw2wea.exe and convert an epw weatherfile into a .wea weather file. Daysim uses .wea weatherfile.
        
        Parameters
        ----------            
        epwweatherfile :  str
            The file path of the epw weather file.
        
        ground_reflectance : float, optional
            The ground reflectance, default = 0.2.
        """
        daysimdir_wea = self.daysimdir_wea
        if daysimdir_wea == None:
            raise NameError("run .initialise_daysim function before running execute_epw2wea")
        head, tail = os.path.split(epwweatherfile)
        wfilename_no_extension = tail.replace(".epw", "")
        weaweatherfilename = wfilename_no_extension + "_60min.wea"
        weaweatherfile = os.path.join(daysimdir_wea, weaweatherfilename)
        command1 = "epw2wea" + " " + epwweatherfile + " " + weaweatherfile
        f = open(self.command_file, "a")
        f.write(command1)
        f.write("\n")
        f.close()

        proc = subprocess.Popen(command1, stdout=subprocess.PIPE, shell=True)
        site_headers = proc.stdout.read()
        site_headers_list = site_headers.split("\r\n")
        hea_filepath = self.hea_file
        hea_file = open(hea_filepath, "a")
        for site_header in site_headers_list:
            if site_header:
                hea_file.write("\n" + site_header)

        hea_file.write("\nground_reflectance" + " " + str(ground_reflectance))
        # get the directory of the long weatherfile
        hea_file.write("\nwea_data_file" + " " + os.path.join(head, wfilename_no_extension + "_60min.wea"))
        hea_file.write("\ntime_step" + " " + "60")
        hea_file.write("\nwea_data_short_file" + " " + os.path.join("wea", wfilename_no_extension + "_60min.wea"))
        hea_file.write("\nwea_data_short_file_units" + " " + "1")
        hea_file.write("\nlower_direct_threshold" + " " + "2")
        hea_file.write("\nlower_diffuse_threshold" + " " + "2")
        hea_file.close()
        # check for the sunuphours
        results = open(weaweatherfile, "r")
        result_lines = results.readlines()
        result_lines = result_lines[6:]
        sunuphrs = 0
        for result in result_lines:
            words = result.replace("\n", "")
            words1 = words.split(" ")
            direct = float(words1[-1])
            diffuse = float(words1[-2])
            total = direct + diffuse
            if total > 0:
                sunuphrs = sunuphrs + 1

        results.close()
        self.sunuphrs = sunuphrs

    def execute_radfiles2daysim(self):
        """
        This function executes the radfiles2daysim.exe and convert an all the rad geometry and material files to daysim files.
        The create_rad function needs to be executed prior to this function.
        """

        hea_filepath = self.hea_file
        head, tail = os.path.split(hea_filepath)
        radfilename = tail.replace(".hea", "")
        radgeomfilepath = self.rad_file_path
        radmaterialfile = self.base_file_path
        if radgeomfilepath == None or radmaterialfile == None:
            raise NameError("run .create_rad function before running radfiles2daysim")

        hea_file = open(hea_filepath, "a")
        hea_file.write("\nmaterial_file" + " " + os.path.join("rad", radfilename + "_material.rad"))
        hea_file.write("\ngeometry_file" + " " + os.path.join("rad", radfilename + "_geometry.rad"))
        hea_file.write("\nradiance_source_files 2," + radgeomfilepath + "," + radmaterialfile)
        hea_file.close()
        command1 = "radfiles2daysim" + " " + hea_filepath + " " + "-g" + " " + "-m" + " " + "-d"
        f = open(self.command_file, "a")
        f.write(command1)
        f.write("\n")
        f.close()
        os.system(command1)

    def write_static_shading(self, hea_file):
        """
        This function writes the static shading into the hea file.
        
        Parameters
        ----------            
        hea_file :  open file mode "a"
            The opened file of the header file.
            
        """
        hea_filepath = self.hea_file
        head, tail = os.path.split(hea_filepath)
        tail = tail.replace(".hea", "")
        self.hea_filename = tail
        dc_file = os.path.join("res", tail + ".dc")
        ill_file = os.path.join("res", tail + ".ill")
        hea_file.write("\nshading" + " " + "1" + " " + "static_system" + " " + dc_file + " " + ill_file)

    def write_radiance_parameters(self, rad_ab, rad_ad, rad_as, rad_ar, rad_aa, rad_lr, rad_st, rad_sj, rad_lw, rad_dj,
                                  rad_ds, rad_dr, rad_dp):
        """
        This function write the radiance parameters for the Daysim simulation.
        
        Parameters
        ----------            
        rad_ab :  int
        rad_ad :  int
        rad_as :  int
        rad_ar :  int
        rad_aa :  float
        rad_lr :  int
        rad_st :  float
        rad_sj :  float
        rad_lw :  float
        rad_dj :  float
        rad_ds :  float
        rad_dr :  int
        rad_dp :  int
        """
        hea_file = open(self.hea_file, "a")
        hea_file.write("\nab" + " " + str(rad_ab))
        hea_file.write("\nad" + " " + str(rad_ad))
        hea_file.write("\nas" + " " + str(rad_as))
        hea_file.write("\nar" + " " + str(rad_ar))
        hea_file.write("\naa" + " " + str(rad_aa))
        hea_file.write("\nlr" + " " + str(rad_lr))
        hea_file.write("\nst" + " " + str(rad_st))
        hea_file.write("\nsj" + " " + str(rad_sj))
        hea_file.write("\nlw" + " " + str(rad_lw))
        hea_file.write("\ndj" + " " + str(rad_dj))
        hea_file.write("\nds" + " " + str(rad_ds))
        hea_file.write("\ndr" + " " + str(rad_dr))
        hea_file.write("\ndp" + " " + str(rad_dp))
        hea_file.close()

    def write_default_radiance_parameters(self):
        """
        This function write the default radiance parameters for the Daysim simulation. 
        The default settings are the complex scene 1 settings of daysimPS
        """
        rad_ab = 2
        rad_ad = 1000
        rad_as = 20
        rad_ar = 300
        rad_aa = 0.1
        rad_lr = 6
        rad_st = 0.15
        rad_sj = 1.0
        rad_lw = 0.004
        rad_dj = 0.0
        rad_ds = 0.2
        rad_dr = 2
        rad_dp = 512
        self.write_radiance_parameters(rad_ab, rad_ad, rad_as, rad_ar, rad_aa, rad_lr,
                                       rad_st, rad_sj, rad_lw, rad_dj, rad_ds, rad_dr, rad_dp)

    def execute_gen_dc(self, output_unit):
        """
        This function executes the gen_dc Daysim command.
     
        Parameters
        ----------
        output_unit : str, optional
            The units of the results, "w/m2" or "lux".
        """
        hea_filepath = self.hea_file
        hea_file = open(hea_filepath, "a")
        sensor_filepath = self.sensor_file_path
        if sensor_filepath == None:
            raise NameError(
                "run .set_sensor_points and create_sensor_input_file function before running execute_gen_dc")

        daysim_pts_dir = self.daysimdir_pts
        if daysim_pts_dir == None:
            raise NameError("run .initialise_daysim function before running execute_gen_dc")

        # first specify the sensor pts
        head, tail = os.path.split(sensor_filepath)
        # move the pts file to the daysim folder
        dest_filepath = os.path.join(daysim_pts_dir, tail)
        shutil.move(sensor_filepath, dest_filepath)
        # write the sensor file location into the .hea
        hea_file.write("\nsensor_file" + " " + os.path.join("pts", tail))
        # write the shading header
        self.write_static_shading(hea_file)
        # write analysis result file
        head, tail = os.path.split(hea_filepath)
        tail = tail.replace(".hea", "")
        # hea_file.write("\nDDS_sensor_file" + " " + os.path.join("res", tail + ".dds"))
        # hea_file.write("\nDDS_file" + " " + os.path.join("res", tail + ".sen"))
        # write output unit
        nsensors = len(self.sensor_positions)
        sensor_str = ""
        if output_unit == "w/m2":
            hea_file.write("\noutput_units" + " " + "1")
            for scnt in range(nsensors):
                # 0 = lux, 2 = w/m2
                if scnt == nsensors - 1:
                    sensor_str = sensor_str + "2"
                else:
                    sensor_str = sensor_str + "2 "

        if output_unit == "lux":
            hea_file.write("\noutput_units" + " " + "2")
            for scnt in range(nsensors):
                # 0 = lux, 2 = w/m2
                if scnt == nsensors - 1:
                    sensor_str = sensor_str + "0"
                else:
                    sensor_str = sensor_str + "0 "

        hea_file.write("\nsensor_file_unit " + sensor_str)

        hea_file.close()
        # copy the .hea file into the tmp directory
        with open(hea_filepath, "r") as hea_file_read:
            lines = hea_file_read.readlines()

        tmp_directory = os.path.join(self.daysimdir_tmp, "")

        # update path to tmp_directory in temp_hea_file
        lines_modified = []
        for line in lines:
            if line.startswith('tmp_directory'):
                lines_modified.append('tmp_directory {}\n'.format(tmp_directory))
            else:
                lines_modified.append(line)

        temp_hea_filepath = os.path.join(self.daysimdir_tmp, tail + "temp.hea")

        with open(temp_hea_filepath, "w") as temp_hea_file:
            temp_hea_file.write('\n'.join(lines_modified))

        # execute gen_dc
        command1 = "gen_dc" + " " + temp_hea_filepath + " " + "-dir"
        command2 = "gen_dc" + " " + temp_hea_filepath + " " + "-dif"
        command3 = "gen_dc" + " " + temp_hea_filepath + " " + "-paste"
        f = open(self.command_file, "a")
        f.write(command1)
        f.write("\n")
        f.write(command2)
        f.write("\n")
        f.write(command3)
        f.write("\n")
        f.close()
        os.system(command1)
        os.system(command2)
        os.system(command3)

    def execute_ds_illum(self):
        """
        This function executes the ds_illum Daysim command.
        """
        hea_filepath = self.hea_file
        # execute ds_illum
        command1 = "ds_illum" + " " + hea_filepath
        f = open(self.command_file, "a")
        f.write(command1)
        f.write("\n")
        f.close()
        os.system(command1)

    def eval_ill(self):
        """
        This function reads the daysim result file from the simulation and returns the results as a dictionaries.
            
        Returns
        -------
        hourly results: list of dictionaries
            List of Dictionaries of hourly irradiance results (Wh/m2) or illuminance in (lux) that corresponds to the sensor points depending on the output parameter.
            Each dictionary is an hour of results of all the sensor points. Each dictionary has key "date" and "result_list". 
            The "date" key points to a date string e.g. "12 31 23.500" which means Dec 31st 23hr indicating the date and hour of the result.
            The "result_list" key points to a list of results, which is the result of all the sensor points. 
        
        """
        if self.hea_filename == None:
            raise Exception("run ds_illum to simulate results")
        ill_path = os.path.join(self.daysimdir_res, self.hea_filename + ".ill")
        ill_file = open(ill_path, "r")
        ill_results = ill_file.readlines()
        res_dict_list = []
        for ill_result in ill_results:
            result_dict = {}
            ill_result = ill_result.replace("\n", "")
            ill_resultlist = ill_result.split(" ")
            date = ill_resultlist[0] + " " + ill_resultlist[1] + " " + ill_resultlist[2]
            result_dict["date"] = date
            resultlist = ill_resultlist[4:]
            resultlist_f = []
            for r in resultlist:
                resultlist_f.append(float(r))
            result_dict["result_list"] = resultlist_f
            res_dict_list.append(result_dict)

        return res_dict_list

    def eval_ill_per_sensor(self):
        """
        This function reads the daysim result file from the simulation and returns a list of results.
            
        Returns
        -------
        results per sensor : list of results
            Each row is a sensor srf with 8760 colume of hourly result
        
        """
        res_dict_list = self.eval_ill()
        npts = len(res_dict_list[0]["result_list"])
        sensorptlist = []
        for _ in range(npts):
            sensorptlist.append([])

        for res_dict in res_dict_list:
            result_list = res_dict["result_list"]
            for rnum in range(npts):
                sensorptlist[rnum].append(result_list[rnum])
        return sensorptlist


class Surface(object):
    """
    An object that contains all the surface information running a Radiance/Daysim simulation.
    
    Parameters
    ----------
    name :  str
        The name of the surface.
        
    points :  pyptlist
        List of points defining the surface. Pyptlist is a list of tuples of floats. A pypt is a tuple that documents the xyz coordinates of a 
        pt e.g. (x,y,z), thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    material :  str
        The name of the material of the surface. The material name must be in the base.rad file.

    Attributes
    ----------
    see Parameters.
    """

    def __init__(self, name, points, material):
        """Initialises the surface class"""
        self.name = name
        self.points = points
        self.material = material


class RadSurface(Surface):
    """
    An object that contains all the surface information running a Radiance/Daysim simulation.
    
    Parameters
    ----------
    name :  str
        The name of the surface.
        
    points :  pyptlist
        List of points defining the surface. Pyptlist is a list of tuples of floats. A pypt is a tuple that documents the xyz coordinates of a 
        pt e.g. (x,y,z), thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    material :  str
        The name of the material of the surface. The material name must be in the base.rad file.
        
    radgeom : Rad class
        The Rad class that contains all the information for running a Radiance/Daysim simulation.

    Attributes
    ----------
    see Parameters.
    """

    def __init__(self, name, points, material, radgeom):
        """Initialises the RadSurface class"""
        super(RadSurface, self).__init__(name, points, material)
        self.radgeom = radgeom
        radgeom.surfaces.append(self)

    def rad(self):
        """
        This function writes the surface information into Radiance readable string.
        
        Returns
        -------
        rad surface :  str
            The surface writtenn into radiance readable string.
            
        """
        name = self.name
        material = self.material
        points = self.points[:]
        return write_rad.surface(name, material, points)


def calculate_reflectance(r, g, b):
    """
    This function converts r g b into reflectance value based on the equation: reflectance = (0.2125 * r) + (0.7154 * g) + (0.0721 * b)
    
    Parameters
    ----------
    r :  float
        The r value.
        
    g :  float
        The g value.
        
    b :  float
        The b value.
    
    Returns
    -------
    reflectance :  float
        The reflectance value.
        
    """
    reflectance = (0.2125 * r) + (0.7154 * g) + (0.0721 * b)
    return reflectance
