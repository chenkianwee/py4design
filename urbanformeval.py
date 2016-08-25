from . import py3dmodel

def calculate_srfs_area(occ_srflist):
    area = 0
    for srf in occ_srflist:
        area = area + py3dmodel.calculate.face_area(srf)
    return area
    
def frontal_area_index(facet_pypolygons, plane_pypolgon, wind_dir):
    #loop thru all the polygons and change them to pythonocc objects
    facet_faces = []
    for pypolgyon in facet_pypolygons:
       facet_face = py3dmodel.construct.make_polygon(pypolgyon)
       facet_faces.append(facet_face)
       

    facet_faces_compound = py3dmodel.construct.make_compound(facet_faces)
     
    #create win dir plane
    #get the bounding box of the compound, so that the wind plane will be placed at the edge of the bounding box
    xmin, ymin, zmin, xmax, ymax, zmax = py3dmodel.calculate.get_bounding_box(facet_faces_compound)
    pymidpt = py3dmodel.calculate.get_centre_bbox(facet_faces_compound)
    #calculate the furthest distance of the bounding box
    pycornerpt = (xmin, ymin, 0)
    
    furtherest_dist = py3dmodel.calculate.distance_between_2_pts(pymidpt, pycornerpt)
    #create the wind plane 
    pt4plane = py3dmodel.modify.move_pt(pymidpt, wind_dir, furtherest_dist) 
    wind_plane = py3dmodel.construct.make_plane_w_dir(pt4plane, wind_dir)
    
    surfaces_projected = []
    projected_facet_faces = []
    for facet_face in facet_faces:
        srf_dir = py3dmodel.calculate.face_normal(facet_face)
        #srf_midpt = py3dmodel.calculate.face_midpt(urb_face)
        angle = py3dmodel.calculate.angle_bw_2_vecs(wind_dir, srf_dir)
        #interpt, interface = py3dmodel.calculate.intersect_shape_with_ptdir(wind_plane, srf_midpt, srf_dir)
        if angle<90:
            surfaces_projected.append(facet_face)
            projected_pts = py3dmodel.calculate.project_face_on_faceplane(wind_plane, facet_face)
            projected_srf = py3dmodel.construct.make_polygon(projected_pts)
            if py3dmodel.calculate.face_area(projected_srf) >0:
                projected_facet_faces.append(projected_srf)
         
    npfaces = len(projected_facet_faces)
    if npfaces == 1:
        fuse_srfs = projected_facet_faces
    else:
        for psrf_cnt in range(npfaces-1):
            if psrf_cnt ==0:
                fuse_shape = py3dmodel.construct.boolean_fuse(projected_facet_faces[psrf_cnt], projected_facet_faces[psrf_cnt+1])
            else:
                fuse_shape = py3dmodel.construct.boolean_fuse(fuse_shape, projected_facet_faces[psrf_cnt+1])
                
        fuse_compound = py3dmodel.fetch.shape2shapetype(fuse_shape) 
        fuse_srfs = py3dmodel.fetch.geom_explorer(fuse_compound,"face")
    
    #calculate the frontal area index
    facet_area = calculate_srfs_area(fuse_srfs)
    plane_polygon = py3dmodel.construct.make_polygon(plane_pypolgon)
    plane_area = py3dmodel.calculate.face_area(plane_polygon)
    fai = facet_area/plane_area
    
    return fai, fuse_srfs, projected_facet_faces, wind_plane, surfaces_projected
    
def public_transport_usability_index():
    