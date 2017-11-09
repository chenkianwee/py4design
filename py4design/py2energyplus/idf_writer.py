# Functions for writing EnergyPlus (IDF) input files

# ================================================================================
def write_surface(
        name, 
        type,
        construction, 
        zone, 
        boundary,
        boundary_object, 
        sun_exp, 
        wind_exp, 
        points):
    """
    This function writes all the surface information into energyplus readable string
    
    Parameters
    ----------
    name : str
        The name of the surface.
        
    type : str
        The type of the surface, options: "Floor", "Wall", "Ceiling", "Roof" .
        
    construction : str
        The name of the construction. The construction must be in the base.idf file. e.g. "Medium Roof/Ceiling"
        
    zone : str
        The name of the zone the surface belongs to.
        
    boundary : str
        The boundary condition of the surface, options: "Outdoors", "Adiabatic", "Ground" or the name of the surface it is adjacent to.
        
    boundary_object : str
        The object the surface is adjacent to. If boundary is "Outdoors" or "Ground" give an empty string, if "Adiabatic" give its own name, else give the name of the surface
        it is adjacent to.
        
    sun_exp : str
        Describes if the surface is exposed to sun. Gives either "SunExposed" or "NoSun".
    
    win_exp : str
         Describes if the surface is exposed to wind. Gives either "WindExposed" or "NoWind".
        
    points : pyptlist
        List of points that defines the surface. Pyptlist is a list of tuples of floats. A pypt is a tuple that documents the xyz coordinates of a 
        pt e.g. (x,y,z), thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    Returns
    -------
    surface data : str 
        The idf string of the surface data.
    """
    surface ="! ==== BUILDING SURFACE\n" +\
    "BuildingSurface:Detailed,\n"+\
    "  "+name+",\n" +\
    "  "+type+",\n" +\
    "  "+construction+",\n" +\
    "  "+zone+",\n" +\
    "  "+boundary+",\n" +\
    "  "+boundary_object+",\n" +\
    "  "+sun_exp+",\n" +\
    "  "+wind_exp+",\n" +\
    "  autocalculate,\n"+\
    "  "+str(len(points))+",\n"
    for counter in range(len(points)):
        point = points[counter]
        text_point = str(point[0])+","+str(point[1])+","+str(point[2])
        if counter < len(points)-1:
            surface = surface + "  "+text_point+",\n"
        else:
            surface = surface + "  "+text_point+";\n\n"
    return surface

# ================================================================================
def write_window(
        name, 
        construction, 
        surface,
        shading,
        frame,
        points):
    
    """
    This function writes all the window information into energyplus readable string
    
    Parameters
    ----------
    name : str
        The name of the surface.
        
    construction : str
        The name of the construction. The construction must be in the base.idf file.
        
    surface : str
        The name of the host surface. e.g. "wall1".
        
    shading : str
        The name of the shading surface that belongs to the window. if none just give an empty string "". 
        
    frame : str
        The name of the frame that belongs to the window. if none just give an empty string "".
        
    points : pyptlist
        List of points that defines the surface. Pyptlist is a list of tuples of floats. A pypt is a tuple that documents the xyz coordinates of a 
        pt e.g. (x,y,z), thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    Returns
    -------
    window data : str 
        The idf string of the window data.
    """
    
    window ="! ==== WINDOW\n"+\
    "FenestrationSurface:Detailed,\n"+\
    "  "+name+",\n"+\
    "  Window,\n"+\
    "  "+construction+",\n"+\
    "  "+surface+",\n"+\
    "  ,\n"+\
    "  autocalculate,\n"+\
    "  "+shading+",\n"+\
    "  "+frame+",\n"+\
    "  1.0,\n"+\
    "  "+str(len(points))+",\n"
    for counter in range(len(points)):
        point = points[counter]
        text_point = str(point[0])+","+str(point[1])+","+str(point[2])
        if counter < len(points)-1:
            window = window + "  "+text_point+",\n"
        else:
            window = window + "  "+text_point+";\n\n" 
    return window

# ================================================================================
def write_building_shade(
        name, 
        transmittance, 
        points):
    """
    This function writes all the all the surfaces of the surrounding context, e.g. shadings that are not attached to the buildings which includes trees and surrounding site
    into energyplus readable string.
    
    Parameters
    ----------
    name : str
        The name of the surface.
        
    transmittance : str
        The transmittance value of the subsurface, only used for shading surfaces. If not provided energyplus will default to 0, means a totally opaque surface.
        
    points : pyptlist
        List of points that defines the surface. Pyptlist is a list of tuples of floats. A pypt is a tuple that documents the xyz coordinates of a 
        pt e.g. (x,y,z), thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    Returns
    -------
    building shade data : str 
        The idf string of the building shade data.
    """
    building_shade ="! ==== BUILDING SHADE\n"+\
    "Shading:Building:Detailed,\n"+\
    "  "+name+",\n"+\
    "  "+transmittance+",\n"+\
    "  "+str(len(points))+",\n"
    for counter in range(len(points)):
        point = points[counter]
        text_point = str(point[0])+","+str(point[1])+","+str(point[2])
        if counter < len(points)-1:
            building_shade = building_shade + "  "+text_point+",\n" 
        else:
            building_shade = building_shade + "  "+text_point+";\n\n" 
    return building_shade

# ================================================================================
def write_shadingoverhang(
        name,
        window_name,
        height_above_window,
        tilt_angle,
        left_extension,
        right_extension,
        depth):
    """
    This function writes all the shading overhang information into energyplus readable string.
    
    Parameters
    ----------
    name : str
        The name of the surface.
        
    window_name : str
        The window name the overhang belongs to.
        
    height_above_window : str
        The height of the overhang above the window in metres.
        
    tilt_angle : str
        The tilt angle of the overhang in degree.
        
    left_extension : str
        The left extension of the overhang in metres.
        
    right_extension : str
        The right extension of the overhang in metres.
        
    depth : str
        The depthof the overhang in metres.
        
    Returns
    -------
    overhang shade data : str 
        The idf string of the overhang shade data.
    """
    
    overhang = "! ==== SHADING OVERHANG\n\n"+\
    "Shading:Overhang,\n"+\
    "    " + name + ",\n"+\
    "    " + window_name + ",\n"+\
    "    " + height_above_window + ",\n"+\
    "    " + tilt_angle+ ",\n"+\
    "    " + left_extension+ ",\n"+\
    "    " + right_extension + ",\n"+\
    "    " + depth + ";\n\n"
    return overhang

# ================================================================================
def write_zone(name):
    """
    This function writes all the zone information into energyplus readable string
    
    Parameters
    ----------
    name : str
        The name of the zone.
        
    Returns
    -------
    zone data : str 
        The idf string of the zone data.
    """
    zone = "! ==== BUILDING ZONE\n"+\
    "Zone,\n"+\
    "  "+name+",\n"+\
    "  0,\n"+\
    "  0, 0, 0, \n"+\
    "  1,\n"+\
    "  1,\n"+\
    "  autocalculate,\n"+\
    "  autocalculate;\n\n"
    return zone 

# ================================================================================
def write_zone_shade(
        name, 
        host_surface, 
        transmittance, 
        points):
    
    """
    This function writes all the zone shade information into energyplus readable string
    
    Parameters
    ----------
    name : str
        The name of the shade.
        
    host_surface : str
        The name of the host surface. e.g. "wall1".
        
    transmittance : str
        The transmittance value of the subsurface. If not provided, an empty string "" is given,  energyplus will default to 0, means a totally opaque surface.
        
    points : pyptlist
        List of points that defines the surface. Pyptlist is a list of tuples of floats. A pypt is a tuple that documents the xyz coordinates of a 
        pt e.g. (x,y,z), thus a pyptlist is a list of tuples e.g. [(x1,y1,z1), (x2,y2,z2), ...]
        
    Returns
    -------
    shade data : str 
        The idf string of the shade data.
    """
    zone_shade ="! ==== SHADING ZONE DETAILED\n"+\
    "Shading:Zone:Detailed,\n"+\
    "    "+name+",\n"+\
    "    "+host_surface+",\n"+\
    "    "+transmittance+",\n"+\
    "    "+str(len(points))+",\n"
    for counter in range(len(points)):
        point = points[counter]
        text_point = str(point[0])+","+str(point[1])+","+str(point[2])
        if counter < len(points)-1:
            zone_shade = zone_shade + "    "+text_point+",\n" 
        else:
            zone_shade = zone_shade + "    "+text_point+";\n\n" 
    return zone_shade

# ================================================================================
def write_hvac_ideal_load_air_system(
        zone_name,
        thermostat):
    """
    This function writes all the ideal load hvac information into energyplus readable string
    
    Parameters
    ----------
    zone_name : str
        The name of the zone to apply the system to.
        
    thermostat : str
        The name of the thermostat schedule.
        
    Returns
    -------
    ideal hvac data : str 
        The idf string of the ideal hvac data.
    """
    hvac = "! ==== ZONE PURCHASED AIR\n"+\
    "HVACTemplate:Zone:IdealLoadsAirSystem,\n"+\
    "    "+zone_name+",\n"+\
    "    "+thermostat + ";\n\n"
        
    return hvac

# ================================================================================
def write_lights(
        zone_name,
        schedule_name,
        watts_per_m2):
    """
    This function writes all the lights information into energyplus readable string
    
    Parameters
    ----------
    zone_name : str
        The name of the zone to apply the system to.
        
    schedule_name : str
        The name of the lighting schedule.
        
    watts_per_m2 : str
        The Watts per m2 of the lighting, e.g. "10"
        
    Returns
    -------
    lights data : str 
        The idf string of the lights data.
    """
    light = "! ==== ZONE LIGHTS\n"+\
    "Lights,\n"+\
    "    "+zone_name+"_lights,\n"+\
    "    "+zone_name+",\n"+\
    "    "+schedule_name+",\n"+\
    "    Watts/Area,\n"+\
    "    ,\n"+\
    "    "+watts_per_m2+",\n"+\
    "    ,\n"+\
    "    0,\n"+\
    "    0.42,\n"+\
    "    0.18,\n"+\
    "    1,\n"+\
    "    GeneralLights;\n\n"
        
    return light
    
# ================================================================================
def write_people(
        zone_name,
        schedule_name,
        people_per_m2):
    """
    This function writes all the occupancy information into energyplus readable string. In PROGRESS ...
    """
    people = "" #TODO : implement the people !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
    return people
    
# ================================================================================
def write_internal_gains_other_equipment(
        zone_name,
        schedule_name,
        watts_per_m2):
    """
    This function writes all the other equipment internal gain information into energyplus readable string.
    
    Parameters
    ----------
    zone_name : str
        The name of the zone to apply the system to.
        
    schedule_name : str
        The name of the internal gain schedule.
        
    watts_per_m2 : str
        The Watts per m2 of the equipment, e.g. "20"
        
    Returns
    -------
    internal gain data : str 
        The idf string of the internal gain data data.
    """
    other_equipment = "! ==== INTERNAL GAINS OTHER EQUIPMENT\n" +\
    "OtherEquipment,\n"+\
    "    "+zone_name+"_internal_gains,\n"+\
    "    None,\n"+\
    "    "+zone_name+",\n"+\
    "    "+schedule_name +",\n"+\
    "    Watts/Area,\n"+\
    "    ,\n"+\
    "    "+watts_per_m2+",\n;"
        
    return other_equipment
# ================================================================================
def write_version(version):
    """
    This function writes all the energyplus version.
    
    Parameters
    ----------
    version : str
        The energyplus version, e.g. "EnergyPlusV8-7-0". 
        
    Returns
    -------
    version data : str 
        The idf string of the version data.
    """
    version_str = "! ==== VERSION\n" +\
    "Version,"+version+";\n\n"
    
    return version_str
    
# ================================================================================
def write_time_step(time_step):
    """
    This function writes all the time step information into energyplus readable string.
    
    Parameters
    ----------
    time_step : str
        The time step of the simulation in minutes.
        
    Returns
    -------
    time step data : str 
        The idf string of the time step data.
    """
    time_step_str = "! ==== TIME STEP\n" +\
    "Timestep,"+time_step+";\n\n"
    
    return time_step_str
    
# ================================================================================
def write_ground_temp_bldg_srf(ground_temp):
    """
    This function writes all the ground temperature information into energyplus readable string.
    
    Parameters
    ----------
    ground_temp :  list of str
        The the ground temperature for each month. e.g. ["20", "20", "20", "20", "20", "20","20", "20", "20", "20", "20", "20"]
        
    Returns
    -------
    ground temperature data : str 
        The idf string of the ground temperature data.
    """
    ground_temp_str = "! ==== GROUND TEMP\n" +\
    "Site:GroundTemperature:BuildingSurface,"+','.join(ground_temp)+";\n\n"
    
    return ground_temp_str
    
# ================================================================================
def write_shadow_calc(calc_frequency, max_figures):
    """
    This function writes all the shadow calculation information into energyplus readable string.
    
    Parameters
    ----------
    calc_frequency : str
        The calculation frequency, e.g. "20".
    
    max_figures : str
        The max figures. e.g. "100000"
        
    Returns
    -------
    shadow calculation data : str 
        The idf string of the shadow calculation data.
    """
    shadow_calc_str = "! ==== SHADOW CALCULATION\n" +\
    "ShadowCalculation,AverageOverDaysInFrequency,\n" +\
    calc_frequency+",\n"+\
    max_figures+ ",\n" +\
    "SutherlandHodgman,\n" +\
    "SimpleSkyDiffuseModeling;\n\n"
    
    return shadow_calc_str
    
# ================================================================================
def write_building(
    north,
    terrain,
    solar_dist,
    max_warmup_days):
    
    """
    This function writes all the building information into energyplus readable string.
    
    Parameters
    ----------
    north :  str
        The north direction in degrees. If "0" it means the y-direction is north, if "90" x-direction is north.
    
    terrain :  str
        The terrain of the simulation environment. e.g. "Urban", "Suburbs", "Country", "City", "Ocean".
        
    solar_dist :  str
        The solar distribuition setting. e.g. "FullExterior", "MinimalShadowing", "FullInteriorAndExterior", "FullExteriorWithReflections", "FullInteriorAndExteriorWithReflections".
        
    max_warmup_days :  str
        The maximum number of warmup days. At least "25".
        
    Returns
    -------
    building data : str 
        The idf string of the building data.
    """
    
    building = "! ==== BUILDING\n" +\
    "Building,\n" +\
    "    Building,\n"+\
    "    "+north+",\n" +\
    "    "+terrain+",\n"+\
    "    0.04,\n"+\
    "    0.4,\n"+\
    "    "+solar_dist+",\n"+\
    "    "+max_warmup_days+";\n\n"
    
    return building

# ================================================================================
def write_runperiod(
    start_month,
    start_day,
    end_month,
    end_day):
    
    """
    This function writes all the run period information into energyplus readable string.
    
    Parameters
    ----------
    start_month : str
        The starting month of the energyplus simulation.
    
    start_day : str
        The starting day of the starting month of the energyplus simulation.
        
    end_month : str
        The end month of the energyplus simulation.
        
    end_day : str
        The end day of the end month of the energyplus simulation.
        
    Returns
    -------
    run period data : str 
        The idf string of the run period data.
    """
    
    runperiod = "! ==== RUN PERIOD\n" +\
    "RunPeriod,\n"+\
    "    ,\n"+\
    "    " + start_month + ",\n"+\
    "    " + start_day + ",\n"+\
    "    " + end_month + ",\n"+\
    "    " + end_day + ",\n"+\
    "    UseWeatherFile,\n"+\
    "    Yes,\n"+\
    "    Yes,\n"+\
    "    No,\n"+\
    "    Yes,\n"+\
    "    Yes;\n\n"
    
    return runperiod

# ================================================================================
def write_schedule_type_limits(
    name,
    lower_limit,
    upper_limit,
    numeric_type,
    unit_type):
    
    """
    This function writes all the schedule type limit information into energyplus readable string.
    
    Parameters
    ----------
    name : str
        The name of the schedule type limit.
    
    lower_limit : str
        The lower limit of the schedule.
        
    upper_limit : str
        The upper limit of the schedule.
        
    numeric_type : str
        The numeric type of the schedule, e.g. "Continuous" or "Discrete" .
        
    unit_type : str
        The unit type of the schedule, e.g. "Dimensionless", "Temperature", "ActivityLevel" etc.
        
    Returns
    -------
    schedule type limit data : str 
        The idf string of the schedule type limit data.
    """
    
    schedule_type_limits = "! ==== SCHEDULE TYPE LIMITS\n" +\
    "ScheduleTypeLimits,\n"+\
    "    " + name + ",\n"+\
    "    " + lower_limit + ",\n"+\
    "    " + upper_limit + ",\n"+\
    "    " + numeric_type + ",\n"+\
    "    " + unit_type + ";\n\n"
    
    return schedule_type_limits
    
# ================================================================================
def write_hvacschedule(
    name,
    sch_type_limits_name,
    day_start_time,
    day_end_time,
    setpoint_day,
    setpoint_night):
    
    """
    This function writes all the hvac schedule information into energyplus readable string.
    
    Parameters
    ----------
    name : str
        The name of the schedule.
    
    sch_type_limits_name : str
        The name of schedule type limit to use.
        
    day_start_time : str
        The starting time of the cooling schedule, e.g. "09:00".
        
    day_end_time : str
        The ending time of the cooling schedule, e.g. "17:00".
        
    setpoint_day : str
        The set point temperature of the cooling, e.g. "25".
        
    setpoint_night : str
        The set point temperature of the cooling after end time, e.g. "50".
        
    Returns
    -------
    hvac schedule data : str 
        The idf string of the hvac schedule data.
    """
    hvac_sch_str  = "! ==== SCHEDULE COMPACT (HVAC)\n"
    if day_start_time != "0:00" and day_end_time == "24:00":
        hvac_sch_str = hvac_sch_str + "Schedule:Compact,\n" +\
         "    " + name + ",\n"+\
         "    " + sch_type_limits_name + ",\n"+\
         "    Through: 12/31,\n"+\
         "    For: AllDays,\n"+\
         "    Until:" + day_start_time + ", " + setpoint_night + ",\n"+\
         "    Until:" + day_end_time + ", " + setpoint_day + ";\n\n"
         
    elif day_start_time == "0:00" and day_end_time == "24:00":
        hvac_sch_str = hvac_sch_str + "Schedule:Compact,\n" +\
         "    " + name + ",\n"+\
         "    " + sch_type_limits_name + ",\n"+\
         "    Through: 12/31,\n"+\
         "    For: AllDays,\n"+\
         "    Until: 24:00, " + setpoint_day + ";\n\n"
    else:
        hvac_sch_str = hvac_sch_str + "Schedule:Compact,\n" +\
         "    " + name + ",\n"+\
         "    " + sch_type_limits_name + ",\n"+\
         "    Through: 12/31,\n"+\
         "    For: AllDays,\n"+\
         "    Until:" + day_start_time + ", " + setpoint_night + ",\n"+\
         "    Until:" + day_end_time + ", " + setpoint_day + ",\n"+\
         "    Until: 24:00, " + setpoint_night + ";\n\n"
     
    return hvac_sch_str

# ================================================================================
def write_alldays_schedule(
    name,
    sch_type_limits_name,
    start,
    end):
    
    """
    This function writes all the all day schedule information into energyplus readable string.
    
    Parameters
    ----------
    name : str
        The name of the schedule.
    
    sch_type_limits_name : str
        The name of schedule type limit to use.
        
    start : str
        The starting time of the schedule, e.g. "09:00".
        
    end : str
        The ending time of the schedule, e.g. "17:00".
        
    Returns
    -------
    all day schedule data : str 
        The idf string of the all day schedule data.
    """
    
    sch_str  = "! ==== SCHEDULE COMPACT\n"
    if end == "24:00":
        sch_str = sch_str + "Schedule:Compact,\n" +\
        "    " + name + ",\n"+\
        "    " + sch_type_limits_name + ",\n"+\
        "    Through: 12/31,\n"+\
        "    For: AllDays,\n"+\
        "    Until:" + start + ", 0,\n"+\
        "    Until:" + end + ", 1;\n\n"
    else:
        sch_str = sch_str + "Schedule:Compact,\n" +\
        "    " + name + ",\n"+\
        "    " + sch_type_limits_name + ",\n"+\
        "    Through: 12/31,\n"+\
        "    For: AllDays,\n"+\
        "    Until:" + start + ", 0,\n"+\
        "    Until:" + end + ", 1,\n"+\
        "    Until: 24:00, 0;\n\n"
    return sch_str

# ================================================================================
def write_thermostat(
    name,
    heat_sch,
    cool_sch):
    
    """
    This function writes all the thermostat information into energyplus readable string.
    
    Parameters
    ----------
    name : str
        The name of the thermostat.
    
    heat_sch : str
        The name of heating schedule to use.
        
    cool_sch : str
        The name of cooling schedule to use.
        
    Returns
    -------
    thermostat data : str 
        The idf string of the thermostat data.
    """
    
    thermostat_str = "! ==== THERMOSTAT\n" +\
    "HVACTemplate:Thermostat,\n" +\
    "    " + name + ",\n"+\
    "    " + heat_sch + ",\n"+\
    "    ,\n"+\
    "    " + cool_sch + ",\n"+\
    "    ;\n\n"
     
    return thermostat_str
    
# ================================================================================
def write_outputvar(variable_name, report_frequency):
    """
    This function writes all the output variable information into energyplus readable string.
    
    Parameters
    ----------
    variable_name : str
        The name of the variable.
    
    report_frequency : str
        The report frequency of the variable, e.g. "Hourly", "Monthly", "Daily".
    
    Returns
    -------
    output variable data : str 
        The idf string of the output variable data.
    """
    return "! ==== OUTPUT VARIABLE\n" +\
    "Output:Variable,*," + variable_name + " ," + report_frequency + ";\n\n"

# ================================================================================
def write_outputmeter(variable_name, report_frequency):
    """
    This function writes all the output meter information into energyplus readable string.
    
    Parameters
    ----------
    variable_name : str
        The name of the variable.
    
    report_frequency : str
        The report frequency of the variable, e.g. "Hourly", "Monthly", "Daily".
    
    Returns
    -------
    output meter data : str 
        The idf string of the output meter data.
    """
    return "! ==== OUTPUT METER\n" +\
    "Output:Meter," + variable_name + " ," + report_frequency + ";\n\n"

# ================================================================================
def write_output_surfaces_drawing(drawing_type):
    """
    This function writes all the output drawing information into energyplus readable string.
    
    Parameters
    ----------
    drawing_type :  str
            The 3D model of the simulated building, e.g. "DXF". 
    
    Returns
    -------
    output drawing  data : str 
        The idf string of the output drawing data.
    """
    
    return "! ==== OUTPUT SURFACES DRAWING\n" +\
    "Output:Surfaces:Drawing," + drawing_type + ";\n\n"

# ================================================================================
def write_output_control_table_style(column_sep, unit_conversion):
    """
    This function writes all the output control table style information into energyplus readable string.
    
    Parameters
    ----------
    column_sep : str
        The style of the table, e.g. "HTML". 
            
    unit_conversion : str
        The unit conversion, e.g. JtoKWH.
    
    Returns
    -------
    table style data : str 
        The idf string of the table style data.
    """
    
    return "! ==== OUTPUT CONTROL TABLE STYLE\n" +\
    "OutputControl:Table:Style," + column_sep + " ," + unit_conversion + ";\n\n"

# ================================================================================
def write_output_table_summary_reports(report_types):
    """
    This function writes all the output table summary information into energyplus readable string.
    
    Parameters
    ----------
    report_type :  str or list of str
            The reports to be outputted after the simulation, e.g. "AllSummary".
    
    Returns
    -------
    table summary data : str 
        The idf string of the table summary data.
    """
    reports_str = "! ==== OUTPUT TABLE SUMMARY REPORTS\n"
    if isinstance(report_types, str):
        return reports_str +\
        "Output:Table:SummaryReports," + report_types + ";\n\n"
    elif isinstance(report_types, list) or isinstance(report_types, tuple):
        return reports_str +\
        "Output:Table:SummaryReports," + " ,".join(report_types) + ";\n\n"

# ================================================================================