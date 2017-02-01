import pyliburo

pyptlist = [[5,5,0],[10,5,0],[10,10,0],[15,10,0],[15,5,0],[20,5,0],[20,15,0],[5,15,0]]
face = pyliburo.py3dmodel.construct.make_polygon(pyptlist)
ext = pyliburo.py3dmodel.construct.extrude(face, (0,0,1), 20)
triangulated_faces = pyliburo.py3dmodel.construct.simple_mesh(ext)

shell = pyliburo.py3dmodel.construct.make_shell_frm_faces(triangulated_faces)[0]
simplified_shell = pyliburo.py3dmodel.modify.simplify_shell(shell)
display_2dlist = []
colour_list = []
display_2dlist.append([simplified_shell])
colour_list.append("WHITE")
pyliburo.py3dmodel.construct.visualise(display_2dlist, colour_list)