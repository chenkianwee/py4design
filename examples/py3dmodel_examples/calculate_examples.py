import envuo

vec1 = envuo.py3dmodel.construct.make_vector((0,0,0), (0,0,1))
vec2 = envuo.py3dmodel.construct.make_vector((0,0,0), (1,0,1))
angle = envuo.py3dmodel.calculate.angle_bw_2_vecs(vec1, vec2)
print angle
