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
import construct
import calculate
import fetch
import modify
import utility

def write_2_collada(occshell_list, collada_filepath, face_rgb_colour_list=None, 
                    occedge_list = None):
    
    import collada
    from collada import asset, material, source, geometry, scene
    import numpy
    mesh = collada.Collada()
    mesh.assetInfo.upaxis = asset.UP_AXIS.Z_UP
    mesh.assetInfo.unitmeter = 1.0
    mesh.assetInfo.unitname = "meter"
    
    if face_rgb_colour_list != None:
        mat_list = []
        colour_cnt = 0
        for rgb_colour in face_rgb_colour_list:
            effect = material.Effect("effect" + str(colour_cnt), [], "phong", diffuse=rgb_colour, specular=rgb_colour, double_sided = True)
            mat = material.Material("material" + str(colour_cnt), "mymaterial" + str(colour_cnt), effect)
            mesh.effects.append(effect)
            mesh.materials.append(mat)
            mat_list.append(mat)
            colour_cnt+=1
            
    else:
        effect = material.Effect("effect0", [], "phong", diffuse=(1,1,1), specular=(1,1,1))
        mat = material.Material("material0", "mymaterial", effect)
        mesh.effects.append(effect)
        mesh.materials.append(mat)
        
    edgeeffect = material.Effect("edgeeffect0", [], "phong", diffuse=(1,1,1), specular=(1,1,1), double_sided = True)
    edgemat = material.Material("edgematerial0", "myedgematerial", effect)
    mesh.effects.append(edgeeffect)
    mesh.materials.append(edgemat)
        
    geomnode_list = []
    shell_cnt = 0
    for occshell in occshell_list:
        vert_floats = []
        normal_floats = []
        vcnt = []
        indices = []
        
        face_list = fetch.geom_explorer(occshell, "face")
        vert_cnt = 0
        for face in face_list:
            wire_list = fetch.geom_explorer(face, "wire")
            nwire = len(wire_list)
            if nwire == 1:
                pyptlist = fetch.pyptlist_frm_occface(face)
                vcnt.append(len(pyptlist))
                face_nrml = calculate.face_normal(face)
                pyptlist.reverse()
                for pypt in pyptlist:
                    vert_floats.append(pypt[0])
                    vert_floats.append(pypt[1])
                    vert_floats.append(pypt[2])
                    
                    normal_floats.append(face_nrml[0])
                    normal_floats.append(face_nrml[1])
                    normal_floats.append(face_nrml[2])
                    
                    indices.append(vert_cnt)
                    vert_cnt+=1
                    
            if nwire >1:
                tri_face_list = construct.simple_mesh(face)
                for tface in tri_face_list:
                    pyptlist = fetch.pyptlist_frm_occface(tface)
                    vcnt.append(len(pyptlist))
                    face_nrml = calculate.face_normal(tface)
                    pyptlist.reverse()
                    for pypt in pyptlist:
                        vert_floats.append(pypt[0])
                        vert_floats.append(pypt[1])
                        vert_floats.append(pypt[2])
                        
                        normal_floats.append(face_nrml[0])
                        normal_floats.append(face_nrml[1])
                        normal_floats.append(face_nrml[2])
                        
                        indices.append(vert_cnt)
                        vert_cnt+=1
                
        vert_id = "ID"+str(shell_cnt) + "1"
        vert_src = source.FloatSource(vert_id, numpy.array(vert_floats), ('X', 'Y', 'Z'))
        normal_id = "ID"+str(shell_cnt) + "2"
        normal_src = source.FloatSource(normal_id, numpy.array(normal_floats), ('X', 'Y', 'Z'))
        geom = geometry.Geometry(mesh, "geometry" + str(shell_cnt), "geometry" + str(shell_cnt), [vert_src, normal_src])
        input_list = source.InputList()
        input_list.addInput(0, 'VERTEX', "#"+vert_id)
        #input_list.addInput(1, 'NORMAL', "#"+normal_id)
        
        vcnt = numpy.array(vcnt)
        indices = numpy.array(indices)
        
        if face_rgb_colour_list!=None:
            mat_name="materialref"+ str(shell_cnt)
            polylist = geom.createPolylist(indices, vcnt, input_list,  mat_name)
            geom.primitives.append(polylist)
            mesh.geometries.append(geom)
            
            matnode = scene.MaterialNode(mat_name, mat_list[shell_cnt], inputs=[])
            geomnode = scene.GeometryNode(geom, [matnode])
            geomnode_list.append(geomnode)
        else:
            mat_name="materialref"
            polylist = geom.createPolylist(indices, vcnt, input_list,  mat_name)
            geom.primitives.append(polylist)
            mesh.geometries.append(geom)
            
            matnode = scene.MaterialNode(mat_name, mat, inputs=[])
            geomnode = scene.GeometryNode(geom, [matnode])
            geomnode_list.append(geomnode)
            
        shell_cnt +=1
        
    if occedge_list:
        edge_cnt = 0
        for occedge in occedge_list:
            vert_floats = []
            indices = []
            occpt_list = fetch.points_from_edge(occedge)
            pypt_list = fetch.occptlist2pyptlist(occpt_list)
            if len(pypt_list) == 2:
                vert_cnt = 0
                for pypt in pypt_list:
                    vert_floats.append(pypt[0])
                    vert_floats.append(pypt[1])
                    vert_floats.append(pypt[2])
                    
                    indices.append(vert_cnt)
                    vert_cnt+=1
                    
                vert_id = "ID"+str(edge_cnt+shell_cnt) + "1"
                vert_src = source.FloatSource(vert_id, numpy.array(vert_floats), ('X', 'Y', 'Z'))
                geom = geometry.Geometry(mesh, "geometry" + str(edge_cnt+ shell_cnt), "geometry" + str(edge_cnt+shell_cnt), [vert_src])
                input_list = source.InputList()
                input_list.addInput(0, 'VERTEX', "#"+vert_id)
                indices = numpy.array(indices)
                
                mat_name="edgematerialref"
                linelist = geom.createLineSet(indices, input_list,  mat_name)
                geom.primitives.append(linelist)
                mesh.geometries.append(geom)
                
                matnode = scene.MaterialNode(mat_name, edgemat, inputs=[])
                geomnode = scene.GeometryNode(geom, [matnode])
                geomnode_list.append(geomnode)
                edge_cnt+=1
        
    vis_node = scene.Node("node0", children=geomnode_list)
    myscene = scene.Scene("myscene", [vis_node])
    mesh.scenes.append(myscene)
    mesh.scene = myscene
    mesh.write(collada_filepath)
    
def write_2_collada_text_string(occshell_list, text_string, collada_filepath, 
                                face_rgb_colour_list=None, occedge_list = None):

    overall_cmpd = construct.make_compound(occshell_list)
    xmin, ymin, zmin, xmax, ymax, zmax = calculate.get_bounding_box(overall_cmpd)
    xdim = xmax-xmin
    d_str = fetch.shape2shapetype(construct.make_brep_text(text_string,xdim/10))
    xmin1, ymin1, zmin1, xmax1, ymax1, zmax1 = calculate.get_bounding_box(d_str)
    corner_pt = (xmin1,ymax1,zmin1)
    corner_pt2 = (xmin,ymin,zmin)
    moved_str = modify.move(corner_pt, corner_pt2, d_str)
    face_list = fetch.geom_explorer(moved_str, "face")
    meshed_list = []
    for face in face_list:    
        meshed_face_list = construct.simple_mesh(face)
        mface = construct.make_shell(meshed_face_list)
        face_mid_pt =  calculate.face_midpt(face)
        str_mid_pt = calculate.get_centre_bbox(mface)
        moved_mface = modify.move(str_mid_pt,face_mid_pt,mface)
        meshed_list.append(moved_mface)
    
    meshed_str_cmpd = construct.make_compound(meshed_list)
    occshell_list.append(meshed_str_cmpd)
    if face_rgb_colour_list !=None:
        face_rgb_colour_list.append((0,0,0))
        
    write_2_collada(occshell_list, collada_filepath, 
                    face_rgb_colour_list=face_rgb_colour_list, 
                    occedge_list = occedge_list)
        
def write_2_collada_falsecolour(occface_list, result_list, unit_str, dae_filepath, description_str = None, 
                                minval = None, maxval=None, other_occface_list = None, other_occedge_list = None):
    if minval == None:
        minval = min(result_list)
    if maxval == None:
        maxval = max(result_list)
        
    #FOR CREATING THE FALSECOLOUR BAR AND LABELS
    topo_cmpd = construct.make_compound(occface_list)
    xmin,ymin,zmin,xmax,ymax,zmax = calculate.get_bounding_box(topo_cmpd)
    topo_centre_pt = calculate.get_centre_bbox(topo_cmpd)
    otopo_centre_pt = (topo_centre_pt[0], topo_centre_pt[1], zmin)
    topo_cmpd = modify.move(otopo_centre_pt, (0,0,0), topo_cmpd)
    xmin,ymin,zmin,xmax,ymax,zmax = calculate.get_bounding_box(topo_cmpd)
    x_extend = xmax-xmin
    y_extend = ymax-ymin
    topo_centre_pt = calculate.get_centre_bbox(topo_cmpd)
    topo_centre_pt = (topo_centre_pt[0], topo_centre_pt[1], zmin)
    loc_pt = modify.move_pt(topo_centre_pt, (1,0,0), x_extend/1.5)
    
    grid_srfs, bar_colour, str_cmpd, str_colour_list, value_midpts = utility.generate_falsecolour_bar(minval, maxval, unit_str, y_extend, 
                                                                                              description_str = description_str, 
                                                                                              bar_pos = loc_pt)
                                                                                       
    
    #DIVIDE THE RESULT INTO 10 DIVISION LIKE THE FALSECOLOUR BAR
    falsecolour_list = []
    for result in result_list:
        if result >= maxval:
            falsecolour_list.append(bar_colour[-1])
            
        elif result <= minval:
            falsecolour_list.append(bar_colour[0])
            
        else:
            inc = (value_midpts[1]-value_midpts[0])/2.0
            ur_cnt=0
            for midpt in value_midpts:
                if midpt-inc <=result<= midpt+inc:
                    falsecolour_list.append(bar_colour[ur_cnt])
                    break
                ur_cnt+=1
    
    #ARRANGE THE SURFACE AS ACCORDING TO ITS COLOUR
    colour_list = []
    c_srf_list = []
    for r_cnt in range(len(falsecolour_list)):
        fcolour = falsecolour_list[r_cnt]
        rf = occface_list[r_cnt]
        rf = modify.move(otopo_centre_pt, (0,0,0),rf)
        if fcolour not in colour_list:
            colour_list.append(fcolour)
            c_srf_list.append([rf])
            
        elif fcolour in colour_list:
            c_index = colour_list.index(fcolour)
            c_srf_list[c_index].append(rf)
          
    cmpd_list = []
    #SORT EACH SURFACE AS A COMPOUND
    for c_cnt in range(len(c_srf_list)):
        c_srfs = c_srf_list[c_cnt]
        compound = construct.make_compound(c_srfs)
        cmpd_list.append(compound)
         
    if other_occface_list !=None:
        other_cmpd = construct.make_compound(other_occface_list)
        other_cmpd = modify.move(otopo_centre_pt, (0,0,0), other_cmpd)
        other_colour_list = [(1,1,1)]
        to_be_written_occface_list = cmpd_list + grid_srfs + [str_cmpd]+[other_cmpd]
        to_be_written_colour_list = colour_list+bar_colour+str_colour_list+other_colour_list
        
    else:
        to_be_written_occface_list = cmpd_list + grid_srfs + [str_cmpd]
        to_be_written_colour_list = colour_list+bar_colour+str_colour_list
        
    if other_occedge_list !=None:
        edge_cmpd = construct.make_compound(other_occedge_list)
        edge_cmpd = modify.move(otopo_centre_pt, (0,0,0), edge_cmpd)
        other_occedge_list = fetch.geom_explorer(edge_cmpd, "edge")
        write_2_collada(to_be_written_occface_list, dae_filepath, face_rgb_colour_list = to_be_written_colour_list, 
                        occedge_list = other_occedge_list)
    else:
        write_2_collada(to_be_written_occface_list, dae_filepath, face_rgb_colour_list = to_be_written_colour_list)