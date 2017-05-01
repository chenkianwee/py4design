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
        base_surface, 
        transmittance, 
        points):

    zone_shade ="! ==== SHADING ZONE DETAILED\n"+\
    "Shading:Zone:Detailed,\n"+\
    "    "+name+",\n"+\
    "    "+base_surface+",\n"+\
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
    
    people = "" #TODO : implement the people !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
    return people
    
# ================================================================================
def write_internal_gains_other_equipment(
        zone_name,
        schedule_name,
        watts_per_m2):
        
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
    
    version_str = "! ==== VERSION\n" +\
    "Version,"+version+";\n\n"
    
    return version_str
    
# ================================================================================
def write_time_step(time_step):
    
    time_step_str = "! ==== TIME STEP\n" +\
    "Timestep,"+time_step+";\n\n"
    
    return time_step_str
    
# ================================================================================
def write_ground_temp_bldg_srf(ground_temp):
    
    ground_temp_str = "! ==== GROUND TEMP\n" +\
    "Site:GroundTemperature:BuildingSurface,"+','.join(ground_temp)+";\n\n"
    
    return ground_temp_str
    
# ================================================================================
def write_shadow_calc(calc_frequency, max_figures):
    
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
    return "! ==== OUTPUT VARIABLE\n" +\
    "Output:Variable,*," + variable_name + " ," + report_frequency + ";\n\n"

# ================================================================================
def write_outputmeter(variable_name, report_frequency):
    return "! ==== OUTPUT METER\n" +\
    "Output:Meter," + variable_name + " ," + report_frequency + ";\n\n"

# ================================================================================
def write_output_surfaces_drawing(drawing_type):
    return "! ==== OUTPUT SURFACES DRAWING\n" +\
    "Output:Surfaces:Drawing," + drawing_type + ";\n\n"

# ================================================================================
def write_output_control_table_style(column_sep, unit_conversion):
    return "! ==== OUTPUT CONTROL TABLE STYLE\n" +\
    "OutputControl:Table:Style," + column_sep + " ," + unit_conversion + ";\n\n"

# ================================================================================
def write_output_table_summary_reports(report_types):
    reports_str = "! ==== OUTPUT TABLE SUMMARY REPORTS\n"
    if isinstance(report_types, str):
        return reports_str +\
        "Output:Table:SummaryReports," + report_types + ";\n\n"
    elif isinstance(report_types, list) or isinstance(report_types, tuple):
        return reports_str +\
        "Output:Table:SummaryReports," + " ,".join(report_types) + ";\n\n"

# ================================================================================